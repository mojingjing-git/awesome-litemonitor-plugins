#!/usr/bin/env python3
"""插件介绍页生成器 —— 生成/刷新 plugins/<id>/README.md

设计：
  * 「配置项」「输出项」两张表从 plugin.json 自动填充，用
    <!-- AUTO:inputs --> / <!-- AUTO:outputs --> 标记圈定，
    脚本只替换标记之间的内容，**不会覆盖人工撰写的部分**。
  * 「功能说明」「注意事项」是人工撰写的核心内容，存放在下面的
    CONTENT 字典里 —— 这是本仓库相对官方索引的价值所在。
  * README 已存在时只刷新表格；不存在时用模板 + CONTENT 全新生成。

用法:
    python3 scripts/init_readme.py            # 生成缺失的 README
    python3 scripts/init_readme.py --force    # 强制用模板重建（丢弃已有 README）
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLUGINS_DIR = ROOT / "plugins"

# --------------------------------------------------------------------------
# 人工撰写的内容 —— 「功能说明」与「注意事项（踩坑提示）」
# --------------------------------------------------------------------------

CONTENT: dict[str, dict] = {
    "bluetooth_battery": {
        "summary": (
            "监控当前正在连接的蓝牙设备电量。只显示**已连接**的设备，按电量从低到高排列，"
            "最多同时显示 6 台；电量低于阈值时数值变红。\n\n"
            "数据来自本机的 `BluetoothBattery.ps1` 本地服务（默认监听 `127.0.0.1:18923`），"
            "该服务负责读取 Windows 蓝牙栈的设备电量并以 JSON 返回。"
        ),
        "notes": [
            "**必须先运行 `BluetoothBattery.ps1` 本地服务**，否则本插件只会显示 `[ERROR]`。"
            "该脚本不在本仓库内，需要自行获取。",
            "服务端口默认 `18923`，如被占用可在插件设置里改 `port` 参数。",
            "`warn` 参数是低电量告警阈值（百分比，默认 20），低于此值时数值变红。",
            "最多显示 6 台设备（`dev1`~`dev6`）。设备多于 6 台时，**按电量从低到高取前 6 台** —— "
            "即最需要关注的低电量设备优先显示。",
            "每台设备对应一条独立的监控项，可在「设置 → 监控项显示」里单独开关；"
            "未连接的设备不占位。",
            "刷新间隔 30 秒。蓝牙设备休眠后可能短暂读取失败，表现为某一行显示 `[EMPTY]`。",
        ],
    },
    "deepseek_balance": {
        "summary": (
            "查询 DeepSeek API 账户的**实时余额**，同时显示人民币与美元两个口径。\n\n"
            "调用官方接口 `https://api.deepseek.com/user/balance`，直接读取账户余额字段，"
            "不做任何缓存之外的加工。"
        ),
        "notes": [
            "需要填写 DeepSeek API Key（在「插件管理」中把类型设为密码类输入，避免被截图泄露）。"
            "Key 只会被发往 `api.deepseek.com`。",
            "这里显示的是**账户余额**（充值后剩余的钱），不是套餐额度，两者含义不同。",
            "刷新间隔 60 秒。余额变动后最多延迟 1 分钟才反映。",
            "Key 失效或余额为负时接口会返回错误，此时会显示 `[ERROR]`。",
        ],
    },
    "DirectPublicIP": {
        "summary": (
            "显示当前网络的**直连**公网 IPv4 地址、归属地（省/市/区）与到国内服务器的延迟。\n\n"
            "只测直连出口，不涉及任何代理 —— 适合排查「我的直连 IP 到底是什么」。"
        ),
        "notes": [
            "IP 归属地来自 `whois.pconline.com.cn`（国内服务），延迟测试打到 `wifi.vivo.com.cn`。"
            "**两个都是国内地址**，在纯 IPv6 或特殊网络环境下可能失败。",
            "延迟测试走的是 **明文 HTTP**（`http://wifi.vivo.com.cn/generate_204`），"
            "仅用于测时延、不传输敏感数据。",
            "刷新间隔 600 秒（10 分钟）—— 实时性要求高的话改 `execution.interval`，"
            "但会相应增加对第三方站点的请求频率。",
            "本插件只测直连。**要同时看代理出口 IP，请另外安装 `public_ip_info` 或 `proxy_public_ip`**。",
        ],
    },
    "fan_speed": {
        "summary": (
            "直接读取 EC（嵌入式控制器）上报的风扇转速，实时显示 CPU 与 GPU 风扇的 RPM。\n\n"
            "不走任何厂商驱动接口，因此不依赖主板厂商的监控软件。"
        ),
        "notes": [
            "**硬编码机型**：本插件针对「机械革命蛟龙 16 Pro」编写，"
            "读取其 EC 暴露在 `http://localhost:18900/fan` 的接口。"
            "**其它机型大概率读不到数据** —— 这是从该机型适配过来的实现，不是通用方案。",
            "需要对应的 EC 查询服务在 `127.0.0.1:18900` 运行，否则显示 `[ERROR]`。",
            "刷新间隔 5 秒，属于比较频繁的轮询。EC 接口不稳定时可能出现数值跳变。",
            "EC 读取有极小概率影响系统稳定性，笔记本电池电量低时更明显。",
        ],
    },
    "gold_price": {
        "summary": (
            "显示伦敦现货黄金（XAU）价格。\n\n"
            "调用 `gold-api.com` 的公开接口，无需 API Key。"
        ),
        "notes": [
            "无需任何凭据，填好就能用。",
            "接口为境外服务，**网络不通时会显示 `[ERROR]`**。",
            "该接口不保证实时行情，**不应用于交易决策**，仅供参考。",
            "价格按接口返回的原始数值显示，未做单位换算。",
        ],
    },
    "MiMoToken": {
        "summary": (
            "显示小米 MiMo Token Plan 套餐的用量与额度占用情况。\n\n"
            "走客户端内置的 `native://mimo` 处理器 —— 传入浏览器 Cookie，"
            "由客户端解析出套餐用量，而不是插件自己去拼接口。"
        ),
        "notes": [
            "需要填写小米账号的 **Cookie**（在浏览器登录后从开发者工具复制）。"
            "Cookie 属于**账号凭据**，只会被发往小米自己的接口，但仍请只在本机可信环境使用。",
            "Cookie 会过期，过期后显示 `[ERROR]`。需要重新获取。",
            "刷新间隔 60 秒。",
            "如果你的账号没有 Token Plan 套餐，接口可能返回空数据。",
        ],
    },
    "minimax_plan": {
        "summary": (
            "查询 MiniMax Token Plan 的 **5 小时窗口**与**周窗口**剩余配额百分比，"
            "以及 5 小时窗口的重置倒计时。\n\n"
            "适合在任务栏常驻观察配额消耗速度。"
        ),
        "notes": [
            "需要填写 MiniMax API Key（密码类输入）。Key 只发往 `api.minimaxi.com`。",
            "`reset` 项显示的是 5 小时窗口的重置倒计时，不是周窗口。",
            "刷新间隔 300 秒（5 分钟）。配额窗口本身就是 5 小时级，刷新再快也没有意义。",
            "Key 失效或账号没有 Token Plan 时接口报错，显示 `[ERROR]`。",
        ],
    },
    "proxy_public_ip": {
        "summary": (
            "显示当前网络的**代理出口**公网 IPv4 地址、代理服务商与所在地区。\n\n"
            "适合确认「我的代理实际出口在哪、是哪家服务商」。"
        ),
        "notes": [
            "IP 来自 `api.ipapi.is`，延迟测试打到 `www.google.com/generate_204` —— "
            "**这两个都是境外地址，国内网络下可能直接超时**，届时延迟项显示 `[ERROR]`。",
            "**只反映代理出口**。要对比直连出口，请安装 `DirectPublicIP` 或 `public_ip_info`。",
            "如果没有走代理，测出的就是你的直连 IP —— 插件无法判断你是否真的开了代理。",
            "刷新间隔 600 秒。",
        ],
    },
    "public_ip_info": {
        "summary": (
            "同时显示**直连**与**代理**两组公网信息：各自的 IPv4 地址、归属地与延迟。\n\n"
            "本插件是 `DirectPublicIP` 与 `proxy_public_ip` 的合并版，"
            "一次调用即可对比两条链路。"
        ),
        "notes": [
            "一次刷新会发起 **4 个外部请求**（直连 IP / 直连延迟 / 代理 IP / 代理延迟），"
            "比单独装一个插件更频繁。",
            "延迟测试涉及 `wifi.vivo.com.cn`（明文 HTTP）与 `www.google.com`（境外），"
            "**国内网络下代理延迟项大概率失败**。",
            "全部走公共第三方接口，**不要用于对 IP 归属有隐私要求的场景**。",
            "刷新间隔 600 秒。",
        ],
    },
    "TokenTracker": {
        "summary": (
            "读取 TokenTracker 本地服务，在任务栏/面板显示 AI 编程工具的 Token 用量与花费。\n\n"
            "显示类别可在插件设置里按目标选择：今日、今日总量（含缓存）、近 7 天、"
            "近 30 天、累计、近 7 天花费、累计花费。"
        ),
        "notes": [
            "**需要 TokenTracker 桌面端处于运行状态**（默认 `http://127.0.0.1:17680`），"
            "否则显示 `[ERROR]`。",
            "「今日总量」含缓存命中的 Token，与「今日」的统计口径不同。",
            "花费数据来自 TokenTracker 自己的计价表，不同模型的价格可能滞后于官方调整。",
            "刷新间隔 60 秒。",
            "`tz` 参数影响「今日/本周」的边界，默认 `Asia/Shanghai`。",
        ],
    },
    "watercooler_manager_local_api_full": {
        "summary": (
            "读取 watercooler-manager 导出的设备状态：工作模式、风扇、水泵、RGB 灯效、"
            "CPU/GPU 温度与运行时间。支持自定义 API 主机与端口。"
        ),
        "notes": [
            "需要 watercooler-manager 开启本地 API 导出（默认 `127.0.0.1:21977`）。",
            "刷新间隔 **3 秒**，是本仓库里最频繁的一个。本地回环查询通常无压力，"
            "但若 API 服务在别的机器上，注意别把轮询打到局域网设备上。",
            "该插件的输出项较多（设备名、模式、风扇、水泵、RGB、两个温度、运行时间），"
            "**建议按需在「监控项显示」里只开需要的几项**，否则面板会很挤。",
            "主机与端口填错时所有输出项都会显示 `[ERROR]`。",
        ],
    },
    "WirelessBattery": {
        "summary": (
            "实时监控英菲克无线鼠标与漫步者花再耳机的电量，分别显示上下两行，"
            "也可合并成一行带 Emoji 图标的摘要。"
        ),
        "notes": [
            "需要配套的本地服务在 `127.0.0.1:28888` 提供电池数据，否则显示 `[ERROR]`。",
            "**只支持英菲克无线鼠标与漫步者花再耳机这两款特定设备** —— "
            "其它蓝牙设备读不到，因为服务是按这两款设备的协议写的。",
            "设备休眠或断开连接时，电量可能短暂显示为空。",
            "刷新间隔 5 秒。",
        ],
    },
    "XinzhiWeather": {
        "summary": (
            "基于心知天气（seniverse）API 的实时天气，支持按 IP 自动定位城市，"
            "也可手动指定城市代码。显示温度、天气现象与体感温度。"
        ),
        "notes": [
            "需要申请**心知天气 API Key**（在 seniverse.com 注册，基础版免费额度有限）。"
            "Key 只发往 `api.seniverse.com`。",
            "自动定位依赖 `whois.pconline.com.cn` 的 IP 库，**只能定位到城市级**，"
            "且 VPN / 代理会让定位指向代理出口城市。",
            "`city` 留空即自动定位；手动指定时填心知天气的城市代码（如 `北京` 或 `101010100`）。",
            "刷新间隔 1800 秒（30 分钟）—— 天气不需要更频繁。",
            "心知天气的免费调用有次数限制，超限后接口会返回错误。",
        ],
    },
}

# --------------------------------------------------------------------------

TEMPLATE = """# {title}（{title_en}）

> {description}

## 功能说明

{summary}

## 配置项

<!-- AUTO:inputs -->
{inputs_table}
<!-- /AUTO:inputs -->

## 输出项

<!-- AUTO:outputs -->
{outputs_table}
<!-- /AUTO:outputs -->

> 标签中含 `{{...}}` 的是**运行时动态值**（如设备名、城市名、模式名），实际显示由插件在运行时填充。

## 使用说明

{usage}

## 注意事项

{notes}

---

*本插件由社区贡献，遵循 [插件开发指南](https://github.com/mojingjing-git/awesome-litemonitor-plugins/blob/main/README.md)。*
"""


def auto_block(text: str, tag: str, body: str) -> str:
    """替换 <!-- AUTO:tag --> ... <!-- /AUTO:tag --> 之间的内容"""
    pat = re.compile(
        rf"(<!-- AUTO:{re.escape(tag)} -->\n).*?(\n<!-- /AUTO:{re.escape(tag)} -->)",
        re.DOTALL,
    )
    return pat.sub(lambda m: m.group(1) + body.rstrip("\n") + m.group(2), text)


def build_inputs_table(data: dict) -> str:
    inputs = [i for i in (data.get("inputs") or []) if i is not None]
    if not inputs:
        return "_本插件无需配置。_"
    lines = [
        "| 参数 | 说明 | 类型 | 默认值 |",
        "|---|---|---|---|",
    ]
    for i in inputs:
        lines.append(
            "| `{key}` | {label} | {type} | `{default}` |".format(
                key=i.get("key", ""),
                label=i.get("label", "") or i.get("label_en", ""),
                type=i.get("type", "text"),
                default=i.get("default", ""),
            )
        )
    return "\n".join(lines)


def build_outputs_table(data: dict) -> str:
    outputs = data.get("outputs") or []
    if not outputs:
        return "_本插件无输出项。_"
    lines = [
        "| key | 显示标签 | 单位 |",
        "|---|---|---|",
    ]
    for o in outputs:
        unit = o.get("unit", "") or ""
        lines.append(
            f"| `{o.get('key', '')}` | {o.get('label', '')} | {unit or '—'} |"
        )
    return "\n".join(lines)


def build_usage(data: dict) -> str:
    return (
        "1. 打开 LiteMonitor++ 的「设置 → 插件市场」，搜索并安装本插件\n"
        "2. 在「设置 → 插件管理」中找到它，打开开关\n"
        "3. 按上面的「配置项」填写参数（没有参数的可跳过）\n"
        "4. 在「设置 → 监控项显示」里挑选要显示的输出项"
    )


def render(plugin_id: str, data: dict, existing: str | None) -> str:
    meta = data.get("meta") or {}
    content = CONTENT.get(plugin_id, {})
    summary = content.get("summary", meta.get("description", ""))
    notes = content.get("notes", [])
    notes_text = "\n".join(f"- {n}" for n in notes) if notes else "- 暂无。"

    if existing:
        text = existing
    else:
        text = TEMPLATE.format(
            title=meta.get("name", plugin_id),
            title_en=meta.get("name_en", ""),
            description=meta.get("description", ""),
            summary=summary,
            inputs_table="",
            outputs_table="",
            usage=build_usage(data),
            notes=notes_text,
        )

    text = auto_block(text, "inputs", build_inputs_table(data))
    text = auto_block(text, "outputs", build_outputs_table(data))

    if not existing:
        text = text.replace("{summary}", summary).replace("{notes}", notes_text)
        text = text.replace("{usage}", build_usage(data))

    return text.rstrip("\n") + "\n"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="强制重建，丢弃已有 README")
    args = ap.parse_args()

    if not PLUGINS_DIR.is_dir():
        print(f"找不到插件目录: {PLUGINS_DIR}", file=sys.stderr)
        return 2

    created = 0
    refreshed = 0
    for d in sorted(p for p in PLUGINS_DIR.iterdir() if p.is_dir()):
        pf = d / "plugin.json"
        rf = d / "README.md"
        if not pf.is_file():
            print(f"  ! {d.name} 缺少 plugin.json，跳过")
            continue
        data = json.loads(pf.read_text(encoding="utf-8"))

        existing = None
        if rf.is_file() and not args.force:
            existing = rf.read_text(encoding="utf-8")

        out = render(data.get("id", d.name), data, existing)
        rf.write_text(out, encoding="utf-8", newline="\n")
        if existing is None:
            created += 1
            print(f"  新建 {d.name}/README.md")
        else:
            refreshed += 1
            print(f"  刷新 {d.name}/README.md")

    print(f"\n完成：新建 {created} 篇，刷新 {refreshed} 篇")
    return 0


if __name__ == "__main__":
    sys.exit(main())
