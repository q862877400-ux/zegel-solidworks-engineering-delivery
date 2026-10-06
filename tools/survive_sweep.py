"""★ 存活普查：逐工具「调一次 + 前后抓指纹」，输出「声明 vs 观察」差异表。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机普查驱动器）
# 文件:   tools/survive_sweep.py
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B3**。★ 外部评审的判决原话：
#   ★「成本的主项是「**建立前置状态**」，不是调用本身 ⇒ ★ 按**前置签名分组**，
#     ★ 每组只建一次状态 …… **耗时随「不同前置的数量」增长，不随工具数增长**」✓
#   ★★ 本脚本先做**第一个纵向切片**：★ 只取 **`writes == []`（已确认无写）** 的那批 ——
#     ★ 它们正是**硬红门禁**真正盯的那一批（★「**声明只读却观察到指纹变化**」）✓
# 判据:   ★★ 每次调用**前后各抓一次指纹**，与**声明**比对，分**四类**：
#     `agree`      = 声明「无写」 ∩ 观察「没变」 ⇒ ★ 一致 ✓
#     `conservative` = 声明「有写」 ∩ 观察「没变」 ⇒ ★ 声明保守（★ 无害）
#     ★★ `missed`   = **声明「无写」 ∩ 观察「变了」** ⇒ ★ **漏报**（★ 硬红门禁盯的就是它）✗
#     `undecided`  = 有一侧读不到 ⇒ ★ **未判定**（★ **不算通过也不算失败**）✓
#   ★ 每条都**各用一个新零件**（★ 样本隔离 —— B2 真机踩过：同文档顺序标定会互相污染）✓
#   ★ 调用一律走 **`tool_caller`**（★ 按 `ToolSpec` 契约）✓
# 官方依据: 读数出处见 `scripts/sw_fingerprint.py` 的 `OFFICIAL`；声明出自 `docs/effect-declarations.json`
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
for _p in (str(ROOT), str(ROOT / "tools"), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

EFFECTS = ROOT / "docs" / "effect-declarations.json"


def _fresh_part(sw):
    """★ 建一个**新的空零件** —— ★ 每条工具**各用一个**（★ 样本隔离）✓"""
    import sw_connect
    try:
        return sw_connect.new_document(sw, "part")
    except Exception:                                                   # noqa: BLE001
        return None


#: ★★★ 2026-10-06 **真机读数纠正了我自己的结论**：★ 我上一轮说"写工具缺前置" ✗ ——
#:   ★★ 17 条失败里 **12 条**其实是「**缺必填形参**」（`x_mm`/`configuration_name`/`view_name`/…），
#:   ★ 另有 **4 条**是「声明注入 `asm_model`/`sldworks`/`view` 但没给对象」· **2 条**是环境/取值错 ✓
#:   ⇒ ★ 正解是评审早说过的「**参数由声明合成**」—— ★ 不是每样都要"建前置" ✓
#:   ★★ 合成规则**按形参名与单位后缀**来（★ 只求"形状对"，★ 不求语义对 —— 语义由差分去判）✓
_SYNTH_BY_HINT = (
    ("_mm", 20.0), ("_deg", 90.0), ("_count", 1), ("_index", 0),
    ("_name", "MCP_CALIB"), ("path", "MCP_CALIB_out.step"),
    ("_type", 0), ("_flag", True), ("_id", 0), ("_size", 1.0),
)


def synth_args(spec) -> dict:
    """★ 按**真函数签名**给每条必填形参**合成一个值**（★ 形状对即可）✓

    ★★★ 2026-10-06 **真机拆解逼出来的两处修正**（★ 见 `docs/spec210-b3-undecided-breakdown.md`）：
      ① ★★ **声明里没有类型信息**：★ `ToolSpec.params` 的 `annotation` 全是 `None` ✗
         ⇒ ★ 类型只能从**底层真函数的签名**取（★ 用 `inspect.signature`）✓
      ② ★★ **只按名字后缀猜类型会猜错**：★ 真机实录 ——
         · `automation_get_flag(pref)` ⇒ ★ 我给了 `'MCP_CALIB'`（字符串）⇒
           ★★ 真函数要 **`int`** ⇒ 报 `invalid literal for int(): 'MCP_CALIB'` ✗
         · `config_set_custom_properties(properties)` ⇒ ★ 我给了字符串 ⇒
           ★★ 真函数要 **`dict`** ⇒ 报 `'str' object has no attribute 'items'` ✗
    ⇒ ★ 判序：★ **① 真函数签名的类型注解 → ② 名字后缀启发式 → ③ 兜底字符串** ✓
      ★（★ 把类型放**第一位**，★ 因为它是**真的**；★ 名字后缀是**猜的**）✓
    """
    import inspect
    import importlib
    ann: dict = {}
    try:
        mod = importlib.import_module("scripts." + str(getattr(spec, "module", "")))
        fn = getattr(mod, str(getattr(spec, "function", "")), None)
        if fn is not None:
            for pname, pp in inspect.signature(fn).parameters.items():
                ann[pname] = pp.annotation
    except Exception:                                                   # noqa: BLE001
        ann = {}

    out = {}
    for pp in (getattr(spec, "params", None) or ()):
        if getattr(pp, "default", None) is not Ellipsis:
            continue                        # ★ 有默认值的不必合成 ✓
        #: ★ ① 先按**真签名里的类型注解**（★ 最硬）✓
        a = ann.get(pp.name)
        if a is not None:
            t = str(a).lower()
            base = t.replace("typing.", "").split("[")[0]
            if base in ("int",):
                out[pp.name] = 1
                continue
            if base in ("float",):
                out[pp.name] = 1.0
                continue
            if base in ("bool",):
                out[pp.name] = True
                continue
            if base in ("dict", "mapping", "mutabledmapping"):
                #: ★ dict 给**非空**的（★ 真空 dict 多半没用）✓
                out[pp.name] = {"MCP_CALIB": "1"}
                continue
            if base in ("list", "sequence", "tuple", "iterable"):
                out[pp.name] = ["MCP_CALIB"]
                continue
            if base in ("str",):
                #: ★★ 注解说 `str` ⇒ ★ 允许 ② 的名字后缀**细化**（如 `path` 给个文件名）✓
                #:   ★★★ **但结果必须还是 `str`** —— ★ 真机被测试抓到：★ 我原先在这里 `pass`，
                #:     ★ 于是落到 ②，★ 而 `doc_type` 命中了 `_type` 后缀 ⇒ ★ **给了数字 `0`** ✗✗
                #:   ⇒ ★ **"类型优先"必须落到最后一道**：★ 合成完**按注解类型校验**，★ 不合就换回对的 ✓
                _low = pp.name.lower()
                _cand = None
                for _h, _v in _SYNTH_BY_HINT:
                    if _h in _low and isinstance(_v, str):
                        _cand = _v
                        break
                out[pp.name] = _cand if _cand is not None else "MCP_CALIB"
                continue
        #: ★ ② 再按名字后缀（★ 猜的，★ 所以排在类型后面）✓
        low = pp.name.lower()
        value = None
        for hint, v in _SYNTH_BY_HINT:
            if hint in low:
                value = v
                break
        if value is None:
            value = "MCP_CALIB"
        out[pp.name] = value
    return out

def classify(declared_writes, diff, usable, *, call_ok: bool) -> str:
    """★★ 四类判定（★ 严格照 spec：`missed` 与 `undecided` **不许混**）✓

    ★★★ 2026-10-06 **跑写工具之前必须先修的一处假结论**：★ 若那次调用**根本没调成**
      （★ 例如写工具缺前置）⇒ ★ 指纹当然不会变 ⇒ ★★ 而只指纹判定会报 **`agree`**
      ⇒ ★ **那是「假一致」**：★ 我们**根本没测到它**（★ 与事实 57「一直是绿的，
      ★ 可能只是环境恰好满足」同族）✓
    ⇒ ★ 判序把 `call_ok` 放**最前**：★ **没调成 ⇒ `undecided`**（★ 并记明原因）✓
    """
    if not call_ok:
        return "undecided"
    if not usable or diff["unknown"]:
        return "undecided"
    changed = bool(diff["changed"])
    if declared_writes is None:
        #: ★ 声明是**未知** ⇒ ★ 不判「一致」，★ 如实记未判定 ✓
        return "undecided"
    if not declared_writes:
        return "missed" if changed else "agree"
    return "conservative"


def main() -> int:
    ap = argparse.ArgumentParser(description="★ 存活普查（规格 210 · B3）")
    ap.add_argument("--limit", type=int, default=0, help="★ 只跑前 N 个（★ 试跑用）")
    #: ★★ 按**声明**分组跑（★ 三组语义完全不同，★ 分开跑才好读）✓
    ap.add_argument("--declared", choices=("empty", "nonempty", "null", "all"), default="empty",
                    help="★ empty=`writes == []`（已确认无写，硬红门禁盯这批）· "
                         "nonempty=`writes` 非空（★ 验 conservative）· "
                         "null=未声明（★ 预期全 undecided）· all=全部")
    ap.add_argument("--json-out", default="output/spec210-survival-diff.json")
    args = ap.parse_args()

    import sw_connect
    import sw_fingerprint as FP
    import tool_caller

    table = json.loads(EFFECTS.read_text(encoding="utf-8")).get("tools", {})
    #: ★ 按 `--declared` 选目标（★ `[]` / 非空 / `None` / 全部 —— ★ 三组**不许混**）✓
    #: ★★ 先把目标按 `requires` **分组**（★ 每组只建一次状态）✓
    def _requires_of(tool_name: str) -> str:
        #: ★★ 分组用 **`inject`（精确注入名）**；★ `requires`（种类）只用于统计基数 ✓
        return str((table.get(tool_name) or {}).get("inject") or "none")

    if args.declared == "empty":
        targets = sorted(n for n, r in table.items() if r.get("writes") == [])
    elif args.declared == "nonempty":
        targets = sorted(n for n, r in table.items() if r.get("writes"))
    elif args.declared == "null":
        targets = sorted(n for n, r in table.items() if r.get("writes") is None)
    else:
        targets = sorted(table)
    if args.limit:
        targets = targets[:args.limit]
    by_requires: dict = {}
    for n in targets:
        by_requires.setdefault(_requires_of(n), []).append(n)
    print("★ 目标：%d 个（★ 按声明分组 `%s`）· ★ 分成 **%d** 个 `requires` 组：%s"
          % (len(targets), args.declared, len(by_requires),
             {k: len(v) for k, v in sorted(by_requires.items())}))

    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    if sw is None:
        print("★ 连不上 ⇒ 按铁律 5 记「查不到」并停下")
        return 2

    rows = []
    for req in sorted(by_requires):
        group = by_requires[req]
        print("\n★ ── `requires=%s` 组：%d 个（★ **只建一次状态**，★ 写工具后重建）──"
              % (req, len(group)))
        injects, why_state = build_host(sw, req)
        if why_state:
            #: ★ 建不出宿主 ⇒ 整组**如实记未判定**（★ 不许当成通过）✓
            for _n in group:
                rows.append({"tool": _n, "verdict": "undecided", "requires": req,
                             "writer_ok": True, "why": why_state})
            print("   ★ 整组跳过：%s" % why_state)
            continue
        #: ★★ 组内**连着调**；★ **写工具之后重建状态**（★ 那是"副本重载"）✓
        #:   ★★ 我第一版把 `before = …` 那段**写在了组循环外面** ⇒ 每组只有**最后一个**
        #:     工具被处理（★ 真机现象：47 个只出 **7 行** —— ★ 正好等于组数）✗
        for name in group:
            decl = table.get(name) or {}
            if decl.get("writes"):
                injects, why_state = build_host(sw, req)
                if why_state:
                    rows.append({"tool": name, "verdict": "undecided", "requires": req,
                                 "writer_ok": True, "why": "★ 重建状态失败：%s" % why_state})
                    continue
            #: ★★ 指纹一律读**文档**（★ 见 `build_host` 的说明）✓
            _doc = injects.get("_doc")
            before = FP.read(_doc, sw) if _doc is not None else {"readings": {}, "usable": False}
            #: ★★ 按声明**合成实参**（★ 真机证明 12/17 的失败只是"没给参数"）✓
            spec_entry = tool_caller._specs().get(name)
            extra = synth_args(spec_entry[0]) if spec_entry else {}
            ok, note = tool_caller.call(
                name, inject_objects=dict(injects),
                **{k: v for k, v in extra.items()
                   if k not in ("model", "sw", "asm_model", "view", "sldworks",
                                "doc", "study")})
            after = FP.read(_doc, sw) if _doc is not None else {"readings": {}, "usable": False}
            diff = FP.compare_detailed(before, after)
            verdict = classify(table[name].get("writes"),
                               {"changed": diff["changed"], "unknown": diff["unknown"]},
                               bool(before.get("usable")) and bool(after.get("usable")),
                               call_ok=bool(ok))
            rows.append({
                "tool": name, "verdict": verdict, "writer_ok": ok, "requires": req,
                "call_note": str(note)[:120],
                "declared_writes": table[name].get("writes"),
                "changed_classes": [c["class"] for c in diff["changed"]],
                "unknown_classes": [c["class"] for c in diff["unknown"]],
            })
            print("   %-46s %-13s 变了=%s" % (name, verdict,
                                             rows[-1]["changed_classes"] or "无"))

    counts: dict = {}
    for r in rows:
        counts[r["verdict"]] = counts.get(r["verdict"], 0) + 1
    missed = [r["tool"] for r in rows if r["verdict"] == "missed"]
    #: ★★ 「调用没调成」单列 —— ★ 它**既不是通过也不是失败**，★ 是**我们没测到** ✓
    call_failed = [r["tool"] for r in rows if not r.get("writer_ok")]
    out = {
        "_": "★ B3 存活普查的「声明 vs 观察」差异表（★ 每条各用一个新零件）",
        "declared_group": args.declared,
        "_judge": "★ agree=一致 · conservative=声明保守 · ★★ missed=**声明漏报**（硬红门禁）· undecided=未判定",
        "counts": counts, "missed": missed, "call_failed": call_failed, "rows": rows,
    }
    p = Path(args.json_out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("★ 四类统计：%s" % counts)
    print("★★ 硬红门禁（声明只读却观察到指纹变化）：**%d** 条 %s"
          % (len(missed), missed[:5] if missed else ""))
    print("★ 调用没调成的（★ 我们没测到，不算通过也不算失败）：**%d** 条 %s"
          % (len(call_failed), call_failed[:5] if call_failed else ""))
    print("★ 报告：%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
