#!/usr/bin/env python3
"""插件索引生成器 —— 校验 plugins/ 下的插件并生成 index.json 与 PLUGINS.md

用法:
    python3 scripts/gen_index.py                      # 校验 + 生成 index.json / PLUGINS.md
    python3 scripts/gen_index.py --check              # 只校验，不生成/不覆盖产物
    python3 scripts/gen_index.py --report <path>      # 指定报告输出路径

产物:
    index.json   客户端消费的唯一契约（纯 CI 产物，禁止手改）
    PLUGINS.md   插件清单（由 CI 生成，根 README 引用它）

约定:
  * 目录名必须等于 plugin.json 的 id
  * plugins/<id>/verified 是人工维护的空标记文件，存在即 verified=true
    （本脚本只读它，永不写它）
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import pathlib
import re
import sys
import traceback

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLUGINS_DIR = ROOT / "plugins"

REPO = "mojingjing-git/awesome-litemonitor-plugins"
BRANCH = "main"
RAW_BASE = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}"
PAGE_BASE = f"https://github.com/{REPO}/tree/{BRANCH}"

SCHEMA_VERSION = 1

# 内置插件 id 保护名单 —— 维护提示：
#   新增内置插件时，必须同步更新
#     - 本文件（BUILTIN_IDS）
#     - 客户端 src/Plugins/PluginConstants.cs 的 BuiltinPluginIds
BUILTIN_IDS = {
    "Bilibili", "Crypto", "Exchange", "GitHub", "Hitokoto", "Holiday",
    "ProxyLatency", "PublicIP", "Stock", "UniversalAPI", "Weather", "WeiboHot",
}

ID_RE = re.compile(r"^[A-Za-z0-9_-]{1,64}$")

REQUIRED_README_SECTIONS = ["## 功能说明", "## 输出项", "## 注意事项"]
OPTIONAL_README_SECTIONS = ["## 使用说明"]


# --------------------------------------------------------------------------
# 采集
# --------------------------------------------------------------------------

def sha256_of(path: pathlib.Path) -> str:
    """对文件的原始字节计算 SHA-256（与客户端的校验口径必须一致）"""
    return hashlib.sha256(path.read_bytes()).hexdigest()


def scan_plugins() -> list[dict]:
    """扫描 plugins/ 下的每个插件目录"""
    found = []
    if not PLUGINS_DIR.is_dir():
        return found

    for d in sorted(p for p in PLUGINS_DIR.iterdir() if p.is_dir()):
        entry = {
            "dir": d,
            "name": d.name,
            "plugin_file": d / "plugin.json",
            "readme_file": d / "README.md",
            "verified_marker": d / "verified",
            "data": None,
            "readme_text": "",
            "error": None,
        }
        if entry["plugin_file"].is_file():
            try:
                entry["data"] = json.loads(
                    entry["plugin_file"].read_text(encoding="utf-8")
                )
            except json.JSONDecodeError as e:
                entry["error"] = f"plugin.json 不是合法 JSON: {e}"
            except Exception as e:  # noqa: BLE001
                entry["error"] = f"plugin.json 读取失败: {e}"
        if entry["readme_file"].is_file():
            try:
                entry["readme_text"] = entry["readme_file"].read_text(encoding="utf-8")
            except Exception as e:  # noqa: BLE001
                entry["error"] = f"README.md 读取失败: {e}"
        found.append(entry)
    return found


# --------------------------------------------------------------------------
# 校验
# --------------------------------------------------------------------------

def validate(plugins: list[dict]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    seen_ids: set[str] = set()

    for p in plugins:
        name = p["name"]

        # ---- 目录级 ----
        if not ID_RE.match(name):
            errors.append(f"[{name}] 目录名不合法（只允许 A-Za-z0-9-_，最长 64）")
        if name in BUILTIN_IDS:
            errors.append(f"[{name}] 与内置插件 id 冲突，不能作为市场插件的 id")
        if name in seen_ids:
            errors.append(f"[{name}] 目录名重复")
        seen_ids.add(name)

        if not p["plugin_file"].is_file():
            errors.append(f"[{name}] 缺少 plugin.json")
            continue
        if p["error"]:
            errors.append(f"[{name}] {p['error']}")
            continue
        if not p["readme_file"].is_file():
            errors.append(f"[{name}] 缺少 README.md（介绍是插件页的必需部分）")

        data = p["data"]
        meta = data.get("meta") or {}

        # ---- 插件级 ----
        pid = data.get("id") or ""
        if not pid:
            errors.append(f"[{name}] plugin.json 缺少 id")
        elif pid != name:
            errors.append(f"[{name}] id 为 {pid!r}，与目录名不一致")

        for field in ("name", "description", "author", "version"):
            if not str(meta.get(field, "") or "").strip():
                errors.append(f"[{name}] meta.{field} 为空")

        for field in ("name_en", "description_en"):
            if not str(meta.get(field, "") or "").strip():
                warnings.append(f"[{name}] meta.{field} 为空，英文界面会回退中文")

        for out in data.get("outputs") or []:
            key = out.get("key", "?")
            if not str(out.get("label_en", "") or "").strip():
                warnings.append(f"[{name}] output {key!r} 缺少 label_en")
            # 注意：short_label 可能是 " "（客户端语义 = 隐藏标签），
            # " ".strip() 是空串，所以这里必须用「原始值非空」判断，
            # 不能 strip 后再判 —— 否则填了 " " 也会被误报为缺失。
            sl = out.get("short_label", "")
            if sl and not out.get("short_label_en"):
                warnings.append(
                    f"[{name}] output {key!r} 的 short_label 非空但缺少 short_label_en"
                )

        for inp in data.get("inputs") or []:
            if inp is None:
                continue
            key = inp.get("key", "?")
            if not str(inp.get("label_en", "") or "").strip():
                warnings.append(f"[{name}] input {key!r} 缺少 label_en")

        # ---- README 级（介绍质量门禁）----
        text = p["readme_text"]
        for section in REQUIRED_README_SECTIONS:
            if section not in text:
                errors.append(f"[{name}] README.md 缺少「{section}」小节")

        has_inputs = bool(data.get("inputs"))
        if has_inputs:
            if "## 配置项" not in text:
                errors.append(f"[{name}] README.md 缺少「## 配置项」小节（本插件有 inputs）")
        else:
            if "## 配置项" not in text:
                warnings.append(f"[{name}] 本插件无 inputs，README 的「## 配置项」小节可省略")

        for section in OPTIONAL_README_SECTIONS:
            if section not in text:
                warnings.append(f"[{name}] README.md 建议补「{section}」小节")

    return errors, warnings


# --------------------------------------------------------------------------
# 生成
# --------------------------------------------------------------------------

def build_index(plugins: list[dict]) -> dict:
    items = []
    for p in plugins:
        data = p["data"]
        if data is None:
            continue
        meta = data.get("meta") or {}
        pid = data.get("id") or p["name"]
        items.append(
            {
                "id": pid,
                "original_id": "",
                "renamed": False,
                "name": meta.get("name", ""),
                "name_en": meta.get("name_en", ""),
                "description": meta.get("description", ""),
                "description_en": meta.get("description_en", ""),
                "author": meta.get("author", ""),
                "version": meta.get("version", ""),
                "file": "plugin.json",
                "download_url": f"{RAW_BASE}/plugins/{pid}/plugin.json",
                "readme_url": f"{RAW_BASE}/plugins/{pid}/README.md",
                "page_url": f"{PAGE_BASE}/plugins/{pid}",
                "source": f"https://github.com/{REPO}/blob/{BRANCH}/plugins/{pid}/plugin.json",
                "sha256": sha256_of(p["plugin_file"]),
                "size": p["plugin_file"].stat().st_size,
                "status": meta.get("status", "ok"),
                "requires": meta.get("requires", []),
                "note": meta.get("note", ""),
                "verified": p["verified_marker"].is_file(),
            }
        )

    return {
        "schema": SCHEMA_VERSION,
        "updated_at": _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "repo": REPO,
        "total": len(items),
        "plugins": items,
    }


def build_plugins_md(index: dict) -> str:
    lines = [
        "# 插件清单",
        "",
        "> 本文件由 `scripts/gen_index.py` 自动生成，请勿手工编辑。",
        "",
        f"共 **{index['total']}** 个插件 · 生成于 {index['updated_at']}",
        "",
        "| 插件 | 简介 | 作者 | 版本 | 状态 | 链接 |",
        "|---|---|---|---|---|---|",
    ]
    for it in index["plugins"]:
        name = it["name"] or it["id"]
        desc = (it["description"] or "").replace("|", "\\|")
        if len(desc) > 60:
            desc = desc[:60] + "…"
        status = "已验证" if it["verified"] else "未验证"
        lines.append(
            f"| [{name}]({it['page_url']}) | {desc} | {it['author']} | {it['version']} | {status} | [源码]({it['source']}) |"
        )
    lines.append("")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# 报告
# --------------------------------------------------------------------------

def render_report(errors: list[str], warnings: list[str], index: dict | None) -> str:
    out: list[str] = ["# 插件仓库校验报告", ""]
    if errors:
        out.append(f"## ✗ 校验失败：{len(errors)} 个错误，{len(warnings)} 个警告")
    else:
        out.append(f"## ✓ 校验通过：0 个错误，{len(warnings)} 个警告")
    out.append("")

    if errors:
        out.append("### 错误")
        out.append("")
        for e in errors:
            out.append(f"- {e}")
        out.append("")
    if warnings:
        out.append("### 警告")
        out.append("")
        for w in warnings:
            out.append(f"- {w}")
        out.append("")
    if index:
        out.append("### 索引")
        out.append("")
        out.append(f"- 插件数：{index['total']}")
        out.append(f"- schema：{index['schema']}")
        out.append(f"- 生成时间：{index['updated_at']}")
        out.append("")
    return "\n".join(out)


def write_report(path: pathlib.Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


# --------------------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="只校验，不生成也不覆盖产物")
    ap.add_argument("--report", default="validation-report.md", help="报告输出路径")
    args = ap.parse_args()

    report_path = ROOT / args.report

    try:
        plugins = scan_plugins()
        errors, warnings = validate(plugins)

        index = None
        if not errors and not args.check:
            index = build_index(plugins)
            (ROOT / "index.json").write_text(
                json.dumps(index, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
                newline="\n",
            )
            (ROOT / "PLUGINS.md").write_text(
                build_plugins_md(index), encoding="utf-8", newline="\n"
            )

        write_report(report_path, render_report(errors, warnings, index))

        for e in errors:
            print(f"ERROR  {e}")
        for w in warnings:
            print(f"WARN   {w}")

        if errors:
            print(f"\n✗ 校验失败：{len(errors)} 个错误，{len(warnings)} 个警告")
            return 1

        if args.check:
            print(f"\n✓ 校验通过（0 错误，{len(warnings)} 个警告）")
        else:
            print(f"\n✓ 已生成 index.json 与 PLUGINS.md（{index['total']} 个插件）")
        return 0

    except Exception:  # noqa: BLE001
        # 脚本自身崩溃时也必须留下报告，否则 CI 的 artifact 步骤会以
        # "找不到文件" 失败，掩盖真正的错误信息
        write_report(
            report_path,
            "# 插件仓库校验报告\n\n## 脚本异常\n\n```\n"
            + traceback.format_exc()
            + "\n```\n",
        )
        raise


if __name__ == "__main__":
    sys.exit(main())
