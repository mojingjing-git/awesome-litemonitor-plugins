# 水冷管理器本地API增强版（Water Cooler Manager Local API Enhanced）

> 读取 watercooler-manager 导出的设备、模式、风扇、水泵、RGB、CPU/GPU温度和运行时间，支持自定义 API 主机和端口。

## 功能说明

读取 watercooler-manager 导出的设备状态：工作模式、风扇、水泵、RGB 灯效、CPU/GPU 温度与运行时间。支持自定义 API 主机与端口。

## 配置项

<!-- AUTO:inputs -->
| 参数 | 说明 | 类型 | 默认值 |
|---|---|---|---|
| `api_host` | API 主机 | text | `127.0.0.1` |
| `api_port` | API 端口 | text | `21977` |
<!-- /AUTO:inputs -->

## 输出项

<!-- AUTO:outputs -->
| key | 显示标签 | 单位 |
|---|---|---|
| `device_name` | 水冷设备 | — |
| `mode_raw` | 水冷模式 | — |
| `fan_text` | 风扇功率 | — |
| `pump_text` | 水泵功率 | — |
| `rgb_text` | RGB 灯效 | — |
| `cpu_c` | CPU 温度 | °C |
| `gpu_c` | 显卡温度 | °C |
| `uptime_text` | 已运行时间 | — |
<!-- /AUTO:outputs -->

> 标签中含 `{...}` 的是**运行时动态值**（如设备名、城市名、模式名），实际显示由插件在运行时填充。

## 使用说明

1. 打开 LiteMonitor++ 的「设置 → 插件市场」，搜索并安装本插件
2. 在「设置 → 插件管理」中找到它，打开开关
3. 按上面的「配置项」填写参数（没有参数的可跳过）
4. 在「设置 → 监控项显示」里挑选要显示的输出项

## 注意事项

- 需要 watercooler-manager 开启本地 API 导出（默认 `127.0.0.1:21977`）。
- 刷新间隔 **3 秒**，是本仓库里最频繁的一个。本地回环查询通常无压力，但若 API 服务在别的机器上，注意别把轮询打到局域网设备上。
- 该插件的输出项较多（设备名、模式、风扇、水泵、RGB、两个温度、运行时间），**建议按需在「监控项显示」里只开需要的几项**，否则面板会很挤。
- 主机与端口填错时所有输出项都会显示 `[ERROR]`。

---

*本插件由社区贡献，遵循 [插件开发指南](https://github.com/mojingjing-git/awesome-litemonitor-plugins/blob/main/README.md)。*
