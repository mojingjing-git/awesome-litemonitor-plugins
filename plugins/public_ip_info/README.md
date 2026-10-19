# 公网IP显示（Public IP）

> 公网IP插件，获取当前网络的公网IPv4地址

## 功能说明

同时显示**直连**与**代理**两组公网信息：各自的 IPv4 地址、归属地与延迟。

本插件是 `DirectPublicIP` 与 `proxy_public_ip` 的合并版，一次调用即可对比两条链路。

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
| `proxy_ip` | 代理IP | — |
| `proxy_addr` | 代理🌏 | — |
| `proxy_latency` | 代理⏳ | — |
<!-- /AUTO:outputs -->

> 标签中含 `{...}` 的是**运行时动态值**（如设备名、城市名、模式名），实际显示由插件在运行时填充。

## 使用说明

1. 打开 LiteMonitor++ 的「设置 → 插件市场」，搜索并安装本插件
2. 在「设置 → 插件管理」中找到它，打开开关
3. 按上面的「配置项」填写参数（没有参数的可跳过）
4. 在「设置 → 监控项显示」里挑选要显示的输出项

## 注意事项

- 一次刷新会发起 **4 个外部请求**（直连 IP / 直连延迟 / 代理 IP / 代理延迟），比单独装一个插件更频繁。
- 延迟测试涉及 `wifi.vivo.com.cn`（明文 HTTP）与 `www.google.com`（境外），**国内网络下代理延迟项大概率失败**。
- 全部走公共第三方接口，**不要用于对 IP 归属有隐私要求的场景**。
- 刷新间隔 600 秒。

---

*本插件由社区贡献，遵循 [插件开发指南](https://github.com/mojingjing-git/awesome-litemonitor-plugins/blob/main/README.md)。*
