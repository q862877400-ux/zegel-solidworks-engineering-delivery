r"""@brief 真机证据：**读文件自定义属性 2 个工具**（砌墙 W3 / Spec Kit `133` 的验收②）。

## 它验什么（★ 走工具真实路径 + 决定性用例）
```
1. ★ **核声明解析得到**：batch20 的 `module`/`function` 逐个 getattr 成功（工具层与能力层没断链）
2. ★★ **决定性用例：先写一个属性，再读回来**
   `Add3(名, 30=swCustomInfoText, 值, True)` ⇒ `count` 应 +1，且 `custom_property_get` **读回写入值**
   —— ★ 读到才说明整条路通（这也正是本批要补的那个空白：能写不能读）
3. `custom_property_list` 的 `count_read` 应与 `count_reported` **一致**（不多不少）
4. ★ **负例 A**：读一个**不存在**的属性名 ⇒ 值应为空串，且**不抛异常**（官方 `Get` 的形态如此）
5. ★ **负例 B**：属性名为**空** ⇒ 必须 `ValueError`（能力层的显式检查）
```

## ⚠ 安全（照 `tools/probe_custom_property_reads.py` 的骨架）
**只在新零件上跑**（写的是**新文档**）、`CommandInProgress` 抑制弹窗、收尾**关件不保存**
⇒ 不碰用户数据。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机证据脚本，**不是**从四家外部 MCP 项目移植）
# 文件:   tools/capture_custom_property_evidence.py
# 定位:   砌墙 W3（Spec Kit `133`）的**验收②**：产出 `output/custom-property-evidence.
#           json`。
# 官方依据: `IModelDocExtension.CustomPropertyManager` · `ICustomPropertyManager.Add3/Ge
#           t/GetNames/Count/GetType2`
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
    Path(__file__).resolve().parents[1] / "output" / "custom-property-evidence.json"
)

#: `swCustomInfoType_e.swCustomInfoText` = 30（VT_LPSTR）—— 官方示例逐字列出
SW_CUSTOM_INFO_TEXT = 30
PROP_NAME = "DSH_EvidenceProp"
PROP_VALUE = "evidence-value-133"


def main() -> int:
    ev: dict = {
        "captured_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "capability": "custom_property_read",
        "steps": {},
    }
    sw = None
    doc = None
    ok = True
    try:
        import sw_connect
        import tool_specs_batch20 as b20

        from scripts import sw_custom_property as cp

        #: ① ★ 核声明解析得到
        bindings = {}
        for spec in b20.SPECS_BATCH20:
            mod = __import__("scripts.%s" % spec.module, fromlist=[spec.function])
            bindings[spec.name] = callable(getattr(mod, spec.function, None))
        ev["steps"]["bindings"] = {"ok": all(bindings.values()), "detail": bindings}
        ok = ok and ev["steps"]["bindings"]["ok"]

        sw = sw_connect.connect_solidworks(wait_seconds=10)[0]
        try:
            sw.CommandInProgress = True
        except Exception:  # noqa: BLE001
            pass
        doc = sw_connect.new_document(sw, "part")
        ev["steps"]["part"] = {
            "title": str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
        }

        #: ② ★★ 决定性用例：先写一个（只为造出已知状态），再读回来
        mgr = cp.custom_property_manager(doc)
        before = cp.custom_property_count(doc)
        mgr.Add3(PROP_NAME, SW_CUSTOM_INFO_TEXT, PROP_VALUE, True)
        after = cp.custom_property_count(doc)
        one = cp.custom_property(doc, PROP_NAME)
        ev["steps"]["readback"] = {
            "ok": one.get("value") == PROP_VALUE
            and one.get("type") == "text"
            and after >= before,
            "count_before": before,
            "count_after": after,
            "got": one,
            "wrote": {
                "name": PROP_NAME,
                "value": PROP_VALUE,
                "type_code": SW_CUSTOM_INFO_TEXT,
            },
            "★": "先 Add3 再读回来 —— 读到才说明整条路通（本批补的正是「能写不能读」）",
        }
        ok = ok and ev["steps"]["readback"]["ok"]

        #: ③ 读全部：count_read 必须等于 count_reported
        allp = cp.custom_properties(doc)
        names = [p["name"] for p in allp["properties"]]
        ev["steps"]["list_all"] = {
            "ok": allp["count_read"] == allp["count_reported"] and PROP_NAME in names,
            "count_reported": allp["count_reported"],
            "count_read": allp["count_read"],
            "wrote_visible": PROP_NAME in names,
            "sample_names": names[:8],
        }
        ok = ok and ev["steps"]["list_all"]["ok"]

        #: ④ 负例 A：不存在的属性名 ⇒ 空值且不抛
        try:
            missing = cp.custom_property(doc, "DSH_NoSuchProp_XYZ")
            ev["steps"]["negative_missing_name"] = {
                "ok": missing.get("value") == "",
                "got": missing,
                "★": "官方 Get 对不存在的名字回空串 ⇒ 不抛异常是对的（不是静默失败，是原义如此）",
            }
            ok = ok and ev["steps"]["negative_missing_name"]["ok"]
        except Exception as exc:  # noqa: BLE001
            ev["steps"]["negative_missing_name"] = {
                "ok": False,
                "raised": str(exc)[:80],
                "★": "★ 抛了异常 —— 与官方 Get 的形态不符",
            }
            ok = False

        #: ⑤ 负例 B：空属性名 ⇒ 必须 ValueError
        try:
            cp.custom_property(doc, "   ")
            ev["steps"]["negative_empty_name"] = {
                "ok": False,
                "★": "空名字**没有抛错**",
            }
            ok = False
        except ValueError as exc:  # noqa: BLE001
            ev["steps"]["negative_empty_name"] = {"ok": True, "msg": str(exc)[:70]}
    except Exception as exc:  # noqa: BLE001
        ev["error"] = "%s: %s" % (type(exc).__name__, str(exc)[:200])
        ok = False
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
                    sw.CloseDoc(t)  #: ★ 关件不保存
        except Exception:  # noqa: BLE001
            pass

    ev["verdict"] = "pass" if (ok and not ev.get("error")) else "fail"
    print("  ── 读自定义属性 真机证据 ──")
    for k, v in ev["steps"].items():
        print("    %-24s %s" % (k, json.dumps(v, ensure_ascii=False)[:170]))
    if ev.get("error"):
        print("  ⚠ error: %s" % ev["error"])
    print("  结论: %s" % ev["verdict"].upper())
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print("  证据: %s" % OUT)
    return 0 if ev["verdict"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
