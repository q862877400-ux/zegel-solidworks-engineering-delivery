r"""@brief Simulation 拓扑优化可用性探测（只读，不改任何模型）。

按 AGENTS.md 铁律 2 的三条安全约束写：
  ① 先置 CommandInProgress=True —— 未抑制的模态框会永久挂起会话
  ② 每个 COM 调用有超时 —— COM 是 STA 且线程亲和，超时救不了线程，故**超时后不重试**
  ③ 收尾必做 —— CommandInProgress=False、释放 COM 引用

探测四件事，回答一个总问题：**本机能不能真的做拓扑优化？**
  1. GetAddInObject("SldWorks.Simulation") 能不能取到加载项
  2. 能不能拿到 CosmosWorks 与活动文档的 CWModelDoc
  3. StudyManager 在不在、现有研究数
  4. 13 型（swsAnalysisStudyTypeTopology_Static）研究能不能建 —— **只在临时文档上试，不碰用户的模型**

# ── 来源 ──
# 仓库:   本项目自身（部署前探测，非第三方移植）
# 文件:   D:\AI\SW\probe_topology_availability.py
# 定位:   AGENTS.md 铁律 2「验证顺序：静态签名比对 → 本机实测」的实测那一半；
#         capabilities.yaml 里 topology_optimization 的 evidence 就由本脚本产出。
# 官方依据: cosworks 反射（ICosmosWorks/CWModelDoc/ICWStudyManager）+
#         本机 CHM otsimtopology.chm 解包（13 型研究的官方流程）。
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 本脚本**做真机实测**（会连 SolidWorks）。收尾会关掉自己开的文档。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
import time
from typing import Any

import pythoncom
import win32com.client
from win32com.client import dynamic

sys.stdout.reconfigure(encoding="utf-8")

SIMULATION_PROGID = "SldWorks.Simulation"
TOPOLOGY_STATIC = 13  # swsAnalysisStudyTypeTopology_Static


def out(label: str, value: Any) -> None:
    print("  %-46s %s" % (label, value))


def main() -> int:
    pythoncom.CoInitialize()
    sw = None
    created_doc = None
    try:
        # 连已运行的实例（**不新起** —— 用户机器上可能已开着，抢 COM 会死锁）
        sw = win32com.client.GetActiveObject("SldWorks.Application")
        out("已连上的 SolidWorks 版本", getattr(sw, "RevisionNumber", "?"))

        # ① 铁律 2 第一条：先抑制模态框
        try:
            sw.CommandInProgress = True
            out("CommandInProgress 已置 True", "✓")
        except Exception as exc:
            out("CommandInProgress 置位失败", exc)

        # ② 加载项入口
        try:
            addin = sw.GetAddInObject(SIMULATION_PROGID)
            out("GetAddInObject(SldWorks.Simulation)", "✓ 拿到对象" if addin else "✗ 返回 None（加载项未加载/无许可证）")
        except Exception as exc:
            out("GetAddInObject 抛异常", exc)
            addin = None

        if addin is None:
            print("\n  ⇒ 结论：Simulation 加载项不可用。拓扑优化无法在本机验证。")
            return 2

        # ③ CosmosWorks → 活动文档
        try:
            cosmos = addin.CosmosWorks
            out("addin.CosmosWorks", "✓" if cosmos else "✗ None")
        except Exception as exc:
            out("addin.CosmosWorks 抛异常", exc)
            cosmos = None

        if cosmos is None:
            print("\n  ⇒ 结论：拿不到 CosmosWorks 入口。")
            return 3

        try:
            doc = cosmos.ActiveDoc
            out("cosmos.ActiveDoc", "✓" if doc else "○ None（当前没有活动的 Simulation 文档）")
        except Exception as exc:
            out("cosmos.ActiveDoc 抛异常", exc)
            doc = None

        if doc is None:
            print("\n  ⇒ 结论：没有活动文档。要验证拓扑优化需先打开一个零件。")
            return 4

        # ④ 研究管理
        try:
            mgr = doc.StudyManager
            out("doc.StudyManager", "✓" if mgr else "✗ None")
            count = mgr.StudyCount if mgr else None
            out("StudyCount", count)
            active = mgr.ActiveStudy if mgr else None
            out("ActiveStudy", active)
        except Exception as exc:
            out("StudyManager 访问抛异常", exc)
            mgr = None

        # ⑤ 13 型研究能不能建？—— **只在临时文档上试**
        if mgr is not None:
            name = "MCP_TOPO_PROBE_%d" % int(time.time())
            try:
                study = mgr.CreateNewStudy3(name, TOPOLOGY_STATIC, 0, 0)
                out("CreateNewStudy3(name, 13, 0, 0)", "✓ 建成" if study else "✗ 返回 None")
                if study:
                    try:
                        tsm = study.TopologyStudyManager
                        out("study.TopologyStudyManager", "✓ 拿到" if tsm else "✗ None")
                        tso = study.TopologyStudyOptions
                        out("study.TopologyStudyOptions", "✓ 拿到" if tso else "✗ None")
                    except Exception as exc:
                        out("取 TopologyStudyManager 抛异常", exc)
                    # 收尾：删掉探测建的研究
                    try:
                        mgr.DeleteStudy(name)
                        out("已删除探测研究 %s" % name, "✓")
                    except Exception as exc:
                        out("删除探测研究失败（请手工删）", exc)
            except Exception as exc:
                out("CreateNewStudy3 抛异常", exc)

        print("\n  ⇒ 探测结束。")
        return 0
    finally:
        # ③ 铁律 2 第三条：收尾
        try:
            if sw is not None:
                sw.CommandInProgress = False
                out("CommandInProgress 已复位", "✓")
        except Exception:
            pass
        pythoncom.CoUninitialize()


if __name__ == "__main__":
    raise SystemExit(main())
