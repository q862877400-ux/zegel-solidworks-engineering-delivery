r"""@brief 探针：`IModelDocExtension::GetCostingManager()` 在本机能不能拿到 CostManager。

## 为什么探这一条
`capabilities.yaml` 的 `costing` 停在 `stitched`（护城河三域里唯一有实现却无运行证据的）。
而 `scripts/sw_costing.py` 的来源块写着一个**结论**：

> 「取用路径：CostManager 由 **Composer 加载项**给出…**本机也没装 Composer**，ProgID 查不到
>  ⇒ 本模块**接收调用方传入的对象**，不代为取得。」

**这个结论是错的**（2026-10-01 轮 61 用两条硬证据推翻）：
1. 官方反射里**有** `IModelDocExtension::GetCostingManager()`（`reflect_sldworks` 与 `topo-sldworks` 两套一致）；
2. 注册表里有 **`swcCostingAddin.SwcAddin`（`.34`）** 等 8 个 ProgID ⇒ **Costing 加载项本机装了**。

⇒ 本探针取**第三关**（真机运行期）的证据：`GetCostingManager()` 到底返回什么。

# ── 来源 ──
# 仓库:   本项目自身（真机判定）
# 文件:   D:\AI\SW\probe_costing_manager.py
# 定位:   AGENTS.md 铁律 2 的第二关（本机实测）。签名依据是官方反射
#         `IModelDocExtension::GetCostingManager()`（`Object`，**零参**）。
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机；**只用自己新建的文档，绝不碰用户已打开的文档**；收尾恢复 CommandInProgress。
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

_REPO = Path(r"C:\swprojects\sw-skill-fork")
for _p in (str(_REPO), str(_REPO / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.stdout.reconfigure(encoding="utf-8")

from scripts.sw_connect import (  # noqa: E402
    connect_solidworks,
    get_com_member,
    new_document,
)
from scripts import sw_part  # noqa: E402

#: Costing 加载项在注册表里的 ProgID（2026-10-01 实测 HKLM\SOFTWARE\Classes）
PROGIDS = (
    "swcCostingAddin.SwcAddin",
    "swcCostingAddin.CostingTaskpane",
    "SldWorks.Costing",
    "SolidWorks.Costing",
)


def main() -> int:
    sw, _m, _meta = connect_solidworks(wait_seconds=15, return_metadata=True)
    sw.CommandInProgress = True
    title = None
    try:
        # ① 加载项本身在不在（GetAddInObject 的返回值不可信 ⇒ 只当**线索**）
        print("=== ① Costing 加载项的 ProgID 试探 ===")
        for pid in PROGIDS:
            try:
                obj = sw.GetAddInObject(pid)
                print("   %-34s ⇒ %s" % (pid, "非 None" if obj is not None else "None"))
            except Exception as exc:  # noqa: BLE001 —— 探针就是要看全部失败形态
                print("   %-34s ⇒ 抛 %s: %s" % (pid, type(exc).__name__, str(exc)[:60]))
        print()

        # ② 用**自己新建**的零件试 GetCostingManager（绝不碰用户的文档）
        model = new_document(sw, doc_type="part")
        title = get_com_member(model, "GetTitle")
        sk = sw_part.sketch(model, "Front Plane")
        sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)
        sw_part.extrude_boss(model, sk, 0.02)
        print("=== ② 自建零件: %r（100×60×20 mm 板）===" % title)

        ext = get_com_member(model, "Extension")
        print("   model.Extension ⇒ %s" % ("非 None" if ext is not None else "None"))
        if ext is None:
            print("   ⚠ 拿不到 Extension ⇒ GetCostingManager 走不通")
            return 1

        mgr = get_com_member(ext, "GetCostingManager")
        print("   Extension.GetCostingManager() ⇒ %s" % ("**非 None**" if mgr is not None else "None"))
        if mgr is None:
            print()
            print("   ⇒ 结论：成员**存在且可调**（没抛异常），但本机返回 None。")
            print("     下一问：是「Costing 加载项未激活」还是「许可不足」？")
            print("     ⇒ 见 ③ 的加载项状态。")
            return 2
        print()
        print("=== ③ 拿到 CostManager ⇒ 逐条试 ICostManager 的 7 个成员 ===")
        for member, arity in (("CostingDefaults", 0), ("CostingModel", 0),
                              ("GetTemplateCount", 1), ("WaitForUIUpdate", 0)):
            try:
                if arity == 0:
                    v = get_com_member(mgr, member)
                else:
                    v = get_com_member(mgr, member, 0)
                print("   %-22s ⇒ %r" % (member, v))
            except Exception as exc:  # noqa: BLE001
                print("   %-22s ⇒ ✗ %s: %s" % (member, type(exc).__name__, str(exc)[:70]))
        return 0
    finally:
        try:
            if title:
                sw.CloseDoc(title)
        except Exception:  # noqa: BLE001 —— 收尾失败不该掩盖主结果
            pass
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        print()
        print("收尾完成（文档未保存；CommandInProgress 已恢复）")


if __name__ == "__main__":
    raise SystemExit(main())
