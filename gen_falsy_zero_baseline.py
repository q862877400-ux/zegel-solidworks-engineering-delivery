"""生成 `docs/falsy-zero-baseline.txt`：把**存量**的 falsy-zero 站点记进基线。

⚠ 用**门禁自己的函数**生成（不重写一份判据）—— 否则基线与门禁会各说各话。
⚠ 键是 `<相对路径>:<成员名>`：同一模块里同名的会**塌成一条**（保守 —— 要全修完才会消失）。
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(r"C:\swprojects\sw-skill-fork")

spec = importlib.util.spec_from_file_location(
    "check_env_pitfalls", REPO / "scripts" / "check_env_pitfalls.py")
mod = importlib.util.module_from_spec(spec)
sys.modules["check_env_pitfalls"] = mod
spec.loader.exec_module(mod)

files = []
for d in mod.FALSY_ZERO_DIRS:      # ⚠ 必须与**门禁的检查③**同一份目录表（**它不扫 tests/**）
    p = REPO / d
    if p.is_dir():
        files.extend(sorted(p.rglob("*.py")))
files = [f for f in files if ".git" not in f.parts]

rows: dict[str, list] = {}
for f in files:
    for ln, member, default in mod.find_falsy_zero_default(f):
        rel = f.relative_to(REPO).as_posix()
        rows.setdefault("%s:%s" % (rel, member), []).append((ln, default))

out = REPO / "docs" / "falsy-zero-baseline.txt"
lines = [
    "# `x or <默认值>` 吞掉合法 `0` 的**存量**站点（基线）。",
    "# 由 `scripts/check_env_pitfalls.py` 的检查③读取：**只拦新增**；修好后从本文件删行。",
    "# 格式：`<相对路径>:<成员名>`（`#` 之后是注释）",
    "#",
    "# 为什么要基线而不是一次全绿：全仓同族 40+ 处，一次全改风险高（事实 61），",
    "# 且每一处都要判断「那个成员的 0 是否有意义」。",
    "# ⚠ 成因与判别：见 `check_env_pitfalls.py` 里 `FALSY_ZERO_PAT` 上面的注释。",
    "",
]
for key in sorted(rows):
    lns = ", ".join("L%d(or %s)" % (l, d) for l, d in rows[key])
    lines.append("%s   # %s" % (key, lns))
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("  已写 %s：**%d** 条基线（覆盖 %d 个模块）"
      % (out.name, len(rows), len({k.split(':')[0] for k in rows})))
