"""★ 门禁：`*_ARITY` 表声明的实参个数，必须与**出厂反射转储**按**显式声明的 by-ref 约定**对得上。"""

# ── 来源 ─────────────────────────────────────────────────
# 仓库:   本项目自身（元门禁）
# 文件:   scripts/check_arity_tables_vs_reflection.py
# 定位:   补「`not-enum arity` 声明**不验值**」的缺口（224 / 225 / 226 三次登记）。
# 官方依据: `_raw/reflect_sldworks/iface_sldworks.txt` 等 `_raw/**/iface_*.txt`（由 `too
#           ls/reflect-interop.ps1` 对出厂程序集做的**纯元数据反射**转储，非实测）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────
#
# ## 为什么（2026-10-09 · spec 227）
# 224/225/226 让每张「自称有出处」的整数表**表态**，`not-enum arity` 是其中一档 ——
# 但那一档**只验子类、不验值**：`ASSEMBLY_DOC_ARITY` 里的 `'AddMate5': 15` 这 15
# 此前**没有任何机器判据**在守（表是运行期 `_checked()` 的校核依据 ⇒ 表错 = 校核错）。
#
# ## 判据（三条）
# 1. **每张 `*_ARITY` 表必须表态**：其起始行**正上方**（跳过空行）那行必须是
#    `#: arity-reflect: byref=included|excluded` —— 未表态 ⇒ `[FAIL]`。
#    ★ 关联方式是**确定性的**（向上跳过空行取第一行非空行），**不用行窗口启发式**
#      —— 15 行窗口对「插入注释」敏感（spec 225 当场踩到），本门禁有意避开。
# 2. **按声明的约定比对值**：`included` ⇒ 与反射原文的**原始实参个数**比；
#    `excluded` ⇒ 与**剔除 by-ref（含 `&`）形参后**的个数比。
# 3. **合成树端到端负例**由 `tests/test_arity_tables_vs_reflection.py` 提供
#    （`DSH_ARITY_GATE_ROOT` + `DSH_ARITY_DUMPS` 指向临时树 ⇒ 改错一个值必须 exit 1）。
#
# ## ★★ 为什么要「显式声明约定」而不是二选一自动挑
# 2026-10-09 第 4 轮量测：552 条声明按「原样计数」不符 **37**、按「剔除 by-ref」不符 **1
# 5**，
# 看着像 37 条真错 —— ★ 真相是**两种约定并存**（`ASSEMBLY_DOC_ARITY` 含 by-ref、其余 13 
# 张不含），
# **各自约定下 552/552 全对**。⇒ ★ 若门禁自己挑约定（取残差最小），
# **错的值会被自动「解释」掉**；约定必须由人**写死**，门禁只负责「按你写的查」。
#
# ## 为什么比的是**原始转储**、不是测试里的手抄常量
# `tests/test_sw_*_contract.py` 的 `REFLECTED_ARITY = {...}` 是**手抄**的 ⇒
# 手抄 ↔ 手抄 = **双盲**（抄错同一处则永不报警）。本门禁直接读 `_raw/**/iface_*.txt`。
#
# ⚠ **便携性**：反射转储在**工作区** ⇒ 一份都拿不到就 `[SKIP]` 并 `exit 0`
#   （与 `check_enum_values_vs_reflection.py` 同口径）。可用 `DSH_ARITY_DUMPS` 覆盖路径。
from __future__ import annotations

import ast
import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

#: ★★ 扫描根可被覆盖 ⇒ 负例能在**合成树**上端到端跑（与 `DSH_ENUM_GATE_ROOT` 同风格）。
ROOT = Path(os.environ.get("DSH_ARITY_GATE_ROOT") or Path(__file__).resolve().parents[1])

#: 表级 by-ref 约定声明（**紧邻表起始行上方**，中间只许有空行）。
DECL = re.compile(r"^#:\s*arity-reflect:\s*byref=(?P<mode>included|excluded)\s*$")
#: 反射转储里的一行成员：`    Int32 GetBreakLineCount(Int32&)`。
MEMBER_ROW = re.compile(r"^\s+[\w\.\[\]<>, ]+?\s+(?P<name>\w+)\((?P<args>.*)\)\s*$")
#: 声明里允许的约定（封闭词表；认不出即未表态）。
MODES = ("included", "excluded")
#: 明细打印上限（超出给「另有 N 条」）。
DETAIL_LIMIT = 25


def find_dumps() -> list[Path]:
    """⇒ 反射转储路径清单（`DSH_ARITY_DUMPS` 覆盖，多个用 `;` 分隔）。"""
    spec = os.environ.get("DSH_ARITY_DUMPS", "")
    if spec.strip():
        return [Path(p) for p in spec.split(";") if p.strip()]
    return sorted(ROOT.glob("_raw/**/iface_*.txt"))


def split_top_level(args: str) -> list[str]:
    """按**顶层**逗号切分形参串（`<>` 与 `[]` 里的逗号不切）。"""
    args = args.strip()
    if not args:
        return []
    parts: list[str] = []
    depth, cur = 0, ""
    for ch in args:
        if ch in "<[":
            depth += 1
        elif ch in ">]":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    parts.append(cur)
    return [p.strip() for p in parts]


def parse_dumps(paths) -> tuple[dict[str, set[tuple[int, int]]], int]:
    """⇒ `(成员名 → {(原始个数, by-ref 个数)}, 转储行数)`。

    ⚠ **按成员名全局取、不按 `## <接口>` 头取**：`iface_sldworks.txt` 的 `## AssemblyDoc`
      段**是空的**（成员不在该头下）⇒ 按接口过滤会**全取不到**（2026-10-09 第 4 轮踩过）。
    """
    per_member: dict[str, set[tuple[int, int]]] = {}
    lines = 0
    for p in paths:
        p = Path(p)
        if not p.is_file():
            continue
        for raw in p.read_text(encoding="utf-8", errors="replace").splitlines():
            lines += 1
            m = MEMBER_ROW.match(raw)
            if not m:
                continue
            params = split_top_level(m.group("args"))
            byref = sum(1 for x in params if "&" in x)
            per_member.setdefault(m.group("name"), set()).add((len(params), byref))
    return per_member, lines


def _table_of(node: ast.stmt) -> dict[str, int] | None:
    """⇒ 该语句若是 `X_ARITY: dict[str, int] = {...}` 则给 `{成员名: 个数}`，否则 `None`。"""
    if isinstance(node, ast.AnnAssign):
        names = [node.target] if isinstance(node.target, ast.Name) else []
        value = node.value
    elif isinstance(node, ast.Assign):
        names = [t for t in node.targets if isinstance(t, ast.Name)]
        value = node.value
    else:
        return None
    if not isinstance(value, ast.Dict):
        return None
    for nm in names:
        if not nm.id.endswith("_ARITY"):
            continue
        tbl: dict[str, int] = {}
        for k, v in zip(value.keys, value.values):
            if (isinstance(k, ast.Constant) and isinstance(k.value, str)
                    and isinstance(v, ast.Constant) and isinstance(v.value, int)):
                tbl[k.value] = v.value
        return {"name": nm.id, "entries": tbl}
    return None
try:
    from .gate_decl import arity_mode_above as _decl
except ImportError:
    from gate_decl import arity_mode_above as _decl


def find_arity_tables() -> list[dict]:
    """⇒ 每张 `*_ARITY` 表：`{file, line, name, entries, decl}`（`decl` 为 `None` 即未表态）。"""
    out: list[dict] = []
    for path in sorted(ROOT.glob("scripts/**/*.py")):
        try:
            src = path.read_text(encoding="utf-8")
            tree = ast.parse(src)
        except (SyntaxError, UnicodeDecodeError):
            continue
        lines = src.splitlines()
        for node in tree.body:
            found = _table_of(node)
            if found is None:
                continue
            out.append({
                "file": path.relative_to(ROOT).as_posix(),
                "line": node.lineno,
                "name": found["name"],
                "entries": found["entries"],
                "decl": _decl(lines, node.lineno),
            })
    return out


def checked_member_index(tree: ast.Module) -> int | None:
    """⇒ 该模块 `_checked()` 里 `member` 形参的下标（`(target, member, *args)`→1）。"""
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "_checked":
            pos = [x.arg for x in node.args.posonlyargs] + [x.arg for x in node.args.args]
            return pos.index("member") if "member" in pos else None
    return None


def entries_used_at_call_sites() -> set[tuple[str, str]]:
    """⇒ 在调用站点被用到的 `(表名, 成员名)` —— **下界**（只认 `_checked` / `call_assembly_doc`）。

    ★ 用途是**透明度**：552 条声明里有多少条**从没被任何调用站点用到**
      （⇒ 没有运行期证据，不该与被调用过的条目混在一个读数里）。
    """
    used: set[tuple[str, str]] = set()
    for path in sorted(ROOT.glob("scripts/**/*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError):
            continue
        tables = {}
        for node in tree.body:
            found = _table_of(node)
            if found is not None:
                tables[found["name"]] = found["entries"]
        if not tables:
            continue
        consumers = {"_checked": checked_member_index(tree), "call_assembly_doc": 1}
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Name):
                continue
            midx = consumers.get(node.func.id)
            if midx is None or len(node.args) <= midx:
                continue
            arg = node.args[midx]
            if not (isinstance(arg, ast.Constant) and isinstance(arg.value, str)):
                continue
            for tname, tbl in tables.items():
                if arg.value in tbl:
                    used.add((tname, arg.value))
                    break
    return used


def main() -> int:
    dumps = find_dumps()
    if not any(p.is_file() for p in dumps):
        print("[SKIP] 找不到出厂反射转储 `_raw/**/iface_*.txt` ⇒ 跳过"
              "（便携性；可用 DSH_ARITY_DUMPS 覆盖路径）")
        return 0

    per_member, dump_lines = parse_dumps(dumps)
    tables = find_arity_tables()

    undeclared, mismatches, ambiguous = [], [], []
    mode_count = {m: 0 for m in MODES}
    entries = 0
    for t in tables:
        if t["decl"] is None:
            undeclared.append(t)
        else:
            mode_count[t["decl"]] += 1
        for member, declared in t["entries"].items():
            entries += 1
            seen = per_member.get(member)
            if not seen:
                mismatches.append({"table": t["name"], "file": t["file"], "member": member,
                                   "declared": declared, "mode": t["decl"], "reflection": []})
                continue
            cands = {raw if t["decl"] == "included" else raw - byref for raw, byref in seen}
            if declared in cands:
                if len(seen) > 1:
                    ambiguous.append({"table": t["name"], "member": member, "declared": declared})
                continue
            mismatches.append({"table": t["name"], "file": t["file"], "member": member,
                               "declared": declared, "mode": t["decl"],
                               "reflection": sorted(seen)})

    used = entries_used_at_call_sites()
    used_n = sum(1 for t in tables for m in t["entries"] if (t["name"], m) in used)

    print("== `*_ARITY` 表 × 出厂反射转储 ==")
    print("转储 %d 行 · 成员名 %d 个 · 表 %d 张 · 声明 %d 条"
          % (dump_lines, len(per_member), len(tables), entries))
    print("by-ref 约定：%s（未表态 %d 张）"
          % (" / ".join("%s %d 张" % (m, mode_count[m]) for m in MODES), len(undeclared)))
    print("调用站点覆盖（下界 · 只认 `_checked` / `call_assembly_doc`）："
          "%d / %d 条（%.1f %%）" % (used_n, entries, 100.0 * used_n / max(entries, 1)))
    print("同名多接口（按声明值可对上）：%d 条" % len(ambiguous))
    for t in tables:
        print("  · %-22s %-30s %s %3d 条"
              % (t["name"], t["file"], t["decl"] or "**未表态**", len(t["entries"])))
    if undeclared:
        print("[FAIL] 未表态 %d 张（每张须在其起始行正上方补一行 "
              "`#: arity-reflect: byref=included|excluded`）：" % len(undeclared))
        for t in undeclared[:DETAIL_LIMIT]:
            print("  %s:%d %s" % (t["file"], t["line"], t["name"]))
    if mismatches:
        print("[FAIL] 值不符 %d 条（按**各自声明的** by-ref 约定）：" % len(mismatches))
        for m in mismatches[:DETAIL_LIMIT]:
            print("  %s %s.%s 声明 %s / 约定 %s / 反射 (原始, by-ref) %s"
                  % (m["file"], m["table"], m["member"], m["declared"], m["mode"],
                     m["reflection"]))
        if len(mismatches) > DETAIL_LIMIT:
            print("  …另有 %d 条" % (len(mismatches) - DETAIL_LIMIT))
    ok = not undeclared and not mismatches
    print("[PASS]" if ok else "[FAIL]")
    print("已表态 %d · 未表态 %d · 值不符 %d · [%s] %d · exit %d"
          % (len(tables) - len(undeclared), len(undeclared), len(mismatches),
             "PASS" if ok else "FAIL", len(tables), 0 if ok else 1))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
