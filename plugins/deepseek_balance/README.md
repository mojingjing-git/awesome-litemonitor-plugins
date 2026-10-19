# DeepSeek 餘額 (CNY/USD)（DeepSeek Balance (CNY/USD)）

> 監控 DeepSeek API 帳戶實時餘額 (同時顯示人民幣與美金)

## 功能说明

查询 DeepSeek API 账户的**实时余额**，同时显示人民币与美元两个口径。

调用官方接口 `https://api.deepseek.com/user/balance`，直接读取账户余额字段，不做任何缓存之外的加工。

## 配置项

<!-- AUTO:inputs -->
| 参数 | 说明 | 类型 | 默认值 |
|---|---|---|---|
| `api_key` | DeepSeek API Key | text | `` |
<!-- /AUTO:inputs -->

## 输出项

<!-- AUTO:outputs -->
| key | 显示标签 | 单位 |
|---|---|---|
| `bal_cny` | DeepSeek (CNY) | — |
| `bal_usd` | DeepSeek (USD) | — |
<!-- /AUTO:outputs -->

> 标签中含 `{...}` 的是**运行时动态值**（如设备名、城市名、模式名），实际显示由插件在运行时填充。

## 使用说明

1. 打开 LiteMonitor++ 的「设置 → 插件市场」，搜索并安装本插件
2. 在「设置 → 插件管理」中找到它，打开开关
3. 按上面的「配置项」填写参数（没有参数的可跳过）
4. 在「设置 → 监控项显示」里挑选要显示的输出项

## 注意事项

- 需要填写 DeepSeek API Key（在「插件管理」中把类型设为密码类输入，避免被截图泄露）。Key 只会被发往 `api.deepseek.com`。
- 这里显示的是**账户余额**（充值后剩余的钱），不是套餐额度，两者含义不同。
- 刷新间隔 60 秒。余额变动后最多延迟 1 分钟才反映。
- Key 失效或余额为负时接口会返回错误，此时会显示 `[ERROR]`。

---

*本插件由社区贡献，遵循 [插件开发指南](https://github.com/mojingjing-git/awesome-litemonitor-plugins/blob/main/README.md)。*
