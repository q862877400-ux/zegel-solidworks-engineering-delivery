import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
W = Path(r"D:\AI\SW")

FACT = """| 144 | **挂柜台第二批（拓扑「脱模/应力/对称」3 个）：先把枚举核清再挂** —— 而"查不到"也要有硬证据** —— 2026-10-01（轮 205 / Spec Kit `124`）。

★★ **口径说明（承接事实 143 的方法）**：本批的候选**不是手挑的**，是 `batch11` 里**明确留批**的那三个 ——
上批留批的理由是「**枚举值未核**」⇒ ★ **本批先把枚举核清了再挂**（宪法 §II / §III）。
```
【出厂反射 D:/AI/SW/_raw/reflect/enum_cosworks.txt】
  swsTopologyDemoldDirectionOption_e       0=TwoDirectionMidPlane · 1=PullDirectionOnly · 2=Stamping
  swsTopologyStudyConstraintComparator_e   0=IsLessThan · 1=IsGreaterThan · 2=IsInBetween
  swsTopologyPreservedRegionOption_e       0=LoadsOnly · 1=FixturesOnly · 2=LoadsAndFixtures · 3=None
```
★★★ **一处"查不到"给了**硬证据**（不是嘴上说查不到）**：
```
对称类型的**枚举名**（`swsTopologySymmetryType_e`）在本地转储里**没有**。
★ 可重跑的命令（`specs/124-topology-batch2/tasks.md` T-12402）一次给出四行：
    swsTopologyDemoldDirectionOption_e         True
    swsTopologyStudyConstraintComparator_e     True
    swsTopologyPreservedRegionOption_e         True
    **swsTopologySymmetryType_e                 False**   ← ★ 这一行就是"查不到"的证据
只查到**官方 VBA 示例** `Create_Topology_Study_Example_VBA.txt` 的用法
  （`SelectSymmetryType 0/1/2` + 注释 `' Define topology one-half symmetry control`）
⇒ ★ 于是 `symmetry_type` 的描述**只声称"取值来自官方示例"**，
  **不声称枚举名、也不声称逐值语义** —— 并在工具描述里写明这一点。
★ 教训（可复用）：**"查不到"要写成一条能跑出 `False` 的命令**，
  否则它与"我没查"、"我忘了查"、"我以为没有"在读者眼里长得一样。
```

★★ **五处口径一致地动 3**（与事实 143 同一模式，互相印证）：
```
被工具引用的公开函数 97→**100** · 孤立能力 298→**295** · 首参可注入 47→**44**
并集 428→**431** · 本仓库独家 79→**82** · 缺口 338 **不变**
```
★ 两处"钉死数量"的测试当场报红 ⇒ 同步更新（**45→48** · **90→93**）。
★ 注册表现有 **48** 条声明；拓扑族从 5 个变 **8 个**。

⚠ **限度**：本批**只做暴露**（★ 真机验证排队列 `135`，**不给任何 `verified` 身份**）·
`symmetry_type` 的**逐值语义未定**（0 未必等于 one-half，示例注释只说"用了它做 one-half"）·
`direction` 的 `2=Stamping` 在示例里**没出现**（语义来自枚举名，**未真机核**）。

**依据**：`mcp-server/tool_specs_batch12.py` · `mcp-server/register_capabilities.py` ·
`D:/AI/SW/_raw/reflect/enum_cosworks.txt` · `specs/124-topology-batch2/` · 事实 143
"""

K = W / "docs" / "known-facts.md"
tk = K.read_text(encoding="utf-8")
if "| 144 |" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT, encoding="utf-8")
    print("  ok known-facts 已加 144")
print("  校验:", K.read_text(encoding="utf-8").count("| 144 |"), "次")

R = W / "docs" / "ROADMAP.md"
B = """           681 🎯 **Spec Kit `124`：挂柜台第二批（拓扑「脱模 / 应力 / 对称」3 个）—— **先把枚举核清再挂****（轮 205）** ——
               ★ 候选**不是手挑的**：是 `batch11` 里**明确留批**的那三个，理由是「枚举值未核」⇒ 本批先把枚举核清。
               ```
               【出厂反射 D:/AI/SW/_raw/reflect/enum_cosworks.txt】
                 swsTopologyDemoldDirectionOption_e       0=TwoDirectionMidPlane · 1=PullDirectionOnly · 2=Stamping
                 swsTopologyStudyConstraintComparator_e   0=IsLessThan · 1=IsGreaterThan · 2=IsInBetween
                 swsTopologyPreservedRegionOption_e       0=LoadsOnly · 1=FixturesOnly · 2=LoadsAndFixtures · 3=None
               ```
            682 ★★★ **一处"查不到"给了****硬证据****（不是嘴上说查不到）**：
               ```
               对称类型的**枚举名**（`swsTopologySymmetryType_e`）在本地转储里**没有**。
               ★ 可重跑的命令（`specs/124-topology-batch2/tasks.md` T-12402）一次给出四行：
                   swsTopologyDemoldDirectionOption_e         True
                   swsTopologyStudyConstraintComparator_e     True
                   swsTopologyPreservedRegionOption_e         True
                   **swsTopologySymmetryType_e                 False**   ← ★ 这一行就是"查不到"的证据
               只查到**官方 VBA 示例**（`SelectSymmetryType 0/1/2` + 注释 `' Define topology one-half symmetry control`）
               ⇒ ★ 于是 `symmetry_type` 的描述**只声称"取值来自官方示例"**，
                 **不声称枚举名、也不声称逐值语义** —— 并在工具描述里写明这一点。
               ★ 教训：**"查不到"要写成一条能跑出 `False` 的命令** ——
                 否则它与"我没查"、"我忘了查"、"我以为没有"在读者眼里长得一样。
               ```
            683 ★★ **五处口径一致地动 3**（与轮 204 同一模式，互相印证）：
               ```
               被工具引用的公开函数 97→**100** · 孤立能力 298→**295** · 首参可注入 47→**44**
               并集 428→**431** · 本仓库独家 79→**82** · 缺口 338 **不变**
               ```
               ★ 两处"钉死数量"的测试当场报红 ⇒ 同步更新（**45→48** · **90→93**）·
                 注册表现有 **48** 条声明，拓扑族从 5 个变 **8 个**。
            684 ⚑ **限度**：本批**只做暴露**（真机验证排队列 `135`，**不给任何 `verified` 身份**）·
               `symmetry_type` 的**逐值语义未定**（0 未必等于 one-half）·
               `direction` 的 `2=Stamping` 在示例里**没出现**（语义来自枚举名，**未真机核**）。
               门禁 + `release_check` exit 0 · 全量回归 **1260 passed / 17 skipped**。
            685 ▶ **队列续作**（`docs/backlog-8h.md`）：下一项 = **B1 静力学真机验收**（`tools/capture_simulation_evidence.py`），
               再 A2（`sw_simulation_study` 族）→ A3（视图/选择族）→ … ⇒ 本轮起**连续推进不等指示**。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None
before = "".join(lines)
if re.search(r"^\s+681 ", before, re.M):
    print("  游标 681 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+685 ", R.read_text(encoding="utf-8"), re.M)
    print("  复核: 685 行已存在 ✓")
