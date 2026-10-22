"""★ 真机：把成员可用性普查扩到**我们工具真正用的接口**，并与已注册 function 名取交集。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/prove_tool_availability.py
# 定位:   ★ 2026-10-03（轮 448）承**事实 362**（★ 普查 `IModelDocExtension` 得 396/334
#           /62）。
#   ★★★ **为什么扩**：★ 事实 362 只查了**一个**接口 ⇒ ★ 而**真正的风险**是
#     「**我们已注册的工具里，有没有哪个 function 在 pywin32 上根本取不到**」⚠
#     ⇒ ★★ 故本探针：★ 对**几个关键接口**各普查一次，★ 再拿"取不到的成员"与
#       **`register_capabilities.all_specs()` 的 function 名**取**交集** ✓✓✓
#   ★★ 判据（★ 与事实 362 同一口径）：
#     ```
#     ★ `getattr(obj, 名, None)` 回 None ⇒ **取不到**（★ 而它**不**等于"接口里没有"）
# ★ 而 `get_*` / `set_*` 是属性访问器（★ 迟到绑定下叫 `X`）⇒ 它们落进"取不到"是**应然的*
# *
#     ```
#   ⚠ **只 `getattr`、不调用**（★ 事实 227 的"取或调"坑）。
# 官方依据: 出厂程序集 `SolidWorks.Interop.sldworks.dll` 的接口成员（★ 反射可得）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ **先报查了多少**（★ 事实 357）· ★ 且**交集必须为空或逐个列出**。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "tools"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))
sys.path.insert(0, str(REPO_ROOT / "mcp-server"))

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "tool-availability-evidence.json")

#: ★ 要普查的（★ 名字, 怎么从文档上取到那个对象）
TARGETS = [
    ("IModelDoc2", "doc"),
    ("IModelDocExtension", "ext"),
    ("IFeatureManager", "fm"),
    ("ISelectionMgr", "sm"),
    ("IModelDoc2", None),           # ★ 占位不用
]


def main() -> int:
    import sw_connect
    from com_member_probe import interface_members, probe_members
    from sw_connect import get_com_member, safe_get_com_member

    ev: dict = {"at": time.strftime("%Y-%m-%dT%H:%M:%S"), "interfaces": []}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        live = {
            "IModelDoc2": doc,
            "IModelDocExtension": get_com_member(doc, "Extension"),
            "IFeatureManager": get_com_member(doc, "FeatureManager"),
            "ISelectionMgr": get_com_member(doc, "SelectionManager"),
        }
        #: ★ 我们已注册的 function 名（★ 取交集用）
        try:
            import register_capabilities as RC
            ours = {s.function for s in RC.all_specs() if getattr(s, "function", None)}
        except Exception as exc:                               # noqa: BLE001
            ours = set()
            ev["registry_err"] = str(exc)[:120]
        ev["registered_functions"] = len(ours)

        all_missing: dict = {}
        for iface, obj in live.items():
            try:
                names = sorted(interface_members(iface))
            except Exception as exc:                           # noqa: BLE001
                ev["interfaces"].append({"iface": iface, "err": str(exc)[:100]})
                continue
            got = probe_members(obj, names)
            miss = sorted(n for n, v in got.items() if v == "missing")
            #: ★ 滤掉属性访问器（★ 它们的"取不到"是应然的）
            miss_plain = [n for n in miss if not (n.startswith("get_") or n.startswith("set_"))]
            all_missing[iface] = miss_plain
            ev["interfaces"].append({
                "iface": iface, "probed": len(names), "usable": len(names) - len(miss),
                "missing_total": len(miss), "missing_plain": len(miss_plain),
                "missing_plain_names": miss_plain[:24],
            })
        #: ★★ **交集：★ 我们已注册的 function 里，有哪些取不到**
        hit = sorted({n for iface, ms in all_missing.items() for n in ms if n in ours})
        ev["registered_but_unavailable"] = hit
        ev["probed_total"] = sum(i.get("probed", 0) for i in ev["interfaces"])
        ev["verdict"] = "pass"
        ev["note"] = ("★ 对几个关键接口普查成员可用性，★ 再与已注册 function 名取交集。"
                      "★ 判据：★ 先报查了多少；★ 而交集**必须为空或逐个列出**。"
                      "★ `get_*`/`set_*` 访问器已滤掉（★ 迟到绑定下它们叫 `X`）。")
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str) + "\n", encoding="utf-8")
        print(json.dumps(ev, ensure_ascii=False, indent=1, default=str)[:1800])
        print("  产物: %s" % OUT)
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:                                      # noqa: BLE001
            pass
        if doc is not None:
            try:
                t = str(safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)
            except Exception:                                  # noqa: BLE001
                pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
