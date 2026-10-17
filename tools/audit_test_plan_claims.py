r"""@brief 核 `D:\AI\SW-transfer\test-plan-final.md` 里点名的**路径 / 模块 / 函数**是否真实存在。

## 判据（写明覆盖面）
```
① 路径类：`scripts/x.py` / `subskills/x/` / `tools/x.py` / `examples/x` / `docs/x` ⇒ 在代码仓库里查
② 点调用：`mod.func`（mod 形如 sw_* / 非 sw_ 前缀的 sketch_relations 等）
   ⇒ 先在 scripts/ 找 `<mod>.py`，再在该模块里找 `def <func>`
③ 裸函数名（无点）：全仓 `def <name>` 搜一遍，报**在哪几个模块里**
④ 计数类断言（如「51 个函数」「13 个模块」）⇒ 数出来比对
```
⚠ **不覆盖**：散文论断（"未验过""需许可证"）· 另一会话在做的事 · 判据阈值是否合理。
⚠ 只读，不连 SolidWorks。

# ── 来源 ──
# 仓库:   本项目自身（审计脚本，非第三方移植）
# 文件:   tools/audit_test_plan_claims.py
# 定位:   外部文档的**事实核对**（同 capability-gap-audit.md 那种做法）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = Path(Path(__file__).resolve().parents[1] / "-transfer" / "test-plan-final.md")
OUT = Path(Path(__file__).resolve().parents[1] / "output" / "test-plan-claim-audit.json")
sys.stdout.reconfigure(encoding="utf-8")

#: 路径形态 —— ⚠ **不匹配 `x.py.func`**（那是点调用，不是路径）
PATH_RE = re.compile(r"`((?:scripts|subskills|tools|examples|docs|tests|mcp-server)/[\w./-]+?)`")
#: 点调用形态：`mod.func`
#: ⚠⚠ **2026-10-01 第一版在这里出了假阳性**：它把 `cnc_strategy.py`（**文件名**）
#:    也当成 `模块.函数`（`func` = `py`）⇒ 一次报 9 个"未命中"，**全是假的**。
#:    ⇒ 排除「点后面是文件扩展名」的形态（`py` / `json` / `md` / `txt` / `csv` / `bmp`）。
#:    ★ 又一次"判据太松"（事实 51 / 185 / 190 / 192 / 193 / 196 / 198 / 200 同族）。
CALL_RE = re.compile(r"`([a-z][a-z0-9_]*)\.([a-z][a-z0-9_]*)`")
_FILE_EXT = {"py", "json", "md", "txt", "csv", "bmp", "png", "jpg", "avi", "step", "stl", "dxf"}
#: `scripts/mod.py.func` 这种**带路径的点调用**（计划里真这么写）
CALL_WITH_PATH = re.compile(r"`(?:scripts|subskills|tools)/([a-z][a-z0-9_]*)\.py\.([a-z][a-z0-9_]*)`")


def _all_defs() -> dict:
    """{模块名: {函数名, …}} + `__files__`（**全仓任意扩展名**的相对路径）。

    ⚠⚠ **2026-10-01 第一版只收集 3 个目录的 `.py`** ⇒ 把
      `examples/generate_fea_convergence_example.py`（真存在）与
      `scripts/jlcfa_index.json`（真存在）都报成"不存在" —— **假阳性**。
      ⇒ ★ 覆盖面要**贴合"路径"这个概念的边界**（仓里任何文件），
        而不是贴合"我以为计划会引用什么"（事实 51 同型）。
    """
    out: dict = {"__files__": set()}
    skip = {".git", "__pycache__", "node_modules", ".pytest_cache"}
    for p in sorted(ROOT.rglob("*")):
        if not p.is_file() or any(s in p.parts for s in skip):
            continue
        rel = p.relative_to(ROOT).as_posix()
        out["__files__"].add(rel)
        if p.suffix == ".py":
            try:
                tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
            except SyntaxError:
                continue
            names = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
            out.setdefault(p.stem, set()).update(names)
    return out


def main() -> int:
    text = PLAN.read_text(encoding="utf-8")
    defs = _all_defs()
    files = defs.pop("__files__", set())

    missing_paths, ok_paths = [], []
    for m in sorted(set(PATH_RE.findall(text))):
        #: ⚠ 排除 `scripts/mod.py.func` 这种**点调用**（它不是路径）
        if re.search(r"\.py\.[a-z]", m):
            continue
        hit = any(f == m or f.startswith(m.rstrip("/") + "/") for f in files)
        (ok_paths if hit else missing_paths).append(m)

    missing_calls, ok_calls = [], []
    #: ① 纯 `mod.func`（排除"点后面是扩展名"的假形态）
    calls = {(a, b) for a, b in CALL_RE.findall(text) if b not in _FILE_EXT}
    #: ② `scripts/mod.py.func` 带路径写法 ⇒ 归一到 (mod, func)
    calls |= set(CALL_WITH_PATH.findall(text))
    for mod, fn in sorted(calls):
        if mod in defs and fn in defs[mod]:
            ok_calls.append("%s.%s" % (mod, fn))
        else:
            missing_calls.append({"call": "%s.%s" % (mod, fn), "module_known": mod in defs})

    print("  ── ① 路径 ──")
    print("     存在 %d · **不存在 %d**" % (len(ok_paths), len(missing_paths)))
    for x in missing_paths:
        print("       ✗ %s" % x)
    print("  ── ② 点调用 `mod.func` ──")
    print("     命中 %d · **未命中 %d**" % (len(ok_calls), len(missing_calls)))
    for x in missing_calls:
        print("       ✗ %-46s （模块%s）" % (x["call"], "在" if x["module_known"] else "**也不在**"))

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"paths_ok": ok_paths, "paths_missing": missing_paths,
                               "calls_ok": ok_calls, "calls_missing": missing_calls},
                              ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print()
    print("  证据: %s" % OUT)
    if not (ok_paths or ok_calls):
        print("  ✗ 一条都没解析到 ⇒ 判据没生效")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
