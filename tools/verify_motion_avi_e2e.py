r"""@brief 验收命令：`animation_export` 的真机端到端 —— **导出出非零 AVI**。

## 为什么需要它
`capabilities.yaml` 的 `animation_export` 现在是 `stitched`：API 链已真机验证，
但**没有**「导出出非零文件」的证据（空装配体导不出 ⇒ 判据如实留空）。
本脚本补那条证据：**造一个真有动画的装配体** → `Calculate` → `SaveToAVI` → 检查文件非零。

## 步骤（每步都打印，失败也能定位）
1. 建**圆柱零件**（`create_basic_part`）并保存到 temp；
2. 建**装配体**，把同一个零件插入**两次**（一个当静止轴、一个当被驱动转子）；
3. `GetMotionStudyManager` → `CreateMotionStudy`；
4. `add_constant_speed_rotary_motor_by_cylinders`（用两个组件的圆柱面）；
5. `Calculate`；
6. `CreateAVIParameter` → `SaveToAVI` → **看文件大小**（⚠ 不看返回值）。

# ── 来源 ──
# 仓库:   本项目自身（真机验收）
# 文件:   tools/verify_motion_avi_e2e.py
# 定位:   `capabilities.yaml` 的 `animation_export` 条目里 `evidence` 字段要指向的命令。
# 官方签名依据: `IMotionStudy::SaveToAVI` / `IMotionStudyManager::CreateAVIParameter` /
#         `IAVIParameter`（swmotionstudy 官方反射）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机；**只用自己新建的文档**；收尾恢复 CommandInProgress 并关自己的文档。
# ─────────────────────────────────────────────────────────────────────────
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
import time
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
for _p in (str(_REPO), str(_REPO / "scripts")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
sys.stdout.reconfigure(encoding="utf-8")

from scripts import (
    sw_assembly,  # noqa: E402
    sw_part,  # noqa: E402
)
from scripts import sw_motion as M  # noqa: E402
from scripts.sw_connect import (  # noqa: E402
    connect_solidworks,
    get_com_member,
    new_document,
    save_document,
)

OUT = Path(Path(__file__).resolve().parents[1] / "output" / "motion-avi-evidence.json")


# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机验收脚本 · 整个文件的执行体）
# 文件:   tools/verify_motion_avi_e2e.py → step() 与 main()
# 定位:   `capabilities.yaml` 的 `animation_export` 条目里 `evidence` 指向的就是本脚本。
#         端到端：建圆柱零件 → 装配体插两次 → Motion 算例 → 匀速旋转马达 →
#         `Calculate` → **挑出「含马达」的那个算例** → `SaveToAVI` → **检查文件非零**。
# 覆盖:   后续同级定义
#         ⚑ 用这个标记是因为本文件就是「下列 N 个薄封装/步骤逐一对应同一份签名来源」的
#           成组声明 —— 逐个 def 贴重复的块是噪声（`check_provenance.py` 的 `GROUP_MARK`
#           用途原文如此）。⚠ 此前我**逐个 def 贴重复块**，是**不知道有这两个作用域标记**
#           （另一个是 `覆盖: 全文件`）⇒ 读门禁的源码才知道。
# ⚠⚠ **为什么曾经报「N 行无出处」**：本文件的来源块原本写在 **module docstring 里**，
# 而 `check_provenance._module_docstring_lines()` 会把 docstring **整段跳过** ⇒ 不算覆盖
# 。
# ⚠ 全部调用照**项目既有封装**的官方签名（铁律 4，先核实再写）：
#   `sw_part.sketch(model, plane)` · `sw_part.sketch_circle(model, cx, cy, radius)` ·
#   `sw_part.extrude_boss(model, sketch_name, depth)` ·
# `sw_connect.save_document(model, path)` · `sw_assembly.add_component(asm, path, x, y,
# z, sw=)`
# ⚠ 反射核实过的签名：`IAssemblyDoc::AddComponent5(String, Int32, String, Boolean, Strin
# g,
#   Double, Double, Double)`（8 参）· `IModelDoc2::SaveAs3(String, Int32, Int32)`（3 参）·
#   `IMotionStudyManager::{GetMotionStudy(String), ActivateMotionStudy(String),
#   CreateAVIParameter()}` · `IMotionStudy::SaveToAVI(String, AVIParameter)`。
# ⚠ 真机实测出的两个关键事实（写进证据文件）：
#   • `create_motion_study` 返回的算例**可能不是**马达所在的那个（实测并列出现两个：
#     「运动算例 1」duration=0.0/无马达 与「运动算例 2」duration=4.0/motor_count=1）
#     ⇒ **必须按「含马达」挑**，否则导的是空算例；
#   • `SaveToAVI` **返 `True` 也可能产出 0 字节文件**（「返回码撒谎」）⇒ 判据只看文件。
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 连真机；只用自己新建的文档；收尾恢复 CommandInProgress。
# ────────────────────────────────────────────────────────────────────
#: ★★ 2026-10-01（轮 288）：`step()` **把异常记进证据**（不只打到 stdout）。
#:   ★ 旧行为：异常只 `print` 到屏幕 ⇒ 证据 JSON 里**只剩 `ok: false`** ⇒
#:   ★★ 那是**判据不够细**（事实 220 的线索：“哪一环、什么错”才是下一步要的）。
#:   ★★★ 现在每个 `step` 的异常（类名 + 消息）都进 `STEP_ERRORS`，下面写证据时一并落盘。
STEP_ERRORS: dict = {}


def step(label, fn):
    try:
        v = fn()
        print("   %-46s ⇒ %r" % (label, v))
        return v
    except Exception as exc:  # noqa: BLE001
        STEP_ERRORS[label] = "%s: %s" % (type(exc).__name__, str(exc)[:220])
        print("   %-46s ⇒ ✗ %s: %s" % (label, type(exc).__name__, str(exc)[:110]))
        return None


def main() -> int:
    sw, _m, _meta = connect_solidworks(wait_seconds=20, return_metadata=True)
    sw.CommandInProgress = True
    opened = []
    ev: dict = {
        "started": time.strftime("%Y-%m-%d %H:%M:%S"),
        "verdict": "unknown",
        "steps": {},
    }
    try:
        # ① 圆柱零件（半径 20mm / 高 100mm）
        # ⚠ 所有调用都照**项目既有封装的官方签名**（铁律 4）：
        #   `sw_part.sketch(model, plane)` · `sketch_circle(model, cx, cy, r)` ·
        # `extrude_boss(model, sketch_name, depth)` · `sw_connect.save_document(model, p
        # ath)`
        part_path = os.path.join(tempfile.gettempdir(), "mcp_avi_shaft.SLDPRT")
        print("=== ① 建圆柱零件 ===")
        part = new_document(sw, doc_type="part")
        ptitle = get_com_member(part, "GetTitle")
        opened.append(ptitle)
        ev["steps"]["part"] = {"title": str(ptitle)}
        #: ★★★ 2026-10-07（规格 216 T-216-07m）**修掉建件写法** —— ★ 这是本脚本长期失败
        #: 的**真因**：
        #:   ★ 原来写的是 `sk = sw_part.sketch(part, "Front Plane")`（**没有 `with`**）+
        #:     `sketch_circle(part, 0, 0, 0.02)`（**0.02 是"米"口径的数**）✗
        #:   ★★ 而 `sw_part.sketch()` 是**上下文管理器**（不进入它 ⇒ 草图没开），
        #: 且**本模块的长度单位就是毫米**（★ 它自己的 docstring 逐字警告「不要写 `mm(25)
        #: `」）⇒
        #:   ★★★ 后果：★ 挤出的**不是有效圆柱** ⇒ 真机逐字
        #:     「`add_constant_speed_rotary_motor_by_cylinders` ⇒ ✗ RuntimeError:
        #:        未找到圆柱面: mcp_avi_shaft-1, **radius=[0.0, inf]**」——
        #:     ★ `radius=[0.0, inf]` **就是退化的证据**（没有有效圆柱面）✓
        #: ★★ 于是本脚本历史上把「**建件写错了**」记成了「**马达建不出**」（★ 台账轮 288
        #:  那条链）✗
        #:   ⇒ ★ 修法：★ 用 **`with`** + ★ **毫米数**（★ 与规格 216 的探针同一写法）✓
        with sw_part.sketch(part, "Front Plane") as sk:
            step(
                "sw_part.sketch_circle(0, 0, r=20) [毫米]",
                lambda: sw_part.sketch_circle(part, 0.0, 0.0, 20.0),
            )
        step(
            "sw_part.extrude_boss(part, sk, 40) [毫米]",
            lambda: sw_part.extrude_boss(part, sk, 40.0),
        )
        step(
            "save_document(part, %s)" % os.path.basename(part_path),
            lambda: save_document(part, part_path),
        )

        # ② 装配体 + 两次插入（用项目既有封装，不自己拼 AddComponent5）
        print()
        print("=== ② 建装配体并插入两次 ===")
        asm = new_document(sw, doc_type="assembly")
        atitle = get_com_member(asm, "GetTitle")
        opened.append(atitle)
        ev["steps"]["assembly"] = {"title": str(atitle)}
        c1 = step(
            "sw_assembly.add_component(第 1 个, x=0)",
            lambda: sw_assembly.add_component(asm, part_path, x=0.0, sw=sw),
        )
        c2 = step(
            "sw_assembly.add_component(第 2 个, x=0.06)",
            lambda: sw_assembly.add_component(asm, part_path, x=0.06, sw=sw),
        )

        # ③ Motion
        print()
        print("=== ③ Motion 类型库 + manager + 算例 ===")
        step("ensure_motion_type_library()", lambda: M.ensure_motion_type_library())
        mgr = step(
            "get_motion_study_manager(asm)", lambda: M.get_motion_study_manager(asm)
        )
        if mgr is None:
            ev["verdict"] = "fail: 拿不到 MotionStudyManager"
            return 2
        study = step("create_motion_study(asm)", lambda: M.create_motion_study(asm))
        if study is None:
            ev["verdict"] = "fail: 建不了算例"
            return 2

        # ⚠⚠ **算例类型**（2026-10-01 轮 66 从**反射**查到官方取值表）：
        #   `swMotionStudyType_e`（`enum_swmotionstudy.txt`）：
        #     swMotionStudyTypeAssembly           = **1**
        #     swMotionStudyTypePhysicalSimulation = 2
        #     swMotionStudyTypeCosmosMotion       = **4**  ← 真正的 Motion 分析
        # swMotionStudyTypeLegacyCosmosMotion = 8 · swMotionStudyTypeNewCosmosMotion = 1
        # 6
        # ⚠ 此前实测拿到的一直是 **1（Assembly）** —— 那是 `create_motion_study` 的默认
        # 。
        #   ★★ **轮 66 逐值实测出的可行性矩阵**（`D:\AI\SW\probe_motion_addin.py`）：
        #     set StudyType=1（Assembly）            ⇒ 回读 **1** ✅ **生效**
        #     set StudyType=2（PhysicalSimulation）  ⇒ 回读 **2** ✅ **生效**
        #     set StudyType=4 / 8 / 16（CosmosMotion 家族）⇒ 回读 2 ❌ **静默失败**
        #   且 **Motion 加载项 4 个 ProgID 全返 None** ⇒ 本机**没有**真正的 Motion 分析。
        # ⇒ 本脚本用**能生效的 2（PhysicalSimulation）**（此前一直用默认的 1，**从没试过
        #  2**）。
        print()
        print(
            "=== ③b ★ 用 PhysicalSimulation(2) 类型的算例（1/2 是实测能生效的两个）==="
        )
        study2 = step(
            "create_motion_study(asm, study_type=2)",
            lambda: M.create_motion_study(
                asm, name="MCP_AVI_PhysSim", duration=4.0, study_type=2
            ),
        )
        if study2 is not None:
            back = step(
                "study2.StudyType（回读，应 2）",
                lambda: M.motion_member(study2, "StudyType"),
            )
            study = study2
            ev["steps"]["study_type"] = 2
            ev["steps"]["study_type_readback"] = back

        # ④ 马达（需要两个组件的圆柱面）
        print()
        print("=== ④ 加匀速旋转马达（两个组件各取一个圆柱面）===")
        motor = None
        if c1 is not None and c2 is not None:
            motor = step(
                "add_constant_speed_rotary_motor_by_cylinders(...)",
                lambda: M.add_constant_speed_rotary_motor_by_cylinders(
                    study, c1, c2, rpm=60.0
                ),
            )
        ev["steps"]["motor"] = {"ok": motor is not None}

        # ⑤ Calculate
        print()
        print("=== ⑤ Calculate ===")
        step(
            "calculate_and_play(study, play=False)",
            lambda: M.calculate_and_play(study, play=False),
        )
        step(
            "collect_motion_study_summary(asm)",
            lambda: M.collect_motion_study_summary(asm),
        )

        # ⑥ 导出（**判据看文件，不看返回值**）
        print()
        print("=== ⑥ ★★ SaveToAVI → 看文件大小 ===")
        # ⚠⚠ **关键修正**（2026-10-01 轮 64 实测）：`create_motion_study` 建的那个算例
        #   可能**不是**马达所在的那个 —— 实测出现两个算例：
        #     运动算例 1（duration=0.0 · motor_count=0）  ← create_motion_study 返回的
        # 运动算例 2（duration=4.0 · motor_count=1 · 有 AEMRotationalMotor）← **马达在这
        # 里**
        #   ⇒ **先按「有马达」挑出真正有动画的那个算例**，再导（否则导的是空算例）。
        target = study
        print("   ── 先挑出「有马达」的算例 ──")
        summary = step(
            "collect_motion_study_summary(asm)",
            lambda: M.collect_motion_study_summary(asm),
        )
        if summary:
            with_motor = [
                s
                for s in summary.get("studies", [])
                if (s.get("motor_count") or 0) > 0
                or (s.get("motion_feature_count") or 0) > 0
            ]
            if with_motor:
                name = with_motor[-1]["name"]
                print(
                    "   ⇒ 挑中: %r（motor_count=%s · features=%s）"
                    % (
                        name,
                        with_motor[-1].get("motor_count"),
                        [
                            f.get("name")
                            for f in with_motor[-1].get("motion_features") or []
                        ],
                    )
                )
                target = (
                    step(
                        "mgr.GetMotionStudy(%r)" % name,
                        lambda: M.motion_member(mgr, "GetMotionStudy", name),
                    )
                    or study
                )
                step(
                    "mgr.ActivateMotionStudy(%r)" % name,
                    lambda: M.motion_member(mgr, "ActivateMotionStudy", name),
                )
                ev["steps"]["target_study"] = name
            else:
                print("   ⚠ 没有任何算例含马达 ⇒ 仍用 create_motion_study 返回的那个")

        param = step("create_avi_parameter(mgr)", lambda: M.create_avi_parameter(mgr))
        if param is not None:
            step(
                "configure(FramePerSecond=10, SaveEntireAnimation=True)",
                lambda: M.configure_avi_parameter(
                    param, FramePerSecond=10.0, SaveEntireAnimation=True
                ),
            )
        out = os.path.join(tempfile.gettempdir(), "mcp_avi_e2e.avi")

        # ⚠ 第 4 次尝试（事实 53：同一处连修 ≥3 次要回退 ⇒ **这是最后一次**）。
        #   两个最可能的前提一起补上：
        #   ① **装配体要有磁盘路径**（Motion 导出可能要求文档已保存）；
        #   ② **先真的 Play 一遍**（让渲染管线跑起来，而不只是算完）。
        print("   ── 补两个前提：保存装配体 + Play 一遍 ──")
        asm_path = os.path.join(tempfile.gettempdir(), "mcp_avi_asm.SLDASM")
        step(
            "save_document(asm, %s)" % os.path.basename(asm_path),
            lambda: save_document(asm, asm_path),
        )
        step(
            "calculate_and_play(target, play=True)",
            lambda: M.calculate_and_play(target, play=True),
        )

        if os.path.isfile(out):
            os.remove(out)
        res = step(
            "export_motion_study_avi(target, out, param)",
            lambda: M.export_motion_study_avi(target, out, param),
        )
        ev["steps"]["export"] = res or {}
        if res:
            print()
            print(
                "   ★ 文件存在=%s · 大小=%s 字节 · 官方返回=%r"
                % (res["exists"], res["size_bytes"], res["returned"])
            )
            ev["verdict"] = (
                "pass"
                if res["ok"]
                else (
                    "fail: 导出未产生非零文件（exists=%s size=%s returned=%r）"
                    % (res["exists"], res["size_bytes"], res["returned"])
                )
            )
        else:
            ev["verdict"] = "fail: export 抛异常"
        return 0 if ev["verdict"] == "pass" else 1
    finally:
        ev["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    #: ★★ 2026-10-01（轮 288）：把 `step()` 捕到的**每一环异常**也写进证据
    #:   —— 旧行为只把它们 print 到屏幕，于是证据里只剩 `ok: false`。
    if STEP_ERRORS:
        ev["step_errors"] = dict(STEP_ERRORS)
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(
            json.dumps(ev, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        for t in reversed(opened):
            try:
                if t:
                    sw.CloseDoc(t)
            except Exception:  # noqa: BLE001
                pass
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass
        print()
        print("  证据已写: %s" % OUT)
        print("  verdict: %s" % ev["verdict"])
        print("收尾完成（文档未保存；CommandInProgress 已恢复）")


if __name__ == "__main__":
    raise SystemExit(main())
