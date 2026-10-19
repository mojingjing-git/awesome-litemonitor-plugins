#!/usr/bin/env python3
"""一次性：把 meta.author 的占位符/空值改为仓库 owner

依据：整个仓库的 2 次提交都由 mojingjing-git 提交（git log 已核实），
这些插件也是他加入仓库的，因此 mojingjing-git 是事实上的作者。
"User" / "Codex" / "OpenAI" 属于生成时留下的占位符，会让用户无法判断
该不该信任，予以替换。
"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent / "plugins"
OWNER = "mojingjing-git"

PLACEHOLDERS = {"", "User", "Codex", "OpenAI", "user", "Unknown", "unknown"}

for d in sorted(p for p in ROOT.iterdir() if p.is_dir()):
    f = d / "plugin.json"
    if not f.is_file():
        continue
    data = json.loads(f.read_text(encoding="utf-8"))
    meta = data.get("meta") or {}
    author = (meta.get("author") or "").strip()
    if author in PLACEHOLDERS:
        meta["author"] = OWNER
        f.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )
        print(f"{d.name}: {author!r} -> {OWNER!r}")
    else:
        print(f"{d.name}: 保持 {author!r}")
