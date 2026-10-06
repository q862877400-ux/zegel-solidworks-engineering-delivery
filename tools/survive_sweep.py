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
    """★ 按**声明**给每条必填形参**合成一个值**（★ 形状对即可）✓

    ★★ 为什么值得做：★ 真机读数证明，**12/17** 的失败只是"没给参数" ⇒
      ★ 不合成的话，我们**永远测不到**这些工具（★ 而它们会被记成 `undecided`）✓
    ★ 优先级：★ 先看名字后缀（`_mm` / `_deg` / `_name` / `path` …），
      ★ 都命不中就看类型提示，★ 再命不中给一个**保守的字符串** ✓
    ★⚠ 限度：★ 合成的值**只保证类型/形状对** —— ★ **不保证语义对**；
      ★ 所以调用**仍可能失败**，★ 那会如实记 `undecided`（★ 不许当成"通过"）✓
    """
    out = {}
    for pp in (getattr(spec, "params", None) or ()):
        if getattr(pp, "default", None) is not Ellipsis:
            continue                        # ★ 有默认值的不必合成 ✓
        low = pp.name.lower()
        value = None
        for hint, v in _SYNTH_BY_HINT:
            if hint in low:
                value = v
                break
        if value is None:
            kind = str(getattr(pp, "kind", "") or "").lower()
            if "int" in kind:
                value = 0
            elif "float" in kind or "double" in kind:
                value = 1.0
            elif "bool" in kind:
                value = True
            else:
                value = "MCP_CALIB"
        out[pp.name] = value
    return out


#: ★★★ **按 `requires` 分组**（★ 规格 210 · B3 的核心优化）——
#:   ★★ 评审的判决：「**成本的主项是"建立前置状态"，不是调用本身**」⇒
#:     ★ 每组**只建一次状态**、组内**连着调** ⇒ ★ **耗时随"不同前置的数量"增长，不随工具数增长** ✓
#:   ★ 本仓实测：★ 448 个工具只落在 **9 种宿主**上（★ `part` 236 · `none` 57 · `app` 45 ·
#:     `study` 40 · `view` 23 · `costing` 15 · `assembly` 14 · `drawing` 9 · `selection` 9）✓
#:   ★ 改写前：★ 每条工具**各建一个新零件**（47 条 ⇒ 47 个）✗
#:   ★ 改写后：★ **`part` 组只建一个**、★ 只在**写工具之后重建**（★ 那就是"副本重载"）✓
_KIND_BY_REQUIRES = {
    "part": "part", "none": "part", "selection": "part", "view": "part",
    "study": "part", "costing": "part",
    "assembly": "assembly", "drawing": "drawing",
    "app": None,          # ★ 只需要应用对象 ⇒ **不用建文档** ✓
}


def build_host(sw, inject_name: str):
    """★★ 按**注入名**建**对的宿主对象** —— ★ 这是分组省时间之后**必须补的那一半** ✓

    ★★★ 2026-10-06 **分组暴露的真问题**：★ 每组需要的**不只是"一个文档"**，★ 而是**那个特定的对象** ——
      ★ `asm_model` 要装配体 · `view` 要视图 · `study` 要研究 · `cost_manager` 要成本管理器 ⇒
      ★★ 而我第一版 `build_state` **只会建文档、且一律当 `model` 传** ⇒
      ★ 于是除 `part`/`none` 外的组**根本没跑到**（★ 真机：`empty` 47 条里 33 条"调用没调成"）✗
    ★★ 另外一处更细的认识：★ 分组的键应当是 **`inject`（精确的注入名）**，
      ★ 不是 `requires`（**种类**）—— ★ `requires` 只用来做**基数统计**（9 种）✓

    :returns: `(inject_objects, why)` —— ★ `why` 非空表示**这一组还没法建**（★ 如实记，不假装）✓
    ★⚠ 限度：★ `view` / `study` / `cost_manager` / `selection` **这四类还没建**
      （★ 要构造视图/研究/成本管理器/选中对象）⇒ ★ 那些组会**如实记 `undecided`** ✓
    """
    import sw_connect
    name = str(inject_name or "")
    #: ★★★ 2026-10-06 **真机查出的 sweep bug**：★ 我把**视图/应用对象当文档**去抓指纹 ⇒
    #:   ★★ 六格全读不到（`selection`/`edit_mode`/`dirty`/`features`/`config`/`rebuild`）✗
    #:   ★ 真机证据：★ `empty` 组里 **13 行**各 6 格未判定（= 78），★ 而 **13 正好等于**
    #:     那些"宿主不是文档"的行数（`view` 3 + `sw` 3 + `sw_app` 3 + `manager` 2 + `sldworks` 1 + `none` 1）✓
    #:   ⇒ ★ 正解：★ **指纹永远读在"文档"上** ⇒ ★ `build_host` 把文档一起回，★ 用 `_doc` 键带走 ✓
    if name in ("", "none"):
        return {"sw": sw}, ""
    #: ★ 应用对象类（`sldworks` / `sw_app` / `sw` / `manager` / `defaults` / `options`）⇒ 给 `sw` ✓
    if name in ("sldworks", "sw_app", "sw", "manager", "defaults", "options"):
        #: ★ 应用对象类：★ 宿主是 `sw` 本身，★ **但指纹要读在活动文档上** ✓
        try:
            doc = sw.ActiveDoc
        except Exception:                                               # noqa: BLE001
            doc = None
        return {name: sw, "sw": sw, "_doc": doc}, ""
    kind = {"model": "part", "doc": "part", "asm_model": "assembly",
            "component": "assembly", "drawing_model": "drawing"}.get(name)
    if kind:
        try:
            doc = sw_connect.new_document(sw, kind)
            return {name: doc, "sw": sw, "_doc": doc}, ""
        except Exception as exc:                                        # noqa: BLE001
            return {}, "★ 建 %s 失败：%s" % (kind, type(exc).__name__)
    #: ★★ 补两类**易取**的（★ 官方属性，★ 已读页面）✓
    #:   · `selection` ⇒ `IModelDoc2.SelectionManager`（★ 官方："makes the currently selected
    #:     object available"）✓
    #:   · `view` ⇒ `IModelDoc2.ActiveView`（★ 官方："Gets the current active model view
    #:     in read-only mode"）✓
    #:   ★ 这两类合起来覆盖 **32 个工具**（`selection` 9 + `view` 23）✓
    if name in ("selection", "view"):
        try:
            import sw_connect as _sc
            doc = _sc.new_document(sw, "part")
            attr = {"selection": "SelectionManager", "view": "ActiveView"}[name]
            host = _sc.get_com_member(doc, attr)
            if host is None:
                return {}, "★ 零件建好了，但 `%s` 取不到（★ 返回 None）" % attr
            #: ★ `selection`/`view` 的宿主**不是文档** ⇒ ★ 但**指纹仍读在文档上** ✓
            return {name: host, "sw": sw, "_doc": doc}, ""
        except Exception as exc:                                        # noqa: BLE001
            return {}, "★ 建 `%s` 宿主失败：%s" % (name, type(exc).__name__)
    #: ★ 剩下两类（study / cost_manager）**还没建** ⇒ ★ 如实报出 ✓
    return {}, ("★ 这一类宿主**还没建**（`%s`）—— ★ 需要构造仿真研究 / 成本管理器"
                "（★ 要加载对应插件）" % name)


def build_state(sw, requires: str):
    """★ 建**这一组**的宿主状态（★ 每组只建一次）✓

    :returns: `(model, why)` —— ★ `None` **不一定**是失败（★ `app` 组本来就不需要文档）✓
    ★⚠ 限度：★ `view` / `study` / `costing` 这三组目前**按零件兜底**
      （★ 真正的"带视图/带研究/带成本管理器"的状态**还没建**）⇒ ★ 那会在读数里**如实体现** ✓
    """
    kind = _KIND_BY_REQUIRES.get(requires)
    if kind is None:
        return None, "★ `app` 组不需要文档"
    import sw_connect
    try:
        return sw_connect.new_document(sw, kind), ""
    except Exception as exc:                                            # noqa: BLE001
        return None, "★ 建 %s 失败：%s" % (kind, type(exc).__name__)


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
