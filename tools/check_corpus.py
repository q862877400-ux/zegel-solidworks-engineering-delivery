"""★ 语料自检门禁（规格 315）：校验 L1/L2/L3 的全部约束。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tools/check_corpus.py
# 定位:   规格 `specs/315-eval-corpus` 的 FR-010 / FR-011（门禁 + 反向验证）
# 官方依据: 工具面真源 `register_capabilities.all_specs()`（★ 不是本仓自造口径）· 规格约
#           束见 `specs/315-eval-corpus/spec.md` §3/§4
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# -----------------------------------------------------------------------------
from __future__ import annotations

import collections
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server"), str(ROOT / "tools")]

import yaml                                                             # noqa: E402

#: ── 规格常量（★ 改这里就是改规格）──────────────────────────────
PRODUCT_CLASSES = ("板件", "轴件", "夹具", "平口钳", "连杆", "箱体")
RESULT_VOCAB = ("READY_FOR_REVIEW", "WAITING_INPUT", "REJECTED_OUT_OF_SCOPE",
                "REJECTED_UNSUPPORTED", "REJECTED_AMBIGUOUS")
CATEGORY_PLAN = {"solvable": 24, "missing_input": 12,
                 "capability_boundary": 12, "adversarial": 12}
SPLIT_PLAN = {"dev": 20, "blind": 40}
DIFFICULTY = ("easy", "medium", "hard")

#: ★ 基础设施组（不是「用户会提的需求」，L2 不要求覆盖）
INFRA = {"gui", "session", "macro", "automation", "repo", "preflight",
         "available", "selector", "list", "get", "read", "current", "clear",
         "activate", "refresh", "build", "api", "undo", "mesh", "set",
         #: ★★ 2026-10-12（规格 329）：`catalog_*` 那 4 个是**基础设施**
         #:   —— ★ 它们是**目录检索入口**（★ Q6 L110「规划入口与必要查询工具」），
         #:   ★ **不是产品任务**（★ 产品任务是"在板上打孔"那种）⇒
         #:   ★ 语料（L2 长尾）**不该**要求覆盖它们。
         #:   ⚠ 实测：不加这一条 ⇒ `L2 缺组 ['catalog']` ⇒ 语料门禁红 ✗
         #:     —— ★ 而"缺组"看起来像"语料漏了"，其实是**我把基础设施当成了产品任务**。
         "catalog"}


def tool_surface() -> set[str]:
    """★ 真实工具面 —— 门禁的锚点。"""
    import register_capabilities as rc
    return {s.name for s in rc.all_specs()}


def groups_of(names: set[str]) -> dict[str, list[str]]:
    g: dict[str, list[str]] = collections.defaultdict(list)
    for n in names:
        s = n
        for p in ("solidworks_", "cadstudio_", "mcp__solidworks__"):
            if s.startswith(p):
                s = s[len(p):]
                break
        g[s.split("_")[0]].append(n)
    return dict(g)


def load(p: pathlib.Path) -> list[dict]:
    return yaml.safe_load(p.read_text(encoding="utf-8")) or []


def check(root: pathlib.Path = ROOT) -> list[str]:
    """★ 返回问题列表（空 = 通过）。"""
    bad: list[str] = []
    surf = tool_surface()
    groups = groups_of(surf)
    task_groups = {g for g in groups if g not in INFRA}

    #: ══ L1 ══════════════════════════════════════════════════════
    l1p = root / "corpus" / "l1-mainline.yaml"
    if not l1p.is_file():
        bad.append("L1 文件不存在：%s" % l1p)
    else:
        l1 = load(l1p)
        if len(l1) != 60:
            bad.append("L1 条数 = %d（应为 60）" % len(l1))
        pc = collections.Counter(x.get("product_class") for x in l1)
        for c in PRODUCT_CLASSES:
            if pc.get(c, 0) < 5:
                bad.append("L1 产品类「%s」只有 %d 条（应 ≥5）" % (c, pc.get(c, 0)))
        for x in l1:
            i = x.get("id", "?")
            if x.get("product_class") not in PRODUCT_CLASSES:
                bad.append("L1 %s 的 product_class 非法：%r" % (i, x.get("product_class")))
            if x.get("difficulty") not in DIFFICULTY:
                bad.append("L1 %s 的 difficulty 非法：%r" % (i, x.get("difficulty")))
            if not x.get("readback"):
                bad.append("L1 %s 缺 readback" % i)
            chains = x.get("tools") or []
            if not chains:
                bad.append("L1 %s 的 tools 为空" % i)
            for c in chains:
                if not c:
                    bad.append("L1 %s 有一条空链" % i)
                for t in (c or []):
                    if t not in surf:
                        bad.append("L1 %s 引用了不存在的工具：%s" % (i, t))
            if "needs_owner_judgment" not in x:
                bad.append("L1 %s 缺 needs_owner_judgment" % i)

    #: ══ L2 ══════════════════════════════════════════════════════
    l2p = root / "corpus" / "l2-longtail.yaml"
    if not l2p.is_file():
        bad.append("L2 文件不存在：%s" % l2p)
    else:
        l2 = load(l2p)
        want = len(task_groups)
        if len(l2) != want:
            bad.append("L2 条数 = %d（应 = 工程任务组数 %d）" % (len(l2), want))
        covered = {x.get("target_group") for x in l2}
        miss = task_groups - covered
        if miss:
            bad.append("L2 未覆盖这些工程任务组：%s" % sorted(miss))
        for x in l2:
            i = x.get("id", "?")
            if x.get("target_group") not in task_groups:
                bad.append("L2 %s 的 target_group 非法：%r" % (i, x.get("target_group")))
            if not x.get("expected_groups"):
                bad.append("L2 %s 缺 expected_groups" % i)
            if not x.get("readback"):
                bad.append("L2 %s 缺 readback" % i)
            for c in (x.get("tools") or []):
                for t in (c or []):
                    if t not in surf:
                        bad.append("L2 %s 引用了不存在的工具：%s" % (i, t))

    #: ══ L3 ══════════════════════════════════════════════════════
    l3p = root / "corpus" / "l3-semantic.yaml"
    if not l3p.is_file():
        bad.append("L3 文件不存在：%s" % l3p)
    else:
        l3 = load(l3p)
        if len(l3) != 60:
            bad.append("L3 条数 = %d（应为 60）" % len(l3))
        cc = collections.Counter(x.get("category") for x in l3)
        for k, v in CATEGORY_PLAN.items():
            if cc.get(k, 0) != v:
                bad.append("L3 类别「%s」= %d（应为 %d）" % (k, cc.get(k, 0), v))
        sc = collections.Counter(x.get("split") for x in l3)
        for k, v in SPLIT_PLAN.items():
            if sc.get(k, 0) != v:
                bad.append("L3 分组「%s」= %d（应为 %d）" % (k, sc.get(k, 0), v))
        for x in l3:
            i = x.get("id", "?")
            lab = x.get("labels") or {}
            for k in ("function", "interface", "question", "result"):
                if not lab.get(k):
                    bad.append("L3 %s 的 labels 缺 %s" % (i, k))
            if lab.get("result") not in RESULT_VOCAB:
                bad.append("L3 %s 的 labels.result 非法：%r" % (i, lab.get("result")))
            if not x.get("requirement"):
                bad.append("L3 %s 缺 requirement" % i)
            if "needs_owner_judgment" not in x:
                bad.append("L3 %s 缺 needs_owner_judgment" % i)

    return bad


def selftest() -> bool:
    """★ 反向验证：改坏语料必须报错（★ FR-011）。

    ★★ 实现纪律：**每个负例必须「写 → 立刻 check」** ——
    不能先写完全部负例再统一 check（那样每次 check 看到的都是最后一次写的状态，
    于是「干净基线」那一例会看到被改坏的语料 ⇒ 假失败）。
    """
    import tempfile

    base1 = load(ROOT / "corpus" / "l1-mainline.yaml")
    base2 = load(ROOT / "corpus" / "l2-longtail.yaml")
    base3 = load(ROOT / "corpus" / "l3-semantic.yaml")
    ok = True

    with tempfile.TemporaryDirectory() as td:
        t = pathlib.Path(td)
        (t / "corpus").mkdir()

        def put(l1, l2, l3) -> None:
            for n, d in (("l1-mainline", l1), ("l2-longtail", l2),
                         ("l3-semantic", l3)):
                (t / "corpus" / ("%s.yaml" % n)).write_text(
                    yaml.safe_dump(d, allow_unicode=True), encoding="utf-8")

        def case(name: str, want_problems: bool, l1, l2, l3) -> None:
            """★ 写 → 立刻 check（★ 关键：不攒着）。"""
            nonlocal ok
            put(l1, l2, l3)
            got = len(check(t))
            passed = (got == 0) if not want_problems else (got > 0)
            if passed:
                print("  ✓ %s" % name)
            else:
                print("  ✗ selftest 失败：%s（期望 %s，实得 %d 处）"
                      % (name, "报错" if want_problems else "通过", got))
                ok = False

        def clone(seq: list[dict]) -> list[dict]:
            return [dict(x) for x in seq]

        #: ① 干净基线必须通过
        case("干净语料应通过", False, base1, base2, base3)

        #: ② 引用不存在的工具
        b = clone(base1)
        b[0]["tools"] = [["solidworks_不存在_工具"]]
        case("L1 引用不存在的工具", True, b, base2, base3)

        #: ③ L1 条数不对
        case("L1 条数不足", True, base1[:59], base2, base3)

        #: ④ L3 类别分布错（★ 找一个**不是** solvable 的条目来改，否则改了个寂寞）
        b3 = clone(base3)
        tgt = next(x for x in b3 if x["category"] != "solvable")
        tgt["category"] = "solvable"
        case("L3 类别分布错", True, base1, base2, b3)

        #: ⑤ L3 result 词表外
        b3 = clone(base3)
        b3[0]["labels"] = dict(b3[0]["labels"])
        b3[0]["labels"]["result"] = "乱写的状态"
        case("L3 result 不在受控词表", True, base1, base2, b3)

        #: ⑥ L2 漏组
        case("L2 漏一个组", True, base1, base2[:-1], base3)

        #: ⑦ L1 缺 readback
        b = clone(base1)
        b[0]["readback"] = []
        case("L1 缺 readback", True, b, base2, base3)

        #: ⑧ L2 引用不存在的工具
        b2 = clone(base2)
        b2[0]["tools"] = [["solidworks_也不存在"]]
        case("L2 引用不存在的工具", True, base1, b2, base3)

        #: ⑨ L3 缺一个 label
        b3 = clone(base3)
        b3[0]["labels"] = dict(b3[0]["labels"])
        b3[0]["labels"]["interface"] = ""
        case("L3 labels 缺一项", True, base1, base2, b3)

        #: ⑩ L1 产品类分布不足
        case("L1 产品类分布不足", True, base1[:9], base2, base3)

    print("selftest %s（%d 例）" % ("OK" if ok else "FAIL", 10))
    return ok


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        return 0 if selftest() else 1
    problems = check()
    if problems:
        print("[FAIL] 语料校验发现 %d 处问题：" % len(problems))
        for p in problems[:40]:
            print("  - %s" % p)
        if len(problems) > 40:
            print("  … 还有 %d 处" % (len(problems) - 40))
        return 1
    print("[PASS] 语料校验通过（L1 60 · L2 66 · L3 60）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
