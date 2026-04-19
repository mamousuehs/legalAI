# 法学素材样例模板

这个目录提供一套可直接交给法学同学填写的 Excel 模板，服务于 TaoxinAI 的“分阶段法律论证系统”。

包含文件：

- `norms_template.xlsx`
  说明：法条规范素材模板
- `cases_template.xlsx`
  说明：案例素材模板
- `issue_templates_template.xlsx`
  说明：争点模板
- `element_templates_template.xlsx`
  说明：要件模板
- `evidence_matrix_template.xlsx`
  说明：证据矩阵模板
- `verification_rules_template.xlsx`
  说明：验证规则模板
- `document_template_example.md`
  说明：文书模板示例

建议使用方式：

1. 法学同学先按这些 Excel 表头填写。
2. 后端同学再把其中规则类表格转换成 YAML 或导入脚本使用的结构。
3. 不要在一个文档里混合“法条原文、场景说明、办案笔记、自由评论”，尽量一行只表达一个结构化单元。

填写约定：

- 多值字段统一用 `;` 分隔。
- `issue_code`、`element_code`、`norm_id`、`case_id` 尽量保持稳定，不要频繁改名。
- `required` 建议使用 `true` 或 `false`。
- `strength` 建议使用 `high`、`medium`、`low`。
- `status_rule`、`severity` 先按示例填写，后续可再细化。
