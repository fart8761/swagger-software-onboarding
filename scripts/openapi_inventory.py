#!/usr/bin/env python3
"""Extract a read-only OpenAPI/Swagger operation inventory.

The script reads a local JSON or YAML definition and writes CSV/JSON artifacts.
It never makes network requests and never invokes documented API operations.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


HTTP_METHODS = {"get", "post", "put", "patch", "delete", "head", "options", "trace"}


def load_definition(source: Path) -> dict[str, Any]:
    text = source.read_text(encoding="utf-8-sig")
    if source.suffix.lower() == ".json" or text.lstrip().startswith(("{", "[")):
        return json.loads(text)
    try:
        import yaml  # type: ignore
    except ImportError as exc:
        raise SystemExit(
            "YAML input requires PyYAML. Use the JSON variant of the same OpenAPI definition "
            "or install PyYAML in an isolated analysis environment."
        ) from exc
    data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise SystemExit("The definition root must be an object.")
    return data


def ref_name(ref: str | None) -> str:
    return ref.rsplit("/", 1)[-1] if ref else ""


def schema_label(schema: Any) -> str:
    if not isinstance(schema, dict) or not schema:
        return "文档未说明"
    if "$ref" in schema:
        return ref_name(schema["$ref"])
    if "allOf" in schema:
        return " & ".join(schema_label(item) for item in schema["allOf"])
    if "oneOf" in schema:
        return "oneOf<" + " | ".join(schema_label(item) for item in schema["oneOf"]) + ">"
    if "anyOf" in schema:
        return "anyOf<" + " | ".join(schema_label(item) for item in schema["anyOf"]) + ">"
    if schema.get("type") == "array" or "items" in schema:
        return f"array<{schema_label(schema.get('items', {}))}>"
    if schema.get("type") == "object" or "properties" in schema:
        props = list((schema.get("properties") or {}).keys())
        shown = ", ".join(props[:12])
        return "object{" + shown + (", …" if len(props) > 12 else "") + "}"
    result = schema.get("type", "文档未说明")
    if schema.get("format"):
        result += f"; format={schema['format']}"
    if schema.get("enum"):
        result += "; enum=" + "|".join(map(str, schema["enum"]))
    return result


def parameter_schema(parameter: dict[str, Any]) -> dict[str, Any]:
    if isinstance(parameter.get("schema"), dict):
        return parameter["schema"]
    return {key: parameter[key] for key in ("type", "format", "items", "enum", "default") if key in parameter}


def security_schemes(doc: dict[str, Any]) -> dict[str, Any]:
    if doc.get("swagger"):
        return doc.get("securityDefinitions") or {}
    return ((doc.get("components") or {}).get("securitySchemes") or {})


def request_bodies(operation: dict[str, Any]) -> list[dict[str, Any]]:
    body = operation.get("requestBody")
    if not isinstance(body, dict):
        return []
    rows = []
    for content_type, media in (body.get("content") or {}).items():
        rows.append({
            "name": "requestBody",
            "in": "body",
            "required": bool(body.get("required")),
            "description": body.get("description", ""),
            "content_type": content_type,
            "schema": (media or {}).get("schema") or {},
        })
    if not rows:
        rows.append({
            "name": "requestBody", "in": "body", "required": bool(body.get("required")),
            "description": body.get("description", ""), "content_type": "", "schema": {},
        })
    return rows


def response_content(response: dict[str, Any]) -> list[tuple[str, dict[str, Any]]]:
    if isinstance(response.get("content"), dict):
        return [(content_type, (media or {}).get("schema") or {}) for content_type, media in response["content"].items()]
    return [("", response.get("schema") or {})]


def collect(doc: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    operations: list[dict[str, Any]] = []
    parameters: list[dict[str, Any]] = []
    responses: list[dict[str, Any]] = []
    global_security = doc.get("security")
    base_path = doc.get("basePath", "")
    servers = doc.get("servers") or []
    server_base = servers[0].get("url", "") if servers and isinstance(servers[0], dict) else ""

    for api_path, path_item in (doc.get("paths") or {}).items():
        if not isinstance(path_item, dict):
            continue
        path_parameters = path_item.get("parameters") or []
        for method, operation in path_item.items():
            if method.lower() not in HTTP_METHODS or not isinstance(operation, dict):
                continue
            op_key = f"{method.upper()} {api_path}"
            op_parameters = [*path_parameters, *(operation.get("parameters") or []), *request_bodies(operation)]
            security = operation["security"] if "security" in operation else global_security
            response_map = operation.get("responses") or {}
            operations.append({
                "operation_key": op_key,
                "method": method.upper(),
                "path": api_path,
                "full_documented_path": server_base + api_path if server_base else base_path + api_path,
                "tags": "; ".join(operation.get("tags") or []),
                "summary": operation.get("summary", ""),
                "description": operation.get("description", ""),
                "operation_id": operation.get("operationId", ""),
                "deprecated": bool(operation.get("deprecated")),
                "security": json.dumps(security, ensure_ascii=False) if security is not None else "文档未说明",
                "parameter_count": len(op_parameters),
                "response_codes": "; ".join(map(str, response_map.keys())),
                "consumes": "; ".join(operation.get("consumes") or doc.get("consumes") or []),
                "produces": "; ".join(operation.get("produces") or doc.get("produces") or []),
            })
            for parameter in op_parameters:
                if not isinstance(parameter, dict):
                    continue
                schema = parameter_schema(parameter)
                parameters.append({
                    "operation_key": op_key, "method": method.upper(), "path": api_path,
                    "location": parameter.get("in", "文档未说明"),
                    "name": parameter.get("name", "文档未说明"),
                    "description": parameter.get("description", ""),
                    "required": bool(parameter.get("required")),
                    "type": schema_label(schema),
                    "enum": json.dumps(schema.get("enum", ""), ensure_ascii=False),
                    "default": json.dumps(schema.get("default", ""), ensure_ascii=False),
                    "content_type": parameter.get("content_type", ""),
                    "schema": json.dumps(schema, ensure_ascii=False),
                })
            for status, response in response_map.items():
                response = response if isinstance(response, dict) else {}
                for content_type, schema in response_content(response):
                    responses.append({
                        "operation_key": op_key, "method": method.upper(), "path": api_path,
                        "status": status, "description": response.get("description", ""),
                        "content_type": content_type, "schema_label": schema_label(schema),
                        "schema": json.dumps(schema, ensure_ascii=False),
                        "headers": json.dumps(response.get("headers") or {}, ensure_ascii=False),
                    })
    return operations, parameters, responses


def write_csv(target: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        target.write_text("", encoding="utf-8-sig")
        return
    with target.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract a read-only OpenAPI/Swagger inventory from a local definition.")
    parser.add_argument("--input", required=True, type=Path, help="Local OpenAPI JSON or YAML file")
    parser.add_argument("--output-dir", required=True, type=Path, help="Directory for generated analysis files")
    args = parser.parse_args()

    doc = load_definition(args.input)
    operations, parameters, responses = collect(doc)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_csv(args.output_dir / "api_inventory.csv", operations)
    write_csv(args.output_dir / "parameters.csv", parameters)
    write_csv(args.output_dir / "responses.csv", responses)

    methods: dict[str, int] = {}
    for operation in operations:
        methods[operation["method"]] = methods.get(operation["method"], 0) + 1
    keys = [operation["operation_key"] for operation in operations]
    summary = {
        "spec_version": doc.get("swagger") or doc.get("openapi") or "文档未说明",
        "title": (doc.get("info") or {}).get("title", "文档未说明"),
        "api_version": (doc.get("info") or {}).get("version", "文档未说明"),
        "path_count": len(doc.get("paths") or {}),
        "operation_count": len(operations),
        "unique_operation_key_count": len(set(keys)),
        "method_counts": methods,
        "security_schemes": security_schemes(doc),
        "global_security": doc.get("security", "文档未说明"),
        "definition_count": len(doc.get("definitions") or (doc.get("components") or {}).get("schemas") or {}),
        "parameter_row_count": len(parameters),
        "response_row_count": len(responses),
        "network_requests_made": 0,
    }
    (args.output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

