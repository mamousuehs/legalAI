# 法律论证系统重构计划与讨论稿

## 1. 文档定位

这份文档用于团队内部讨论当前项目应如何从“能回答问题的法律聊天工具”演进为“可解释、可验证、分阶段的法律论证系统”。

面向实现的计划稿,重点是把以下问题说清楚：

- 我们要做的系统到底不是什么
- 目标架构应该分成哪些层
- 每一层的输入输出是什么
- 当前仓库已经到哪里了
- 下一步最值得做的部分是什么
- 如何拆成几次可落地的 PR

## 2. 项目目标

项目目标不是构建一个“检索几段法条后直接生成答案”的普通法律 RAG 问答系统。

项目目标是构建一个：

- 能输出结构化法律分析过程的系统
- 能保留中间分析结果的系统
- 能说明“为什么得出这个结论”的系统
- 能指出“哪些地方证据不足、哪些地方仍需补强”的系统
- 能对生成结果进行自动检查和降强表达的系统

一句话概括：

`目标系统 = 检索底座 + 规则模板骨架 + LLM 辅助分析 + 验证层`

## 3. 与普通 RAG 的区别

普通 RAG 的典型流程是：

`问题 -> 检索 -> 拼接上下文 -> LLM 直接回答`

我们要做的系统应该是：

`案件输入 -> 预处理 -> 检索 -> 争点识别 -> 事实抽取 -> 要件匹配 -> 理由构建 -> IRAC 生成 -> 验证`

核心区别不在于“有没有向量库”，而在于“检索之后是否继续做结构化法律分析”。

普通 RAG 的主要风险：

- 检索后直接自由生成
- 争点是否完整取决于一次生成
- 要件是否遗漏取决于 prompt
- 结论强度不可控
- 很难知道哪一句话来自哪条依据

目标系统的主要特征：

- 检索结果进入后续分析层，而不是直接变成答案
- 每一层都有中间结构化输出
- 规则和模板控制分析边界
- LLM 负责理解、归纳、改写，不负责独自决定整条流程
- 最终文本可追溯到事实、依据和要件匹配结果

## 4. 总体架构

### 4.1 八阶段流水线

建议将系统分为八个连续阶段：

1. 数据库建设
2. 检索层
3. 争点识别层
4. 事实抽取层
5. 要件匹配层
6. 理由构建层
7. IRAC 生成层
8. 验证层

### 4.2 流水线示意

```text
用户输入 / 案件材料
        |
        v
[1] 输入预处理
        |
        v
[2] 检索层
  - 召回法条
  - 召回类案
  - 召回模板
        |
        v
[3] 争点识别
  - 本案需要讨论哪些法律问题
        |
        v
[4] 事实抽取
  - 围绕争点提取关键事实和证据状态
        |
        v
[5] 要件匹配
  - 事实与法条要件逐项对齐
        |
        v
[6] 理由构建
  - 支持理由
  - 反对理由
  - 证据缺口
        |
        v
[7] IRAC 生成
  - Issue
  - Rule
  - Application
  - Conclusion
        |
        v
[8] 验证层
  - 引用检查
  - 完整性检查
  - 一致性检查
  - 表达强度检查
```

### 4.3 每层角色分工

- 规则系统负责：
  - 必审项
  - 字段约束
  - 模板骨架
  - 结论强度控制
  - 验证规则
- LLM 负责：
  - 非结构化文本理解
  - 争点补充识别
  - 事实归纳
  - 理由压缩与重写
  - IRAC 语言表达
- NLI 或验证模块负责：
  - 判断事实是否支持要件
  - 判断文本是否可由前提推出
  - 识别幻觉、矛盾和跳步

## 5. 推荐的数据与知识底座

### 5.1 规范库

规范库不应只是保存法条原文，而应该保存结构化元数据：

- `source_id`
- `title`
- `article_no`
- `content`
- `effective_date`
- `expiry_date`
- `status`
- `law_level`
- `jurisdiction`
- `keywords`
- `embedding`

### 5.2 案例库

案例库不应只是“相似文本集合”，应支持结构化参照：

- `case_id`
- `title`
- `court`
- `case_type`
- `cause`
- `result`
- `cited_articles`
- `fact_summary`
- `issue_tags`
- `reasoning_summary`
- `full_text`
- `embedding`

### 5.3 模板库

模板库是与普通 RAG 最大的差异点之一，建议至少包含：

- 争点模板
- 要件模板
- IRAC 模板
- 文书模板
- 缺失证据提示模板
- 风险提示模板

### 5.4 规则库

规则库存放程序化约束，不是自然语言材料库。建议包含：

- 某类案件必须分析的要件列表
- 结论前必须回应的反对理由
- 缺少哪些字段时不能输出强结论
- 哪些表述需要降级，例如“倾向于”“初步判断”“仍需补强”
- 验证阶段的拦截规则

## 6. 每一层的目标、输入、输出

### 6.1 输入预处理层

目标：

- 把用户原始叙述标准化，供后续模块使用

输入：

- 用户消息历史
- 已有结构化字段

输出：

- 标准化案件输入
- 基础实体信息
- 时间/金额归一结果
- 诉求摘要
- 可见证据线索

应做的事情：

- 去噪
- 切分案情与诉求
- 标准化时间表达
- 标准化金额表达
- 初步识别当事人角色
- 标记明显缺失字段

### 6.2 检索层

目标：

- 形成候选依据包，而不是直接回答用户

输入：

- 标准化案件输入
- 领域提示

输出：

- 候选法条列表
- 候选案例列表
- 候选模板列表

推荐方法：

- 关键词检索
- 向量检索
- 重排

### 6.3 争点识别层

目标：

- 判断本案需要讨论哪些法律问题

输入：

- 案件输入
- 候选法条
- 候选案例
- 争点模板

输出：

- `Issue` 列表

注意：

- 争点识别不是判断是否满足要件
- 争点识别是决定“哪些问题必须进入分析”

### 6.4 事实抽取层

目标：

- 围绕每个争点，抽出相关事实与证据状态

输入：

- 案件材料
- `Issue` 列表
- 事实模板

输出：

- 结构化事实表
- 缺失事实项
- 证据状态

建议优先规则抽取的字段：

- 主体
- 时间
- 地点
- 金额
- 合同状态
- 欠条或结算单
- 微信聊天
- 考勤记录
- 工友证言

### 6.5 要件匹配层

目标：

- 将事实逐项对齐到法条要件

输入：

- `Issue` 列表
- 事实表
- 候选规范
- 要件模板

输出：

- 要件满足度表

状态建议统一为：

- `satisfied`
- `partial`
- `insufficient`
- `not_satisfied`

### 6.6 理由构建层

目标：

- 将要件结果组织成正反理由集合

输入：

- 要件匹配结果
- 法条
- 类案

输出：

- 支持理由
- 反对理由
- 证据缺口
- 暂定结论

### 6.7 IRAC 生成层

目标：

- 将结构化分析结果写成正式可读的法律文本

输入：

- 争点
- 规范
- 要件匹配
- 理由集合

输出：

- IRAC 文本
- 引用列表
- 风险提示

要求：

- 不允许脱离中间结果自由发挥
- 每段结论必须绑定依据
- 每段结论应体现确定性程度

### 6.8 验证层

目标：

- 审查生成结果，而不是重新生成一份新答案

输入：

- IRAC 草稿
- 全部中间分析结果

输出：

- 验证报告
- 风险提示
- 是否允许出具最终文本

应检查：

- 是否错引法条
- 是否引用不存在的案例
- 是否遗漏必审要件
- 是否存在结论无事实支撑
- 是否存在事实未被分析
- 是否存在互相矛盾的陈述
- 是否在证据不足时输出过强结论

## 7. 推荐的目录结构

建议把后端从单文件升级为可维护结构：

```text
huxin_backend/
  app/
    main.py
    api/
      chat.py
      generate.py
      analysis.py
    schemas/
      common.py
      intake.py
      retrieval.py
      issue.py
      fact.py
      match.py
      reasoning.py
      verification.py
    services/
      intake/
        normalizer.py
        entity_extractor.py
      retrieval/
        law_retriever.py
        case_retriever.py
        template_retriever.py
        reranker.py
      issue/
        rule_based_identifier.py
        llm_identifier.py
      fact/
        rule_based_extractor.py
        llm_extractor.py
      matching/
        element_matcher.py
        rule_packs.py
      reasoning/
        reason_builder.py
        irac_generator.py
      verification/
        citation_checker.py
        completeness_checker.py
        consistency_checker.py
        nli_checker.py
      repositories/
        chroma_repo.py
        template_repo.py
        rule_repo.py
    pipelines/
      case_analysis.py
    data_import/
      import_norms.py
      import_cases.py
      import_templates.py
      import_rules.py
    templates/
      labor/
        issue_templates.yaml
        element_templates.yaml
        verification_rules.yaml
        irac_prompt.txt
        document_templates/
          complaint.md
          arbitration.md
    tests/
      test_intake.py
      test_issue_identifier.py
      test_fact_extractor.py
      test_element_matcher.py
      test_irac_generator.py
```

## 8. 推荐的核心数据模型

下面这些对象建议优先统一下来，避免各模块之间互相传裸字典。

```python
from pydantic import BaseModel
from typing import Literal


class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class CaseInput(BaseModel):
    messages: list[Message]
    extracted_info: dict = {}
    case_type_hint: str | None = None


class RetrievedAuthority(BaseModel):
    source_type: Literal["norm", "case", "template"]
    source_id: str
    title: str
    snippet: str
    score: float
    metadata: dict = {}


class Issue(BaseModel):
    issue_code: str
    issue_name: str
    description: str
    priority: int = 0
    triggered_by: list[str] = []


class FactItem(BaseModel):
    issue_code: str | None = None
    fact_type: str
    value: str
    evidence_status: Literal["supported", "claimed", "missing", "contradicted"]
    source_span: str | None = None


class ElementMatch(BaseModel):
    issue_code: str
    element_name: str
    status: Literal["satisfied", "partial", "insufficient", "not_satisfied"]
    supporting_facts: list[str] = []
    supporting_authorities: list[str] = []
    missing_evidence: list[str] = []


class ReasonBundle(BaseModel):
    issue_code: str
    support_reasons: list[str] = []
    oppose_reasons: list[str] = []
    evidence_gaps: list[str] = []
    tentative_conclusion: str = ""


class IRACDraft(BaseModel):
    issue: str
    rule: str
    application: str
    conclusion: str
    citations: list[str] = []


class VerificationResult(BaseModel):
    passed: bool
    citation_errors: list[str] = []
    missing_elements: list[str] = []
    unsupported_claims: list[str] = []
    consistency_warnings: list[str] = []
```

## 9. 推荐的 API 接口设计

### 9.1 `/api/chat`

用途：

- 多轮收集案件信息
- 返回当前阶段的结构化结果
- 推动案件分析逐步前进

请求体建议：

```json
{
  "messages": [
    { "role": "user", "content": "老板拖欠我三个月工资" }
  ],
  "extracted_info": {
    "worker_name": "",
    "employer_type": "",
    "_stage": "initial"
  },
  "case_type_hint": "labor_wage"
}
```

响应体建议：

```json
{
  "reply": "我先确认几个关键事实……",
  "quick_replies": ["有劳动合同", "没有劳动合同"],
  "conversation_stage": "contract_status",
  "extracted_info": {
    "employer_type": "company",
    "_stage": "contract_status"
  },
  "retrieved_authorities": [],
  "issues": [],
  "facts": [],
  "element_matches": [],
  "reasoning_summary": {},
  "verification": {},
  "can_generate_doc": false
}
```

### 9.2 `/api/analyze`

用途：

- 对当前案件做一次完整分析
- 适合后端调试和评估

请求：

- `CaseInput`

响应：

- 完整分析结果，包括检索、争点、事实、匹配、理由、验证

### 9.3 `/api/generate-document`

用途：

- 将已分析结果映射为申请书、投诉书、仲裁申请书等

请求：

```json
{
  "document_type": "labor_complaint",
  "case_input": { "...": "..." },
  "analysis": { "...": "..." }
}
```

响应：

```json
{
  "document": "正式文书文本",
  "citations": ["劳动合同法第82条"],
  "risk_notes": ["金额证据仍需补强"]
}
```

## 10. 劳动争议场景的最小可行版本

建议不要一开始覆盖所有案由，而是先选一个你们现在已经有数据基础、容易展示的垂直方向。

当前最适合的方向：

- 欠薪
- 事实劳动关系认定
- 劳动报酬请求

### 10.1 MVP 应至少包含

- 规范库
- 案例库
- 模板库
- 检索层
- 争点识别层
- 事实抽取层
- 要件匹配层
- IRAC 生成层
- 基础验证层

### 10.2 MVP 可以暂时不做或弱化

- 全法域覆盖
- 高级重排模型
- 完整 NLI 模块
- 大规模案例标签体系
- 多案由统一调度

### 10.3 MVP 核心展示目标

MVP 最重要的不是“结论像律师一样完整”，而是能展示：

- 系统先识别争点，再分析
- 系统知道自己用了哪些法条和案例
- 系统能列出已满足要件和证据不足要件
- 系统最终文本来自中间结构化分析
- 系统会提示风险，不会盲目输出强结论

## 11. 推荐的规则优先策略

### 11.1 哪些内容优先用规则做

- 字段是否缺失
- 时间、金额、身份类型归一
- 劳动争议场景的必审项
- 每类争点的要件清单
- 缺失哪些字段时不能出强结论
- 文书的固定结构

### 11.2 哪些内容适合让 LLM 辅助

- 从长文本中归纳案情
- 将事实填入模板
- 对模糊叙述做结构化补充
- 将要件匹配结果写成自然语言
- 将 IRAC 草稿写得更顺畅

### 11.3 哪些内容适合验证模块做

- 判断一句结论是否有依据
- 判断是否遗漏必审项
- 判断前后是否矛盾
- 判断引用是否存在
- 判断表达是否过强

## 12. 当前仓库与目标架构的差距

### 12.1 已有内容

- 有 `FastAPI + Chroma + LLM` 的最小链路
- 有法条与案例的导入脚本
- 有前端结构化字段和阶段式交互的原型
- 有文书生成的前端 mock

### 12.2 当前主要问题

- 后端仍是单文件、单接口
- 仍是“检索后直接生成”的单阶段流程
- 前后端接口不一致
- 没有统一 schema
- 没有模板库和规则库
- 没有争点识别模块
- 没有事实抽取模块
- 没有要件匹配模块
- 没有理由构建模块
- 没有 IRAC 草稿对象
- 没有验证层
- 知识库缺少元数据

## 12A. 现有代码对照与改造建议

这一节用于把“目标架构”映射回当前代码，明确指出现在哪些文件代表了当前实现、它们的不足是什么、后续要改哪里以及需要新增什么模块。

### 12A.1 `huxin_backend/main.py` 当前是单轮 RAG 入口，不是分阶段论证入口

当前现状：

- 只有一个 `ChatRequest`，字段只有 `message: str`
- 只有一个 `/api/chat` 接口
- 流程是：收到问题 -> 向量检索 -> 拼接 `context` -> LLM 直接回答
- 返回值只有 `status`、`retrieved_context`、`reply`

对应代码位置：

- `ChatRequest` 定义在 `huxin_backend/main.py`
- 检索和生成逻辑集中在 `/api/chat`

当前不足：

- 不支持 `messages + extracted_info` 形式的多轮输入
- 不支持阶段化处理中间结果
- 无法承载争点识别、事实抽取、要件匹配、理由构建、IRAC 和验证
- 输出结构不足，无法支撑前端展示中间分析结果

建议改造：

- 保留 `main.py` 只做应用装配，不再承载全部业务逻辑
- 将 `/api/chat` 拆到 `app/api/chat.py`
- 引入统一输入输出 schema
- 引入分析流水线 `pipelines/case_analysis.py`

建议新增：

- `app/api/chat.py`
- `app/api/generate.py`
- `app/api/analysis.py`
- `app/schemas/intake.py`
- `app/schemas/retrieval.py`
- `app/schemas/issue.py`
- `app/schemas/fact.py`
- `app/schemas/match.py`
- `app/schemas/reasoning.py`
- `app/schemas/verification.py`
- `app/pipelines/case_analysis.py`

建议替换的接口思路：

- 旧接口：`message -> reply`
- 新接口：`messages + extracted_info + case_type_hint -> 结构化分析结果`

### 12A.2 当前检索逻辑只有“拼接上下文”，缺少候选依据包

当前现状：

- 使用单个 Chroma collection：`laws`
- 法条和案例混在一起
- 检索后直接将结果拼成一个字符串 `context`
- 这个 `context` 被直接送入 prompt

当前不足：

- 无法区分法条、案例、模板三类来源
- 无法知道某段结论具体引用了哪一条法条或哪个案例
- 无法为后续要件匹配和验证提供结构化输入
- 无法实现“模板召回”

建议改造：

- 将检索层改为输出“候选依据包”
- 将法条、案例、模板分别召回
- 允许后续阶段引用结构化检索结果，而不是只吃一段字符串

建议新增：

- `app/services/retrieval/law_retriever.py`
- `app/services/retrieval/case_retriever.py`
- `app/services/retrieval/template_retriever.py`
- `app/services/retrieval/reranker.py`
- `app/repositories/chroma_repo.py`

建议新增的数据对象：

- `RetrievedAuthority`
- `RetrievedAuthorityList`

### 12A.3 `huxin_backend/import_data.py` 只导入纯文本，缺少结构化元数据

当前现状：

- 脚本会读取 Word 法条和 Excel 案例
- 最终只写入 `documents` 和 `ids`
- 没有写入 `metadatas`

当前不足：

- 法条没有条号、标题、效力状态、层级等信息
- 案例没有法院、案号、争点标签、适用法条、理由摘要等信息
- 后续无法做可解释引用、可验证检查和模板匹配
- 无法支撑规则库和模板库

建议改造：

- 不再使用单一 `import_data.py` 统一导入所有类型
- 按规范、案例、模板、规则分别导入
- 导入时补齐结构化元数据

建议新增：

- `data_import/import_norms.py`
- `data_import/import_cases.py`
- `data_import/import_templates.py`
- `data_import/import_rules.py`

建议补充的元数据字段：

- 规范：
  - `source_type`
  - `title`
  - `article_no`
  - `effective_date`
  - `status`
  - `law_level`
  - `jurisdiction`
  - `keywords`
- 案例：
  - `source_type`
  - `title`
  - `case_no`
  - `court`
  - `cause`
  - `result`
  - `cited_articles`
  - `issue_tags`
  - `fact_summary`
  - `reasoning_summary`
- 模板：
  - `source_type`
  - `template_type`
  - `case_type`
  - `issue_codes`
  - `element_list`

### 12A.4 当前没有真实的争点识别层

当前现状：

- 后端没有 `issue` 模块
- 当前系统不会输出“本案需要分析哪些法律问题”
- 前端虽然有阶段式问答原型，但不是后端真实争点识别

当前不足：

- 无法将案件拆成多个法律讨论单元
- 无法保证后续分析覆盖必审问题
- 无法在复杂案件中区分主争点和子争点

建议改造：

- 新增争点识别层，优先规则与模板驱动
- LLM 用于补充和归纳，不负责独自决定争点边界

建议新增：

- `app/services/issue/rule_based_identifier.py`
- `app/services/issue/llm_identifier.py`
- `templates/labor/issue_templates.yaml`
- `app/schemas/issue.py`

建议第一批支持的劳动争议争点：

- 是否存在劳动关系
- 是否存在拖欠劳动报酬
- 欠薪金额是否明确
- 证据是否足以支撑主张
- 请求路径是投诉、仲裁还是诉讼

### 12A.5 当前没有真实的事实抽取层

当前现状：

- 前端维护了 `extractedInfo`
- 但这些字段主要来自前端 mock 逻辑
- 后端并没有事实抽取器，也没有统一事实对象

当前不足：

- 结构化字段没有真实来源链
- 字段更新逻辑不在后端，难以统一维护
- 无法把“事实”和“证据状态”明确区分

建议改造：

- 将结构化事实抽取迁移到后端
- 先做规则抽取，再用 LLM 补充不确定字段
- 对每一条事实记录证据状态

建议新增：

- `app/services/fact/rule_based_extractor.py`
- `app/services/fact/llm_extractor.py`
- `app/schemas/fact.py`

建议优先抽取的字段：

- 工人姓名
- 用工主体
- 用工主体类型
- 工作地点
- 工作时段
- 欠薪金额
- 有无合同
- 有无欠条或结算单
- 有无聊天记录
- 有无考勤记录
- 有无工友证言

### 12A.6 当前没有要件匹配层

当前现状：

- 系统不会显式判断“某一法条要件是否已满足”
- 也不会说明“缺什么证据才能更有力地支撑这个要件”

当前不足：

- 系统无法形成真正的法律分析骨架
- 只能给出自然语言建议，不能给出逐项可审计结论
- 无法支持理由构建层和验证层

建议改造：

- 将争点对应到要件模板
- 将事实逐项对齐到要件
- 输出满足度、支撑事实和缺失证据

建议新增：

- `app/services/matching/element_matcher.py`
- `app/services/matching/rule_packs.py`
- `templates/labor/element_templates.yaml`
- `app/schemas/match.py`

建议统一输出状态：

- `satisfied`
- `partial`
- `insufficient`
- `not_satisfied`

### 12A.7 当前没有理由构建层

当前现状：

- 当前系统要么直接回答问题，要么在前端 mock 中给出建议
- 没有明确区分支持理由、反对理由和证据缺口

当前不足：

- 无法体现“论证过程”
- 无法体现“为何暂时倾向某结论但仍需补强”
- 无法支撑更稳健的 IRAC 生成

建议改造：

- 引入理由构建层
- 将要件匹配结果组织为正反理由集合
- 增加证据缺口和暂定结论

建议新增：

- `app/services/reasoning/reason_builder.py`
- `app/schemas/reasoning.py`

建议输出：

- `support_reasons`
- `oppose_reasons`
- `evidence_gaps`
- `tentative_conclusion`

### 12A.8 当前没有 IRAC 生成层

当前现状：

- 现有后端只是让模型直接回复
- 前端有文书生成 mock，但不是基于完整结构化分析结果

当前不足：

- 生成结果不是标准化法律论证文本
- 文本和中间分析结果之间缺乏强绑定关系
- 不利于解释、复核和局部修订

建议改造：

- 先生成 `IRACDraft`，再转成面向用户的自然语言或文书
- 每段 IRAC 必须绑定依据和事实

建议新增：

- `app/services/reasoning/irac_generator.py`
- `templates/labor/irac_prompt.txt`
- `app/schemas/reasoning.py`

建议至少输出：

- `issue`
- `rule`
- `application`
- `conclusion`
- `citations`

### 12A.9 当前没有验证层

当前现状：

- 没有引用核验
- 没有完整性检查
- 没有一致性检查
- 没有结论强度降级机制

当前不足：

- 无法拦截幻觉
- 无法发现必审项遗漏
- 无法在证据不足时降低结论强度

建议改造：

- 先做规则验证，再逐步引入 NLI
- 验证层不负责重新生成结论，只负责审稿

建议新增：

- `app/services/verification/citation_checker.py`
- `app/services/verification/completeness_checker.py`
- `app/services/verification/consistency_checker.py`
- `app/services/verification/nli_checker.py`
- `app/schemas/verification.py`

建议至少检查：

- 是否错引法条
- 是否引用了不存在的案例
- 是否遗漏了必审要件
- 是否存在结论无事实支撑
- 是否存在互相矛盾的陈述
- 是否在证据不足时输出过强结论

### 12A.10 当前前后端契约不一致，必须优先修正

当前现状：

- 前端设计的是 `messages + extracted_info`
- 前端期待返回：
  - `reply`
  - `quick_replies`
  - `extracted_info`
  - `conversation_stage`
  - `can_generate_doc`
- 前端还预期存在 `/api/generate-document`
- 后端当前只接受 `message`
- 后端也没有 `generate-document` 接口

当前不足：

- 前端真实接后端时无法得到预期结果
- 现有 mock 流程和真实后端能力不一致
- 即使后续新增分析层，也没有稳定的接口承载

建议改造：

- 将前端当前契约正式固化为后端 schema
- 让后端真实返回阶段化结构化结果
- 增加 `generate-document` 接口

建议新增：

- `ChatRequest/ChatResponse` schema
- `GenerateDocumentRequest/GenerateDocumentResponse` schema

### 12A.11 当前目录结构过于扁平，不利于后续扩展

当前现状：

- `huxin_backend` 目前主要只有：
  - `main.py`
  - `import_data.py`
  - `legal_db/`

当前不足：

- 所有逻辑容易继续堆进单文件
- 模块边界不清晰
- 测试和分工都不方便

建议改造：

- 采用本方案第 7 节中的目录结构
- 至少先完成 `api`、`schemas`、`services`、`pipelines` 四层

### 12A.12 建议的优先改造顺序

第一优先级：先修后端骨架和接口契约

- 改 `huxin_backend/main.py`
- 新建 `app/api`
- 新建 `app/schemas`
- 新建 `app/pipelines`
- 新增 `/api/generate-document`

第二优先级：重构知识库和检索层

- 改 `huxin_backend/import_data.py`
- 拆导入脚本
- 增加元数据
- 拆分法条、案例、模板

第三优先级：补齐分析核心三层

- 新增争点识别
- 新增事实抽取
- 新增要件匹配

第四优先级：补齐论证和验证

- 新增理由构建
- 新增 IRAC 生成
- 新增验证层

第五优先级：前端联调与展示优化

- 让前端不再依赖 mock
- 展示争点、事实、要件、风险提示

## 13. 建议的开发路线图

### 第一阶段：打基础

目标：

- 统一接口
- 统一数据结构
- 将后端拆出基本目录

交付物：

- `schemas/`
- `pipelines/`
- 新版 `/api/chat`
- 基础 `/api/generate-document`

### 第二阶段：重构检索层

目标：

- 将法条、案例、模板拆开
- 增加元数据
- 构建候选依据包

交付物：

- 新导入脚本
- 新检索服务
- 结构化检索结果

### 第三阶段：补齐分析核心

目标：

- 争点识别
- 事实抽取
- 要件匹配

交付物：

- 劳动争议模板
- 劳动争议规则包
- 结构化分析结果

### 第四阶段：生成与验证

目标：

- IRAC 生成
- 验证报告
- 风险提示

交付物：

- IRAC 模块
- 基础验证器
- 文书生成器

### 第五阶段：评测与优化

目标：

- 分层评测
- 误差定位
- 再做模型和规则优化

交付物：

- 测试样例集
- 分层指标
- 优化建议

## 14. 建议的 PR 拆分

### PR1：后端骨架与契约重构

内容：

- 新建 `app/api`、`app/schemas`、`app/pipelines`
- 将 `/api/chat` 改为接收 `messages + extracted_info`
- 统一返回前端需要的字段

完成标准：

- 前后端能在非 mock 模式下正确通一次
- 后端接口不再只是 `message -> reply`

### PR2：知识库与检索层重构

内容：

- 导入脚本拆为规范、案例、模板
- 检索输出改为结构化依据包
- 补元数据字段

完成标准：

- 每条检索结果可知来源、标题、类型、分数

### PR3：劳动争议场景的争点模板与事实模板

内容：

- 建立劳动争议场景 issue 模板
- 建立 facts schema
- 建立基础提取规则

完成标准：

- 能对典型欠薪输入输出稳定的争点与事实表

### PR4：要件匹配与理由构建

内容：

- 建立要件模板
- 输出要件满足度
- 输出支持/反对理由

完成标准：

- 系统能明确指出哪些要件已满足、哪些证据不足

### PR5：IRAC 与基础验证层

内容：

- 生成 IRAC
- 增加引用检查和完整性检查
- 缺少依据时自动降强表达

完成标准：

- 最终文本附带风险提示

### PR6：文书生成与展示优化

内容：

- 基于结构化分析结果生成投诉书、申请书
- 优化前端展示中间结果

完成标准：

- 前端可展示争点、事实、要件、风险提示

## 15. 团队分工建议

### 法学同学更适合负责

- 场景选定
- 争点模板设计
- 要件模板整理
- 常见反对理由整理
- 文书模板与规范校对
- 标注和验收

### 后端同学更适合负责

- schema 设计
- 检索与导入脚本
- 流水线编排
- 验证层实现
- API 设计

### 前端同学更适合负责

- 结构化结果展示
- 对话分阶段交互
- 文书预览与导出
- 风险提示与证据缺口展示

### 全队共同参与

- 选定 MVP 场景
- 审核中间数据结构
- 制定验收样例
- 评估每层的输出是否稳定

## 16. 近期最值得优先完成的 12 项

1. 将后端请求体从 `message: str` 改为 `messages + extracted_info`
2. 将后端响应改为结构化响应
3. 新建后端目录骨架
4. 拆出 `schemas`
5. 将法条、案例、模板分开存储
6. 导入时补充元数据
7. 新增劳动争议 issue 模板
8. 新增规则版事实抽取器
9. 新增要件匹配器
10. 新增理由构建器
11. 新增 IRAC 生成器
12. 新增基础验证器

## 17. 不建议当前阶段做的事情

- 一开始就支持所有法律领域
- 先花大量时间调最强模型
- 没有 schema 就直接继续写 prompt
- 把所有逻辑继续塞进 `main.py`
- 没有模板库时直接追求复杂理由生成
- 没有验证层时直接输出强结论

## 18. 讨论结论建议

如果团队要快速形成共识，建议优先回答这 4 个问题：

1. MVP 是否聚焦在劳动争议中的欠薪场景
2. 是否接受“规则/模板优先，LLM 辅助”的实现路线
3. 是否同意先重构后端契约和目录结构，再做模型效果
4. 是否同意把“可解释中间结果”作为阶段验收标准，而不是只看最终回复是否顺畅

## 19. 下一步建议

从工程角度，最合理的下一步不是继续优化当前 `main.py` 的 prompt，而是直接开始做：

- `PR1：后端骨架与契约重构`

原因：

- 这是后续所有模块的挂载点
- 能立刻解决当前前后端接口错位问题
- 能让争点、事实、要件、验证这些模块有稳定输出位置
- 能把项目从“聊天原型”推进到“可扩展分析系统”
