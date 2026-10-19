# Token 用量 (TokenTracker)（Token Usage (TokenTracker)）

> 读取 TokenTracker 本地服务，在任务栏/面板显示 AI 编程工具的 Token 用量与花费。显示类别可在插件设置里按目标选择：今日、今日总量(含缓存)、近7天、近30天、累计、近7天花费、累计花费。需要 TokenTracker 桌面端处于运行状态。

## 功能说明

读取 TokenTracker 本地服务，在任务栏/面板显示 AI 编程工具的 Token 用量与花费。

显示类别可在插件设置里按目标选择：今日、今日总量（含缓存）、近 7 天、近 30 天、累计、近 7 天花费、累计花费。

## 配置项

<!-- AUTO:inputs -->
| 参数 | 说明 | 类型 | 默认值 |
|---|---|---|---|
| `base_url` | TokenTracker 本地地址 | text | `http://127.0.0.1:17680` |
| `tz` | 统计时区 | text | `Asia/Shanghai` |
| `display_mode` | 显示类别 | select | `today` |
<!-- /AUTO:inputs -->

## 输出项

<!-- AUTO:outputs -->
| key | 显示标签 | 单位 |
|---|---|---|
| `main` | {{mode_label ?? 'Token'}} | — |
| `today` | 今日 Token | — |
| `week` | 近 7 天 Token | — |
| `month` | 近 30 天 Token | — |
| `cost` | 近 7 天花费 | — |
<!-- /AUTO:outputs -->

> 标签中含 `{...}` 的是**运行时动态值**（如设备名、城市名、模式名），实际显示由插件在运行时填充。

## 使用说明

1. 打开 LiteMonitor++ 的「设置 → 插件市场」，搜索并安装本插件
2. 在「设置 → 插件管理」中找到它，打开开关
3. 按上面的「配置项」填写参数（没有参数的可跳过）
4. 在「设置 → 监控项显示」里挑选要显示的输出项

## 注意事项

- **需要 TokenTracker 桌面端处于运行状态**（默认 `http://127.0.0.1:17680`），否则显示 `[ERROR]`。
- 「今日总量」含缓存命中的 Token，与「今日」的统计口径不同。
- 花费数据来自 TokenTracker 自己的计价表，不同模型的价格可能滞后于官方调整。
- 刷新间隔 60 秒。
- `tz` 参数影响「今日/本周」的边界，默认 `Asia/Shanghai`。

---

*本插件由社区贡献，遵循 [插件开发指南](https://github.com/mojingjing-git/awesome-litemonitor-plugins/blob/main/README.md)。*
