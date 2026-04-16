# api

这一层负责暴露 HTTP 接口，不承载复杂业务逻辑。

负责人：我

这里的职责是：

- 接收请求
- 调用 pipeline
- 返回结构化响应

业务判断尽量下沉到 `pipelines/` 和 `services/`。
