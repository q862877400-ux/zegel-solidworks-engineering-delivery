"""★ 门禁：`call_assembly_doc(doc, "<成员>", …)` 的**调用形状** —— arity + by-ref 占位。"""

# ── 来源 ─────────────────────────────────────────────────
# 仓库:   本项目自身（元门禁）
# 文件:   scripts/check_assembly_doc_call_shape.py
# 定位:   补 `call_assembly_doc` 在 **by-ref 审计**里的**盲区**（2026-10-09 · spec 228
#           ）。
# 官方依据: `_raw/**/iface_*.txt`（出厂反射转储，纯元数据，非实测）+ `scripts/sw_assembl
#           y_doc.py` 上方已有的 `#: arity-reflect: byref=included` 声明+ `scripts/sw_co
#           nnect.py::out_i4` 的**真机结论**（2026-10-01 · SW 2026 SP4.1）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────
#
# ## 靶子：`call_assembly_doc` **不在** `audit_byref_args.WRAPPERS` 里
# `audit_byref_args.WRAPPERS = {"_safe_member", "get_com_member", "safe_get_com_member",
# "call_com_member"}` ⇒ ★ 它只审「**成员名写在调用点**」的那些包装器。
# `call_assembly_doc(doc, "<成员>", …)` 把成员名**当第二实参**传进去，
# 而它内部转发的那句 `get_com_member(doc, member, *args)` 的成员名**是变量** ⇒
# **静态审计看不见** ⇒ ★★ 这一族调用点**从来没有任何 by-ref 判据在守**。
#
# ## 契约（本门禁据以判罪；**由人写死**，门禁只负责「按你写的查」）
# 复用 227 已立的那**一个**声明（一个事实一个家）：`ASSEMBLY_DOC_ARITY` 起始行正上方的
# `#: arity-reflect: byref=included`。两条规则：
#   ① **arity**：实参个数 == 表值。表值 = 反射**原始形参个数**（by-ref 计入）。
#   ② **by-ref 占位**：形参类型以 `&` 结尾的位置，实参必须是 **by-ref 包装器**
#      （`out_i4()` / `out_dispatch()` / 任何 `out_*()` / `VARIANT(VT_BYREF|…)` /
#       已知由 by-ref 构造来的变量 —— 口径从 `audit_byref_args` **import，不重写**）。
#
# ## ★★ 为什么是 `included`（而不是「纯出参不用传」）—— 证据链
# 1. `sw_connect.out_i4()` 的**真机实测**（2026-10-01，SW 2026 SP4.1）逐形态试过：
#    `VARIANT(VT_BYREF|VT_I4, 0)` ✓ / **`省略该参数` ✗ `DISP_E_PARAMNOTOPTIONAL`**
#    ⇒ ★ 迟到绑定（`getattr` → `IDispatch::Invoke`）下**每个形参都必须给一个 VARIANT**，
#      **不能省**。
# 2. `sw_connect.out_dispatch()` 的**真机实测**（2026-10-03 轮 499）：
#    `Object&` 出参传 `VARIANT(VT_BYREF|VT_DISPATCH, None)` ✓ 通过。
# 3. 仓库里**已经在这么写**：`sw_assembly_doc.edit_part_in_context` 的 `EditPart2`
#    （原始 3 参、第 3 参 `Int32&`）就是 `call_com_member(asm, "EditPart2", …,
#    out_i4())` —— **3 个实参**。
# ⇒ ★ 结论：`ASSEMBLY_DOC_ARITY` 的 `byref=included` **不是错**，
#   它正是**调用方要给的实参个数** ⇒ 交接单里「by-ref 出参不由调用方传入 ⇒ 会假拒」的
#   **前提是错的**（★ 记在 spec 228 §四，免得下一轮去"修"一个不是 bug 的东西）。
#
# ## ⚠ 跨工具口径不一致（**只报不判罪**）
# `audit_call_arity.PURE_OUT` 认定 `Object&` / `Variant&` / `Dispatch&` 是「纯出参、
# **不用传**」⇒ 与上面的真机证据**相反**。本门禁按 `included` 口径查，并把
# 「表值与 `PURE_OUT` 口径不符」的条目**列出来**（当前 5 条），**不判失败** ——
# 那属于 `audit_call_arity` / `audit_byref_args` 的口径问题，需真机另行裁决。
#
# ## 假绿守卫
# ★ 「检查过的调用点 == 0」**判失败**（事实 46：`检查过 0 个` 不许 PASS）。
#
# ## 便携性
# 拿不到反射转储 ⇒ **仍做 arity 检查**（表值就在源码里），只把 by-ref 一项标为
# **未核**并在读数里写明（缺数据源 ≠ 检查失败，与 227 同口径）。
# 合成树开关：`DSH_ASSEMBLY_CALL_ROOT`（扫描根）· `DSH_ARITY_DUMPS`（反射路径，与 227 共
# 用）。
from __future__ import annotations

import ast
import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

#: ★★ 扫描根可被覆盖 ⇒ 负例能在**合成树**上端到端跑（与 `DSH_ARITY_GATE_ROOT` 同风格）。
ROOT = Path(
    os.environ.get("DSH_ASSEMBLY_CALL_ROOT") or Path(__file__).resolve().parents[1]
)
#: 反射转储路径覆盖（与 `check_arity_tables_vs_reflection.py` **共用同一个开关**）。
DUMPS_ENV = "DSH_ARITY_DUMPS"
#: 被审的包装器名（成员名作为**第二实参**传入的那一族）。
WRAPPER = "call_assembly_doc"
#: 表名（登记表真源）。
TABLE_NAME = "ASSEMBLY_DOC_ARITY"
#: 227 已立的声明（本门禁**复用**它，不新造一个机制）。
DECL = re.compile(r"^#:\s*arity-reflect:\s*byref=(?P<mode>included|excluded)\s*$")
#: 明细打印上限。
DETAIL_LIMIT = 25


def _import_byref_helpers():
    """⇒ `(load_full_signatures, BYREF_OK, byref_variables, byref_alias_names)`。

    ★ **口径同源**：by-ref 包装器的判定**从 `audit_byref_args` import，不重写一份** ——
      两处各写一份必然漂移（`audit_byref_args` 自己的注释就是这么写的）。
    """
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import audit_byref_args as abr  # noqa: PLC0415

    return (
        abr.load_full_signatures,
        abr.BYREF_OK,
        abr.byref_variables,
        abr.byref_alias_names,
    )


def find_dumps() -> list[Path]:
    """⇒ 反射转储路径清单（`DSH_ARITY_DUMPS` 覆盖，多个用 `;` 分隔）。"""
    spec = os.environ.get(DUMPS_ENV, "")
    if spec.strip():
        return [Path(p) for p in spec.split(";") if p.strip()]
    return sorted(ROOT.glob("_raw/**/iface_*.txt"))


def _table_of(node: ast.stmt):
    """⇒ 该语句若是 `<TABLE_NAME>: dict[str, int] = {...}` 则给 `{成员名: 个数}`。"""
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
        if nm.id != TABLE_NAME:
            continue
        tbl = {}
        for k, v in zip(value.keys, value.values):
            if (
                isinstance(k, ast.Constant)
                and isinstance(k.value, str)
                and isinstance(v, ast.Constant)
                and isinstance(v.value, int)
            ):
                tbl[k.value] = v.value
        return tbl
    return None


try:
    from .gate_decl import arity_mode_above as _decl
except ImportError:
    from gate_decl import arity_mode_above as _decl


def iter_sources():
    """⇒ `ROOT/scripts/**/*.py` 里能解析的文件 `(path, src, tree, lines)`。"""
    for path in sorted(ROOT.glob("scripts/**/*.py")):
        try:
            src = path.read_text(encoding="utf-8")
            tree = ast.parse(src)
        except (SyntaxError, UnicodeDecodeError):
            continue
        yield path, src, tree, src.splitlines()


def find_table():
    """⇒ `(table, file, line, decl)`；找不到 ⇒ `(None, None, None, None)`。"""
    for path, _src, tree, lines in iter_sources():
        for node in tree.body:
            tbl = _table_of(node)
            if tbl is not None:
                return (
                    tbl,
                    path.relative_to(ROOT).as_posix(),
                    node.lineno,
                    _decl(lines, node.lineno),
                )
    return None, None, None, None


def _callee_name(fn: ast.expr) -> str | None:
    if isinstance(fn, ast.Name):
        return fn.id
    if isinstance(fn, ast.Attribute):
        return fn.attr
    return None


def find_call_sites():
    """⇒ `[(file, lineno, member, [实参源码文本…], 该文件)]`（只收**成员名为字面量**的点）。"""
    out = []
    for path, src, tree, _lines in iter_sources():
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call) or _callee_name(node.func) != WRAPPER:
                continue
            if len(node.args) < 2:
                continue
            m = node.args[1]
            if not (isinstance(m, ast.Constant) and isinstance(m.value, str)):
                continue
            texts = [
                (ast.get_source_segment(src, a) or "").strip().replace("\n", " ")
                for a in node.args[2:]
            ]
            out.append(
                (path.relative_to(ROOT).as_posix(), node.lineno, m.value, texts, path)
            )
    return sorted(out)


def main() -> int:
    tbl, tbl_file, tbl_line, decl = find_table()
    sites = find_call_sites()
    dumps = find_dumps()
    have_dumps = any(p.is_file() for p in dumps)

    print('== `%s(doc, "<成员>", …)` 调用形状 ==' % WRAPPER)
    if tbl is None:
        print(
            "[FAIL] 找不到登记表 `%s`（在 %s/scripts/**/*.py 里）" % (TABLE_NAME, ROOT)
        )
        print("已核 0 · 违规 1 · [FAIL] 0 · exit 1")
        return 1
    print(
        "表 %s:%d · %d 条 · 声明 `byref=%s`"
        % (tbl_file, tbl_line, len(tbl), decl or "**未表态**")
    )
    print(
        "扫描调用点 %d 个（成员名为字面量）· 反射转储 %s"
        % (len(sites), "已加载" if have_dumps else "**缺失（by-ref 一项将标为未核）**")
    )

    violations: list[dict] = []
    #: ★ 声明缺失 ⇒ 判失败（「一个事实一个家」：契约必须有家）。
    if decl is None:
        violations.append(
            {
                "kind": "undeclared",
                "file": tbl_file,
                "line": tbl_line,
                "detail": "表起始行正上方缺 `#: arity-reflect: byref=included|excluded`",
            }
        )
    if decl == "excluded":
        violations.append(
            {
                "kind": "contract",
                "file": tbl_file,
                "line": tbl_line,
                "detail": "本门禁按 `included` 口径查；声明写成 `excluded` 即契约冲突",
            }
        )

    byref_sites = 0
    unverified = 0
    if have_dumps:
        load_full_signatures, byref_ok, byref_variables, byref_alias_names = (
            _import_byref_helpers()
        )
        table = load_full_signatures([str(p) for p in dumps])
    else:
        table, byref_ok, byref_variables, byref_alias_names = {}, None, None, None

    for rel, lineno, member, args, path in sites:
        expected = tbl.get(member)
        if expected is None:
            violations.append(
                {
                    "kind": "unknown-member",
                    "file": rel,
                    "line": lineno,
                    "member": member,
                    "detail": "不在 `%s` 里 ⇒ 运行期必抛 KeyError" % TABLE_NAME,
                }
            )
            continue
        if expected != len(args):
            violations.append(
                {
                    "kind": "arity",
                    "file": rel,
                    "line": lineno,
                    "member": member,
                    "detail": "表值 %d，调用给了 %d 个" % (expected, len(args)),
                }
            )
            continue
        if not have_dumps:
            unverified += 1
            continue
        variants = table.get(member)
        if not variants:
            unverified += 1
            continue
        cands = [v for v in variants if len(v[1]) == len(args)]
        if not cands:
            unverified += 1
            continue
        has_byref = any("&" in p for _, plist in cands for p in plist)
        if has_byref:
            byref_sites += 1
        byref_vars = byref_variables(path)
        aliases = byref_alias_names(path)
        alias_inline = [re.compile(r"^\s*%s\s*\(" % re.escape(a)) for a in aliases]
        ok = False
        for _sig, plist in cands:
            bad_pos = None
            for i, ptype in enumerate(plist):
                if not ptype.strip().endswith("&"):
                    continue
                actual = args[i]
                if byref_ok.match(actual) or any(
                    rx.match(actual) for rx in alias_inline
                ):
                    continue
                if actual in byref_vars:
                    continue
                bad_pos = (i, ptype.strip(), actual)
                break
            if bad_pos is None:
                ok = True
                break
        if not ok and bad_pos is not None:
            violations.append(
                {
                    "kind": "bare-byref",
                    "file": rel,
                    "line": lineno,
                    "member": member,
                    "detail": "第 %d 位形参是 `%s`，实参却是 `%s`"
                    % (bad_pos[0], bad_pos[1], bad_pos[2][:40]),
                }
            )

    #: ★ 跨工具口径不一致（**只报不判罪**）。
    cross = []
    if have_dumps:
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            from audit_byref_args import counted_positions  # noqa: PLC0415

            for member, declared in sorted(tbl.items()):
                variants = table.get(member)
                if not variants:
                    continue
                raws = {len(plist) for _, plist in variants}
                cnts = {len(counted_positions(plist)) for _, plist in variants}
                if declared in raws and declared not in cnts:
                    cross.append((member, declared, sorted(cnts)))
        except ImportError:
            pass

    print(
        "含 by-ref 的调用点 %d 个 · 因无反射而未核 by-ref %d 个"
        % (byref_sites, unverified)
    )
    if cross:
        print(
            "⚠ 与 `audit_call_arity.PURE_OUT`（纯出参不传）口径不符 %d 条（**不判罪**，"
            "见本文件来源块与 spec 228 §四）：" % len(cross)
        )
        for member, declared, cnts in cross[:DETAIL_LIMIT]:
            print("   · %-34s 表值 %d / PURE_OUT 口径 %s" % (member, declared, cnts))
    if violations:
        print("[FAIL] 违规 %d 处：" % len(violations))
        for v in violations[:DETAIL_LIMIT]:
            head = "  [%s] %s:%s %s" % (
                v["kind"],
                v["file"],
                v.get("line", "-"),
                v.get("member", ""),
            )
            print("%s —— %s" % (head, v["detail"]))
        if len(violations) > DETAIL_LIMIT:
            print("  …另有 %d 处" % (len(violations) - DETAIL_LIMIT))
    if not sites:
        print("[FAIL] 检查过的调用点 == 0（事实 46：`检查过 0 个` 不许 PASS）")
        violations.append(
            {"kind": "zero-checked", "file": "-", "line": 0, "detail": "0 个调用点"}
        )
    ok = not violations
    print("[PASS]" if ok else "[FAIL]")
    print(
        "已核 %d · 含 by-ref %d · 未核 by-ref %d · 违规 %d · [%s] · exit %d"
        % (
            len(sites),
            byref_sites,
            unverified,
            len(violations),
            "PASS" if ok else "FAIL",
            0 if ok else 1,
        )
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
