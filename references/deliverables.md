# Deliverables and quality checks

Read this reference when producing the final software-onboarding package.

## Required outputs

The final package must contain:

1. 软件整体介绍
2. 功能模块地图
3. API完整清单
4. API按业务模块分类
5. API详细说明
6. API依赖关系
7. 认证机制分析
8. 风险接口清单
9. 研发确认问题清单
10. 产品经理需要重点理解的内容
11. 从整体到细节的学习路线

## API inventory columns

Keep one operation per primary inventory row. Include:

- inventory number;
- normalized business module and classification basis;
- original Tag or `无Tag`;
- API name, summary, description, and product-language explanation;
- explanation evidence level;
- HTTP method, Path, full documented Path, and operationId;
- Path, Query, Header, Cookie, Form, and Request Body summaries;
- required parameters, types, formats, enum values, and defaults;
- response descriptions, response schemas, status codes, and content types;
- authentication conclusion;
- data-impact class and risk rationale;
- prerequisites and dependency notes;
- deprecated status;
- documentation-quality notes.

Use separate parameter and response detail tables when flattening them into one cell would lose information.

## Suggested workbook structure

For large definitions, prefer these searchable sheets:

- `总览`
- `API完整清单`
- `参数明细`
- `响应明细`
- `模块统计`
- `风险接口`
- `接口关系`
- `研发确认`
- `数据模型`

Freeze headers, enable filters, wrap long text, and preserve source URLs on the overview sheet. Avoid formulas unless they materially improve usability.

## Knowledge-map structure

Use a compact tree:

```text
软件
├── 业务模块
│   ├── 功能或原始Tag
│   │   ├── METHOD /path — API名称
│   │   └── ...
│   └── ...
└── ...
```

For very large modules, show representative operations in the narrative map and point to the complete inventory. Do not imply that representative operations are the whole module.

## Developer-confirmation checklist

Generate evidence-backed questions covering:

- unclear API or parameter descriptions;
- undocumented ID sources and prerequisites;
- ambiguous authentication and token propagation;
- lifecycle/state-transition gaps;
- missing response and error models;
- duplicate or competing endpoints;
- deprecated endpoints and replacements;
- state-changing GET operations;
- multiple body parameters or other spec violations;
- generic Paths that may have lost service prefixes;
- standard-product versus customer-specific boundaries;
- Swagger-to-deployment and Swagger-to-UI differences.

Each question should contain the evidence, likely impact, and the exact decision needed from engineering.

## Final verification

Before delivery, verify:

- Path and Operation counts are both stated and not confused;
- method totals sum to the Operation total;
- the inventory key set exactly matches the source key set;
- security conclusions reflect declarations rather than guesses;
- every inference is labeled;
- every write-risk operation is listed;
- state-changing GET candidates are listed separately;
- no business endpoint was called during phase one;
- the user can find the exhaustive inventory without reading the narrative report line by line.
