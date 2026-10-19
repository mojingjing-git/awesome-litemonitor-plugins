# 直连公网IP显示（Direct Public IP）

> 直连公网IP插件，获取当前网络的直连公网IPv4地址

## 功能说明

显示当前网络的**直连**公网 IPv4 地址、归属地（省/市/区）与到国内服务器的延迟。

只测直连出口，不涉及任何代理 —— 适合排查「我的直连 IP 到底是什么」。

## 配置项

<!-- AUTO:inputs -->
_本插件无需配置。_
<!-- /AUTO:inputs -->

## 输出项

<!-- AUTO:outputs -->
| key | 显示标签 | 单位 |
|---|---|---|
| `direct_ip` | 直连IP | — |
| `direct_addr` | 直连🌏 | — |
| `direct_latency` | 直连⏳ | — |
<!-- /AUTO:outputs -->

> 标签中含 `{...}` 的是**运行时动态值**（如设备名、城市名、模式名），实际显示由插件在运行时填充。

## 使用说明

1. 打开 LiteMonitor++ 的「设置 → 插件市场」，搜索并安装本插件
2. 在「设置 → 插件管理」中找到它，打开开关
3. 按上面的「配置项」填写参数（没有参数的可跳过）
4. 在「设置 → 监控项显示」里挑选要显示的输出项

## 注意事项

- IP 归属地来自 `whois.pconline.com.cn`（国内服务），延迟测试打到 `wifi.vivo.com.cn`。**两个都是国内地址**，在纯 IPv6 或特殊网络环境下可能失败。
- 延迟测试走的是 **明文 HTTP**（`http://wifi.vivo.com.cn/generate_204`），仅用于测时延、不传输敏感数据。
- 刷新间隔 600 秒（10 分钟）—— 实时性要求高的话改 `execution.interval`，但会相应增加对第三方站点的请求频率。
- 本插件只测直连。**要同时看代理出口 IP，请另外安装 `public_ip_info` 或 `proxy_public_ip`**。

---

*本插件由社区贡献，遵循 [插件开发指南](https://github.com/mojingjing-git/awesome-litemonitor-plugins/blob/main/README.md)。*
