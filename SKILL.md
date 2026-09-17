---
name: swagger-software-onboarding
description: Analyze unfamiliar software from product-manager and developer perspectives using Swagger/OpenAPI as the primary source. Use when the user wants a complete software overview, exhaustive API inventory, business-module mapping, dependency and authentication analysis, write-risk review, knowledge map, developer questions, or a learning route. This skill is for read-only discovery first; it does not test business endpoints or modify the software unless the user separately authorizes a later phase.
---

# Swagger Software Onboarding

Build an evidence-based understanding of an unfamiliar software product before implementation or integration work begins.

## Operating boundary

- Treat the supplied Swagger/OpenAPI definition, product documentation, and visible product UI as the sources of truth.
- During the first phase, retrieve documentation assets only. Do not invoke documented business operations, including GET operations, merely to inspect responses.
- Do not call POST, PUT, PATCH, or DELETE operations. Do not guess IDs, credentials, tokens, parameters, enum values, or undocumented behavior.
- Do not modify the user's application project.
- A documentation URL such as `swagger.json`, `openapi.json`, `doc.json`, or `doc.yaml` may be downloaded and parsed. This is not a business-endpoint test.
- Keep facts, document-derived interpretation, and inference visibly separate. Label uncertainty as `文档未说明`, `推测`, or `需要研发确认`.
- If the product page requires authentication and no suitable read-only access is available, stop at the login boundary and record the UI-to-API mapping as unverified.

## Workflow

### 1. Establish sources and scope

Record every supplied URL or file, the analysis date, reachable documentation definition, Swagger/OpenAPI version, title, version, host/server list, and base path.

Prefer the machine-readable definition over scraping Swagger UI. Locate it through the UI configuration or conventional documentation assets, but do not probe business endpoints.

State explicitly what was and was not accessed.

### 2. Parse the complete definition

Count unique Paths and Operations separately. Include every HTTP operation under every Path.

For repeatable extraction, use `scripts/openapi_inventory.py` when the definition is available as a local JSON or YAML file. Read the script help before running it. The script only reads the definition and writes analysis artifacts.

For each operation retain:

- name, summary, description, operationId;
- method, path, full documented path, tags;
- path, query, header, cookie, form, and request-body parameters;
- required flags, types, formats, enums, defaults, descriptions, and schemas;
- response status codes, descriptions, headers, content types, and schemas;
- operation-level and global security requirements;
- deprecation state and relevant vendor extensions.

Resolve references enough to make request and response models understandable, but also preserve raw `$ref` or schema data for traceability.

### 3. Verify inventory completeness

Recount Operations independently from the generated inventory and compare the two sets using `METHOD + PATH` as the key.

Completion requires:

- source count equals inventory count;
- no missing or extra operation keys;
- every operation has an authentication conclusion, data-impact label, and product-language explanation;
- every parameter and response remains traceable to an operation.

Do not claim completeness if these checks fail.

### 4. Understand the software as a product

Explain, using only documented evidence:

- what the software does;
- which business problems it addresses;
- functional modules and relationships;
- primary user-facing capabilities;
- likely core versus supporting capabilities;
- the main product workflow.

When a workflow or module boundary is inferred from names, paths, or CRUD shape, mark it as inference rather than official product structure.

### 5. Reclassify APIs by business capability

Do not merely repeat Swagger order or Tags. Build one normalized business-module classification from the actual Tags, Paths, summaries, descriptions, operationIds, and schemas.

Always retain the original Tag and record why the normalized classification was chosen. Use `待确认` when evidence is insufficient. Keep customer-specific or deployment-specific extensions distinct from standard platform capabilities when the documentation suggests that distinction.

### 6. Explain every API in product language

For each operation answer: `这个接口解决什么业务问题？`

Prefer explicit descriptions. If only a summary exists, explain no more than that summary supports and state that the concrete scenario or boundary is undocumented. If neither exists, write: `根据当前文档无法完全确定，需要研发确认。`

Do not use a generic explanation such as “这是一个GET请求”.

### 7. Analyze relationships and prerequisites

Separate relationship confidence:

- `文档明确`: linked by explicit descriptions or schemas;
- `高可信推测`: clear list/detail/create/update/delete or nested-resource structure;
- `推测`: inferred from names or conventional product behavior.

Identify prerequisites such as required identifiers, parent resources, templates, tasks, sessions, credentials, and state transitions. Never invent an identifier source. If an ID source is not documented, say so.

### 8. Analyze authentication

Inspect Swagger 2 `securityDefinitions` and OpenAPI 3 `components.securitySchemes`, plus global and operation-level `security`.

Report only declared mechanisms: Bearer/OAuth2, API key, Basic, Cookie, mutual TLS, OpenID Connect, or custom headers. Login or token endpoints are clues, not proof of how all business APIs authenticate.

If schemes or requirements are absent, use: `目前无法从Swagger确定认证方式，需要研发确认。`

### 9. Identify risky operations

Classify operations conservatively:

- GET/HEAD normally `只读接口`, unless the path or description indicates refresh, sync, clear, load, execute, confirm, generate, start, stop, or another side effect;
- POST/PUT/PATCH normally `可能修改数据`, even if the summary sounds query-like;
- DELETE normally `可能删除数据`;
- ambiguous method/description combinations require confirmation.

List state-changing GET operations separately. Do not invoke any risk operation during phase one.

### 10. Audit documentation quality

Check at least:

- missing summaries, descriptions, Tags, response schemas, or error responses;
- missing or mismatched path parameters;
- duplicate operationIds;
- Swagger 2 operations with multiple body parameters;
- generic or apparently prefix-stripped Paths;
- deprecated wording without a deprecation flag;
- unsafe method semantics, such as state-changing GET;
- missing security declarations;
- unclear IDs, enums, units, timestamps, statuses, and lifecycle fields;
- possible mismatch between Swagger version and deployed UI.

Turn these findings into specific questions for product or engineering.

### 11. Produce the deliverables

Read [references/deliverables.md](references/deliverables.md) before authoring the final report or workbook.

For large definitions, do not place the exhaustive inventory only in chat. Create a searchable workbook or CSV/JSON package plus a readable report. Keep generated analysis outside the user's application project unless the user requests another location.

### 12. Close with a learning route

Recommend a progression from product boundary to core domain objects, collection/discovery, monitoring and alert lifecycle, risky operational workflows, permissions/authentication, supporting modules, and finally customer-specific extensions.

Do not recommend real endpoint testing until the unresolved authentication, environment, and safety questions have been reviewed.

## Phase-two boundary

Real API testing is a separate task. Before any later test, define the environment, read-only account, approved endpoints, credentials handling, expected response, rate limits, and cleanup requirements. Obtain explicit authorization before any state-changing request.
