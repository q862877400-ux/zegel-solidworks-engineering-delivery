"""★ 门禁：**分发口调用点**的标量 by-ref 占位（把 spec 230 的「可解析面」接进判据）。"""

# ── 来源 ─────────────────────────────────────────────────
# 仓库:   本项目自身（元门禁）
# 文件:   scripts/check_dispatch_byref_guard.py
# 定位:   收 spec 230 登记的「下一 WIP ①」—— 230 **只分类、不判罪**，
#         本门禁把 `resolved` 的那批分发口调用点喂进 `audit_byref_args` 的**同一套**判据。
# 官方依据: `_raw/**/iface_*.txt`（由 `tools/reflect-interop.ps1` 对出厂程序集做的**纯元
#           数据反射**转储，非实测）；by-ref 语义依据见 spec 228 §三。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────
#
# ## 为什么（2026-10-09 · spec 231）
# `audit_byref_args.own_call_sites()` 只认「成员名是**字符串字面量**」的调用点
# （`if not isinstance(m, ast.Constant): continue`）⇒ 分发口（成员名以**形参**转发）
# 的调用点**一律看不见**。spec 229 把这条边界量了出来（**91** 个不可见调用点），
# spec 230 把其中 37 个分发口里**可静态解析**的 **18** 个（**327** 个调用点）分出来。
# ⇒ ★★ **「可解析」只是前置条件，不是「已核」** —— 本门禁就是那个「接进判据」的动作。
#
# ## 判据（三条）
# 1. **裸传即红**：某 `resolved` 分发口的调用点，其 COM 实参里
#    「签名说 `&` 的**标量**位」传的**不是** by-ref 包装器 ⇒ `[FAIL]`。
# 2. **只增不减**（下界冻结）：可核分发口数 / 已核调用点数**只允许增** ——
#    减少 = 解析器或取点漏了（**不是**「问题解决了」）。
# 3. **零检查判失败**（事实 46）：下界非 0 而核了 0 个 ⇒ 不许 PASS。
#
# ## ⚠ 口径**全部 import，不重写**（228/229/230 同一纪律）
# * 取点/绑定/一级转发：`check_dispatch_entry_guard.{scan, resolution, _entry_sites,
#   _import_map, _bind, inner_wrapper_call, forward_slots}`
# * by-ref 判据：`audit_byref_args.{PURE_OUT, SCALAR_OUT, BYREF_OK, counted_positions,
#   byref_variables, byref_alias_names, load_full_signatures}`
#
# ## ⚠ 两条**只计数、不判罪**的桶（约定问题，门禁不得自动挑选约定 —— spec 227 教训）
# * 成员名在转储里**查不到** ⇒ 无法判；
# * 实参个数与任何候选签名都对不上 ⇒ 那是 **arity 审计**的活（230 实测 16 条全是
#   「实参 = 反射计数 − 1」，其内联签名表自己写着「不含末尾 by-ref `ErrorCode`」）。
#
# ## ⚠ 便携性
# 反射转储在**工作区**（gitignored）⇒ 一份都拿不到 ⇒ `[SKIP]` + `exit 0`
# （与 `check_arity_tables_vs_reflection.py` 同口径）。
# 合成树开关：`DSH_DISPATCH_BYREF_ROOT` · `DSH_DISPATCH_BYREF_DUMPS` ·
# `DSH_DISPATCH_BYREF_BASELINE_MIN`（仅测试用，`entries,sites` 两个值）。
from __future__ import annotations

import ast
import os
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

#: ★ 扫描根可被覆盖 ⇒ 负例能在**合成树**上端到端跑。
ROOT = Path(
    os.environ.get("DSH_DISPATCH_BYREF_ROOT") or Path(__file__).resolve().parents[1]
)

sys.path.insert(0, str(Path(__file__).resolve().parent))

import check_dispatch_entry_guard as deg  # noqa: E402
from audit_byref_args import (  # noqa: E402
    BYREF_OK,
    SCALAR_OUT,
    byref_alias_names,
    byref_variables,
    counted_positions,
    load_full_signatures,
)

#: ★ 下界（真树实测 · 2026-10-09 · spec 231）—— **只增不减**。
#: `entries` = 至少有一个调用点被**真正判过签名**的分发口数；`sites` = 被真正判过的调用
#: 点数。
#: ★ 实测 `311 + 16(arity) = 327` = spec 230 的 `resolved_sites` ⇒ **覆盖完整、无静默漏
#: 点**。
BASELINE_BYREF_ENTRIES = 21
BASELINE_BYREF_SITES = 311
#: 明细打印上限。
DETAIL_LIMIT = 25


def _baseline() -> tuple[int, int]:
    """⇒ `(entries, sites)`；`DSH_DISPATCH_BYREF_BASELINE_MIN` 可整体覆盖（仅测试用）。"""
    spec = os.environ.get("DSH_DISPATCH_BYREF_BASELINE_MIN", "")
    if spec.strip():
        parts = [int(x) for x in spec.split(",")]
        if len(parts) == 2:
            return tuple(parts)
    return (BASELINE_BYREF_ENTRIES, BASELINE_BYREF_SITES)


def find_dumps() -> list[Path]:
    """⇒ 反射转储路径清单（`DSH_DISPATCH_BYREF_DUMPS` 覆盖，多个用 `;` 分隔）。

    ★ **只回真实存在的文件** —— 一份都拿不到 ⇒ 调用方走 `[SKIP]`
      （缺数据源 ≠ 检查失败；与 `check_arity_tables_vs_reflection.py` 同口径）。
    """
    spec = os.environ.get("DSH_DISPATCH_BYREF_DUMPS", "")
    if spec.strip():
        cands = [Path(p) for p in spec.split(";") if p.strip()]
    else:
        cands = sorted(ROOT.glob("_raw/**/iface_*.txt"))
    return [p for p in cands if p.is_file()]


def _seg(src: str, node) -> str:
    """⇒ 节点的源码文本（单行化、去首尾空白）。"""
    return (ast.get_source_segment(src, node) or "").strip().replace("\n", " ")


def com_args(entry, call_file: Path, call, slots, srcs, table=None):
    """⇒ `("ok", 成员名, [COM 实参文本...])` / `("nonliteral", None, None)` / `("unbound", None, None)`。

    ★ 位置绑定（spec 230 教训）：调用方实参 → 分发口形参 → 内部包装调用的**实参槽**。
    **不用** `idx±k` 猜下标 —— 成员名形参的下标不是常数。
    ★★ 三态**显式**返回（spec 230 教训：解析不出必须判出来，不能静默降级成 0）：
    `nonliteral` = 该调用点传的成员名不是字面量（本来就不在解析面内）；
    `unbound` = 成员名是字面量，但某个**形参槽**在调用点没绑上 ⇒ 组不出 COM 实参。
    ★★ **spec 267 试过「`*args` 没传 ⇒ 单列一桶」并已回滚** —— ★ 理由见下面那段注释。
    ★★★ **一句话记号（★ `tests/test_starargs_fix_rollback.py` 逐字核它）**：
      ★★ **spec 267 **试过、已回滚**** ✓
    """
    path, fn, _idx, pname, _ln = entry
    env = deg._bind(fn, call)
    mnode = env.get(pname)
    if not (isinstance(mnode, ast.Constant) and isinstance(mnode.value, str)):
        return ("nonliteral", None, None)
    def_src = srcs[path]
    call_src = srcs[call_file]
    out: list[str] = []
    for name, fixed in slots:
        if fixed is not None:
            out.append(_seg(def_src, fixed))
        elif name is not None and name.startswith("*"):
            #: ★★★ spec 270 **试过「双条件」并已回滚** —— ★★ **它是空改动**（★ 门禁读数
            #: 一字未变）。
            #: ★★ **为什么**：★ 那 3 处的 `slots` 是 `[('*args', None)]` 而 **`com = 1`*
            #: *
            #: ⇒ ★ **`env.get("*args")` 不是空的**（★ 有 1 个元素）⇒ ★ `if not starred`
            #: **不成立**
            #:   ⇒ ★ 那个早返回**从未触发**。
            #:   ★★★ **新认识（留给下一轮）**：★ 判据条件不该是「`*args` **为空**」，
            #:   而是「★ `*args` **恰好 1 个**（= 对象本身）」⇒ ★ **下一轮要按这个改**。
            for a in env.get(name) or []:
                out.append(_seg(call_src, a))
        else:
            node = env.get(name)
            if node is None:
                return ("unbound", None, None)
            out.append(_seg(call_src, node))
    return ("ok", mnode.value, out)


def judge(member: str, com: list[str], table, byref_vars: set[str], alias_inline):
    """⇒ `"ok"` / `"unknown"` / `"arity"` / `"starred"` / `("bad", 位置, 类型, 实参文本, 签名)`。

    ⚠ `unknown` 与 `arity` 是**只计数、不判罪**的桶（见文件头）。
    ★★ `starred`（spec 268）= ★ **`*args` 该补而没补 ⇒ arity 不可判** ⇒ ★ 单列一桶，
      ★★ **但与 `arity` 不同：它算「已核」**（★ 免得像 267 那样丢调用点）。
    """
    variants = table.get(member)
    if not variants:
        return "unknown"
    cands = [v for v in variants if len(counted_positions(v[1])) == len(com)]
    if not cands:
        #: ★★★ spec 271 的**判别规则**（★ 在 268 的窄规则上加一层，★ 分开了 `starargs`
        #: 与 `real-gap`）。
        #:   ★★ **为什么还要再加一层**：★ 271 量出那两类在 AST 上**完全同形** ——
        #:   ★ `_checked(route_manager, "CreateFlattenRoute", *args)` 与
        #:   ★ `_checked(mesh, "GetNodeLocation", int(node_number))`
        #:   ★ **`slots` 都是 `[('*args', None)]`、`com` 都是 1** ⇒ ★ **AST 分不开**。
        #:   ★★★ **但形参表能分**：
        #: · `GetNodeLocation(Int32, Double&, Double&, Double&)` ⇒ 缺的 3 个**全是 `Doub
        #: le&`（by-ref 出参）**
        #:       ⇒ ★ 调用方**拿不到**它们 ⇒ ★ **真缺口**（★ 不该判 `starred`）
        #:     · `CreateFlattenRoute(Int32, Int32, Double, …)` ⇒ 缺的 10 个**全是普通入参**
        #:       ⇒ ★ `*args` **该补** ⇒ ★ `starred`
        #: ⇒ ★★ **规则：`len(com) == 1` 且 最少计入形参 ≥2 且「缺的形参**不全是 by-ref」
        #: ** ⇒ `starred`。**
        #: ★★★ **spec 267 的教训**（★ `tests/test_starargs_narrow_rule.py` 逐字要求这句
        #: 话**在窄规则旁边**）：
        #: ★ 267 **试过、已回滚** —— ★★ 它当时的做法是「**只要** `*args` 没传 ⇒ **单列一
        #: 桶**」
        #:     ⇒ ★★ 那会**把 `*args` 吞掉的 `real-gap` 也一起算进 `starred`** ⇒
        #:       ★ **真缺口被掩盖**（★ 那正是「`starred` **不算已核**」这条纪律要防的）。
        #: ★★★ **⇒ 所以窄规则必须带「最少计入形参 ≥2」这一半** —— ★★ **去掉它就把规则改
        #: 宽了**。
        #: ⚠ **判据**：`tests/test_starargs_narrow_rule.py::test_narrow_rule_is_in_the_s
        #: ource`
        #: 逐字核 `len(com) == 1 and min(len(counted_positions(v[1])) for v in variants)
        #:  >= 2`
        #:     与**本段里的「spec 267 的教训」** ⇒ ★ **改这段前先跑它** ✓
        if len(com) == 1 and min(len(counted_positions(v[1])) for v in variants) >= 2:
            missing_all_byref = all(
                all(
                    p.strip().endswith("&")
                    for _i, p in counted_positions(v[1])[len(com) :]
                )
                for v in variants
            )
            if not missing_all_byref:
                return "starred"
        return "arity"
    for sig_name, plist in cands:
        for pos, (_raw_i, ptype) in enumerate(counted_positions(plist)):
            if not ptype.endswith("&") or not SCALAR_OUT.match(ptype):
                continue
            actual = com[pos] if pos < len(com) else ""
            if BYREF_OK.match(actual):
                continue
            if any(rx.match(actual) for rx in alias_inline):
                continue
            if actual in byref_vars:
                continue
            return ("bad", pos, ptype.strip(), actual, sig_name)
    return "ok"


def main() -> int:
    dumps = find_dumps()
    if not dumps:
        print("⚠ 找不到反射转储（`_raw/**/iface_*.txt`）⇒ [SKIP]")
        print("分发口 by-ref · [SKIP] · exit 0")
        return 0
    table = load_full_signatures(dumps)

    entries, _visible, _nonlit, _buckets, _df, _cf, files = deg.scan(ROOT)
    classes, _resolved_sites = deg.resolution(entries, files)
    srcs = {p: files[p][0] for p in files}
    imap = deg._import_map(files)
    min_entries, min_sites = _baseline()

    byref_cache: dict[Path, set[str]] = {}
    alias_cache: dict[Path, list] = {}
    violations: list[dict] = []
    judged_sites = 0
    judged_entries = 0
    unknown = 0
    arity = 0
    starred = 0
    unbound = 0
    nonliteral = 0
    n_entries = 0

    for entry in entries:
        key = (entry[0], entry[1].lineno)
        cls = classes.get(key, ("", 0))[0]
        if cls == "no-callers":
            continue
        #: ★ 判**所有可一级转发的入口**，不只 `resolved` —— `partial` 入口的**字面量调用
        #: 点**
        #:   同样可判（230 实测那 3 个 `partial` 入口贡献了 42 个可解析调用点）。
        inner = deg.inner_wrapper_call(entry[1], entry[3])
        slots = deg.forward_slots(entry[1], inner) if inner is not None else None
        if slots is None:
            continue
        n_entries += 1
        hit = 0
        for cp, call in deg._entry_sites(entry, files, imap):
            status, member, com = com_args(entry, cp, call, slots, srcs)
            if status == "nonliteral":
                nonliteral += 1
                continue
            if status == "unbound":
                #: ★★ **显式计数**，不静默降级（spec 230 教训）。
                unbound += 1
                continue
            if cp not in byref_cache:
                byref_cache[cp] = byref_variables(cp)
                alias_cache[cp] = [
                    re.compile(r"^\s*%s\s*\(" % re.escape(a))
                    for a in sorted(byref_alias_names(cp))
                ]
            res = judge(member, com, table, byref_cache[cp], alias_cache[cp])
            if res == "unknown":
                unknown += 1
                continue
            if res == "arity":
                arity += 1
                continue
            if res == "starred":
                #: ★★★ spec 268：`*args` 该补而没补 ⇒ arity 不可判 ⇒ ★ 单列一桶，
                #: ★★ **但算「已核」** —— ★ 这正是 267 丢 189 个调用点的原因（★ 那时它不
                #: 算）。
                starred += 1
                judged_sites += 1
                hit += 1
                continue
            judged_sites += 1
            hit += 1
            if isinstance(res, tuple):
                _, pos, ptype, actual, sig_name = res
                rel = (
                    cp.relative_to(ROOT).as_posix()
                    if cp.is_relative_to(ROOT)
                    else cp.as_posix()
                )
                violations.append(
                    {
                        "file": rel,
                        "line": call.lineno,
                        "member": member,
                        "position": pos,
                        "type": ptype,
                        "actual": actual,
                        "entry": "%s::%s" % (entry[0].name, entry[1].name),
                        "signature": sig_name,
                    }
                )
        if hit:
            judged_entries += 1

    print("== 分发口调用点的标量 by-ref 占位（spec 231）==")
    print(
        "扫描 `%s/scripts/**/*.py` · 反射转储 %d 份 · 成员 %d 个"
        % (ROOT.as_posix(), len(dumps), len(table))
    )
    print(
        "可一级转发入口 %d · 其中已核 by-ref 的 %d 个 · 已核调用点 %d"
        % (n_entries, judged_entries, judged_sites)
    )
    print(
        "（非字面量调用点 %d · 成员名查不到 %d · arity 不符 %d · 形参未绑定 %d —— 只计数、不判罪）"
        % (nonliteral, unknown, arity, unbound)
    )

    if judged_entries < min_entries:
        violations.append(
            {
                "kind": "baseline-shrunk",
                "file": "-",
                "line": 0,
                "detail": "可核分发口 %d < 下界 %d（只增不减：先查解析器/取点）"
                % (judged_entries, min_entries),
            }
        )
    if judged_sites < min_sites:
        violations.append(
            {
                "kind": "baseline-shrunk",
                "file": "-",
                "line": 0,
                "detail": "已核调用点 %d < 下界 %d（只增不减：先查解析器/取点）"
                % (judged_sites, min_sites),
            }
        )
    #: ★ 假绿守卫（事实 46）：下界非 0 而核了 0 个 ⇒ 不许 PASS。
    if min_sites > 0 and judged_sites == 0:
        violations.append(
            {
                "kind": "zero-checked",
                "file": "-",
                "line": 0,
                "detail": "已核调用点 == 0（解析器/取点失效 ⇒ 不许 PASS）",
            }
        )

    if violations:
        print("[FAIL] 违规 %d 处：" % len(violations))
        for v in violations[:DETAIL_LIMIT]:
            if v.get("kind"):
                print("  [%s] %s —— %s" % (v["kind"], v.get("file", "-"), v["detail"]))
            else:
                print(
                    "  [bare-byref] %s:%d %s <- %s 第 %d 位应为 %s，实参是 `%s`"
                    % (
                        v["file"],
                        v["line"],
                        v["member"],
                        v["entry"],
                        v["position"],
                        v["type"],
                        v["actual"][:40],
                    )
                )
        if len(violations) > DETAIL_LIMIT:
            print("  …另有 %d 处" % (len(violations) - DETAIL_LIMIT))
    ok = not violations
    print("[PASS]" if ok else "[FAIL]")
    print(
        "分发口 by-ref · 可核分发口 %d · 已核调用点 %d · 查不到 %d · arity 不符 %d · "
        "形参未绑定 %d · 违规 %d · [%s] · exit %d"
        % (
            judged_entries,
            judged_sites,
            unknown,
            arity,
            unbound,
            len(violations),
            "PASS" if ok else "FAIL",
            0 if ok else 1,
        )
    )
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
