r"""@brief P1 终局判定：运行期枚举活对象的成员，查三个「看结果」入口是否真的不存在。

背景（静态三源已查完，全部指向「不存在」）：
  - `SolidWorks.Interop.cosworks.dll` 的接口清单：`SmoothedMesh` 0 命中；唯一 Export 方法是
    `ICWStudy.ExportSimulationStudy`（导出研究，非平滑网格）
  - 该 DLL 二进制：`ExportSmoothedMesh` 12 处命中**全是** `swsExportSmoothedMesh_*` **枚举值名**；
    而真方法名（`CreateMassConstraint` 等）在 `#Strings` 堆里各 1 处 ⇒ 对照成立
  - CHM API 参考 2790 页：`Smoothed` 0 命中
  - 枚举确实存在：`swsExportSmoothedMeshError_e`（10 值）/ `swsExportSmoothedMeshOption_e`（3 值）
  - 官方教程描述的是**纯 UI 操作**（右键 Results → View Convergence Data and Graph；
    右键 Material Mass1 → Export Smoothed Mesh）

⇒ 静态三源一致说「无公开 API」。**最后一步是运行期实测**（AGENTS.md 铁律 2 的第二关）：
   枚举活对象的所有成员，看有没有静态没列出来的（迟到绑定下 IDispatch 可能暴露更多）。

# ── 来源 ──
# 仓库:   本项目自身（真机判定）
# 文件:   D:\AI\SW\probe_results_api_surface.py
# 定位:   AGENTS.md 铁律 5「查不到就说查不到」的**取证**动作：三源静态 + 一关运行期，
#         四关都说没有才允许写「查不到」。结论回写 ROADMAP 与 capabilities 的限制项。
# 官方签名依据: D:\AI\SW\_raw\topo-reflect\iface_cosworks.txt（ICWResults 107 成员）
#         + enum_cosworks.txt（swsExportSmoothedMesh*）+ C:\cworks_en\api（2790 页）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机；不保存任何文档。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
import time

sys.path.insert(0, r"C:\swprojects\sw-skill-fork")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.stdout.reconfigure(encoding="utf-8")

from scripts.sw_connect import (  # noqa: E402
    connect_solidworks,
    get_com_member,
    new_document,
    out_i4,
)
from scripts import sw_part  # noqa: E402

WANTED = (
    "smoothed", "smoothmesh", "convergence", "materialmass", "viewconv",
    "exportmesh", "exporttopology", "savemesh", "createmeshbody",
)


def surface(obj, label):
    """列出对象上所有可枚举的成员名（迟到绑定下 dir() 常为空，故多路尝试）。"""
    names: list[str] = []
    for getter in (
        lambda: list(dir(obj)),
        lambda: [d.Name for d in obj._oleobj_.GetTypeInfo().GetTypeAttr() and [] or []],
    ):
        try:
            got = getter()
            if got:
                names.extend(got)
                break
        except Exception:
            continue
    if not names:
        # 迟到绑定下拿不到 → 用 GetIDsOfNames 逐个试探已知候选名
        return None
    return sorted(set(names))


def main() -> int:
    sw, _m, _meta = connect_solidworks(wait_seconds=15, return_metadata=True)
    sw.CommandInProgress = True
    title = None
    try:
        model = new_document(sw, doc_type="part")
        title = get_com_member(model, "GetTitle")
        sk = sw_part.sketch(model, "Front Plane")
        sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)
        sw_part.extrude_boss(model, sk, 0.02)
        doc = get_com_member(get_com_member(sw.GetAddInObject("SldWorks.Simulation"),
                                            "CosmosWorks"), "ActiveDoc")
        mgr = get_com_member(doc, "StudyManager")
        n = "SURFACE_%d" % int(time.time())
        get_com_member(mgr, "DeleteStudy", n)
        study = get_com_member(mgr, "CreateNewStudy3", n, 13, 0, out_i4())
        print("  拓扑研究建成: %r" % (study is not None))
        results = get_com_member(study, "Results")
        print("  study.Results: %r" % (results is not None))
        print()

        for obj, label in ((study, "ICWStudy"), (results, "ICWResults")):
            if obj is None:
                continue
            names = surface(obj, label)
            print("=== %s 的成员 ===" % label)
            if names is None:
                print("  ○ 迟到绑定拿不到 dir()，改用「逐个候选名试探」")
                for w in WANTED:
                    try:
                        get_com_member(obj, w)
                        print("    ✓ 存在: %s" % w)
                    except Exception:
                        pass
            else:
                print("  共 %d 个成员" % len(names))
                hits = [x for x in names if any(w in x.lower() for w in WANTED)]
                print("  与「看结果」相关的: %r" % (hits or "（无）"))
                for kw in ("Export", "Plot", "Result"):
                    sub = [x for x in names if kw in x]
                    print("  含 %-8s 的 %d 个: %r" % (kw, len(sub), sub[:12]))
            print()

        # 直接试探三个目标名（迟到绑定下 GetIDsOfNames 会明确报「未知名称」）
        print("=== 直接试探三个目标成员（无论静态怎么说不存在，都试一次）===")
        for obj, label in ((results, "ICWResults"), (study, "ICWStudy")):
            if obj is None:
                continue
            for cand in ("ExportSmoothedMesh", "GetSmoothedMesh", "ViewConvergenceData",
                         "MaterialMass", "GetMaterialMassPlot", "ExportSmoothedMesh2"):
                try:
                    r = get_com_member(obj, cand)
                    print("  ✓ %s.%s 存在 → %r" % (label, cand, r))
                except Exception as exc:
                    msg = str(exc)
                    tag = "名字不存在" if ("未知" in msg or "unknown" in msg.lower()
                                          or "找不到" in msg or "not found" in msg.lower()) else msg[:50]
                    print("  ✗ %s.%s → %s" % (label, cand, tag))
        return 0
    finally:
        try:
            if title:
                sw.CloseDoc(title)
        except Exception:
            pass
        try:
            sw.CommandInProgress = False
        except Exception:
            pass
        print("收尾完成（文档未保存）")


if __name__ == "__main__":
    raise SystemExit(main())
