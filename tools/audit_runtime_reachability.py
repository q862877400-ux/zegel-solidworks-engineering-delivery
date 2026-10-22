"""@brief 运行期可达性审计：`scripts/` 用到的 COM 成员，在**活着的对象**上取得到吗？

## 为什么需要它（本项目已证实的盲区）
**已知事实 28**：`IModeler` 的 14 个曲面创建入口，反射里**全都有**，
但**运行期只有 5 个可取**；`CreatePlanarSurface` / `CreateLine` 取到 `None`
（调用报含混的 `'NoneType' object is not callable`），`CreatePoint` / `CreateBodyFromSurf`
**成员不存在**，`CreateBsplineSurface` **服务器异常 `0x80010105`**。

**⇒ 而判据 A5（`docs/signature-audit.md`「每个 COM 调用的参数顺序与类型与官方签名对齐」）
只覆盖了**签名层**。签名对齐了、成员却取不到，一样跑不了。**
**⇒ 本工具补上另一半：运行期可达性。**

## 它做什么（以及**不**做什么）
| 做 | 不做 |
|---|---|
| 静态抽出 `scripts/` 里所有 `get_com_member(obj, "成员")` 的**成员名** | **不**做数据流分析（不判「哪个调用点用的是哪个对象」）—— 那需要类型推断，本工具不假装能做 |
| 在一组**声明好的规范对象**上逐个 `getattr`，看是否拿到可调用成员 | **不**保证对象集完整 ⇒ 报「不可达」时**同时报我试了哪些对象**，由人判是不是我漏了对象 |
| 输出「在所有试过的对象上都取不到」的成员清单 | **不**调用任何方法（只 `getattr`，**零副作用**）|

**⚠ 判据的诚实边界**：本工具报的「不可达」= **「在我试过的 N 个对象上都取不到」**，
不是「绝对不存在」。**要定「绝对不存在」得逐个对象穷举** —— 那是另一件事。

## 规范对象集（`OBJECT_BUILDERS`）—— **显式声明，可复核**
覆盖 `scripts/` 最常挂在的几类宿主：`ISldWorks` / `IModelDoc2` / `IPartDoc` /
`IFeatureManager` / `ISketchManager` / `ISelectionManager` / `IModelDocExtension` /
`IModeler` / `ISimulation` 入口。**新增用途时在这里加，不在代码里临时拼。**

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（审计工具，非第三方移植）
# 文件:   tools/audit_runtime_reachability.py
# 定位:   `AGENTS.md` 已知事实 28–31 的**工具化**；判据 A5 的另一半。
#         形状照 `scripts/audit_call_arity.py`（那一个管签名层，本工具管运行层）。
# 官方签名依据: 不适用（本工具**只 getattr，不调方法**）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机（需要活动文档）。**零副作用**：只 `getattr`，不调任何方法、不改模型。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

MEMBER_RE = re.compile(r'get_com_member\(\s*[^,]+,\s*"([A-Za-z_]\w*)"')

#: 会被 `getattr` 但**不是 COM 成员**的假阳性来源（本项目自己的辅助函数名等）
NOT_A_MEMBER = frozenset(
    {
        "X",
        "Y",
        "Z",  # 极短的占位名，几乎必然来自拼接
    }
)


def collect_members(scripts_dir: Path) -> dict[str, list[str]]:
    """返回 ``{成员名: [出现它的文件…]}`` —— 静态抽取，**不判对象**。"""
    found: dict[str, list[str]] = {}
    for path in sorted(scripts_dir.glob("sw_*.py")):
        text = path.read_text(encoding="utf-8", errors="replace")
        for name in MEMBER_RE.findall(text):
            if name in NOT_A_MEMBER:
                continue
            found.setdefault(name, [])
            if path.name not in found[name]:
                found[name].append(path.name)
    return found


def build_objects(sw, model):
    """构造规范对象集。**取不到的记 None 并如实报出**（不假装）。"""
    from scripts.sw_connect import get_com_member

    def safe(obj, name):
        try:
            return get_com_member(obj, name) if obj is not None else None
        except Exception:
            return None

    objs: dict[str, object] = {"ISldWorks": sw, "IModelDoc2": model}
    if model is not None:
        objs["IPartDoc"] = model  # 同一对象，不同接口
        objs["IFeatureManager"] = safe(model, "FeatureManager")
        objs["ISketchManager"] = safe(model, "SketchManager")
        objs["ISelectionManager"] = safe(model, "SelectionManager")
        objs["IModelDocExtension"] = safe(model, "Extension")
        objs["IConfigurationManager"] = safe(model, "ConfigurationManager")
    objs["IModeler"] = safe(sw, "GetModeler")

    # ── Simulation 对象族（2026-10-01 补）────────────────────────────
    # ⚠ 第一版只有上面那 10 个通用对象 ⇒ 424 个成员里 365 个报「不可达」（86%），
    #   **那是假阳性**：这些成员挂在 Simulation 的对象族上，通用对象里没有它们。
    #   **⇒ 本工具的输出上限就是对象集** —— 缺一族就多一片假阳性。
    #   下面这族的构造方式来自本项目**已跑通**的探针
    #   （`probe_topology_loop.py` / `capture_simulation_evidence.py`）。
    try:
        addin = get_com_member(sw, "GetAddInObject", "SldWorks.Simulation")
        objs["ISldWorks.Simulation"] = addin
        cosmos = safe(addin, "CosmosWorks") if addin is not None else None
        objs["ICosmosWorks"] = cosmos
        cw_doc = safe(cosmos, "ActiveDoc")
        objs["ICWModelDoc"] = cw_doc
        mgr = safe(cw_doc, "StudyManager")
        objs["ICWStudyManager"] = mgr
        # 取一个研究（第一个），再挂它的子对象
        study = None
        if mgr is not None:
            try:
                from scripts.sw_connect import out_i4

                # `CWStudy GetStudy(Int32)` —— **只一个参数**（反射与 CHM 一致）
                study = get_com_member(
                    mgr, "GetStudy", 0
                )  # CWStudy GetStudy(Int32) —— 只一个参数
            except Exception:
                study = None
        objs["ICWStudy"] = study
        if study is not None:
            objs["ICWMesh"] = safe(study, "Mesh")
            objs["ICWLoadsAndRestraintsManager"] = safe(
                study, "LoadsAndRestraintsManager"
            )
            objs["ICWTopologyStudyManager"] = safe(study, "TopologyStudyManager")
            objs["ICWTopologyStudyOptions"] = safe(study, "TopologyStudyOptions")
            objs["ICWResults"] = safe(study, "Results")
            objs["ICWSolidManager"] = safe(study, "SolidManager")
    except Exception:
        pass
    return objs


def audit(objs: dict[str, object], members: dict[str, list[str]]) -> dict:
    """对每个成员在**所有**对象上试 `getattr`；只读，零副作用。"""
    reachable: dict[str, list[str]] = {}
    unreachable: dict[str, list[str]] = {}
    obj_names = list(objs)
    for name, files in members.items():
        hits: list[str] = []
        for oname, obj in objs.items():
            if obj is None:
                continue
            try:
                if callable(getattr(obj, name, None)):
                    hits.append(oname)
            except Exception:
                pass
        if hits:
            reachable[name] = hits
        else:
            unreachable[name] = files
    return {
        "objects": {k: (v is not None) for k, v in objs.items()},
        "object_count": len(obj_names),
        "member_count": len(members),
        "reachable_count": len(reachable),
        "unreachable_count": len(unreachable),
        "unreachable": unreachable,
        "reachable_objects": {k: v for k, v in reachable.items() if len(v) == 1},
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="运行期可达性审计（只 getattr，零副作用）")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--out", default="", help="把结果写成 JSON 到这个路径")
    ap.add_argument("--top", type=int, default=40, help="打印多少条不可达")
    args = ap.parse_args()

    members = collect_members(ROOT / "scripts")
    print(
        "静态抽取：`scripts/sw_*.py` 里 get_com_member 用到的成员名 **%d** 个"
        % len(members)
    )
    print(
        "⚠ 本审计的**上限就是对象集**：缺一族对象，那一族的成员就全报「不可达」（假阳性）。"
    )
    print(
        "  2026-10-01 的教训：第一版只有 10 个通用对象 ⇒ 365/424 报不可达（86%），"
        "几乎全是假阳性。"
    )

    from scripts.sw_connect import connect_solidworks, new_document
    from scripts import sw_part

    sw, _m, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
    title = None
    model = new_document(sw, doc_type="part")
    title = __import__(
        "scripts.sw_connect", fromlist=["get_com_member"]
    ).get_com_member(model, "GetTitle")
    # 建一个有特征、有草图的零件（对象集才不会空）
    sk = sw_part.sketch(model, "Front Plane")
    sw_part.sketch_corner_rectangle(model, -0.05, -0.03, 0.05, 0.03)
    sw_part.extrude_boss(model, sk, 0.02)
    print("构造的规范对象集（在零件 %r 上）:" % title)

    # ⚠ 可达性审计的**第二个上限**：对象集依赖**文档状态**。
    #   第一版只建了裸零件 ⇒ `ICWStudy` 取不到 ⇒ 它整族（`ICWMesh` /
    #   `ICWLoadsAndRestraintsManager` / `ICWTopologyStudyManager` / `ICWResults`）
    #   全没建出来，那一族的成员就全报「不可达」（**又一片假阳性**）。
    #   ⇒ **先把研究对象建出来，再构造对象集。**
    try:
        from scripts.sw_connect import out_i4 as _out_i4

        _cosmos = __import__(
            "scripts.sw_connect", fromlist=["get_com_member"]
        ).get_com_member(
            __import__(
                "scripts.sw_connect", fromlist=["get_com_member"]
            ).get_com_member(sw, "GetAddInObject", "SldWorks.Simulation"),
            "CosmosWorks",
        )
        _cwdoc = __import__(
            "scripts.sw_connect", fromlist=["get_com_member"]
        ).get_com_member(_cosmos, "ActiveDoc")
        _mgr = __import__(
            "scripts.sw_connect", fromlist=["get_com_member"]
        ).get_com_member(_cwdoc, "StudyManager")
        _name = "REACH_%d" % __import__("time").time()
        __import__("scripts.sw_connect", fromlist=["get_com_member"]).get_com_member(
            _mgr, "DeleteStudy", _name
        )
        _st = __import__(
            "scripts.sw_connect", fromlist=["get_com_member"]
        ).get_com_member(_mgr, "CreateNewStudy3", _name, 0, 0, _out_i4())
        print("    （已建一个静力学研究以让研究对象存在: %r）" % (_st is not None))
    except Exception as _exc:
        print("    ⚠ 建研究失败（研究对象族将缺失）: %s" % str(_exc)[:70])

    try:
        objs = build_objects(sw, model)
        result = audit(objs, members)
        for k, ok in result["objects"].items():
            print("    %-24s %s" % (k, "✓" if ok else "✗ 取不到"))
        print()
        print(
            "成员总数 %d：**可达 %d**，在试过的对象上都取不到 **%d**"
            % (
                result["member_count"],
                result["reachable_count"],
                result["unreachable_count"],
            )
        )
        print()
        if result["unreachable"]:
            print("=== 在所有试过的对象上都取不到的成员（前 %d）===" % args.top)
            for name in sorted(result["unreachable"])[: args.top]:
                print(
                    "  %-34s 出现在: %s"
                    % (name, ", ".join(result["unreachable"][name][:3]))
                )
            print()
            print(
                "  ⚠ 判据边界：这是「**在我试过的 %d 个对象上**都取不到」，"
                "不是「绝对不存在」。" % result["object_count"]
            )
            print("     要定绝对不存在需逐个对象穷举；本工具不假装能做。")
        if args.out:
            Path(args.out).write_text(
                json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            print("证据已写入 %s" % args.out)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if not result["unreachable"] else 1
    finally:
        try:
            sw.CloseDoc(title)
        except Exception:
            pass


if __name__ == "__main__":
    raise SystemExit(main())
