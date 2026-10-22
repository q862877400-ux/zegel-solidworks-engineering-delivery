"""★ 真机：直接读**出厂类型库**里 `AddTemperature` 的真实参数表（`ITypeInfo.GetFuncDesc`）。"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（工具）
# 文件:   tools/probe_typelib_add_loads.py
# 定位:   ★ 2026-10-03（轮 409）承事实 323 的**具体下一步**。
#   ★★ 背景：`AddTemperature` 真机报 `-2147352561`（**缺必填参数**），
#     ★ 而 CHM 那页写的是 **2 参** —— ★ 那页是 **2021 版**，★ 本机是 **2026**。
#   ★ 两条路都试过：★ ① **CHM 的示例代码**（★ 全库只有那一页提到 `AddTemperature(`，
#     示例页没被解出来）；★ ② **反射 dump 与生成的 arity 表**里**都没有这个名字**。
#   ⇒ ★★★ 正解是**第三条路**：★ **直接问 COM 对象要它的 `ITypeInfo`** ——
# ★★ 那就是**出厂类型库本身**（★ 铁律 4：**冲突以出厂类型库为准**），★ 而且它**在运行期
# 可读**。
# 官方依据: `ITypeInfo::GetTypeAttr` / `GetFuncDesc` / `GetNames`（OLE 自动化标准接口）·
#   `ICWLoadsAndRestraintsManager`（cosworks 册）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
#
# ★ 判据：★ 打印每条 `Add*` 的**形参名与个数** —— ★ 那比"猜"硬。

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

OUT = Path(
    Path(__file__).resolve().parents[1] / "output" / "typelib-add-loads-evidence.json"
)
WANT = (
    "AddTemperature",
    "AddConvection",
    "AddHeatFlux",
    "AddHeatPower",
    "AddRadiation",
    "AddElasticConnector",
    "AddForce",
    "AddPressure",
    "AddGravity",
)


def main() -> int:
    import sw_connect
    from scripts import sw_simulation as sim
    from scripts.sw_part import (
        current_sketch_name,
        end_sketch,
        extrude_boss,
        sketch_corner_rectangle,
        start_sketch,
    )

    ev: dict = {"methods": {}, "at": time.strftime("%Y-%m-%dT%H:%M:%S")}
    sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
    doc = None
    try:
        doc = sw_connect.new_document(sw, "part")
        start_sketch(doc, plane_name="Front Plane")
        sketch_corner_rectangle(doc, -20.0, -15.0, 20.0, 15.0)
        sk = current_sketch_name(doc, "")
        end_sketch(doc)
        extrude_boss(doc, sk, 20.0)
        sim.create_static_study(sw, "DSH-TLB", study_type=3)
        mgr = sim._loads_and_restraints_manager(sim.get_study_by_name(sw, "DSH-TLB"))
        ev["manager"] = type(mgr).__name__

        #: ★ 第一版写 `GetTypeInfo()`（无参）⇒ 报 `-2147352565 无效索引`
        #:   （动态 dispatch 对象的常见形态）⇒ 显式传索引与 LCID。
        ole = mgr._oleobj_
        ev["typeinfo_count"] = int(ole.GetTypeInfoCount())
        ti = ole.GetTypeInfo(0, 0)
        attr = ti.GetTypeAttr()
        ev["func_count"] = int(attr.cFuncs)
        for i in range(int(attr.cFuncs)):
            try:
                fd = ti.GetFuncDesc(i)
                names = ti.GetNames(fd.memid)
            except Exception:  # noqa: BLE001
                continue
            if not names:
                continue
            nm = names[0]
            if nm in WANT or nm.startswith("Add"):
                #: ★ `names[0]` 是方法名，后面依次是形参名（★ 官方类型库给的）
                ev["methods"][nm] = {
                    "params": list(names[1:]),
                    "param_count": len(names) - 1,
                }
        ev["verdict"] = "pass" if ev["methods"] else "partial"
        ev["note"] = (
            "★ 直读**出厂类型库**（`ITypeInfo`）—— ★ 铁律 4 说冲突时以它为准，"
            "★ 而它**在运行期可读** ⇒ 比 CHM（2021 版）与离线 dump 都硬。"
        )
        OUT.write_text(
            json.dumps(ev, ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
        for k in sorted(ev["methods"]):
            m = ev["methods"][k]
            print(
                "  %-24s %d \u53c2  %s"
                % (k, m["param_count"], ", ".join(m["params"])[:96])
            )
        print(
            "  \u5171 %d \u4e2a\u65b9\u6cd5 \u00b7 产物: %s" % (len(ev["methods"]), OUT)
        )
    finally:
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        if doc is not None:
            t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
            if t:
                sw.CloseDoc(t)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
