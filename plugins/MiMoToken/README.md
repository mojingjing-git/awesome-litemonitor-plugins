# 小米MiMo套餐（Xiaomi MiMo Plan）

> 显示小米MiMo Token Plan套餐用量（自动从浏览器获取Cookie）

## 功能说明

显示小米 MiMo Token Plan 套餐的用量与额度占用情况。

走客户端内置的 `native://mimo` 处理器 —— 传入浏览器 Cookie，由客户端解析出套餐用量，而不是插件自己去拼接口。

## 配置项

<!-- AUTO:inputs -->
| 参数 | 说明 | 类型 | 默认值 |
|---|---|---|---|
| `cookies` | Cookie | text | `` |
<!-- /AUTO:inputs -->

## 输出项

<!-- AUTO:outputs -->
| key | 显示标签 | 单位 |
|---|---|---|
| `plan` | 套餐额度 | — |
| `comp` | 补偿额度 | — |
<!-- /AUTO:outputs -->

> 标签中含 `{...}` 的是**运行时动态值**（如设备名、城市名、模式名），实际显示由插件在运行时填充。

## 使用说明

1. 打开 LiteMonitor++ 的「设置 → 插件市场」，搜索并安装本插件
2. 在「设置 → 插件管理」中找到它，打开开关
3. 按上面的「配置项」填写参数（没有参数的可跳过）
4. 在「设置 → 监控项显示」里挑选要显示的输出项

## 注意事项

- 需要填写小米账号的 **Cookie**（在浏览器登录后从开发者工具复制）。Cookie 属于**账号凭据**，只会被发往小米自己的接口，但仍请只在本机可信环境使用。
- Cookie 会过期，过期后显示 `[ERROR]`。需要重新获取。
- 刷新间隔 60 秒。
- 如果你的账号没有 Token Plan 套餐，接口可能返回空数据。

---

*本插件由社区贡献，遵循 [插件开发指南](https://github.com/mojingjing-git/awesome-litemonitor-plugins/blob/main/README.md)。*
