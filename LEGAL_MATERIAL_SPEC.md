# 法学素材整理规范与导入说明

## 1. 这份文档解决什么问题

这份文档是给法学同学、后端同学和项目负责人共同使用的工作说明。它回答四个核心问题：

1. 法学同学需要整理什么素材。
2. 素材应该整理成什么结构，才能服务“分阶段法律论证系统”，而不是普通 RAG 问答。
3. 这些素材如何被当前仓库导入。
4. 目前已经整理的 `法条适用.docx` 和 `涉欠薪典型案例汇总.xlsx` 哪些地方有价值，哪些地方还不符合要求。

本项目当前目标不是“把法条和案例喂给模型，让模型自由回答”，而是做一个可解释、可验证、分阶段推进的讨薪法律论证系统。因此，法学素材不能只是一堆文本，还要带有结构化字段，能够支撑：

- 检索层：法条、案例、模板召回
- 争点识别层
- 事实抽取层
- 要件匹配层
- 理由构建层
- IRAC 文本生成层
- 验证层

## 2. 法学同学需要整理的素材类型

建议法学同学整理 4 大类素材。

### 2.1 法条规范素材

用途：

- 给检索层召回法条
- 给要件匹配层提供法律依据
- 给理由构建和 IRAC 生成提供引用来源

最低应包含：

- 法律名称
- 条文编号
- 条文原文
- 适用场景
- 对应争点
- 对应要件
- 证明方向

典型例子：

- 《保障农民工工资支付条例》第三十条
- 《劳动合同法》第八十二条
- 《劳动争议调解仲裁法》关于仲裁前置的规定

### 2.2 案例素材

用途：

- 给检索层召回类案
- 给理由构建层提供“法院/实践怎么处理”的经验支持
- 给模板层提供“哪些事实组合对应哪些处理路径”

最低应包含：

- 案例标题
- 案件类型
- 争点
- 关键事实
- 裁判/处理结论
- 结论理由摘要
- 可借鉴规则
- 适用前提

注意：

案例不是只存“故事”或“办案经验”。对论证系统来说，最重要的是“在什么事实前提下，支持了什么结论，依据是什么”。

### 2.3 规则/模板素材

用途：

- 给争点识别层提供 issue template
- 给要件匹配层提供 element template
- 给验证层提供 completeness / consistency / citation 规则
- 给文书生成层提供固定结构模板

最低应包含：

- 争点编码
- 争点名称
- 要件列表
- 每个要件需要什么事实支持
- 每个要件可接受哪些证据
- 风险提示
- 常见反方抗辩

### 2.4 证据与事实抽取提示素材

用途：

- 告诉系统“哪些话属于金额、哪些话属于主体、哪些话属于证据”
- 告诉系统“哪些证据可以支持哪个要件”

最低应包含：

- 证据类型
- 证据名称
- 可证明事项
- 证明力强弱
- 常见瑕疵
- 替代证据

这部分非常适合由法学同学整理，后端同学再把它转成 YAML 规则包。

## 3. 素材文件结构

在仓库里新建一个素材目录，比如：

```text
materials/
  norms/
    norms.xlsx
  cases/
    cases.xlsx
  rule_packs/
    issue_templates.xlsx
    element_templates.xlsx
    evidence_matrix.xlsx
    verification_rules.xlsx
  document_templates/
    arbitration_application.md
    complaint.md
```

最小可行版本也可以先按下面方式：

- 一个 `norms.xlsx`
- 一个 `cases.xlsx`
- 一个 `issue_element_rules.xlsx`
- 一个 `evidence_matrix.xlsx`

这样已经比“一个 docx + 一个经验表”更适合系统导入。

## 4. 推荐字段设计

下面给的是适合当前 TaoxinAI 主线架构的字段设计。不是所有字段第一天都要填满，但表头最好一次定好。

### 4.1 法条表 `norms.xlsx`

建议字段：

| 字段名 | 是否必填 | 含义 |
|---|---|---|
| norm_id | 是 | 法条唯一 ID，例如 `norm_gzzl_30` |
| law_name | 是 | 法律/法规名称 |
| article_no | 是 | 条号，例如“第三十条” |
| article_title | 否 | 条文小标题，没有可空 |
| article_text | 是 | 条文原文 |
| scenario | 是 | 适用场景，例如“违法分包欠薪”“未签合同欠薪” |
| issue_codes | 是 | 对应争点编码，多个用 `;` 分隔 |
| element_codes | 否 | 对应要件编码，多个用 `;` 分隔 |
| effect | 否 | 条文支持什么结论，例如“总包先行清偿” |
| source_level | 否 | 法律、行政法规、司法解释、地方规定 |
| keywords | 否 | 检索关键词，多个用 `;` 分隔 |
| notes | 否 | 法学同学补充备注 |

示例：

| norm_id | law_name | article_no | article_text | scenario | issue_codes | effect |
|---|---|---|---|---|---|---|
| norm_gzzl_30 | 保障农民工工资支付条例 | 第三十条 | 分包单位拖欠农民工工资的，由施工总承包单位先行清偿，再依法进行追偿。 | 违法分包/转包欠薪 | unpaid_wages;liable_subject | 总包先行清偿 |

### 4.2 案例表 `cases.xlsx`

建议字段：

| 字段名 | 是否必填 | 含义 |
|---|---|---|
| case_id | 是 | 案例唯一 ID |
| case_title | 是 | 案件标题 |
| case_type | 是 | 劳动争议 / 劳务合同纠纷 / 执行案件等 |
| procedure_stage | 否 | 仲裁 / 一审 / 二审 / 执行 |
| court_or_source | 否 | 法院或案例来源 |
| issue_codes | 是 | 对应争点编码 |
| facts_summary | 是 | 关键事实摘要 |
| claimant_position | 否 | 劳动者/申请人的核心主张 |
| respondent_position | 否 | 用工方/被申请人的主要抗辩 |
| decision_summary | 是 | 裁判结果/处理结果 |
| reasoning_summary | 是 | 裁判理由摘要 |
| applicable_conditions | 否 | 适用该案例经验的前提 |
| risk_points | 否 | 不宜机械套用的风险 |
| evidence_focus | 否 | 该案关键证据 |
| keywords | 否 | 检索关键词 |

示例：

| case_id | case_title | case_type | issue_codes | facts_summary | decision_summary | reasoning_summary |
|---|---|---|---|---|---|---|
| case_exec_001 | 黄某某等31人与谢某某劳务合同纠纷执行案 | 劳务合同纠纷/执行 | unpaid_wages;execution_path | 劳务报酬未支付，进入执行程序，被执行人资金周转困难。 | 达成执行和解，先付部分款项，剩余分期履行。 | 在直接强制执行效果有限时，通过执行和解提高兑现率。 |

### 4.3 争点模板表 `issue_templates.xlsx`

建议字段：

| 字段名 | 是否必填 | 含义 |
|---|---|---|
| issue_code | 是 | 争点编码 |
| issue_name | 是 | 争点名称 |
| description | 是 | 争点说明 |
| trigger_keywords | 否 | 触发关键词，多个用 `;` 分隔 |
| priority | 否 | 优先级 |
| typical_questions | 否 | 系统可向用户追问的问题 |
| related_norms | 否 | 关联法条 ID |
| related_elements | 否 | 关联要件编码 |

示例：

| issue_code | issue_name | description | trigger_keywords |
|---|---|---|---|
| unpaid_wages | 是否存在拖欠劳动报酬 | 判断是否存在欠薪事实及金额范围。 | 欠薪;拖欠工资;没发工资;工资没结 |

### 4.4 要件模板表 `element_templates.xlsx`

建议字段：

| 字段名 | 是否必填 | 含义 |
|---|---|---|
| issue_code | 是 | 所属争点 |
| element_code | 是 | 要件编码 |
| element_name | 是 | 要件名称 |
| required | 是 | 是否必备 |
| proof_target | 是 | 该要件需要证明什么 |
| preferred_evidence | 否 | 优先证据 |
| fallback_evidence | 否 | 替代证据 |
| common_defense | 否 | 常见抗辩 |
| notes | 否 | 备注 |

示例：

| issue_code | element_code | element_name | required | proof_target | preferred_evidence |
|---|---|---|---|---|---|
| labor_relationship | relationship_proof | 是否能证明劳动/劳务关系 | 是 | 证明申请人与被申请人之间存在实际用工关系 | 劳动合同;考勤记录;工作群聊天;工牌;工友证言 |

### 4.5 证据矩阵表 `evidence_matrix.xlsx`

建议字段：

| 字段名 | 是否必填 | 含义 |
|---|---|---|
| evidence_code | 是 | 证据编码 |
| evidence_name | 是 | 证据名称 |
| evidence_type | 是 | 书证 / 电子数据 / 证人证言等 |
| proves_elements | 是 | 可证明的要件编码 |
| proves_facts | 否 | 可证明的事实类型 |
| strength | 否 | 强 / 中 / 弱 |
| common_risks | 否 | 常见瑕疵 |
| fallback_options | 否 | 替代证据 |

示例：

| evidence_code | evidence_name | evidence_type | proves_elements | strength | common_risks |
|---|---|---|---|---|---|
| ev_chat_salary | 微信催款聊天记录 | 电子数据 | wage_fact;relationship_proof | 中 | 身份关联不明、上下文缺失 |

## 5. 与当前代码如何对应

我们现在的 TaoxinAI 主线已经有这些结构：

- 争点：`[TaoxinAI/schemas/issue.py](D:/legal/legalAI/TaoxinAI/schemas/issue.py:1)`
- 事实：`[TaoxinAI/schemas/fact.py](D:/legal/legalAI/TaoxinAI/schemas/fact.py:1)`
- 要件匹配：`[TaoxinAI/schemas/match.py](D:/legal/legalAI/TaoxinAI/schemas/match.py:1)`
- 检索结果：`[TaoxinAI/schemas/retrieval.py](D:/legal/legalAI/TaoxinAI/schemas/retrieval.py:1)`

这意味着法学素材不应该只整理成“阅读方便”，而要能被映射成下面这些对象：

- `Issue`
- `FactItem`
- `ElementMatch`
- `RetrievedAuthority`

换句话说，法学同学整理的材料，最好能直接回答下面这些问题：

1. 这条材料对应哪个争点 `issue_code`？
2. 这条材料支持哪个要件 `element_code`？
3. 这条材料适用于什么场景？
4. 它支持什么结论？
5. 它需要什么事实和证据才能成立？

如果法学素材无法回答这几个问题，那它更像“知识笔记”，还不够成为系统可消费的规则素材。

## 6. 当前仓库如何导入这些素材

### 6.1 当前已经能导入什么

当前仓库里已经有两个基础导入脚本：

- `[TaoxinAI/data_import/import_norms.py](D:/legal/legalAI/TaoxinAI/data_import/import_norms.py:1)`
- `[TaoxinAI/data_import/import_cases.py](D:/legal/legalAI/TaoxinAI/data_import/import_cases.py:1)`

当前能力大致是：

- 从 `docx` 中切分法条文本，导入 `laws`
- 从 `xlsx` 中读取案例摘要，导入 `cases`

这适合“先把资料放进去，支持初步检索”，但还不够支撑分阶段论证系统。

### 6.2 现阶段推荐的导入方式

建议按三层导入：

1. 文本检索层
   - 法条表导入 `laws` collection
   - 案例表导入 `cases` collection

2. 本地规则层
   - 争点模板转成 `issue_templates.yaml`
   - 要件模板转成 `element_templates.yaml`
   - 验证规则转成 `verification_rules.yaml`

3. 文书模板层
   - 仲裁申请书、起诉状等保持 `md/txt` 模板


- `norms.xlsx` -> 新增或重写 `import_norms.py`
- `cases.xlsx` -> 新增或重写 `import_cases.py`
- `issue_templates.xlsx` -> 手动或脚本转换为 `[TaoxinAI/templates/taoxin/issue_templates.yaml](D:/legal/legalAI/TaoxinAI/templates/taoxin/issue_templates.yaml:1)`
- `element_templates.xlsx` -> 手动或脚本转换为 `[TaoxinAI/templates/taoxin/element_templates.yaml](D:/legal/legalAI/TaoxinAI/templates/taoxin/element_templates.yaml:1)`
- `verification_rules.xlsx` -> 转为 `[TaoxinAI/templates/taoxin/verification_rules.yaml](D:/legal/legalAI/TaoxinAI/templates/taoxin/verification_rules.yaml:1)`

### 6.3 为什么不建议继续只靠 `docx + xlsx` 混合自由输入

因为：

- `docx` 适合人工阅读，不适合稳定解析
- 同一个段落里常常混有场景、法条原文、解释、备注
- 后端难以准确区分“标题”“条文”“结论”“备注”
- 一旦法学同学改了段落格式，解析脚本就容易失效

所以更建议：

- 法条和案例用 `xlsx/csv`
- 规则和模板用 `yaml/md`



### 7.1 `huxin_backend/法条适用.docx` 

文件：`[huxin_backend/法条适用.docx](D:/legal/legalAI/huxin_backend/法条适用.docx)`

优点：

- 已经按讨薪场景整理了一些专题
- 有“适用场景 + 法条 + 补充说明”的意识
- 内容方向和你们项目高度相关，不是泛泛法条堆砌

不足：

- 它更像“法学分析笔记”，不是“可稳定导入的数据源”
- 一个段落里混合了标题、场景、法条原文、通俗说明
- 缺少统一字段，比如 `issue_code`、`element_code`、`keywords`
- 缺少“该条法条支持哪个结论”的显式标注
- 缺少“对应哪些证据”的结构化字段
- 对当前导入脚本来说，切分粒度不稳定

结论：

- 这份 `docx` 适合作为“原始知识底稿”
- 不适合作为最终生产导入格式
- 最好把它拆成 `norms.xlsx + issue/element 对照表`

### 7.2 `huxin_backend/涉欠薪典型案例汇总.xlsx` 

文件：`[huxin_backend/涉欠薪典型案例汇总.xlsx](D:/legal/legalAI/huxin_backend/涉欠薪典型案例汇总.xlsx)`

当前已有列：

- `序号`
- `案件名称`
- `案件性质`
- `有无前置程序`
- `案由`
- `主张`
- `问题`
- `被执行人的问题`
- `申请执行人的困难`
- `是否已解决`
- `解决路径`

优点：

- 这比纯文档强很多，因为它是结构化表格
- 有真实案件、真实问题、真实路径，适合做“经验层素材”
- 对执行难、路径选择这类场景很有参考价值

不足：

- 它更像“执行经验汇总表”，不是“法律论证案例表”
- 缺少 `issue_codes`
- 缺少 `facts_summary`
- 缺少 `reasoning_summary`
- 缺少 `decision_summary`
- 缺少 `evidence_focus`
- 缺少“该案对你们系统可复用的规则结论”

举个例子：

当前表里的“解决路径 = 破产重整程序”，这对人类很有用，但对系统还不够。系统还需要知道：

- 它对应的争点是什么
- 是哪类事实触发走这条路径
- 这条路径适用于劳动关系还是劳务关系
- 是支持“立即主张工资”还是支持“先执行/重整/追加股东”

结论：

- 这份表可以保留
- 但需要升级为“案例论证表”，而不是仅仅“办案经验表”

## 8. 最小改造方案

建议按下面方式最小改造。

### 8.1 对法条材料

把 `法条适用.docx` 中每一个专题拆成多行表格，至少补齐：

- `law_name`
- `article_no`
- `article_text`
- `scenario`
- `issue_codes`
- `effect`

### 8.2 对案例材料

在现有 `涉欠薪典型案例汇总.xlsx` 基础上新增这些列：

- `issue_codes`
- `facts_summary`
- `decision_summary`
- `reasoning_summary`
- `evidence_focus`
- `applicable_conditions`
- `risk_points`

### 8.3 对规则模板

让法学同学再单独交两张表：

1. `issue_templates.xlsx`
2. `element_templates.xlsx`

这两张表会直接决定你们系统是不是“分阶段法律论证系统”，这是和普通 RAG 最大的区别。

## 9. 可以直接发给法学同学的整理要求

下面这段你可以直接转给法学同学。

### 9.1 法条整理要求

请不要只提供整篇 Word。请将每条可用法条整理为表格的一行，并补充：

- 该条文适用什么讨薪场景
- 该条文解决哪个争点
- 该条文支持什么结论
- 该条文通常需要哪些事实和证据配合

### 9.2 案例整理要求

请不要只写案件故事或办案心得。请按“争点 - 事实 - 结论 - 理由 - 证据”的方式整理，每个案例至少说明：

- 这是哪一类争点
- 哪些关键事实导致这个结果
- 最终支持了什么结论
- 理由是什么
- 对后续类似案件有什么借鉴限制

### 9.3 规则素材整理要求

请额外整理：

- 欠薪场景下常见争点清单
- 每个争点的成立要件
- 每个要件可接受的证据类型
- 常见抗辩和风险点


## 10. 后端同学

后端侧建议按下面顺序接收法学素材：

1. 先把法条表、案例表标准化
2. 再把争点模板、要件模板标准化
3. 再把证据矩阵和验证规则补上

对应当前仓库，后端后续可做的事情是：

- 重写 `import_norms.py`，按表头导入 metadata
- 重写 `import_cases.py`，保留更多结构化列
- 写一个 `xlsx -> yaml` 的转换脚本，把法学同学的规则表转成模板文件
- 在 `services/matching` 和 `services/verification` 中优先消费这些结构化规则

