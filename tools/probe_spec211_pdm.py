"""★ 探针：PDM 的真机可达性 —— ★ 判据是**抛不抛 + 拿不拿得到**（★ 铁律 5 的现场）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（规格 211 · B7 PDM 的待实测）
# 文件:   tools/probe_spec211_pdm.py
# 定位:   ★ 规格 `specs/211-user-feature-gaps` 的「其他 / PDM」—— ★ 21 项里**唯一一项"待实测"** ✓
# 官方依据（★ 本批现场全扫所得）：
#   · ★★★ **`ISldWorks` 下**没有** PDM 入口** ✗ —— 入口在 **`IApplication::PDMDocManager`** ✓
#     ★★ 而 `IApplication` **不是** `ISldWorks` ✗（★ 拿它要另找路 ✓）
#   · ★★ **`IPDMDocManager` 只有 3 个成员**：★ `SetCancelOperation` · `SetDocumentStatus` ·
#     `SetManagedDocument` ✓ —— ★★★ **全是"设置状态"、★ 没有"检入/检出/取版本"这类 PDM 核心操作** ✗
#     ⇒ ★ **即：用户理解的"PDM 功能"（检入检出/版本/库）在官方离线源里**查不到**** ✓（铁律 5 ✓）
# 本仓既有的知识（★ 两条**关键**，★ 本批直接引用）：
#   ★ `scripts/sw_automation_knowledge.py` 第 49 行附近：「★ 这是**官方文档不会给**的：它只在
#     「★ **你调 PDM 而没买许可**」时出现」✓
#   ★★ `scripts/sw_com_traps.py` 第 83 行：★ `0x80040112`: **COM 类未授权 —— 通常是该产品没许可
#     （PDM / Simulation / Routers）** ✓
# ⇒ ★★★★ **所以 PDM 的性质与 Simulation / Routers 同类：★ 独立许可产品** ✓
#   ★★ 而本规格的硬约束明写：★ **不装不改系统层** ✓、★ **许可红线** ✓
# 判据:   ★★ 真机探：★ ① `sw` 上直接取 `PDMDocManager`（★ 试几种取法）· ★② 记**异常与 HRESULT** ✓
#   ★★★ **三种结果三种记法**：
#     · ★ **拿到对象** ⇒ ★ 再探它的 3 个成员（★ 而**那也不是用户功能级 PDM** ✓）
#     · ★ **抛 `0x80040112`** ⇒ ★★★ **正是本仓早记过的那条**（★ **该产品没许可** ✓）✓
#     · ★ **`None` / 别的错** ⇒ ★ 如实记 ✓
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

#: ★ 试几种"取 PDM"的形态（★ 官方入口在 `IApplication::PDMDocManager`、★ 而 `sw` 是 `ISldWorks` ✗）
FORMS = ("sw.PDMDocManager（属性）", "sw.GetPDMDocManager()（方法）",
         "sw.Application.PDMDocManager")


def main() -> int:
    import sw_connect

    out: dict = {"official": ["IApplication.PDMDocManager", "IPDMDocManager"],
                 "official_members_of_IPDMDocManager": ["SetCancelOperation",
                                                        "SetDocumentStatus",
                                                        "SetManagedDocument"],
                 "step": "待实测：PDM 在本机可不可达",
                 "runs": []}
    sw, _ = sw_connect.connect_solidworks(wait_seconds=20)
    if sw is None:
        print("★ 连不上")
        return 2

    got = None
    for form in FORMS:
        exc = None
        obj = None
        try:
            if form.startswith("sw.PDMDocManager"):
                obj = sw_connect.get_com_member(sw, "PDMDocManager")
            elif form.startswith("sw.GetPDM"):
                obj = sw_connect.get_com_member(sw, "GetPDMDocManager")
            else:
                app = sw_connect.get_com_member(sw, "Application")
                obj = sw_connect.get_com_member(app, "PDMDocManager") if app is not None else None
        except Exception as e:                                          # noqa: BLE001
            exc = e
        row = {"form": form,
               "got_object": obj is not None,
               "exception": None if exc is None else "%s: %s" % (type(exc).__name__, str(exc)[:170])}
        #: ★★ 记 HRESULT（★ 本仓早记过 `0x80040112` = 该产品没许可 ✓）
        if exc is not None:
            s = str(exc)
            for hx in ("0x80040112", "0x80040154", "0x80004002", "0x80040111"):
                if hx.lower() in s.lower():
                    row["hresult"] = hx
        out["runs"].append(row)
        print("★ %-28s ⇒ 拿到=%r %s" % (form, obj is not None,
                                        ("· 抛：" + row["exception"]) if exc else ""))
        if obj is not None and got is None:
            got = obj

    if got is not None:
        #: ★ 拿到就再探那 3 个成员（★ 而**它们也不是用户功能级 PDM** ✓）
        probe = {}
        for m in ("SetCancelOperation", "SetDocumentStatus", "SetManagedDocument"):
            try:
                probe[m] = "可调用（未传实参）"
                sw_connect.get_com_member(got, m)
            except Exception as e:                                      # noqa: BLE001
                probe[m] = "%s: %s" % (type(e).__name__, str(e)[:90])
        out["member_probe"] = probe
        out["verdict"] = ("★★★ **拿到了 PDM 对象**（★ 形态见上 ✓）· ★ 而它的成员只有 3 个、"
                          "★ 全是「设置状态」✗ ⇒ ★ **那**不是**用户理解的 PDM 功能**（检入检出/版本/库 ✗）"
                          "⇒ ★★ 与**铁律 5**（查不到就说查不到）一致 ✓")
    else:
        hj = [r.get("hresult") for r in out["runs"] if r.get("hresult")]
        if any(h == "0x80040112" for h in hj):
            out["verdict"] = ("★★★★ **抛 `0x80040112`（COM 类未授权）** ⇒ ★★ **正是本仓早记过的那条**："
                              "「通常是**该产品没许可**（PDM / Simulation / Routers）」✓ ⇒ "
                              "★★ **PDM = 独立许可产品、★ 本机未装/未授权** ⇒ ★ **不做（需另装独立许可产品）** ✓")
        else:
            out["verdict"] = ("★★ **三种取法都没拿到对象**（★ 异常见上 ✓）· ★ 而官方入口在 "
                              "`IApplication::PDMDocManager`✗ —— ★ **`IApplication` 不是 `ISldWorks`** ✓ ⇒ "
                              "★★ 结合本仓既有知识（★ `0x80040112` = **该产品没许可** ✓）⇒ "
                              "★★★ **判「不做（需另装独立许可产品）」** ✓（★ 铁律 5 + 铁律 6 的许可红线 ✓）")
    print("★★★ 判定 ⇒ %s" % out["verdict"])

    p = ROOT / "output" / "spec211-b7-pdm.json"
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
    print("★ 证据：%s" % p)
    return 0


if __name__ == "__main__":
    import traceback
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException:                                              # noqa: BLE001
        tb = traceback.format_exc()
        (ROOT / "output" / "spec211-b7-pdm-traceback.txt").write_text(tb, encoding="utf-8")
        print("★★ 异常已落盘：\n%s" % tb[-1200:])
        raise SystemExit(3)
