#!/usr/bin/env python3
"""双语字段补全工具 —— 检查并补全插件的 _en 字段

用法:
    python3 scripts/fix_i18n.py            # 只检查，报告缺口（不写文件）
    python3 scripts/fix_i18n.py --apply    # 检查 + 补全可自动推导的部分

自动推导规则（只处理「安全」的情况）：
  1. short_label 非空且不是 " "，而 short_label_en 缺失：
     - 若 short_label 是纯 ASCII（缩写/数字，中英通用）→ 直接复制
     - 若 short_label 含中文 → 不自动处理，报告出来交给人工
  2. short_label == " "（客户端语义：隐藏标签）→ 复制 " "，
     保持「英文界面下同样隐藏」的一致性
  3. inputs[].label 缺失 label_en，且 label 是纯 ASCII → 直接复制
  4. meta.author 去掉首尾空格

无法自动推导的（中文 label / 模板变量）会列在报告里，需要人工在
OVERRIDES 表里补充，或直接改 plugin.json。
"""

import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLUGINS_DIR = ROOT / "plugins"

# 纯 ASCII（不含中文等非 ASCII 字符）判定
ASCII_RE = re.compile(r"^[\x20-\x7E]*$")

# 中日韩文字判定 —— 含 CJK 的文案无法直接复用为英文，必须人工翻译
CJK_RE = re.compile(
    r"[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uac00-\ud7af]"
)

# 人工覆盖：无法从现有字段自动推导的 _en 值
# 结构: { 插件id: { "outputs": { key: {"label_en": ..., "short_label_en": ...} },
#                   "inputs": { key: {"label_en": ...} } } }
OVERRIDES = {
    # TokenTracker 的 main 项标签由运行时变量 mode_label / mode_short 决定，
    # 那两张 map 是中文的。这里给插件补两张英文 map（见 TOKEN_TRACKER_MAPS），
    # 然后用 ?? 回退语法引用它们。
    "TokenTracker": {
        "outputs": {
            "main": {
                "label_en": "{{mode_label_en ?? 'Token'}}",
                "short_label_en": "{{mode_short_en ?? 'TK'}}",
            }
        }
    },
}

# 需要注入到插件 process 段的新 transform（英文 map）
TOKEN_TRACKER_MAPS = [
    {
        "var": "mode_label_en",
        "source": "display_mode",
        "function": "map",
        "map": {
            "today": "Today",
            "today_all": "Today (Total)",
            "week": "Last 7 Days",
            "month": "Last 30 Days",
            "total": "Total",
            "week_cost": "Last 7 Days Cost",
            "total_cost": "Total Cost",
        },
    },
    {
        "var": "mode_short_en",
        "source": "display_mode",
        "function": "map",
        "map": {
            "today": "Day",
            "today_all": "Day+",
            "week": "7D",
            "month": "30D",
            "total": "Total",
            "week_cost": "7D$",
            "total_cost": "Total$",
        },
    },
]


def is_ascii(s: str) -> bool:
    return bool(s) and bool(ASCII_RE.match(s))


def has_cjk(s: str) -> bool:
    """是否含中日韩文字 —— 含则无法自动翻译为英文"""
    return bool(s) and bool(CJK_RE.search(s))


def apply_overrides(plugin_id: str, data: dict) -> bool:
    """套用人工覆盖表，返回是否发生了修改"""
    changed = False
    ov = OVERRIDES.get(plugin_id)
    if not ov:
        return False

    for out in data.get("outputs", []) or []:
        patch = (ov.get("outputs", {}) or {}).get(out.get("key"))
        if not patch:
            continue
        for field, value in patch.items():
            if out.get(field) != value:
                out[field] = value
                changed = True

    for inp in data.get("inputs", []) or []:
        patch = (ov.get("inputs", {}) or {}).get(inp.get("key"))
        if not patch:
            continue
        for field, value in patch.items():
            if inp.get(field) != value:
                inp[field] = value
                changed = True

    return changed


def inject_process_maps(plugin_id: str, data: dict) -> bool:
    """给指定插件的 execution.process 注入额外的 transform"""
    if plugin_id != "TokenTracker":
        return False
    proc = data.get("execution", {}).get("process")
    if not isinstance(proc, list):
        return False
    changed = False
    for new in TOKEN_TRACKER_MAPS:
        if any(t.get("var") == new["var"] for t in proc):
            continue
        # 插到对应中文 map 之后，保持可读性
        idx = len(proc)
        for i, t in enumerate(proc):
            if t.get("var") == new["var"].replace("_en", ""):
                idx = i + 1
                break
        proc.insert(idx, dict(new))
        changed = True
    return changed


def fix_one(path: pathlib.Path, apply: bool) -> tuple[bool, list[str]]:
    """处理单个插件文件。返回 (是否修改, 人工待办列表)"""
    data = json.loads(path.read_text(encoding="utf-8"))
    plugin_id = data.get("id", path.parent.name)
    manual: list[str] = []
    changed = False

    # --- meta.author 规范化 ---
    meta = data.get("meta") or {}
    author = meta.get("author")
    if isinstance(author, str) and author != author.strip():
        if apply:
            meta["author"] = author.strip()
            changed = True

    # --- outputs ---
    for out in data.get("outputs", []) or []:
        key = out.get("key", "?")
        sl = out.get("short_label", "")
        sle = out.get("short_label_en")

        if sle is None or sle == "":
            if sl == "" or sl == " ":
                # 客户端语义：短标签为空或空格 = 隐藏标签。英文下同样隐藏。
                if apply:
                    out["short_label_en"] = sl
                    changed = True
            elif is_ascii(sl):
                # 缩写/数字，中英通用
                if apply:
                    out["short_label_en"] = sl
                    changed = True
            else:
                manual.append(f"outputs[{key}].short_label_en  （short_label={sl!r} 含中文，需人工）")

        # label_en 缺失且 label 不含中日韩文字 → 可直接复用
        # （ASCII 缩写、emoji、符号等，中英含义一致）
        le = out.get("label_en")
        if (le is None or le == "") and out.get("label") and not has_cjk(out["label"]):
            if apply:
                out["label_en"] = out["label"]
                changed = True

    # --- inputs ---
    for inp in data.get("inputs", []) or []:
        key = inp.get("key", "?")
        le = inp.get("label_en")
        il = inp.get("label", "")
        if (le is None or le == "") and il and not has_cjk(il):
            if apply:
                inp["label_en"] = il
                changed = True
        elif le is None or le == "":
            manual.append(f"inputs[{key}].label_en  （label={il!r}）")

    # --- 人工覆盖 + 注入 map ---
    if apply:
        changed |= apply_overrides(plugin_id, data)
        changed |= inject_process_maps(plugin_id, data)

    if changed and apply:
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )

    return changed, manual


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="实际写回文件")
    args = ap.parse_args()

    if not PLUGINS_DIR.is_dir():
        print(f"找不到插件目录: {PLUGINS_DIR}", file=sys.stderr)
        return 2

    all_manual: list[str] = []
    changed_count = 0

    for d in sorted(p for p in PLUGINS_DIR.iterdir() if p.is_dir()):
        f = d / "plugin.json"
        if not f.is_file():
            all_manual.append(f"[{d.name}] 缺少 plugin.json")
            continue
        changed, manual = fix_one(f, args.apply)
        if changed:
            changed_count += 1
        for m in manual:
            all_manual.append(f"[{d.name}] {m}")

    mode = "已写回" if args.apply else "仅检查"
    print(f"双语补全（{mode}）：{changed_count} 个插件有改动")

    if all_manual:
        print("\n需人工处理：")
        for m in all_manual:
            print("  " + m)
    else:
        print("无待人工处理项 ✓")

    return 0


if __name__ == "__main__":
    sys.exit(main())
