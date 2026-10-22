"""★ 门禁：函数内的相对导入必须带兜底（否则非包导入路径下必炸）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（门禁）
# 文件:   scripts/check_relative_imports.py
# 定位:   ★ **起因（真机）**：★ 2026-10-06 存活普查（规格 210 · B3）跑到
#   `solidworks_simulation_apply_link_connector` 时报
#   ★★ `ImportError: attempted relative import with no known parent package` ✗
#   ★ 追到 `scripts/sw_simulation_loads.py`：★ 它**函数体内**有 17 处
#     `from .sw_selection_spec import …` / `from .sw_simulation import …`，★ **没有兜底** ⇒
#     ★★ 作为 `scripts.X` 导入时成立，★ **一旦按顶层模块导入就炸** ✓
#   ★★ 而**仓库自己早就写好了正确写法**（同文件那处 `sw_connect`）：
#     ★ `try: from .X import Y` / ★ `except ImportError: from X import Y` ✓
#   ⇒ ★ 本门禁把这个写法**变成可执行的不变量** ✓
# 判据:   ★★ **顶层 / 函数内的 `from .X import Y` 必须紧跟在 `try:` 之后** ✓
# ★★ **棘轮（ratchet）**：★ 存量欠账记在 `BASELINE_COUNT`（★ 只许**变少**、★ 不许变多）—
# —
#     ★ 一次改 22 个文件风险太高（★ 事实 61：批量改动要先看 `deletions`）⇒
#     ★ **先钉住不许增长**，★ 再逐个还 ✓
#   ★★ **注意（我第一版栽在这）**：★ 判据必须用 `startswith("try:")` ——
#     ★ 因为**我自己的修法**写的是 `try:   # noqa: SIM105`（**带注释**）⇒
#     ★ 用 `== "try:"` 会把**已经修好的**也算成"没兜底" ✗（★ 真机现象：修完仍是 54 处）✓
# ★ 负例（★ 证明门禁真能抓到）：★ 用**修复前**的原文（`git show HEAD:<file>`）跑 ⇒ **必
# 须命中** ✓
# 官方依据: 无 —— ★ Python 语言语义（相对导入要求有父包），如实标注 ✓
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

#: ★★ 中文 Windows 上打印 `⇒`（U+21D2）会 `UnicodeEncodeError: 'gbk' codec can't encode
#: character` ✓
#: ★ 2026-10-07 实测：本门禁**逻辑上是绿的**（**35 = 基线 35**，加 `PYTHONIOENCODING=utf
#: -8` 跑即 exit 0）✗
#: ★★ 而**控制台是 GBK 时它整个崩掉** ⇒ ★ `release_check` 那条子进程拿到的是**退出码 ≠ 0
#: **
#:     ⇒ ★★ 报成 FAIL —— ★ 那是**事实 58**（`subprocess` + GBK）**在门禁自己身上**的又一例 ✓
#:   ⚠ `release_check.py` **不给子进程设** `PYTHONIOENCODING`/`PYTHONUTF8`（已核），
#: ★ 所以**必须在门禁自己这里兜住** —— 与 `check_refuted_patterns.py` 的既有修法逐字同型
#:  ✓
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
except Exception:  # noqa: BLE001
    pass

#: ★ 认"相对导入"（★ 缩进不限；★ `from .x import y` 形态）✓
PATTERN = re.compile(r"^(\s*)from \.([\w.]+) import (.+?)\s*$")

#: ★★ **存量欠账的棘轮基线**：★ 2026-10-06 **实测 35 处**（★ 我先前估的 37 是**估的** ——
#:   ★ **基线必须实测、不许估**：★ 修完那一处后全仓实扫就是 35 ✓）
BASELINE_COUNT = 35


def scan(root: Path) -> list:
    """★ 扫出所有**没有兜底**的相对导入（★ 前一行不是 `try:`）✓"""
    found = []
    scripts = root / "scripts"
    if not scripts.is_dir():
        return found
    for p in sorted(scripts.glob("*.py")):
        try:
            lines = p.read_text(encoding="utf-8").splitlines()
        except Exception:  # noqa: BLE001
            continue
        for i, ln in enumerate(lines):
            if not PATTERN.match(ln):
                continue
            prev = lines[i - 1].strip() if i else ""
            #: ★★ 用 `startswith` —— ★ 修法带 `# noqa` 注释（★ 见来源块）✓
            if prev.startswith("try:"):
                continue  # ★ 有兜底 ⇒ 合格 ✓
            found.append({"file": p.name, "line": i + 1, "text": ln.strip()[:80]})
    return found


def main() -> int:
    ap = argparse.ArgumentParser(description="★ 门禁：相对导入必须带兜底")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--root", default=str(ROOT))
    a = ap.parse_args()
    found = scan(Path(a.root))
    ok = len(found) <= BASELINE_COUNT
    if a.json:
        print(
            json.dumps(
                {
                    "ok": ok,
                    "count": len(found),
                    "baseline": BASELINE_COUNT,
                    "items": found,
                },
                ensure_ascii=False,
                indent=1,
            )
        )
        return 0 if ok else 1
    verdict = "不增长 ✓" if ok else "**增长了 ✗**"
    print(
        "★ 无兜底的相对导入：**%d** 处（★ 棘轮基线 **%d**）⇒ %s"
        % (len(found), BASELINE_COUNT, verdict)
    )
    if not ok:
        for it in found:
            print("   %s:%d  %s" % (it["file"], it["line"], it["text"]))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
