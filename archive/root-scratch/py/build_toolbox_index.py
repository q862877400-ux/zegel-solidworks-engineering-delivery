# -*- coding: utf-8 -*-
"""扫描 SolidWorks Toolbox，建一份可查询的零件索引（JSON）。

⚑ 为什么不用 ``browser/ToolboxFiles.index``
  它是 .NET **BinaryFormatter** 二进制（头 ``00 01 00 00 00 ff ff ff ff`` +
  内部类型名 ``Isldtoolboxdata``）。反序列化这种来路不明的二进制**有代码执行风险**，
  而遍历目录树能得到同样的清单 —— **安全且够用**。

产出结构（按官方目录层级 1:1 对应）：
    standard / category / subcategory / part_name / path / size_bytes
另外从**文件名**抽一个 ``code``（如 ``heavy hex bolt_ai`` → ``heavy hex bolt``），
供按型号模糊查。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT = Path(r"D:\SOLIDWORKS Data\browser")
OUT = Path(r"C:\swprojects\sw-skill-fork\scripts\toolbox_index.json")


def main() -> int:
    if not ROOT.is_dir():
        print("[FATAL] Toolbox 未安装：%s 不存在" % ROOT)
        return 2
    items = []
    for std_dir in sorted(p for p in ROOT.iterdir() if p.is_dir()):
        std = std_dir.name
        for part in sorted(std_dir.rglob("*.sldprt")):
            rel = part.relative_to(std_dir)
            parts = rel.parts
            category = parts[0] if len(parts) > 1 else ""
            subcat = parts[1] if len(parts) > 2 else ""
            stem = part.stem
            # 官方命名约定：`heavy hex bolt_ai` —— 去掉末尾的尺寸/单位后缀
            code = re.sub(r"_(ai|mi|mm|in|inch|metric)$", "", stem, flags=re.I)
            items.append({
                "standard": std,
                "category": category,
                "subcategory": subcat,
                "part": stem,
                "code": code,
                "path": str(part),
                "size_bytes": part.stat().st_size,
            })
    data = {
        "source_root": str(ROOT),
        "note": ("由目录树机械生成；**未解析** browser/ToolboxFiles.index"
                 "（.NET BinaryFormatter 二进制，反序列化有代码执行风险）。"
                 "本索引只记录路径与命名，不含型号→尺寸的工程数据。"),
        "standards": sorted({i["standard"] for i in items}),
        "count": len(items),
        "parts": items,
    }
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

    print("  写出 %s（%.1f MB）" % (OUT.name, OUT.stat().st_size / 1e6))
    print("  零件 %d 个 / 标准 %d 套" % (len(items), len(data["standards"])))
    from collections import Counter
    c = Counter(i["standard"] for i in items)
    for k, v in c.most_common():
        print("    %-16s %4d" % (k, v))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
