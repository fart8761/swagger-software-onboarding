# Swagger Software Onboarding

A reusable Codex skill for understanding unfamiliar software from both product-manager and developer perspectives, using Swagger/OpenAPI as the primary source.

中文简介：这是一个“先理解、后测试”的软件熟悉与 API 梳理 Skill。它会完整盘点 Swagger/OpenAPI 接口、按业务模块重新分类、解释业务用途、分析依赖与认证、识别写操作风险，并生成研发确认清单和学习路线。

## What it produces

- Software and product overview
- Functional module and knowledge maps
- Exhaustive API operation inventory
- Parameter, request-body, response, and schema details
- Business-oriented explanation for every operation
- API relationships and prerequisites
- Authentication analysis
- State-changing and deletion-risk inventory
- Documentation-quality findings
- Engineering confirmation questions
- A learning route from product concepts to implementation details

## Safety model

The first phase is documentation-only:

- Downloads and parses Swagger/OpenAPI definitions
- Does not call documented business endpoints
- Does not call POST, PUT, PATCH, or DELETE operations
- Does not guess credentials, tokens, identifiers, or parameters
- Labels every inference and undocumented point
- Treats real endpoint testing as a separately authorized phase

## Install

Copy this repository into your Codex skills directory:

```text
~/.codex/skills/swagger-software-onboarding
```

Restart or refresh Codex if the skill does not appear immediately.

## Use

Invoke it explicitly:

```text
Use $swagger-software-onboarding to analyze this software and its Swagger/OpenAPI documentation without calling business APIs.
```

Then provide the product URL, Swagger UI URL, or a local OpenAPI JSON/YAML file.

## Read-only inventory script

The included script extracts a local definition into CSV and JSON artifacts without making network requests:

```bash
python scripts/openapi_inventory.py \
  --input ./openapi.json \
  --output-dir ./outputs
```

Outputs:

- `api_inventory.csv`
- `parameters.csv`
- `responses.csv`
- `summary.json`

JSON works with the Python standard library. YAML input additionally requires PyYAML.

## Repository structure

```text
swagger-software-onboarding/
├── SKILL.md
├── agents/openai.yaml
├── references/deliverables.md
└── scripts/openapi_inventory.py
```

The skill instructions are in `SKILL.md`. The detailed output contract is in `references/deliverables.md`.

## License

Released under the [MIT License](LICENSE).

