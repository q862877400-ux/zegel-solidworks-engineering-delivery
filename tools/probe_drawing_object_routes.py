r"""@brief 探针：**工程图对象怎么取** —— 三条读数路（图纸 / 当前图纸属性 / 视图链）。

## 为什么要有这个探针（2026-10-01 轮 224，砌墙 W2 的前置）
W2 要挂「**当前活动工程图的轻量只读读数**」。挂之前必须先回答一个**只有真机能答**的问题：
```
① `IDrawingDoc` 要从哪里来？—— 官方示例 `Get_Drawing_View_Names_and_Types_Example_CSharp`：
     swModel = (ModelDoc2)swApp.ActiveDoc;
     swDraw  = (DrawingDoc)swModel;      ← ★ **是"转换"，不是"取一个子对象"**
   ⇒ ★ 也就是说 **model 本身就是 IDrawingDoc**。
   ⚠ 但 pywin32 **迟到绑定**下，`model` 这个 Dispatch **能不能直接调 `GetCurrentSheet`** 是未知的
     —— COM 的 QueryInterface 由 IDispatch 处理，通常可以，但本项目已多次遇到"看起来该可以却不行"
     （事实 32 / 36 / 47）。**⇒ 这就是本探针要答的第一问。**
② `ISheet.GetProperties2()` 返回什么形状？（官方文档：`GetProperties` 是 **7 个 double 的数组**，
   不是 out 参数 ⇒ ★ 避开了事实 8 那个"by-ref 不回写"的坑；且 `GetProperties` 已 Obsolete）
③ `GetFirstView() → GetNextView()` 这条链在**空图纸**上是什么？（官方示例说它只遍历**当前图纸**）

## ⚠ 安全（照 `tools/probe_sketch_object_routes.py` 的骨架）
**只在新文档上跑**、不改用户文档；`CommandInProgress` 抑制弹窗；收尾**关件不保存**。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针，**不是**从四家外部 MCP 项目移植）
# 文件:   tools/probe_drawing_object_routes.py
# 定位:   给砌墙 W2 定包装层；产出 `output/drawing-object-routes.json`。
# 官方依据: `IDrawingDoc.GetCurrentSheet` / `GetFirstView` / `GetSheetCount` / `GetSheet
#           Names` ·
#          `ISheet.GetName` / `GetProperties2` · `IView.GetName2` / `Type` / `GetNextView`;
#          官方示例 `Get_Drawing_View_Names_and_Types_Example_CSharp`（`C:\swapi\examples\`）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 真机脚本：跑之前确认只有一个 SolidWorks 实例（已知事实 24）。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (str(ROOT), str(ROOT / "scripts"), str(ROOT / "mcp-server")):
    if p not in sys.path:
        sys.path.insert(0, p)
sys.stdout.reconfigure(encoding="utf-8")

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "drawing-object-routes.json")


def _try(fn, *a, **kw):
    """跑一个探测调用，返回 (ok, value_or_error)。**不抛**。"""
    try:
        return True, fn(*a, **kw)
    except Exception as exc:                                   # noqa: BLE001
        return False, "%s: %s" % (type(exc).__name__, str(exc)[:90])


def probe(model, sc) -> dict:
    """三条读数路各试一次。"""
    out: dict = {}

    #: ① model 能不能直接当 IDrawingDoc 用
    ok, v = _try(lambda: int(sc.safe_get_com_member(model, "GetType")))
    out["A_model_GetType"] = v if ok else v
    ok, v = _try(lambda: sc.safe_get_com_member(model, "GetCurrentSheet"))
    out["B_GetCurrentSheet_on_model"] = ("拿到对象" if (ok and v is not None)
                                         else (v if not ok else None))

    #: ② 图纸级读数
    ok, sheet = _try(lambda: sc.safe_get_com_member(model, "GetCurrentSheet"))
    if ok and sheet is not None:
        ok2, nm = _try(lambda: sc.safe_get_com_member(sheet, "GetName"))
        out["C_Sheet_GetName"] = nm if ok2 else nm
        ok2, props = _try(lambda: sc.safe_get_com_member(sheet, "GetProperties2"))
        if ok2:
            try:
                out["D_Sheet_GetProperties2"] = {"len": len(props),
                                                 "values": [round(float(x), 4) for x in props][:10]}
            except Exception:                                  # noqa: BLE001
                out["D_Sheet_GetProperties2"] = {"raw": str(props)[:120]}
        else:
            out["D_Sheet_GetProperties2"] = props
        ok2, fmt = _try(lambda: sc.safe_get_com_member(sheet, "GetSheetFormatName"))
        out["E_Sheet_GetSheetFormatName"] = fmt if ok2 else fmt

    #: ③ 张数与名字清单
    ok, n = _try(lambda: int(sc.safe_get_com_member(model, "GetSheetCount")))
    out["F_GetSheetCount"] = n if ok else n
    ok, names = _try(lambda: sc.safe_get_com_member(model, "GetSheetNames"))
    if ok:
        try:
            out["G_GetSheetNames"] = [str(x) for x in names]
        except Exception:                                      # noqa: BLE001
            out["G_GetSheetNames"] = {"raw": str(names)[:120]}
    else:
        out["G_GetSheetNames"] = names

    #: ④ 视图链（官方示例的写法：GetFirstView → GetNextView，只覆盖当前图纸）
    ok, view = _try(lambda: sc.safe_get_com_member(model, "GetFirstView"))
    chain = []
    if ok and view is not None:
        for _ in range(50):                                    #: 防御上限
            nm_ok, nm = _try(lambda v=view: sc.safe_get_com_member(v, "GetName2"))
            ty_ok, ty = _try(lambda v=view: int(sc.safe_get_com_member(v, "Type")))
            chain.append({"name": nm if nm_ok else str(nm),
                          "type": ty if ty_ok else str(ty)})
            nxt_ok, nxt = _try(lambda v=view: sc.safe_get_com_member(v, "GetNextView"))
            if not nxt_ok or nxt is None:
                break
            view = nxt
    out["H_view_chain"] = chain
    out["H_note"] = ("空图纸上 GetFirstView 多半回 None（官方示例的前提是「已打开一张有视图的工程图」）"
                     if not chain else "★ 真取到了视图链")
    return out


def main() -> int:
    ev: dict = {"captured_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "steps": []}
    sw = None
    docs: list = []
    try:
        import sw_connect

        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:                                      # noqa: BLE001
            pass

        #: ① 空工程图
        doc = sw_connect.new_document(sw, "drawing")
        docs.append(doc)
        ev["steps"].append({"tag": "新建空工程图", "title":
                            str(sw_connect.safe_get_com_member(doc, "GetTitle") or ""),
                            **probe(doc, sw_connect)})

        #: ② 一个零件（供对照：确认 GetType 不同）
        part = sw_connect.new_document(sw, "part")
        docs.append(part)
        ok, ty = _try(lambda: int(sw_connect.safe_get_com_member(part, "GetType")))
        ev["steps"].append({"tag": "新建零件（对照）", "GetType": ty if ok else ty,
                            "查文档类型": "swDocPART=1 / swDocASSEMBLY=2 / swDocDRAWING=3"})
    except Exception as exc:                                   # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:                                      # noqa: BLE001
            pass
        for d in docs:                                         #: ★ 关件不保存
            try:
                t = str(sw_connect.safe_get_com_member(d, "GetTitle") or "")
                if t and sw is not None:
                    sw.CloseDoc(t)
            except Exception:                                  # noqa: BLE001
                pass

    print("  ── 工程图对象三条读数路 ──")
    for s in ev["steps"]:
        print("  ══ %s ══" % s["tag"])
        for k, v in s.items():
            if k != "tag":
                print("     %-28s %s" % (k, json.dumps(v, ensure_ascii=False)[:150]))
    if ev.get("error"):
        print("  ⚠ error: %s" % ev["error"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("  证据: %s" % OUT)
    return 0 if not ev.get("error") else 1


if __name__ == "__main__":
    raise SystemExit(main())
