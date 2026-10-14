"""★ 第 19 轮：全仓最后一遍扫描 —— 判「还剩什么」。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tools/final_sweep.py
# 定位:   规格 `specs/332-known-facts-triage` 的**收口扫描**。
#           ★★ 业主 2026-10-14 的收口判据：
#             「**连续 2 轮扫出新东西但全部判定为放过 ⇒ 认为已挖干净**」。
#           ★ 本工具给**最后一遍**的「还剩什么」。
# 官方依据: 本仓文件系统
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# -----------------------------------------------------------------------------
from __future__ import annotations

import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parents[1]

NORM = re.compile(r"(不要|必须|应当|优先|推荐|避免|禁止|正确做法|惯例|判据)")
MODEL = re.compile(
    r"(草图|几何|约束|倒角|圆角|拉伸|旋转|切除|阵列|孔|螺纹|槽|基准|"
    r"中心线|轮廓|尺寸|标注|工程图|配合|装配)")

#: ★★ **我自己的产出**（★ 自引不算新知识）
MINE = ("specs/332-", "specs/315-eval-corpus/", "specs/335-", "specs/336-",
        "specs/334-", "specs/330-")
#: ★★ **工作产物目录**（★ 不是知识源）
WORK = ("recon/", "filler-chunks/", "c3-rows/", "verify50/", "api-pre/",
        "_raw/", "output/")
DIRS = ("docs", "references", "subskills", "apps", "examples", "agents")


def main() -> int:
    cited = set()
    for f in (ROOT / "specs" / "332-known-facts-triage").glob("*.md"):
        t = f.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"[\w\u4e00-\u9fff\-/.]+\.(md|py|yaml|ps1|txt|json)",
                             t):
            cited.add(m.group(0).split("/")[-1])
    rows = []
    for d in DIRS:
        for f in (ROOT / d).rglob("*"):
            if not f.is_file():
                continue
            rel = str(f.relative_to(ROOT)).replace("\\", "/")
            if any(rel.startswith(m) for m in MINE):
                continue
            if "src-tauri/resources/skill" in rel:
                continue
            if f.name in cited:
                continue
            if f.stat().st_size > 300000:
                continue
            try:
                t = f.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            n = sum(1 for ln in t.splitlines()
                    if 12 < len(ln.strip()) < 240
                    and NORM.search(ln) and MODEL.search(ln))
            if n >= 3:
                rows.append((n, rel))
    rows.sort(reverse=True)
    print("★ 第 19 轮：非我产出、未引用、规范句 ≥3 的 = **%d 份**" % len(rows))
    print()
    work = [r for r in rows if any(w in r[1] for w in WORK)]
    other = [r for r in rows if not any(w in r[1] for w in WORK)]
    print("★ 其中**工作产物目录**里的：**%d 份**（★ 不是知识源）" % len(work))
    for n, name in work[:8]:
        print("   %3d 条  %s" % (n, name))
    print()
    print("★ 其余（★ 要看的）：**%d 份**" % len(other))
    for n, name in other[:12]:
        print("   %3d 条  %s" % (n, name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
