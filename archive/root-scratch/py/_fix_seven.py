"""★ 修 7 个脚本式文件：把 `from pathlib import Path` + `_ROOT_S` 定义插到**第一次使用之前**。"""

import ast
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW")
#: ★ **显式清单**（★ 不再用目录遍历 —— 那样会扫进 1055 个草稿）
FILES = [
    "tools/emit_iview_module.py",
    "tools/emit_study_options_module.py",
    "tools/freeze_unattended_baseline.py",
    "tools/w4_semantics.py",
    "tools/w5_feature.py",
    "tools/w6_cand.py",
    "tools/w6_shapes.py",
]
NOTE = "#: ★ 本仓库根（★ 2026-10-03 合并后自定位）"


def main() -> int:
    for rel in FILES:
        p = R / rel
        lines = p.read_text(encoding="utf-8").splitlines()
        #: ① \u5148\u5220\u6389\u63d2\u9519\u4f4d\u7f6e\u7684\u90a3\u4e24\u884c
        keep = []
        dropped = 0
        for l in lines:
            if l.strip().startswith(NOTE) or re.match(r"^_ROOT_S\s*=", l.strip()):
                dropped += 1
                continue
            keep.append(l)
        #: ② \u627e**\u7b2c\u4e00\u6b21\u4f7f\u7528** `_ROOT_S` \u7684\u884c
        idx = next((i for i, l in enumerate(keep) if "_ROOT_S" in l), None)
        if idx is None:
            print("  **%s\uff1a\u6ca1\u627e\u5230\u4f7f\u7528\uff0c\u8df3\u8fc7**" % rel)
            continue
        d = len(p.relative_to(R).parts) - 1
        ins = []
        if not re.search(r"^(from pathlib import|import pathlib)", "\n".join(keep), re.M):
            ins.append("from pathlib import Path")
        ins += [NOTE, "_ROOT_S = str(Path(__file__).resolve().parents[%d])" % d, ""]
        new = "\n".join(keep[:idx] + ins + keep[idx:]) + "\n"
        try:
            ast.parse(new)
        except SyntaxError as exc:
            print("  **%s \u8bed\u6cd5\u574f\u4e86\uff1a%s**" % (rel, exc))
            continue
        p.write_text(new, encoding="utf-8")
        #: \u2605 \u56de\u8bfb\uff08\u4e8b\u5b9e 48 \u5b9a\u5219\u2461\uff09
        chk = p.read_text(encoding="utf-8").splitlines()
        ui = next(i for i, l in enumerate(chk) if "_ROOT_S" in l)
        di = next((i for i, l in enumerate(chk) if re.match(r"^_ROOT_S\s*=", l)), -1)
        ok = di >= 0 and di < ui
        print("  %s %-46s \u5220%d \u884c \u00b7 \u5b9a\u4e49L%d < \u4f7f\u7528L%d" % (
            "\u2713" if ok else "**\u2717**", rel, dropped, di + 1, ui + 1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
