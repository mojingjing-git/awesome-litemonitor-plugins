# 心知天气（Xinzhi Weather）

> 心知天气基础API，基于IP自动定位，获取天气数据，支持多种显示方式

## 功能说明

基于心知天气（seniverse）API 的实时天气，支持按 IP 自动定位城市，也可手动指定城市代码。显示温度、天气现象与体感温度。

## 配置项

<!-- AUTO:inputs -->
| 参数 | 说明 | 类型 | 默认值 |
|---|---|---|---|
| `city` | 城市名称 | text | `` |
| `api_key` | API Key | text | `` |
| `style` | 显示内容 | select | `standard` |
<!-- /AUTO:inputs -->

## 输出项

<!-- AUTO:outputs -->
| key | 显示标签 | 单位 |
|---|---|---|
| `temp` | {{city_display ?? city ?? auto_city}}天气 | — |
<!-- /AUTO:outputs -->

> 标签中含 `{...}` 的是**运行时动态值**（如设备名、城市名、模式名），实际显示由插件在运行时填充。

## 使用说明

1. 打开 LiteMonitor++ 的「设置 → 插件市场」，搜索并安装本插件
2. 在「设置 → 插件管理」中找到它，打开开关
3. 按上面的「配置项」填写参数（没有参数的可跳过）
4. 在「设置 → 监控项显示」里挑选要显示的输出项

## 注意事项

- 需要申请**心知天气 API Key**（在 seniverse.com 注册，基础版免费额度有限）。Key 只发往 `api.seniverse.com`。
- 自动定位依赖 `whois.pconline.com.cn` 的 IP 库，**只能定位到城市级**，且 VPN / 代理会让定位指向代理出口城市。
- `city` 留空即自动定位；手动指定时填心知天气的城市代码（如 `北京` 或 `101010100`）。
- 刷新间隔 1800 秒（30 分钟）—— 天气不需要更频繁。
- 心知天气的免费调用有次数限制，超限后接口会返回错误。

---

*本插件由社区贡献，遵循 [插件开发指南](https://github.com/mojingjing-git/awesome-litemonitor-plugins/blob/main/README.md)。*
