r"""@brief 元门禁：`scripts/check_*.py` 每个都必须**被 `release_check.py` 调用**，或**显式豁免带理由**。

## 为什么（2026-10-01 轮 70 实测暴露的真缺口）
`AGENTS.md` 的整个方法论是「**把验证责任转移到静态比对**」——靠的是一整套门禁。
⚠ 但轮 70 实测发现：**`scripts/check_workspace_shadowing.py` 早就存在，却从没被
`release_check.py` 调用**，而它当时**正红着**（工作区根的 `mcp.py` 遮蔽 `mcp` 包）：

```
[FAIL] 工作区根有 **1 个**会遮蔽依赖包的文件/目录：mcp ← D:\AI\SW\mcp.py
```

**★ 一个存在但没人跑的门禁，与没有门禁等价。**
本项目反复记录过「**守卫存在但没人用**」（事实 40），这次是同一教训的**另一个面**：
**门禁存在，但没接线** —— 而「接线」这一步**只靠人记**，就会漏。

## 判据（不靠文件名文本匹配）
「被调用」= 源码里出现 `str(ROOT / "scripts" / "<名字>")` 这个**精确形态** ——
那正是 `subprocess` 调用点用的写法。
⚠ 只匹配文件名（`check_xxx.py`）**不行**：`release_check.py` 的**注释与 docstring 里**
也反复提到文件名（如「接入 `scripts/check_provenance.py`」）⇒ 会**全部误判为已接线**。

## 双向
* **未接线、又不在豁免清单里** ⇒ 报（防漏）；
* **豁免清单里、却已接线** ⇒ 也报（**名单腐坏**：豁免了不该豁免的）。

## 豁免怎么登记
`docs/gate-wiring-exemptions.json`：每条给 `gate` / `reason` / `evidence` 三者**非空**
（与 `union-not-doing.json` 的 R14 同型 —— 一个没有理由的豁免等于没写）。

# ── 来源 ──
# 仓库:   本项目自身（元门禁，非第三方移植）
# 文件:   scripts/check_gate_wiring.py
# 定位:   给「门禁接线」这一步加机器判据 —— 轮 70 漏接一个门禁的直接后果。
# 官方依据: 不适用（本项目内部工具，不调 SolidWorks API）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "scripts" / "release_check.py"
EXEMPTIONS = ROOT / "docs" / "gate-wiring-exemptions.json"
#: ⚑ **分类登记表**（2026-10-01 轮 72 加）—— 每个门禁声明自己是**硬门禁**还是**诊断**。
#: ⚠ 轮 71 只解决了「门禁**接线了没**」，**接线的方式**没管：一个**本该拦**的门禁若写成
#:   诊断，就会**静默放行**（「守卫存在但没人用」的第三种面孔）。
CLASSIFICATION = ROOT / "docs" / "gate-classification.json"


def wired_pattern(name: str) -> re.Pattern:
    """⇒ 「被 `subprocess` 调用」的精确形态（见本文件 docstring 的口径）。"""
    return re.compile(
        r"str\(\s*ROOT\s*/\s*\"scripts\"\s*/\s*\"%s\"\s*\)" % re.escape(name)
    )


def _has_raise(node) -> bool:
    return any(isinstance(n, ast.Raise) for n in ast.walk(node))


def _is_fail_check(stmt, var: str) -> bool:
    """`if <var>.get("status") == "fail": … raise …` 形态。"""
    if not isinstance(stmt, ast.If):
        return False
    dumped = ast.dump(stmt.test)
    if f"'{var}'" not in dumped and f'"{var}"' not in dumped:
        return False
    if "status" not in dumped or "fail" not in dumped:
        return False
    return _has_raise(stmt)


#: ⚑ **允许出现 `skipped` 的条件**（2026-10-01 轮 73 加）。
#: 「同一个问题的第四层」：门禁**接好了**（轮 71）、**方式对了**（轮 72），
#: 但**它跳过的时候**呢？调用点只看 `"fail"` ⇒ **`skipped` 会被静默放行**。
#: ⇒ 实测：`release_check.py` 里原有 **5 处**「**无法启动**（`TimeoutExpired`/`OSError`
#: ）」
#:   返回 `skipped` —— **那是故障，不是便携性**！已全部改成 `fail`。
#: ⇒ 剩下的 `skipped` 只允许由下面这些**条件**触发（都得是可核的"数据源缺失/脚本约定"）
#: ：
ALLOWED_SKIP_CONDITIONS = (
    "_git_available",  # 非 git 工作树 ⇒ 无法判定新增行（便携性）
    "returncode == 2",  # 脚本自己的 SKIP 约定（`check_provenance.py` 读不到锚点）
    #: ⚑ 被检查脚本**自己在输出里报 `[SKIP]`** ⇒ 由它驱动状态分类（`_run_interface_owner
    #: ship_probe`
    #:   的 `skipped = any(... startswith("[SKIP]") ...)`）。
    #: ⚠ 本 token 要在**该 `If` 之前若干行**里找（因为条件是**变量**，来源在它上面）——
    #:   第一版判据只看 `If.test`，把这条**合法的** `skipped` 误报成了违规。
    "[SKIP]",
)


def skip_branches(src: str) -> list:
    """⇒ `[(行号, 用于判断的源码片段)]` —— 返回 `skipped` 的分支及其**条件的来源**。

    ⚠ 判据：`"skipped"` 字符串常量必须出现在**某条 `if`/`elif` 的体内**，且
      **该分支往上的 12 行**（`test` 与变量来源都在这段里）要含 `ALLOWED_SKIP_CONDITIONS` 之一。
    ⚠⚠ **第一版只看 `if` 的 `test`** ⇒ 把 `_run_interface_ownership_probe` 里那条
      **合法的** `if skipped:`（`skipped` 是变量，来源在上一行）**误报成违规** ——
      又是「判据的范围没有贴合它要抓的那件事」（已知事实 51 同族）。
    ★ 这是**第四层**：不能只看「有没有 `skipped`」，要看「**凭什么**可以 `skipped`」。
    """
    tree = ast.parse(src)
    lines = src.splitlines()
    out = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.If):
            continue
        body_src = "\n".join(ast.unparse(s) for s in node.body)
        # 只看**本分支**（不含 `orelse`）：`elif` 在 AST 里是 `orelse` 里的 `If`
        if '"skipped"' not in body_src and "'skipped'" not in body_src:
            continue
        lo = max(0, node.lineno - 13)  # 往上 12 行（含 test 与变量来源）
        context = "\n".join(lines[lo : node.end_lineno or node.lineno])
        out.append(
            (
                node.lineno,
                " | ".join(l_.strip() for l_ in lines[lo : node.lineno] if l_.strip())[
                    -150:
                ]
                or ast.unparse(node.test),
                context,
            )
        )
    return sorted(out)


def aggregated_vars(src: str) -> set:
    """⇒ 返回体里被汇总的门禁变量名集合（`_gate_results` 那个 dict 的 value）。

    ⚑ **第五层**（2026-10-01 轮 74）：`release_check` 的返回体此前只汇总了 **4 个**门禁
      （`provenance` / `diff_markers` / `member_names` / `interface_ownership`），
      其余 **9 个的状态根本没被汇总** —— 更关键的是**没有任何地方统计 `skipped`**
      ⇒ **「跳过了」是隐形的**。★ 一个**静默跳过**的门禁与**没跑**等价。
    ⇒ 本函数把「**每个门禁的结果都要进返回体**」也变成机器判据。
    """
    tree = ast.parse(src)
    names: set = set()
    for node in ast.walk(tree):
        if not (
            isinstance(node, ast.Assign)
            and any(getattr(t, "id", None) == "_gate_results" for t in node.targets)
            and isinstance(node.value, ast.Dict)
        ):
            continue
        for v in node.value.values:
            if isinstance(v, ast.Name):
                names.add(v.id)
    return names


def actual_runners(src: str) -> dict:
    """⇒ `{runner 函数名: "hard"|"diagnostic"}` —— **精确到兄弟语句**的实况。

    ⚠⚠ **不用行窗口**（2026-10-01 轮 72 实测踩过）：18 行的窗口把
      `_run_interface_ownership_probe`（**诊断**）也算成了 raise —— 因为它后面紧跟的是
      **另一件事**（`bundled_drift`）的 `raise`。
    ⇒ 判据只看**该赋值节点的下一个兄弟语句**：「本次调用的**直接后果**」。
    ★ 与已知事实 51 同族：**判据的范围必须贴合它要抓的那件事**。
    """
    tree = ast.parse(src)
    out: dict = {}
    for fn in ast.walk(tree):
        if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        body = fn.body
        for idx, stmt in enumerate(body):
            if not (isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call)):
                continue
            callee = getattr(stmt.value.func, "id", None) or getattr(
                stmt.value.func, "attr", None
            )
            if not (callee and callee.startswith("_run_")):
                continue
            var = getattr(stmt.targets[0], "id", "?") if stmt.targets else "?"
            nxt = body[idx + 1] if idx + 1 < len(body) else None
            out[callee] = (
                "hard"
                if (nxt is not None and _is_fail_check(nxt, var))
                else "diagnostic"
            )
    return out


def main() -> int:
    if not RELEASE.is_file():
        print("[FAIL] 找不到 %s" % RELEASE.relative_to(ROOT))
        return 1
    src = RELEASE.read_text(encoding="utf-8")
    # ⚠ **不排除自己** —— 元门禁**自己也必须被接线**，否则就是同一个笑话
    #   （「一个存在但没人跑的元门禁」比普通门禁更讽刺）。
    gates = sorted(p.name for p in (ROOT / "scripts").glob("check_*.py"))

    exempt: dict = {}
    if EXEMPTIONS.is_file():
        try:
            data = json.loads(EXEMPTIONS.read_text(encoding="utf-8"))
            for item in data.get("exemptions") or []:
                if isinstance(item, dict) and item.get("gate"):
                    exempt[item["gate"]] = item
        except json.JSONDecodeError as exc:
            print("[FAIL] %s 不是合法 JSON：%s" % (EXEMPTIONS.name, exc))
            return 1

    print(
        "门禁接线元门禁 · `scripts/check_*.py` %d 个 · 豁免登记 %d 条"
        % (len(gates), len(exempt))
    )
    print()

    unwired_unexempted, wired_but_exempted, bad_exemptions = [], [], []
    for g in gates:
        is_wired = bool(wired_pattern(g).search(src))
        if is_wired and g in exempt:
            wired_but_exempted.append(g)
        elif not is_wired and g not in exempt:
            unwired_unexempted.append(g)
        print("    %-40s %s" % (g, "已接线" if is_wired else "**未接线**"))

    # 豁免条目必须有理由与依据（同 R14 的口径）
    for g, item in exempt.items():
        if not str(item.get("reason") or "").strip():
            bad_exemptions.append("%s 缺 `reason`" % g)
        ev = item.get("evidence")
        if not isinstance(ev, list) or not [e for e in ev if str(e).strip()]:
            bad_exemptions.append("%s 缺**非空** `evidence`" % g)
        if g not in gates:
            bad_exemptions.append(
                "%s 不在 `scripts/check_*.py` 里（名单腐坏：文件已改名/删除？）" % g
            )

    # ⚑ **接线方式**（2026-10-01 轮 72 加）：登记的分类必须与**实况**一致。
    #   实况用 AST 从 `release_check.py` 现算（精确到兄弟语句），**不读登记表的自述**。
    runners = actual_runners(src)
    declared: dict = {}
    if CLASSIFICATION.is_file():
        try:
            cdata = json.loads(CLASSIFICATION.read_text(encoding="utf-8"))
            for item in cdata.get("classification") or []:
                if isinstance(item, dict) and item.get("runner"):
                    declared[item["runner"]] = item
        except json.JSONDecodeError as exc:
            print("[FAIL] %s 不是合法 JSON：%s" % (CLASSIFICATION.name, exc))
            return 1

    print()
    print("接线方式（登记 vs 实况）：")
    kind_bad = []
    for runner in sorted(set(runners) | set(declared)):
        act = runners.get(runner)
        want = (declared.get(runner) or {}).get("kind")
        gate = (declared.get(runner) or {}).get("gate", "—")
        if act is None:
            kind_bad.append(
                "%s（登记为 `%s`）在 `release_check.py` 里**找不到这个 `_run_*` 调用点**"
                "（名单腐坏：函数改名/删除了？）" % (runner, want)
            )
            continue
        if want is None:
            kind_bad.append(
                "%s 在 `release_check.py` 里被调用，却**没登记分类**"
                "（登记表必须覆盖每一个调用点）" % runner
            )
            continue
        if want not in (
            "hard",
            "diagnostic",
            "release_static",
            "release_hardware",
            "retired",
        ):
            #: ★★ 2026-10-12（规格 324 · Q16）扩到**四类**：
            #:   `release_static` / `release_hardware` / `diagnostic` / `retired`
            #:   ★ `hard` 与 `diagnostic` 是**旧名**，仍收（★ 向后兼容）。
            kind_bad.append(
                "%s 的 `kind=%r` 不在枚举 "
                "`release_static`/`release_hardware`/`diagnostic`/"
                "`retired`（旧名 `hard`/`diagnostic` 也收）内" % (runner, want)
            )
            continue
        #: ★★ 新旧名等价映射（★ 规格 324 的 `LEGACY_KIND_MAP`）
        _alias = {"hard": "release_static", "diagnostic": "diagnostic"}
        if _alias.get(want, want) != _alias.get(act, act):
            kind_bad.append(
                "%s（%s）登记为 **%s**，而实测是 **%s** —— "
                "「本该拦的写成诊断」会**静默放行**（后者更危险）"
                % (runner, gate, want, act)
            )
            continue
        for field in ("gate", "reason"):
            if not str((declared.get(runner) or {}).get(field) or "").strip():
                kind_bad.append("%s 的分类条目缺非空 `%s`" % (runner, field))
        print("    %-40s %-12s ✓" % (runner, act))

    # ⚑ **第四层：`skipped` 的合法性**（2026-10-01 轮 73 加）—— 见 `ALLOWED_SKIP_CONDITI
    # ONS`。
    print()
    print("返回 `skipped` 的分支（必须由登记的「数据源缺失/脚本约定」触发）：")
    skips = skip_branches(src)
    skip_bad = []
    for ln, cond, context in skips:
        ok = any(tok in context for tok in ALLOWED_SKIP_CONDITIONS)
        print(
            "    L%-4d %-64s %s"
            % (ln, cond[:62], "✓" if ok else "**✗ 依据不在白名单**")
        )
        if not ok:
            skip_bad.append(
                "L%d 的 `skipped` 依据是 `%s` —— 不在白名单 %s 内；"
                "⚠ **「无法启动/超时/异常」必须是 `fail`**，"
                "因为调用点只看 `fail` ⇒ `skipped` 会被**静默放行**"
                % (ln, cond[:60], list(ALLOWED_SKIP_CONDITIONS))
            )
    if not skips:
        print("    （本文件里没有 `skipped` 分支）")

    # ⚑ **第五层：汇总完整性**（2026-10-01 轮 74 加）—— 每个 `_run_*` 的结果都要进返回体
    # 。
    #   ⚠ 实测：返回体此前只汇总 4 个 ⇒ 其余 9 个**是隐形的**（含"跳过了"这件事）。
    print()
    print("汇总完整性（每个 `_run_*` 的结果都要进 `_gate_results`）：")
    agg = aggregated_vars(src)
    run_vars = set()
    tree2 = ast.parse(src)
    for fn in ast.walk(tree2):
        if isinstance(fn, ast.FunctionDef) and fn.name == "run_release_check":
            for stmt in fn.body:
                if isinstance(stmt, ast.Assign) and isinstance(stmt.value, ast.Call):
                    callee = getattr(stmt.value.func, "id", None)
                    if callee and callee.startswith("_run_"):
                        run_vars.add(getattr(stmt.targets[0], "id", "?"))
    agg_bad = []
    for v in sorted(run_vars):
        ok = v in agg
        print("    %-24s %s" % (v, "已汇总 ✓" if ok else "**✗ 没进返回体**"))
        if not ok:
            agg_bad.append(
                "`%s` 的结果**没有进返回体** ⇒ 「它跳过了/它没跑」在外面**看不见**"
                "（★ 静默跳过与没跑等价）⇒ 加进 `_gate_results`" % v
            )
    for v in sorted(agg - run_vars):
        agg_bad.append(
            "`_gate_results` 里的 `%s` 没有对应的 `_run_*` 赋值"
            "（名单腐坏：变量名改了？）" % v
        )

    # ⚑ **第六层：覆盖范围（`scripts/` + `tools/`）与「应执行 vs 实际」**
    #   （2026-10-12 · 规格 324 · Q16 逐字：「元门禁**同时覆盖** `scripts/`、`tools/`，
    #     并核对「应执行集合」与「实际执行结果」，**不只检查文件被发现**」）
    print()
    print("覆盖范围与「应执行 vs 实际」（Q16 · 规格 324）：")
    cover_bad: list = []
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        from engineering import gate_inventory as gi  # noqa: PLC0415

        inv = gi.build_inventory()
        print(
            "    `scripts/` 检查文件 = %d · `tools/` 检查文件 = %d"
            % (inv["scripts"]["n"], inv["tools"]["n"])
        )
        #: ★★ **`tools/` 必须被扫到**（★ Q16 逐字要求覆盖）
        if inv["tools"]["n"] <= 0:
            cover_bad.append("★ `tools/` 里**一个检查文件都没扫到** ⇒ 覆盖不成立")
        else:
            print("    `tools/` 抽样：%s" % ", ".join(inv["tools"]["checks"][:3]))
        #: ★★ **应执行 vs 实际**（★ Q16 逐字「不只检查文件被发现」）
        should = set(inv["should_run_in_release"])
        declared = set(inv["declared"])
        miss = sorted(should - declared)
        print(
            "    应执行 %d · 已登记 %d · **应执行却没登记 %d**"
            % (len(should), len(declared), len(miss))
        )
        #: ★ 判据：**已登记的门禁必须有文件**（★ 名单腐坏）
        ghost = inv["declared_but_no_file"]
        if ghost:
            cover_bad.append(
                "★ 这些门禁**登记了却没有文件**（名单腐坏）：%s" % ghost[:4]
            )
        #: ★★ **四类计数如实报**（★ 0 条也要报 —— ★ 不假装四类都满）
        counts = inv["counts"]
        print("    四类计数：%s" % counts)
        #: ★ 真机门禁必须**单独编排且明确 NOT_RUN**
        print("    真机门禁（单独编排 · NOT_RUN）= %d" % inv["not_run_n"])
        #: ★ `retired` 必须带替代关系
        cls = gi.load_classification().get("classification") or []
        ret = [e for e in cls if e.get("kind") == gi.RETIRED]
        for e in ret:
            if not e.get("replaced_by"):
                cover_bad.append("★ %s 是 retired 却没有 `replaced_by`" % e.get("gate"))
    except Exception as exc:  # noqa: BLE001
        cover_bad.append("★ 清点失败：%s: %s" % (type(exc).__name__, str(exc)[:120]))

    print()
    failed = bool(kind_bad) or bool(skip_bad) or bool(agg_bad) or bool(cover_bad)
    if cover_bad:
        print("[FAIL] 覆盖范围/应执行-vs-实际 有问题：")
        for b in cover_bad:
            print("    · %s" % b)
    if agg_bad:
        print("[FAIL] 门禁结果汇总不完整：")
        for b in agg_bad:
            print("    · %s" % b)
    if skip_bad:
        print("[FAIL] `skipped` 的触发条件有问题：")
        for b in skip_bad:
            print("    · %s" % b)
    if kind_bad:
        print("[FAIL] 接线方式有问题：")
        for b in kind_bad:
            print("    · %s" % b)
    if unwired_unexempted:
        failed = True
        print(
            "[FAIL] %d 个门禁**没有被 `release_check.py` 调用**，也没登记豁免："
            % len(unwired_unexempted)
        )
        for g in unwired_unexempted:
            print("    · `scripts/%s`" % g)
        print()
        print(
            "  ⚠ 一个存在但没人跑的门禁，与没有门禁等价（轮 70 实测：`check_workspace_shadowing.py`"
        )
        print("     早就存在却从没被调用，而它当时**正红着**）。")
        print("  ⇒ 两条修法（**由人定**）：")
        print("     ① **接进** `release_check.py`（照现有 `_run_*_gate` 的写法）；")
        print(
            "     ② 或登记进 `docs/gate-wiring-exemptions.json` 并**写明理由与依据**。"
        )
    if wired_but_exempted:
        failed = True
        print(
            "[FAIL] %d 个门禁**已接线却仍挂在豁免名单里**（名单腐坏）："
            % len(wired_but_exempted)
        )
        for g in wired_but_exempted:
            print("    · `scripts/%s`" % g)
        print("  ⇒ 从 `docs/gate-wiring-exemptions.json` 删掉那些条目。")
    if bad_exemptions:
        failed = True
        print("[FAIL] 豁免名单本身有问题：")
        for b in bad_exemptions:
            print("    · %s" % b)
    if failed:
        print()
        print("门禁接线元门禁未通过")
        return 1
    print("[PASS] %d 个门禁全部已接线（或已豁免且理由/依据齐备）" % len(gates))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
