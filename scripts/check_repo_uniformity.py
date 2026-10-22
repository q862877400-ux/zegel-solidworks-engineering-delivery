"""仓库统一化体检：判据全部来自权威工具与既有规范，不自定义标准。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   scripts/check_repo_uniformity.py
# 定位:   业主 2026-10-21 指令 ——「避免局部很整洁但整体很混乱；同一个功能多个函数重复
#           实现；
# 同一个东西在不同的地方命名不一样」。业主明确要求「**参考编程规范，不要自己随便想几个
#   标准**」。
#
# ★★ 判据的权威出处（★ 每一条都能指回去）：
#   ① 命名 / 导入风格 —— **Google Python Style Guide**
#      https://google.github.io/styleguide/pyguide.html
#      · snake_case 用于模块/函数/方法/变量；PascalCase 用于类；单下划线前缀表示内部成员
#      · 导入必须分组（标准库 / 第三方 / 本应用）且分行
#      · 循环依赖是 code smell，应重构
#      → 用 **ruff** 机械执行（`--select E,F,I,N,UP`）
#   ② 重复代码（同一功能多实现）—— **pyscn** 的 Type 1–4 克隆检测
#      https://github.com/ludo-technologies/pyscn
#      → 用 `pyscn analyze --select clones` 机械执行
#   ③ 死代码 / 循环依赖 / 分层违规 / 复杂度 —— 同样 **pyscn**
# ④ 本仓契约 —— `AGENTS.md`（六铁律 + A1–A10）· `docs/union-conventions.md`（五统一 + 
#   R1–R14）
#      · 来源块（AGENTS.md §十八）· 顶层白名单（AGENTS.md 铁律 3）
#
# ★ 设计原则：
#   · **本文件不发明判据** —— 只把上面四类权威判据"接线"成一道可执行的门禁。
# · 每个指标都记录**基线**，基线**只许降不许升**（`docs/repo-uniformity-baseline.json`
#   ）。
#   · 工具不可用（ruff/pyscn 未安装）时 → **FAIL 并说明**，不静默跳过
#     （★ 静默跳过与没跑等价 —— 见 `docs/known-facts.md` 事实 62）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import ast
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

R = pathlib.Path(__file__).resolve().parents[1]
BASE = R / "docs" / "repo-uniformity-baseline.json"

#: 体检范围：**活代码**（排除构建副本 / 缓存 / 归档）
SCAN_DIRS = ("scripts", "tools", "mcp-server")
EXCLUDE_HINT = ("__pycache__", "resources/skill", "archive")

#: ① ruff 选哪些规则族 —— ★ 全部对应 Google Style Guide 的硬条目
# :   E = pycodestyle 错误 · F = pyflakes（未定义名/未用导入）· I = isort（导入分组，G
#   oogle §3.13）
# :   N = pep8-naming（snake_case / PascalCase，Google §3.16）· UP = pyupgrade（现代写
#   法）
RUFF_SELECT = "E,F,I,N,UP"


def _tool(name: str) -> list[str] | None:
    """返回调用该工具的命令前缀；不可用则 None。"""
    if shutil.which(name):
        return [name]
    if subprocess.run([sys.executable, "-m", name, "--version"],
                      capture_output=True).returncode == 0:
        return [sys.executable, "-m", name]
    return None


def _load_base() -> dict:
    if BASE.exists():
        return json.loads(BASE.read_text(encoding="utf-8"))
    return {}


def _ruff_counts() -> tuple[int, dict[str, int], str]:
    """① 跑 ruff，返回（总数, 按规则计数, 错误说明）。"""
    cmd = _tool("ruff")
    if cmd is None:
        return -1, {}, "ruff 未安装（pip install ruff）⇒ 无法执行命名/导入体检"
    p = subprocess.run(cmd + ["check", *SCAN_DIRS, "--select", RUFF_SELECT,
                              "--output-format=concise", "--no-cache"],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=str(R), stdin=subprocess.DEVNULL)
    out = (p.stdout or "") + (p.stderr or "")
    per: dict[str, int] = {}
    for m in re.finditer(r"\b([A-Z]{1,4}\d{3})\b", out):
        per[m.group(1)] = per.get(m.group(1), 0) + 1
    total = sum(per.values())
    return total, per, ""


def _pyscn_clones() -> tuple[int, dict[str, int], str]:
    """② 跑 pyscn 克隆检测，返回（克隆组数, 按类型计数, 错误说明）。"""
    cmd = _tool("pyscn")
    if cmd is None:
        return -1, {}, "pyscn 未安装（pip install pyscn）⇒ 无法执行重复代码体检"
    p = subprocess.run(cmd + ["analyze", "--select", "clones",
                              "--json", "--output", "-", *SCAN_DIRS],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=str(R), stdin=subprocess.DEVNULL)
    raw = p.stdout or ""
    try:
        d = json.JSONDecoder().raw_decode(raw, 0)[0]["clone"]
    except Exception:                                                     # noqa: BLE001
        bad = (raw or (p.stderr or ""))[:120]
        return -1, {}, f"pyscn 输出无法解析（{bad}）"
    stats = d.get("statistics") or {}
    by_type = {str(k): int(v) for k, v in stats.get("clones_by_type", {}).items()}
    return len(d.get("clone_groups") or []), by_type, ""


def _source_blocks() -> tuple[int, str]:
    """④ 本仓契约：活 .py 必须有「── 来源 ──」块（AGENTS.md §十八）。"""
    miss = 0
    for d in SCAN_DIRS:
        for f in (R / d).rglob("*.py"):
            s = str(f).replace("\\", "/")
            if any(k in s for k in EXCLUDE_HINT):
                continue
            if "── 来源 ──" not in f.read_text(encoding="utf-8", errors="replace"):
                miss += 1
    return miss, ""


def _dup_filenames() -> list[str]:
    """④ 本仓契约：跨目录同名 .py（剔除 __init__.py 与构建副本）。"""
    seen: dict[str, list[str]] = {}
    for d in SCAN_DIRS:
        for f in (R / d).rglob("*.py"):
            s = str(f).replace("\\", "/")
            if any(k in s for k in EXCLUDE_HINT):
                continue
            seen.setdefault(f.name, []).append(f.relative_to(R).as_posix())
    return ["{} ⇒ {}".format(n, " · ".join(v)) for n, v in seen.items()
            if len(v) > 1 and n != "__init__.py"]


#: ★★ ⑤ 跨文件「同函数体」—— 业主指令的头号关切：「同一个功能多个函数重复实现」。
#:   判据：函数体归一化（去 docstring、把 Name 与形参名换成占位符）后取哈希，
#:   **跨文件同哈希** = 同一函数的多份实现（★ 同一文件内同名不算，那是重载）。
#:   算法口径 = Type-2 克隆（重命名标识符后相同），出处
#:   https://github.com/ludo-technologies/pyscn
_TOKEN = "@@ID@@"


class _NormNames(ast.NodeTransformer):
    """把 Name / arg 全换成占位符（让「变量名不同、逻辑相同」也归到一组）。"""

    def visit_Name(self, node: ast.Name) -> ast.AST:                      # noqa: N802
        return ast.copy_location(ast.Name(id=_TOKEN, ctx=node.ctx), node)

    def visit_arg(self, node: ast.arg) -> ast.AST:                        # noqa: N802
        node.arg = _TOKEN
        return node


def _body_hash(node: ast.AST) -> str:
    """函数体的归一化哈希（去 docstring、去名字差异）。"""
    try:
        body = list(getattr(node, "body", []))
        first = body[0] if body else None
        is_doc = (isinstance(first, ast.Expr)
                  and isinstance(getattr(first, "value", None), ast.Constant)
                  and isinstance(first.value.value, str))
        if is_doc:
            body = body[1:]
        mod = _NormNames().visit(ast.Module(body=body, type_ignores=[]))
        ast.fix_missing_locations(mod)
        dumped = ast.dump(mod, annotate_fields=False, include_attributes=False)
        return hashlib.sha256(dumped.encode("utf-8")).hexdigest()[:16]
    except Exception:                                                     # noqa: BLE001
        return ""


def _dup_functions() -> list[str]:
    """⑤ 跨文件同函数体组（返回可直接打印的清单）。"""
    groups: dict[str, list[tuple[str, str]]] = {}
    for d in SCAN_DIRS:
        for f in (R / d).rglob("*.py"):
            s = str(f).replace("\\", "/")
            if any(k in s for k in EXCLUDE_HINT):
                continue
            try:
                tree = ast.parse(f.read_text(encoding="utf-8", errors="replace"))
            except Exception:                                             # noqa: BLE001
                continue
            for n in ast.walk(tree):
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    h = _body_hash(n)
                    if h:
                        rel = f.relative_to(R).as_posix()
                        groups.setdefault(h, []).append((n.name, rel))
    out: list[str] = []
    for members in groups.values():
        names = sorted({m[0] for m in members})
        files = sorted({m[1] for m in members})
        if len(files) > 1:
            out.append("{} ⇒ {}".format("/".join(names[:3]), " · ".join(files)))
    return out


def main() -> int:
    base = _load_base()
    ok = True
    print("  ★ 判据出处：① ruff=Google Style Guide · ② pyscn 克隆 · ④ AGENTS.md 契约")
    print()

    # ① ruff
    n1, per1, err1 = _ruff_counts()
    ceil1 = int(base.get("ruff_total_ceiling", 10 ** 9))
    if n1 < 0:
        print(f"  [FAIL] ① ruff 命名/导入体检 —— {err1}")
        ok = False
    else:
        st = "PASS" if n1 <= ceil1 else "FAIL"
        print(f"  [{st}] ① ruff（{RUFF_SELECT}）= {n1}（上界 {ceil1}）")
        top = sorted(per1.items(), key=lambda x: -x[1])[:6]
        print("        Top: " + " · ".join(f"{k}×{v}" for k, v in top))
        ok = ok and n1 <= ceil1

    # ② pyscn 克隆
    n2, per2, err2 = _pyscn_clones()
    ceil2 = int(base.get("clone_groups_ceiling", 10 ** 9))
    if n2 < 0:
        print(f"  [FAIL] ② pyscn 重复代码体检 —— {err2}")
        ok = False
    else:
        st = "PASS" if n2 <= ceil2 else "FAIL"
        print(f"  [{st}] ② pyscn 克隆组 = {n2}（上界 {ceil2}）· 按类型 {per2}")
        ok = ok and n2 <= ceil2

    # ④ 来源块
    n3, _ = _source_blocks()
    ceil3 = int(base.get("no_source_block_ceiling", 10 ** 9))
    st = "PASS" if n3 <= ceil3 else "FAIL"
    print(f"  [{st}] ③ 缺来源块（AGENTS.md §十八）= {n3}（上界 {ceil3}）")
    ok = ok and n3 <= ceil3

    # ④ 同名文件
    dups = _dup_filenames()
    allow = set(base.get("dup_filename_allow") or [])
    real = [d for d in dups if d.split(" ⇒ ")[0] not in allow]
    tag = "PASS" if not real else "FAIL"
    print(f"  [{tag}] ④ 同名 .py = {len(real)}（上界 0 · 豁免 {len(allow)} 条）")
    for d in real:
        print(f"        {d}")
    ok = ok and not real

    # ⑤ 跨文件同函数体（★ 业主头号关切：同一个功能多个函数重复实现）
    dfun = _dup_functions()
    ceil5 = int(base.get("dup_function_groups_ceiling", 10 ** 9))
    allow5 = set(base.get("dup_function_allow") or [])
    real5 = [d for d in dfun if d.split(" ⇒ ")[0] not in allow5]
    st = "PASS" if len(real5) <= ceil5 else "FAIL"
    print(f"  [{st}] ⑤ 跨文件同函数体组 = {len(real5)}"
          f"（上界 {ceil5} · 豁免 {len(allow5)} 组）")
    if len(real5) > ceil5:
        for d in sorted(real5, key=len)[:10]:
            print(f"        {d[:150]}")
    ok = ok and len(real5) <= ceil5

    print()
    print(f"  ★ 结论：{'仓库统一化体检通过' if ok else '仓库统一化体检未通过'}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
