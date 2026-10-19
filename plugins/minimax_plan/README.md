# MiniMax 余量（MiniMax Quota）

> 查询 MiniMax Token Plan 5小时/周窗口剩余配额

## 功能说明

查询 MiniMax Token Plan 的 **5 小时窗口**与**周窗口**剩余配额百分比，以及 5 小时窗口的重置倒计时。

适合在任务栏常驻观察配额消耗速度。

## 配置项

<!-- AUTO:inputs -->
| 参数 | 说明 | 类型 | 默认值 |
|---|---|---|---|
| `api_key` | API Key | text | `` |
<!-- /AUTO:inputs -->

## 输出项

<!-- AUTO:outputs -->
| key | 显示标签 | 单位 |
|---|---|---|
| `interval` | MiniMax 5h | — |
| `weekly` | MiniMax 周 | — |
| `reset` | 5h重置 | — |
<!-- /AUTO:outputs -->

> 标签中含 `{...}` 的是**运行时动态值**（如设备名、城市名、模式名），实际显示由插件在运行时填充。

## 使用说明

1. 打开 LiteMonitor++ 的「设置 → 插件市场」，搜索并安装本插件
2. 在「设置 → 插件管理」中找到它，打开开关
3. 按上面的「配置项」填写参数（没有参数的可跳过）
4. 在「设置 → 监控项显示」里挑选要显示的输出项

## 注意事项

- 需要填写 MiniMax API Key（密码类输入）。Key 只发往 `api.minimaxi.com`。
- `reset` 项显示的是 5 小时窗口的重置倒计时，不是周窗口。
- 刷新间隔 300 秒（5 分钟）。配额窗口本身就是 5 小时级，刷新再快也没有意义。
- Key 失效或账号没有 Token Plan 时接口报错，显示 `[ERROR]`。

---

*本插件由社区贡献，遵循 [插件开发指南](https://github.com/mojingjing-git/awesome-litemonitor-plugins/blob/main/README.md)。*
