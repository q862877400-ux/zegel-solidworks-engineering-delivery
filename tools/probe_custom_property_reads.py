r"""@brief 探针：**读文件自定义属性**的三条路 —— 以及 pywin32 下 by-ref 出参到底回不回写。

## 为什么要有这个探针（2026-10-01 轮 226，砌墙 W3 的前置）
★★ **本仓库能"写"自定义属性（`solidworks_set_custom_properties`，上游给的），却**读不回来验****
—— 能力层里**没有任何"读文件自定义属性"的实现**（`sw_pdm` 那一族要 **PDM 许可证**，不是这条路）。
⇒ 本探针回答"读"该怎么读。

## 三个未知（都要真机答）
```
① **`CustomPropertyManager` 从哪取？** 官方示例给了两条路：
     · `swFeat.CustomPropertyManager`（`Add_and_Get_Custom_Properties_Example_VB`）
     · `IModelDocExtension.CustomPropertyManager`（swapi 有该页，kind = property）
   ⚠ 后者是**属性**还是**方法**（要不要配置名）必须实测。
② ★ **读值走哪个成员？** swapi 的链条是 `Get`（Obsolete）→ `Get2` → … → `Get6`：
     · `Get(FieldName) → System.string`            ★ **单返回值**（官方示例就是这么用的）
     · `Get2(FieldName, out ValOut, out ResolvedValOut) → void`   ★ **两个 out**
     · `Get3..Get6(FieldName, UseCached, out Val, out ResolvedVal) → bool/int` ★ **两个 out**
   ⇒ ★★ **本探针的核心问题**：pywin32 **迟到绑定**下那些 `out` **到底回不回写**？
      —— 这与已知事实 8（`ISelectionMgr.AddSelectionListObject` 的 bool 不可信）
        和事实 33（`Callout` 必须传 VARIANT）同一族：**COM 封送的形状决定成败**。
      ★ 若不回写 ⇒ 必须只用 `Get`（单返回值）；若 `Get` 也不可达 ⇒ **本能力做不了**。
③ ★ **决定性用例**：先 `Add3` 写一个属性，**再读回来** —— 读到才说明整条路通。
```

## ⚠ 安全（照 `tools/probe_drawing_object_routes.py` 的骨架）
**只在新零件上跑**（写入的是**新文档**、收尾**关件不保存**）⇒ 不碰用户数据；
`CommandInProgress` 抑制弹窗。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机探针，**不是**从四家外部 MCP 项目移植）
# 文件:   tools/probe_custom_property_reads.py
# 定位:   给砌墙 W3 定包装层；产出 `output/custom-property-reads.json`。
# 官方依据: `IModelDocExtension.CustomPropertyManager` · `ICustomPropertyManager.Get/Get
#           2/Get6/GetNames/Count/Add3`；
#          官方示例 `C:\swapi\examples\Add_and_Get_Custom_Properties_Example_VB.md`（在那里 `Get(vName)
` 被当**单返回值**用）
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

OUT = Path(
    Path(__file__).resolve().parents[1] / "output" / "custom-property-reads.json"
)

#: `swCustomInfoType_e`（官方示例 `Get_Custom_Properties_Example_VB` 里逐字列出）
SW_CUSTOM_INFO_TEXT = 30  #: VT_LPSTR

PROP_NAME = "DSH_ReadProbe"
PROP_VALUE = "hello-from-probe"


def _try(fn, *a, **kw):
    try:
        return True, fn(*a, **kw)
    except Exception as exc:  # noqa: BLE001
        return False, "%s: %s" % (type(exc).__name__, str(exc)[:80])


def _is_mgr(obj) -> bool:
    """★ **严判据**：它得像一个 `ICustomPropertyManager` 才有意义。

    ⚠⚠ 2026-10-01 轮 227：本探针**第一版**的判据是
      `obj is not None and not isinstance(obj, (str, int, float))`
    —— ★ **那个判据是假阳性**：pywin32 迟到绑定下 `Extension.CustomPropertyManager`
      返回的是一个**函数对象**（`AttributeError: 'function' object has no attribute 'Count'`），
      而函数**恰好不是** str/int/float ⇒ 判据说"拿到对象了"。
    ⇒ 改用**行为判据**：它必须**真的有 `Count` 这个成员**。
    """
    return obj is not None and hasattr(obj, "Count") and hasattr(obj, "GetNames")


def get_mgr_paths(model, sc) -> dict:
    """① CustomPropertyManager 的两条取法 —— ★ 属性形态与**调用**形态都试。"""
    out: dict = {}
    ext = None
    ok, ext = _try(lambda: sc.safe_get_com_member(model, "Extension"))
    out["model.Extension"] = (
        "拿到对象" if (ok and _is_mgr(ext) or (ok and ext is not None)) else str(ext)
    )
    if ok and ext is not None:
        #: 形态 A：当**属性**取
        ok2, v = _try(lambda: sc.safe_get_com_member(ext, "CustomPropertyManager"))
        out["A_当属性取 Extension.CustomPropertyManager"] = (
            "★ 是管理器"
            if (ok2 and _is_mgr(v))
            else (
                "拿到的是 %s（不是管理器）" % type(v).__name__ if ok2 else str(v)[:60]
            )
        )
        #: 形态 B：取到之后**调用它**（pywin32 可能把它封成方法）
        if ok2 and callable(v) and not _is_mgr(v):
            ok3, v3 = _try(lambda: v(""))
            out['B_把它当方法调用 CustomPropertyManager("")'] = (
                "★ 是管理器"
                if (ok3 and _is_mgr(v3))
                else (
                    "拿到的是 %s（不是管理器）" % type(v3).__name__
                    if ok3
                    else str(v3)[:60]
                )
            )
        else:
            out['B_把它当方法调用 CustomPropertyManager("")'] = (
                "（不可调用或已是管理器）"
            )
        #: 形态 C：直接带配置名当方法调
        ok4, v4 = _try(lambda: sc.safe_get_com_member(ext, "CustomPropertyManager", ""))
        out['C_直接带配置名调 Extension.CustomPropertyManager("")'] = (
            "★ 是管理器"
            if (ok4 and _is_mgr(v4))
            else (
                "拿到的是 %s（不是管理器）" % type(v4).__name__ if ok4 else str(v4)[:60]
            )
        )
    #: 从 Feature 取（官方示例那条路）
    ok5, feat = _try(lambda: sc.safe_get_com_member(model, "FirstFeature"))
    if ok5 and feat is not None:
        ok6, fm = _try(lambda: sc.safe_get_com_member(feat, "CustomPropertyManager"))
        out["D_Feature.CustomPropertyManager（官方示例那条）"] = (
            "★ 是管理器"
            if (ok6 and _is_mgr(fm))
            else (
                "拿到的是 %s（不是管理器）" % type(fm).__name__ if ok6 else str(fm)[:60]
            )
        )
    return out


def probe_reads(model, sc, mgr) -> dict:
    """② 各类读法：Count / GetNames / Get（单返回值）/ Get6（两个 out）/ GetAll3。"""
    out: dict = {}
    if mgr is None:
        return {"skipped": "没拿到 CustomPropertyManager"}
    ok, n = _try(lambda: int(sc.safe_get_com_member(mgr, "Count")))
    out["Count"] = n if ok else n
    ok, names = _try(lambda: sc.safe_get_com_member(mgr, "GetNames"))
    if ok:
        try:
            out["GetNames"] = [str(x) for x in names][:12]
        except TypeError:
            out["GetNames"] = {"raw": str(names)[:100]}
    else:
        out["GetNames"] = names
    #: ★ 单返回值那条（官方示例的用法）
    ok, v = _try(lambda: sc.safe_get_com_member(mgr, "Get", PROP_NAME))
    out["★ Get(name)（单返回值）"] = v if ok else v
    #: ★ 两个 out 那条（结果取决于 pywin32 是否回写）
    ok, r = _try(lambda: sc.safe_get_com_member(mgr, "Get6", PROP_NAME, False, "", ""))
    out["★ Get6(name,False,'','')（两个 out）"] = r if ok else r
    #: 类型
    ok, t = _try(lambda: sc.safe_get_com_member(mgr, "GetType2", PROP_NAME))
    out["GetType2(name)"] = t if ok else t
    return out


def main() -> int:
    ev: dict = {"captured_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "steps": {}}
    sw = None
    doc = None
    try:
        import sw_connect

        from scripts.sw_connect import mm as _mm  # noqa: F401  (确认模块可用)

        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass
        doc = sw_connect.new_document(sw, "part")
        ev["steps"]["part"] = {
            "title": str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
        }

        ev["steps"]["managers"] = get_mgr_paths(doc, sw_connect)

        #: 取一个**真的是管理器**的 mgr 用于后续读（★ 严判据，见 `_is_mgr`）
        mgr = None
        candidates = []
        ext = sw_connect.safe_get_com_member(doc, "Extension")
        if ext is not None:
            v = sw_connect.safe_get_com_member(ext, "CustomPropertyManager")
            candidates.append(v)
            if callable(v):  #: ★ 可能被封成方法 ⇒ 调它
                try:
                    candidates.append(v(""))
                except Exception:  # noqa: BLE001
                    pass
            try:
                candidates.append(
                    sw_connect.safe_get_com_member(ext, "CustomPropertyManager", "")
                )
            except Exception:  # noqa: BLE001
                pass
        feat = sw_connect.safe_get_com_member(doc, "FirstFeature")
        if feat is not None:
            candidates.append(
                sw_connect.safe_get_com_member(feat, "CustomPropertyManager")
            )
        for c in candidates:
            if _is_mgr(c):
                mgr = c
                break
        ev["steps"]["mgr_obtained"] = mgr is not None

        ev["steps"]["before_write"] = probe_reads(doc, sw_connect, mgr)

        #: ★★ 决定性用例：先写一个，再读回来
        ok, r = _try(
            lambda: sw_connect.safe_get_com_member(
                mgr, "Add3", PROP_NAME, SW_CUSTOM_INFO_TEXT, PROP_VALUE, True
            )
        )
        ev["steps"]["write"] = {
            "ok": ok,
            "ret": r if ok else r,
            "wrote": "%s = %r" % (PROP_NAME, PROP_VALUE),
        }
        ev["steps"]["after_write"] = probe_reads(doc, sw_connect, mgr)
        got = ev["steps"]["after_write"].get("★ Get(name)（单返回值）")
        ev["steps"]["verdict_readback"] = {
            "ok": got == PROP_VALUE,
            "read": got,
            "★": "先 Add3 再读回来 —— 读到才说明整条路通",
        }
    except Exception as exc:  # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
    finally:
        try:
            if sw is not None:
                sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        try:
            if doc is not None and sw is not None:
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)  #: ★ 关件不保存（写的是新文档）
        except Exception:  # noqa: BLE001
            pass

    print("  ── 自定义属性读取三条路 ──")
    for k, v in ev["steps"].items():
        print("  ══ %s ══" % k)
        print("     %s" % json.dumps(v, ensure_ascii=False)[:400])
    if ev.get("error"):
        print("  ⚠ error: %s" % ev["error"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("  证据: %s" % OUT)
    return 0 if not ev.get("error") else 1


if __name__ == "__main__":
    raise SystemExit(main())
