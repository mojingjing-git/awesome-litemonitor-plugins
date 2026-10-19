# 代理公网IP显示（Proxy Public IP）

> 代理公网IP插件，获取当前网络的代理公网IPv4地址

## 功能说明

显示当前网络的**代理出口**公网 IPv4 地址、代理服务商与所在地区。

适合确认「我的代理实际出口在哪、是哪家服务商」。

## 配置项

<!-- AUTO:inputs -->
_本插件无需配置。_
<!-- /AUTO:inputs -->

## 输出项

<!-- AUTO:outputs -->
| key | 显示标签 | 单位 |
|---|---|---|
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

- IP 来自 `api.ipapi.is`，延迟测试打到 `www.google.com/generate_204` —— **这两个都是境外地址，国内网络下可能直接超时**，届时延迟项显示 `[ERROR]`。
- **只反映代理出口**。要对比直连出口，请安装 `DirectPublicIP` 或 `public_ip_info`。
- 如果没有走代理，测出的就是你的直连 IP —— 插件无法判断你是否真的开了代理。
- 刷新间隔 600 秒。

---

*本插件由社区贡献，遵循 [插件开发指南](https://github.com/mojingjing-git/awesome-litemonitor-plugins/blob/main/README.md)。*
