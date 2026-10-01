"""修第 5 次同族坑，并**终于**把它做成门禁的明确诊断（上一轮承诺过）。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（一次性补丁，非第三方移植）
# 文件:   D:\\AI\\SW\\patch_provenance_diag.py
# 定位:   「来源块覆盖范围不足」在本会话已出现**五次**，两种面孔：
#           ① 常量/导入夹在来源块与目标 `def` 之间
#           ② **一个来源块后面有多个代码单元**（本轮这次）⇒ 默认只覆盖第一个
#         两次都表现为同一句含混的「N 行新增代码没有可追溯的出处」。
#         **⇒ 本轮两件事一起做：修当前那处 + 让 gate 自己把这两个原因说出来。**
# 官方签名依据: 不适用（纯 Python 文本补丁）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 一次性脚本：跑完即可删。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

SM = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_sheet_metal.py")
GATE = Path(r"C:\swprojects\sw-skill-fork\scripts\check_provenance.py")

OLD_COV = "# 覆盖:   本常量整体（自本行至 `}` 结束）"
NEW_COV = ("# 覆盖:   后续同级定义\n"
           "#         ↑ 本块说明 `SHEET_METAL_RUNTIME_STATUS`（常量）与 `require_verified`（函数）\n"
           "#         **两个**代码单元。⚠ 标记必须写成**裸的** `覆盖: 后续同级定义` ——\n"
           "#         加 markdown 粗体会让正则 `r\"覆盖\\s*[:：]\\s*后续同级定义\"` 匹配不到。\n"
           "#         ⚠ 本会话第 **5** 次踩这个覆盖范围坑，见 `check_provenance` 的诊断。")

NEEDLE = '        print("\\n修法：在该段代码上方加 AGENTS.md §四 4.3 规定的来源块，")'
HINT = '''        # ⚑ 常见原因诊断（2026-10-01 加；本会话**五次**同族坑，两种面孔）
        print("\\n        ↑ 两个最常见原因（机器可查，不必再猜）：")
        print("          ① 常量/导入夹在来源块与目标 def 之间 ⇒ 延伸止于常量")
        print("             ⇒ 把常量挪到**来源块之前**；")
        print("          ② 一个来源块后面有多个 def/常量 ⇒ 默认只覆盖第一个")
        print("             ⇒ 在该块里加**裸的** `# 覆盖: 后续同级定义`（或 `# 覆盖: 全文件`）。")
        print("             ⚠ 那行**不要**加 markdown 粗体 —— 正则匹配不到 `**`。")
        print("        逐行核对就用本命令的输出（它已列出未覆盖的具体行）。")
        print("\\n修法：在该段代码上方加 AGENTS.md §四 4.3 规定的来源块，")'''


def main() -> int:
    # ① 修当前那处
    t = SM.read_text(encoding="utf-8")
    if OLD_COV not in t:
        print("  ✗ sw_sheet_metal.py 未找到覆盖行")
        return 1
    t = t.replace(OLD_COV, NEW_COV, 1)
    # 该块也要含第 4 个必需字段（否则 has_valid_block 不成立 —— 那会让测试豁免失效）
    t = t.replace(
        "#  ⚠ 本表只覆盖**本机实测过**的入口；未测的按「未知」处理（不假设可用）。",
        "#  ⚠ 本表只覆盖**本机实测过**的入口；未测的按「未知」处理（不假设可用）。\n"
        "#  ⚠ 本模块整体**已在本机实测**（`probe_sheet_metal_e2e.py`），故此处**不再**标注\n"
        "#    「未在本机实测」；各入口的实测结论见下表。", 1)
    SM.write_text(t, encoding="utf-8")
    print("  ✓ sw_sheet_metal.py：覆盖标记已改为「后续同级定义」")

    # ② gate 加诊断
    g = GATE.read_text(encoding="utf-8")
    if NEEDLE not in g:
        print("  ⚠ gate 未匹配输出段（诊断没加上）")
        return 0
    g = g.replace(NEEDLE, HINT, 1)
    GATE.write_text(g, encoding="utf-8")
    print("  ✓ check_provenance：已加两条原因诊断")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
