"""★ 给足超时 + 正确网格尺寸，验 `analysis_run_readback` 的「跑求解」能不能算出结果。

（★ 处置 SPEC `202-user-coverage-gaps` 的 SC-004：★ 第 3 条候选 `analysis_run_readback`）
"""
# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身 + SolidWorks 官方文档（本机 `C:\swapi\types\`）
# 文件:   `tools/capture_mesh_solve_evidence.py`（★ 本探针照它的流程写 —— ★ 照 AGENTS.md 的
#         「按 ToolSpec 的契约调，别手调内部实现」）· `tools/capture_simulation_evidence.py`
#         （★ **它才是跑通的那条链**） · `scripts/sw_simulation.py` · `scripts/sw_isolate.py`
# 定位:   ★★★ **第四版（★ 2026-10-04）—— 前三版都栽在同一个前提上，而那个前提是错的**：
#     | 版本 | element_size | 单元数 | 求解读数 |
#     |---|---|---|---|
#     | ①（T_RUN=300） | 4.9339（默认，**正确**）| **7310** | ★ **1 秒 · 4 张图**（★ 成功）|
#     | ② 12.0 mm     | 退化 ⇒ 静默退回默认 | 7250 | 无结果 |
#     | ③ 20.0 mm     | 退化 ⇒ 静默退回默认 | 7250 | 无结果 |
#     ★★ **⇒ 真因（本版据此改写，★ 且它推翻了 `capabilities.yaml` 的一段措辞）**：
#     ① `create_mesh` 的 `element_size` **吃毫米** —— ★ 证据：`capture_simulation_evidence.py`
#        传 **4.9339** ⇒ **7310 单元**（那才是"正确网格"）；
#     ② ★★ 而 `capabilities.yaml` 把 **7250 单元那一次**记成了「`run_analysis` 进入求解即挂
#        （timed_out=True · 300 s）」—— ★ 而**同一份证据**（`output/mesh-solve-evidence.json`，
#        `captured_at: 2026-10-02T23:50:18`）逐字写着 `timed_out=False` · `wall_seconds=1.5`
#        ⇒ ★★★ **7250 那一次没挂，只是**没有结果**（网格退化 ⇒ 无解）** ——
#        ★ 而它是**上一版手工把 4930.5 喂进去**造成的（4.9 米一个单元 > 零件 100 mm）✓
#     ③ ★ 真正 `timed_out=True` 的是 **element_size=4.9339** 那一次，而**那一次网格是对的**
#        ⇒ 求解**真的在算**（观察窗：建立刚度矩阵 · 已用 33 分钟 · 自由度 30,456 · 7250 单元）✓
#     ★★★★ **⇒ 故本版做三件事**：① `element_size` **照 `units=-1` 的原值喂**（4.9339）；
#     ② `T_RUN` 300 s → **1800 s**；③ **求解后轮询 `Results`**（★ 求解可能异步 ——
#     ★ 而"算完了"的判据是**结果读数**、不是返回码）✓
#   ★★★ **判据（★ 含几何/结果读数）**：★ ① `element_count`（网格读数）·
#     ★ ② `results_present` / `plot_count` / `plot_names`（★ **解算结果读数**）·
#     ★ ③ `timed_out` · ★ ④ `wall_seconds` ✓
#   ★★★★★★ **⚠⚠ 第六版（本版）—— 上一版把整机内存打爆了，★ 事故与修法都记在这里**：
#     ★ **事故**：第五版用一个"自校准"循环挑候选（`units=2/-1/0` 各读一次，取第一个过闸的）
#       ⇒ ★★ 而当时那道闸**只判一侧**（只拒"单元尺寸大于零件最大边"）
#       ⇒ ★ 于是它把 `units=2` 回的**米**级值 **0.0049** 当成毫米选了 ⇒
#       ⇒ 求解进程 `cwbcbfmesh.exe` 实测 **38.5 GB 工作集 / 52.6 GB 提交**
#         （整机 63.8 GB、剩余 5.7 GB）⇒ **整机卡死、SolidWorks 无响应** ✓
#     ★ **修法（两层，都已落地）**：
#       ① ★★★ `scripts/sw_simulation.py::check_mesh_size_sane` **改成双侧** ——
#          新增「太小 ⇒ 预估求解内存超预算就拒」，★ 两个系数**各有出处**：
#          · 每 **2,000,000** 自由度 **1 GB** RAM —— 官方逐字（`c_Analysis_Solvers.htm`）✓
#          · 每单元 **4.2** 自由度 —— 事实 293 的进度窗（30,456 / 7,250 = 4.2）✓
#          · 预算默认 = min(物理内存一半, 16 GB)，★ 可用 `memory_budget_gb` 覆盖 ✓
#          负例自证 `tests/test_mesh_size_memory_gate.py`（**6 passed**）：
#          ★ 正例逐字就是**事故里那个数** 0.0049 ⇒ 必须拒；★ 跑通的 4.9339 ⇒ 必须放行 ✓
#       ② ★ 本探针的候选循环**沿用那道闸** ⇒ 现在 0.0049 会在**建网格之前**被拒 ✓
#     ★★★ **教训（可复用）**：★ **"自校准"这类循环必须配一条双侧判据** ——
#       单侧判据会把"另一侧的离谱值"当成合法解，★ 而它比"判不出来"更危险（会真跑下去）✓
#   ★★★★★★★ **只报不动**：★ 不改仓 · ★ 只写 `output/` · ★ 关掉**自己开的**那份文档 ✓
#   许可:   本仓库 MIT。★ 无第三方代码引入。
#   覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

REPO = Path(Path(__file__).resolve().parents[1])
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

OUT = REPO / "output" / "analysis-run-long-timeout-evidence.json"
#: ★ 带时间戳的唯一名（★ 本仓逐字：「算例**重名**会让计数回读取不到」）✓
STUDY = "SPEC202_LongSolve_%d" % int(time.time())
T_RUN = 1800.0        # ① 300 s → 1800 s
T_MESH = 600.0
#: ★ 2026-10-04（第十版）：★ **建网格这一步单独用一个更短的上限** —— ★ 真机实测它**卡过 9 分钟**
  #: 没回来（内存平稳、SW `Not Responding`）⇒ ★ 为了"探得动"，这一步**有界在 5 分钟**：
  #: ★ 到点就**杀子进程并如实报 `timed_out`**（★ 那本身就是一条可用结论）✓
T_MESH_SAFE = 300.0
#: ③ 求解后轮询：★ 每 15 s 读一次 `Results`，最多 40 次（10 分钟）
POLL_EVERY, POLL_MAX = 15.0, 40


def main() -> int:
    ev: dict = {"★_目的": "给足超时 + **正确网格尺寸**，验「跑求解」能不能算出结果",
                "★_T_RUN_秒": T_RUN,
                "★_根因假设": "create_mesh 的 element_size 吃**毫米**；"
                              "mesh_size_report(units=-1) 回的是**米** ⇒ 上一版喂 4930.5 毫米 = 4.9 米/单元",
                "★_前情": "① element_size=4.9339(mm) ⇒ 7310 单元 ⇒ 求解 1 秒出 4 张图（跑通）"
                          "；② element_size=4930.5 ⇒ 退化退回默认 7250 单元 ⇒ 结果为空"
                          "；③ 真正 timed_out=True 的那次网格是对的（观察窗：建立刚度矩阵 33 分钟）",
                "steps": {}}
    doc = None

    def flush() -> None:
        """★ **每一步都落盘**（★ 第八版新增）—— ★ 上一版挂住时 `ev` 还在内存里、**读数全丢** ✓"""
        OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str),
                       encoding="utf-8")

    try:
        import sw_connect
        from scripts import sw_part, sw_simulation as sim
        from scripts.sw_isolate import run_isolated

        sw = sw_connect.connect_solidworks(wait_seconds=30)[0]
        try:
            sw.CommandInProgress = True
        except Exception:                                             # noqa: BLE001
            pass

        #: ① 造零件 + 材料 + 研究 + 夹具 + 载荷（★ 这些不弹框 ⇒ 留父进程）
        doc = sw_connect.new_document(sw, "part")
        ev["steps"]["doc"] = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
        sw_part.start_sketch(doc, plane_name="Front Plane")
        sw_part.sketch_corner_rectangle(doc, -50.0, -30.0, 50.0, 30.0)
        sk = sw_part.current_sketch_name(doc)
        sw_part.end_sketch(doc)
        sw_part.extrude_boss(doc, sk, 20.0)
        sim.set_material(doc, "AISI 1020")
        material = str(sw_connect.safe_get_com_member(doc, "MaterialIdName") or "")
        sim.ensure_simulation_addin(sw)

        sim.create_static_study(sw, STUDY)
        study = sim.get_study_by_name(sw, STUDY)
        if study is None:
            raise RuntimeError("按名字取不到研究 %r" % STUDY)
        #: ★★★★★ 2026-10-04（第十一版）**修正夹具/载荷的面选择 —— 这是那条弹窗的根因**：
        #:   ★ 原文用的是**裸坐标** `select_face_at(0,0,-0.02)` / `select_face_at(0,0,0)`，
        #:     而本文件自己的注释（`sw_simulation.select_face_at` 的来源块）逐字记着真机实测：
        #:       `SelectByID2("", "FACE", 0, 0, 0, …)`      → 计数 **0**（★ 原点在**实体内部**）
        #:       `SelectByID2("", "FACE", 0, 0, -0.02, …)`  → 计数 **1** ✓
        #:   ★★ 于是**力的那一步是加在空选区上的** ⇒ 载荷建成也无效 ⇒ Simulation 弹
        #:     「**未定义载荷或规定的位移** … 固定-刚性零件上的载荷将不处于活动状态」⇒
        #:     `RunAnalysis` 回 0 而 `Results` 为空 ⇒ ★ **整条链白跑**（三次都栽在这）✓
        #:   ⇒ ★ 现在**不再用坐标**：按**声明式选择器**（`-z` 固定 / `+z` 施力）选面，
        #:     并且两个 apply **都会拒绝空选区**（★ 那条判据终于被执行了）✓
        sim.apply_fixed_restraint(study, model=doc, face_selector="-z")
        sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
        sim.apply_normal_force(study, 100.0, model=doc, face_selector="+z")
        #: ★★ **证前读数**：载荷与夹具到底建成了几条、各是什么（★ 以前这里什么都没记）
        try:
            _mgr = sim._loads_and_restraints_manager(study)
            _cnt = int(sw_connect.safe_get_com_member(_mgr, "Count") or 0)
            _items = []
            for _i in range(_cnt):
                try:
                    _it = sw_connect.safe_get_com_member(_mgr, "GetLoadsAndRestraints", _i,
                                                         sw_connect.out_i4())
                    _items.append({"name": str(sw_connect.safe_get_com_member(_it, "Name") or ""),
                                   "type": sw_connect.safe_get_com_member(_it, "Type"),
                                   "entities": sw_connect.safe_get_com_member(_it, "EntityCount"),
                                   "state": sw_connect.safe_get_com_member(_it, "State")})
                except Exception as exc:                                   # noqa: BLE001
                    _items.append({"error": "%s: %s" % (type(exc).__name__, str(exc)[:60])})
            ev["steps"]["loads_and_restraints"] = {"count": _cnt, "items": _items}
        except Exception as exc:                                           # noqa: BLE001
            ev["steps"]["loads_and_restraints"] = {"error": "%s: %s" % (type(exc).__name__,
                                                                       str(exc)[:120])}
        print("  [1e] 夹具/载荷读数: %s" % str(ev["steps"]["loads_and_restraints"])[:220])
        flush()
        ev["steps"]["setup"] = {"material": material, "study": STUDY}

        def iso(fn: str, args: list, kwargs: dict, timeout: float) -> dict:
            t0 = time.time()
            r = run_isolated("scripts.sw_simulation_worker", fn,
                             args=args, kwargs=kwargs, timeout=timeout)
            r["wall_seconds"] = round(time.time() - t0, 1)
            return r

        #: ② ★★★ **单位口径：本探针不再"假设"，改成"三个单位各读一次 + 用几何闸选"** ——
        #:     ★★ 第五版（本版）的**实测起点**（第四版的负结果，★ 已落盘）：
        #:     `mesh_size_report(study, units=-1)` 在本机回 **4930.501659457233**，
        #:     ★★ **不是** `sw_simulation.py` 注释里那个"跑通"的 **4.933908705960544**
        #:     ⇒ ★ 两处记录**差 ~1000×**、且**官方页没写单位** ⇒ ★ 按铁律 5：**不猜**，
        #:     改成**当场把三个单位都读出来**（-1 / 0=SI / 2=Metric），★ 全部记进证据 ✓
        #:   ★★★ **选哪个**：★ 用**几何判据**（`check_mesh_size_sane`：单元尺寸不得大于零件最大边）
        #:     —— ★ 它是**既有的那道闸**、且与本探针的零件尺寸直接相关
        #:     ⇒ ★ 候选按「更像毫米」排序，**取第一个过闸的**；★ 三个都不过就**停下报事实** ✓
        #:   ★★★★ **先等 SolidWorks 闲下来**（★ 第十版新增）：★ 真机实测（2026-10-04）——
        #:     ★ 刚把 SW 拉起来那几秒它自己在忙 ⇒ ★ **忙检把三次读数全拒了**（★ 假警报）
        #:     ⇒ ★ 故用**有界**的 `wait_until_idle`（★ 事实 526 纪律：不做无界等待）✓
        from sw_busy import wait_until_idle

        idle = wait_until_idle(timeout=90, interval=3.0)
        ev["steps"]["wait_until_idle"] = idle
        flush()
        print("  [1a] 等 SolidWorks 空闲: idle=%s waited=%ss attempts=%s"
              % (idle.get("idle"), idle.get("waited"), idle.get("attempts")))
        if not idle.get("idle"):
            raise RuntimeError("SolidWorks 一直忙 ⇒ 停下（★ 忙时下发调用会卡死，事实 526）：%s"
                               % idle.get("reason"))
        reading: dict = {}
        for u in (-1, 0, 2):
            r = iso("mesh_size_by_name", [STUDY], {"units": u}, 120)
            got = (r.get("result") or {}) if isinstance(r.get("result"), dict) else {}
            if got.get("blocked") == "SOLIDWORKS_BUSY":
                #: ★ 忙拒绝 ⇒ **等一下重试一次**（★ 那是设计好的拒绝，不是能力坏了）
                wait_until_idle(timeout=60, interval=3.0)
                r = iso("mesh_size_by_name", [STUDY], {"units": u}, 120)
                got = (r.get("result") or {}) if isinstance(r.get("result"), dict) else {}
                if got.get("blocked") == "SOLIDWORKS_BUSY":
                    raise RuntimeError("忙检两次都拒 ⇒ 停下（★ 不硬闯，事实 526）：%s"
                                       % got.get("error"))
            reading["units=%d" % u] = {"ok": r.get("ok"), "timed_out": r.get("timed_out"),
                                       "result": r.get("result")}
            print("  [1] units=%-3d element_size=%r tolerance=%r"
                  % (u, got.get("element_size"), got.get("tolerance")))

        #: ★ 候选：每个都是「**值 + 与之配套的单位口径**」的一对（★ 口径写在名字里）——
        #:   ★★★ 真机对照（`tools/probe_mesh_profile_matrix.py` 四档）把这件事**钉死了**：
        #:     `units=2`（Metric=**毫米**）+ `element_size=4.9305` ⇒ 网格 **7250 单元 / 1.1 s** ✓
        #:     ★ 而 `units=0`（**SI=米**）+ 同一个 `4.9305` ⇒ 单元 = **4.93 米** ⇒ 比零件还大
        #:     ⇒ ★★ **网格退化 ⇒ `CreateMesh` 回 `rc=8` / 0 单元**（★ 那正是本探针先前"建不出来"的根源）✓
        #:   ⇒ ★ 故候选必须是 `(标签, 值, 容差, **units**)` 四元组，★ 且**选中的 units 原样传给 create_mesh** ✓
        cands: list[tuple[str, float, float, int]] = []
        for u in (2, -1, 0):
            got = (reading.get("units=%d" % u) or {}).get("result") or {}
            s, t = got.get("element_size"), got.get("tolerance")
            if s is None:
                continue
            s, t = float(s), float(t or 0.0)
            if u == 2:
                cands.append(("units=2 原值", s, t, 2))
            if u == -1:
                cands.append(("units=-1 ÷1000 配 units=2", s / 1000.0, t / 1000.0, 2))
                cands.append(("units=-1 原值 配 units=0", s, t, 0))
            if u == 0:
                cands.append(("units=0 ×1000 配 units=2", s * 1000.0, t * 1000.0, 2))
        chosen, sane, tried = None, None, []
        for label, s, t, u_used in cands:
            chk = sim.check_mesh_size_sane(doc, s)
            tried.append({"候选": label, "element_size": s, "tolerance": t, "units": u_used,
                          "sane": chk.get("ok"), "reason": chk.get("reason")})
            print("      [候选] %-16s element_size=%-12.4f units=%-3s sane=%s %s"
                  % (label, s, u_used, chk.get("ok"), str(chk.get("reason"))[:56]))
            if chk.get("ok"):
                chosen, sane = (label, s, t, u_used), chk
                break
        ev["steps"]["mesh_size"] = {
            "readings": reading, "候选": tried,
            "★_选中": chosen[0] if chosen else None,
            "★_选中的 units": chosen[3] if chosen else None,
            "★": "★ 官方**没写单位** ⇒ 三个单位各读一次 + 用几何闸选（★ 不许隐式换算）；"
                 "★★ **选中的 units 必须原样传给 create_mesh** —— 值与其单位口径要配套 ✓",
        }
        ev["steps"]["mesh_size_sane"] = sane
        #: ★ 把**内存预算与预估**一并落进证据（★ 事后能看出"当时放行时预估是多少"）
        ev["★_内存预算_GB"] = sane.get("memory_budget_gb")
        flush()
        ev["★_预估求解内存_GB"] = sane.get("est_ram_gb")
        flush()
        ev["★_预估单元数"] = sane.get("est_elements")
        flush()
        if not chosen:
            raise RuntimeError("三个单位口径的读数都不合理 ⇒ 停下报事实（不猜单位）")
        element_size, tolerance, mesh_units = chosen[1], chosen[2], chosen[3]
        print("  [1b] ★ 选中 %s ⇒ element_size=%.4f · tolerance=%.4f · **units=%d**（max_dim=%s）"
              % (chosen[0], element_size, tolerance, mesh_units, sane.get("max_dim")))

        #: ③ ★★★ **建网格之前先按官方那几条"降规模"的旋钮设一遍**（★ 第七版 · 本轮新增）——
        #:   ★★ 真因（★ 官方手册给了机制）：★ **曲率自适应网格器会在高曲率处自动加密**，
        #:     而加密下界由 **`MinElementSize`** 定、**不由全局 `element_size` 定**
        #:     ⇒ ★ 这解释了"同一名义单元尺寸，一条链 7250 单元/1.4 s、另一条 40 GB" ✓
        #:   ★ 逐条取值与依据：
        #:     · `Quality = 0`（`swsMeshQualityDraft`）—— 官方：draft「**does not have midside
        #:       nodes**」⇒ 线性四面体 ⇒ 节点/DOF 大降；★ **代价**：官方说 draft 是给"quick
        #:       evaluation"用的 ⇒ 弯曲为主的问题该换机器/换求解器，**不该**靠 draft 蒙；
        #:     · `MesherType = 0`（`swsMesherTypeStandard`）—— 避开曲率自适应自动加密；
        #:     · `MinElementSize = element_size/2`、`MaxElementSize = element_size*2` —— 官方逐字：
        #:       「For this option to have effect, **h_min < h < h_max**」⇒ 给上**上下界**才管得住；
        #:     · `MinElementsInCircle = 4` —— 官方的曲率密度旋钮（"minimum number of elements
        #:       that fit in a hypothetical circle"），★ 越小越省 ✓
        #:   ⚠ ★ **不改** `NumberOfLoops` / `AutomaticLooping2` —— ★ 它们的语义**未查证**
        #:     （铁律 5：查不到就别动）✓
        #:   ★★ **第七版（实测后修正）—— 只设两个"枚举"旋钮，不碰带单位的 Double**：
        #:     ★ 只读实测（`output/mesh-settings-readonly-evidence.json`）拿到的**出厂默认**是：
        #:       `Quality=1`（High）· **`MesherType=2`（`AlternateCB` = 曲率自适应）** ·
        #:       `ElementSize=0` · **`MinElementSize=0`** · `MaxElementSize=0` ·
        #:       `ElementSizeFactorForEachLoop=0.8` · `MinElementsInCircle=8` ·
        #:       `NumberOfLoops=3` · `AutomaticLooping2=False` ✓
        #:     ★★★ **这就是"同一 `element_size` 两条链差别巨大"的机制**（★ 官方逐字）：
        #:       `c_meshing_options.htm`「**Curvature-based mesher** — Creates **more elements in
        #:       higher-curvature areas automatically**」+ `c_Element_Size_in_Curvature_Based_Mesher.htm`
        #:       「the element size is determined … by the **minimum number of elements that fit in
        #:       a hypothetical circle**」·「For this option to have effect, **h_min < h < h_max**」
        #:       ⇒ ★★ **加密下界 `MinElementSize` 出厂是 0（=没有下界）** ⇒ ★ 曲率自适应**可以无限
        #:       细化**、而**全局 `element_size` 管不住它** ✓
        #:     ⚠ ★ **为什么不设 `MinElementSize`**（★ 第六版在这里栽过）：★ 它的**单位口径未定**
        #:       （只读实测回的是 `0.0` ⇒ 定不了）；★ 我上一轮按毫米写了 `2.465` ⇒
        #:       ★★ **探针在 SW 里卡了 13 分钟、SW 主线程 `Not Responding`** ✓
        #:       ⇒ ★ 按铁律 5：**不猜单位** —— ★ 先只用两个**枚举**旋钮（`Int32`，**无单位风险**）：
        #:         · `Quality = 0`（`swsMeshQualityDraft`）⇒ 线性四面体（无中间节点）⇒ DOF 大降；
        #:         · `MesherType = 0`（`swsMesherTypeStandard`）⇒ **避开曲率自适应自动加密** ✓
        #: ★★ **读写都走隔离层**（★ 第六版的教训）：非隔离调用一旦把 SW 带进长计算，
        #:   ★ 主进程被杀之后 **SW 自己还在烧 CPU**（实测：`Not Responding` + 每个 6 秒吃 1 核）
        #:   ⇒ ★ **凡可能在 SW 侧触发计算的调用，一律经 `run_isolated`**（可杀）✓
        ms_r = iso("mesh_settings_by_name", [STUDY], {}, 180)
        before_settings = ms_r.get("result") if isinstance(ms_r.get("result"), dict) else {}
        ev["steps"]["mesh_settings_before"] = {**ms_r, "result": before_settings}
        ev["steps"]["mesh_settings_before"] = before_settings
        print("  [1c] 改动前的网格设置：Quality=%s MesherType=%s MinElementSize=%s "
              "MaxElementSize=%s MinElementsInCircle=%s ElementSize=%s"
              % (before_settings.get("Quality"), before_settings.get("MesherType"),
                 before_settings.get("MinElementSize"), before_settings.get("MaxElementSize"),
                 before_settings.get("MinElementsInCircle"), before_settings.get("ElementSize")))
        cfg_r = iso("configure_mesh_settings_by_name", [STUDY],
                    {"quality": 0, "mesher_type": 0}, 300)
        cfg = cfg_r.get("result") if isinstance(cfg_r.get("result"), dict) else {}
        #: ⚠ ★ **不设** `min_element_size` / `max_element_size` / `min_elements_in_circle` ——
        #:   ★ 前两个是**带单位的 Double**、口径未定（见上）；★ 后一个虽是无量纲 Int32，
        #:   但它属于**曲率自适应那条路**，而本版已把 `MesherType` 换成 Standard ⇒ 先不动它 ✓
        ev["steps"]["mesh_settings_configure"] = {**cfg_r, "result": cfg}
        flush()
        print("  [1d] 设网格旋钮: ok=%s changed=%s"
              % (cfg.get("ok"), [c["name"] for c in cfg.get("changed") or []]))

        #: ④ ★★★★ **建网格 —— 走"唯一推荐入口"**（★ 第九版 · 本轮把整条链收进一个能力）：
        #:   `create_mesh_safely` 一次做七件事：① 量预算前置闸 → ② **网格安全档**
        #:   （关曲率自适应 + Draft）→ ③ 建网格 → ④ 读**真节点数** → ⑤ 求解前内存闸 →
        #:   ⑥ **还原网格设置**（★ 不离开用户的模型）→ ⑦ 回可入证据的报告 ✓
        #:   ★ 而且 worker 入口**先过忙检** ⇒ ★ SolidWorks 忙时**一个 COM 调用都不发** ✓
        mesh_r = iso("create_mesh_safely_by_name", [STUDY],
                     {"units": mesh_units, "element_size": element_size,
                      "tolerance": tolerance},
                     T_MESH_SAFE)
        mesh_safe = mesh_r.get("result") if isinstance(mesh_r.get("result"), dict) else {}
        ev["steps"]["create_mesh"] = {k: mesh_r.get(k) for k in
                                      ("ok", "timed_out", "wall_seconds", "error")}
        ev["steps"]["create_mesh"]["result"] = mesh_safe
        flush()
        mesh_res = mesh_safe.get("mesh") if isinstance(mesh_safe.get("mesh"), dict) else {}
        print("  [2] 建网格(安全入口): ok=%s timed_out=%s wall=%ss blocked=%s"
              % (mesh_r.get("ok"), mesh_r.get("timed_out"), mesh_r.get("wall_seconds"),
                 mesh_safe.get("blocked")))
        print("      element_count=%s node_count=%s ⇒ %s"
              % (mesh_safe.get("element_count"), mesh_safe.get("node_count"),
                 mesh_safe.get("★_结论")))
        if mesh_safe.get("blocked"):
            raise RuntimeError("安全入口**拒了**（★ 这是设计好的拒绝、不是失败）：%s ⇒ %s"
                               % (mesh_safe["blocked"], mesh_safe.get("reason")))
        after_settings = mesh_safe.get("after_settings") or {}
        ev["steps"]["mesh_settings_after"] = after_settings
        flush()
        print("      ★ 真实读数：ElementCount=%s **NodeCount=%s** Quality=%s"
              % (after_settings.get("ElementCount"), after_settings.get("NodeCount"),
                 after_settings.get("Quality")))

        #: ⑤ ★★★ **跑求解前的第二道闸**（★ 优先用**真节点数** ⇒ DOF≈3×节点数）——
        #:   ★ `check_mesh_size_sane` 只能按**包围盒**估；★ 这里用**真实读数**
        #:   ⇒ ★★ **内存超预算就绝不进求解**（★ 官方：内存不够会走 out-of-core、极慢）
        #:   ★★★ 2026-10-04（第十三版）：★ 先把**本研究的求解器**读出来一起交给闸门 ——
        #:     ★ 因为那条换算「每 2e6 自由度 1 GB」**逐字出自 FFEPlus**，
        #:     而真机跑的是 **`Intel Direct Sparse`** ⇒ ★ **不能当同一把尺子**（★ 结果里会写明）✓
        _solver = sim.static_solver_type_report(study)
        ev["steps"]["solver_type"] = _solver
        flush()
        print("  [2a] 本研究求解器: ok=%s value=%s name=%s%s"
              % (_solver.get("ok"), _solver.get("value"), _solver.get("name"),
                 ("（读不到：%s）" % _solver.get("reason"))[:80] if not _solver.get("ok") else ""))
        pre = sim.solve_memory_preflight(int(mesh_res.get("element_count") or 0),
                                        node_count=int(after_settings.get("NodeCount") or 0) or None,
                                        solver_name=_solver.get("name"))
        ev["steps"]["solve_memory_preflight"] = pre
        print("  [2b] 求解前内存闸: ok=%s est_dof=%s est_ram_gb=%s budget=%s"
              % (pre.get("ok"), pre.get("est_dof"), pre.get("est_ram_gb"),
                 pre.get("memory_budget_gb")))
        if not pre.get("ok"):
            raise RuntimeError("求解前内存闸不放行 ⇒ 停下（★ 不拿内存去赌）：%s" % pre.get("reason"))

        #: ⑥ ★★ 跑求解 —— 本探针的核心（★ T_RUN=1800）✓
        run_r = iso("run_analysis_by_name", [STUDY], {}, T_RUN)
        run_res = run_r.get("result") if isinstance(run_r.get("result"), dict) else {}
        ev["steps"]["run_analysis"] = {k: run_r.get(k) for k in
                                       ("ok", "timed_out", "wall_seconds", "error")}
        ev["steps"]["run_analysis"]["result"] = run_r.get("result")
        print("  [3] 跑求解: ok=%s **timed_out=%s** wall=%ss"
              % (run_r.get("ok"), run_r.get("timed_out"), run_r.get("wall_seconds")))
        print("      results_present=%s plot_count=%s"
              % (run_res.get("results_present"), run_res.get("plot_count")))

        #: ⑤ ★★★ **轮询结果读数**（★ 求解可能异步 ⇒ 判据是**结果**、不是返回码）
        poll = []
        if not run_res.get("results_present"):
            for i in range(POLL_MAX):
                time.sleep(POLL_EVERY)
                try:
                    res = sw_connect.safe_get_com_member(study, "Results")
                    cnt = None
                    if res is not None:
                        cnt = sw_connect.safe_get_com_member(res, "GetPlotCount")
                    poll.append({"i": i + 1, "elapsed_s": round((i + 1) * POLL_EVERY, 1),
                                 "results_present": res is not None, "plot_count": cnt})
                    print("      [poll %d] +%ss results=%s plot_count=%s"
                          % (i + 1, round((i + 1) * POLL_EVERY, 1), res is not None, cnt))
                    if res is not None and int(cnt or 0) > 0:
                        break
                except Exception as exc:                              # noqa: BLE001
                    poll.append({"i": i + 1, "error": str(exc)[:120]})
                    break
        ev["steps"]["results_poll"] = poll

        #: ⑥ ★ 终局回读：★ **重用契约里那一条**（`run_analysis_by_name` 走 `run_analysis_report`）
        #:   —— ★ **不自己搓读数器**（★ 它复跑一次 `RunAnalysis` 只为回读 `Results`/图数，
        #:   而求解已完成 ⇒ 秒级返回）✓
        final_r = iso("run_analysis_by_name", [STUDY], {}, 600)
        final_res = final_r.get("result") if isinstance(final_r.get("result"), dict) else {}
        ev["steps"]["final_readback"] = {k: final_r.get(k) for k in
                                         ("ok", "timed_out", "wall_seconds", "error")}
        ev["steps"]["final_readback"]["result"] = final_r.get("result")
        print("      [终局回读] results_present=%s plot_count=%s"
              % (final_res.get("results_present"), final_res.get("plot_count")))
        evi = sim.collect_study_evidence(sw)
        ev["steps"]["collect_evidence"] = {
            "ok": isinstance(evi, dict) and int(evi.get("study_count") or 0) >= 1,
            "study_count": evi.get("study_count"),
            "names": [s.get("name") for s in (evi.get("studies") or [])],
        }

        #: ⑦ 判据汇总
        plot_count = run_res.get("plot_count")
        if plot_count in (None, 0) and poll:
            plot_count = poll[-1].get("plot_count")
        #: ★ 终局回读优先（★ 它跑在轮询之后、读数最新）
        if final_res.get("plot_count") not in (None, 0):
            plot_count = final_res.get("plot_count")
        ev["★_timed_out"] = run_r.get("timed_out")
        flush()
        ev["★_element_count"] = mesh_res.get("element_count")
        flush()
        ev["★_results_present"] = bool(run_res.get("results_present")
                                       or final_res.get("results_present")
                                       or (poll and poll[-1].get("results_present")))
        flush()
        ev["★_plot_count"] = plot_count
        flush()
        ev["★_ok"] = bool(ev["★_results_present"] and int(plot_count or 0) > 0)
        flush()
        ev["★_判据"] = ("★ ① element_count（网格读数）② results_present/plot_count/plot_names"
                        "（**解算结果读数**）③ timed_out ④ wall_seconds")
        flush()
    except Exception as exc:                                          # noqa: BLE001
        ev["★_异常"] = "%s: %s" % (type(exc).__name__, str(exc)[:240])
        flush()
    finally:
        try:
            import sw_connect
            if doc is not None:
                sw_connect.safe_get_com_member(doc, "ClearSelection2", True)
                t = str(sw_connect.safe_get_com_member(doc, "GetTitle") or "")
                if t:
                    sw.CloseDoc(t)                                    #: ★ 只关自己那份
        except Exception:                                             # noqa: BLE001
            pass

    OUT.write_text(json.dumps(ev, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print("★ ★_timed_out =", ev.get("★_timed_out"), "· ★_element_count =", ev.get("★_element_count"),
          "· ★_results_present =", ev.get("★_results_present"), "· ★_plot_count =", ev.get("★_plot_count"),
          "· ★_ok =", ev.get("★_ok"))
    print("★ wrote", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
