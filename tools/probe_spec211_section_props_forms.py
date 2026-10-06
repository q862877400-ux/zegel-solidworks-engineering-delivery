"""★ 探针：`GetSectionProperties2` 的形态判定（★ 与事实 386 那类"后端造不出包装"是不是同一形态）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 211 · B1-1 的形态判定探针）
# 文件:   tools/probe_spec211_section_props_forms.py
# 定位:   ★ 规格 `specs/211-user-feature-gaps` 的 **B1-1**。★ 真机第一轮拿到的是
#   `TypeError: … 取回来的成员**不可调用**（`getattr` 回了 `tuple`）` —— ★ 那是**本仓守卫**报的，
#   ★ 而它明写「★ 这**多半是 pywin32 迟到绑定造不出该方法的调用包装**，★ **不是参数没传对**」
#   ⇒ ★★ 但**不能凭一个报错就定性**（★ 不许把"一个实例"推广成"一族"）⇒ ★ **逐形态实测** ✓
#   ★★ 仓里已有**同型先例（事实 386）**：`IModelDocExtension.InsertChainDimensions`
#     —— 官方 `kind: method`、`System.object …(System.object)`，而 `type(getattr(...))` = `tuple`、
#     `callable` = `False`、`repr` = `(None, None, None)`、`dir()` 里**没有该名字** ✓
# 判据:   ★★ **五问**（★ 每一问都要落盘）：
#     ① `type(getattr(ext, M))` 是什么？
#     ② `callable(...)` 是真是假？
#     ③ `M in dir(ext)` 吗？
#     ④ ★ **老入口 `GetSectionProperties`** 同不同命？（★ 新入口不行、老入口行 ⇒ 就有兜底路）✓
#     ⑤ ★ **`I` 前缀的指针变体 `IGetSectionProperties2`** 呢？（★ 事实 47 说那族不可用）✓
#   ★★ 结论只能落在**这五问的读数**上 —— ★ **不许**用"它跟 386 长得像"当结论 ✓
# 官方依据: `C:\swapi\types\IModelDocExtension\GetSectionProperties2.md`（签名 + Remarks + 24 元）
# 许可:   本仓库 MIT。无第三方代码引入。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
for _p in (str(ROOT), str(ROOT / "tools"), str(ROOT / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

MEMBERS = ("GetSectionProperties2", "GetSectionProperties",
           "IGetSectionProperties2", "IGetSectionProperties")
RECT = {"x1_mm": 0.0, "y1_mm": 0.0, "x2_mm": 100.0, "y2_mm": 60.0}


def _probe(obj, name: str) -> dict:
    """★ 五问的读数（★ 全部落盘；★ 不抛出去，★ 只记）✓"""
    import sw_connect
    out = {"member": name}
    try:
        out["in_dir"] = name in dir(obj)
    except Exception as exc:                                            # noqa: BLE001
        out["in_dir"] = "★ dir() 失败：%s" % type(exc).__name__
    try:
        raw = getattr(obj, name)
        out["type"] = type(raw).__name__
        out["callable"] = callable(raw)
        out["repr"] = repr(raw)[:80]
    except Exception as exc:                                            # noqa: BLE001
        out["type"] = "★ getattr 抛 %s" % type(exc).__name__
        out["callable"] = None
        out["repr"] = str(exc)[:80]
        return out
    #: ★ 若可调用 ⇒ 试**空实参**（★ 只记结果，★ 不当判据）
    if out.get("callable"):
        try:
            sw_connect.get_com_member(obj, name, None)
            out["call_with_None"] = "没抛"
        except Exception as exc:                                        # noqa: BLE001
            out["call_with_None"] = "%s: %s" % (type(exc).__name__, str(exc)[:70])
    return out


def main() -> int:
    import sw_connect
    import tool_caller

    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    if sw is None:
        print("★ 连不上")
        return 2
    model = sw_connect.new_document(sw, "part")
    inj = {"model": model, "sw": sw}
    for step, params in (("solidworks_sketch_start", {}),
                         ("solidworks_sketch_add_rectangle", RECT),
                         ("solidworks_extrude_boss",
                          {"sketch_name": "Sketch1", "depth_mm": 20.0})):
        ok, _note = tool_caller.call(step, inject_objects=inj, **params)
        if not ok:
            print("★ 建状态没成：%s" % step)
            return 1
    tool_caller.call("solidworks_select_by_selector", inject_objects=inj,
                     selector="index:0", kind="FACE", body_index=0)

    ext = sw_connect.get_com_member(model, "Extension")
    print("★ Extension 取到 =", ext is not None)
    #: ★★ 事实 386 的那个**对照样本**（★ 同接口、同签名形态）—— ★ 一起量，★ 才知道是不是同一族 ✓
    rows = [_probe(ext, m) for m in MEMBERS]
    rows.append(_probe(ext, "InsertChainDimensions"))     # ★ 事实 386 的样本（对照）✓
    rows.append(_probe(ext, "GetMassProperties2"))        # ★ 同接口上一个**已知可用**的对照 ✓

    for r in rows:
        print("★ %-24s type=%-14s callable=%-5s in_dir=%-5s %s"
              % (r["member"], str(r.get("type"))[:14], r.get("callable"),
                 r.get("in_dir"), str(r.get("repr"))[:40]))

    out = {"official": "IModelDocExtension.GetSectionProperties2",
           "expect_area_mm2": 6000.0, "forms": rows}
    p = ROOT / "output" / "spec211-b1-section-props-forms.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("★ 证据：%s" % p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
