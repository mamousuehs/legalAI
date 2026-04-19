# 三人分工方案一

## 分工原则



- 我负责后端主线和最终集成
- lzy负责检索、导入和模板规则整理
- hzr同学负责页面展示与联调

这样拆分的目的，是让主流程由一个人统一掌控，减少后端逻辑分叉；同时把检索与前端拆成相对独立的工作包，方便并行推进。



### 我负责的目录

- `TaoxinAI/api/`
- `TaoxinAI/pipelines/`
- 后续新增的核心后端目录：
  - `TaoxinAI/schemas/`
  - `TaoxinAI/services/issue/`
  - `TaoxinAI/services/fact/`
  - `TaoxinAI/services/matching/`
  - `TaoxinAI/services/reasoning/`
  - `TaoxinAI/services/verification/`

### 我负责的内容

- 后端目录结构搭建
- API 设计与统一
- schema 设计
- 讨薪场景主流程编排
- 争点识别
- 事实抽取
- 要件匹配
- 理由构建
- IRAC 生成
- 验证层
- 最终联调与集成

## lzy负责的部分


### 负责的目录

- 后续新增的目录：
  - `TaoxinAI/data_import/`
  - `TaoxinAI/services/retrieval/`
  - `TaoxinAI/repositories/`
  - `TaoxinAI/templates/taoxin/`
  - `TaoxinAI/tests/` 中与检索、模板、导入相关部分

### 负责的内容

- 法条、案例、模板数据整理
- 导入脚本拆分
- 元数据补充
- 检索层实现
- 模板文件整理
- 规则文件整理
- 检索相关测试样例

## 前端同学负责的部分

前端同学是“展示与联调 owner”，负责页面和交互，不需要深入后端内部分析逻辑。

### 负责的目录

- `前端相关/src/`

### 负责的内容

- 保留和整理当前页面交互
- 结构化信息展示
- 争点/要件/风险提示展示
- 文书预览和下载
- 前后端联调



