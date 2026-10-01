import re
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = Path(r"D:\AI\SW\docs\ROADMAP.md")
B = """           598 🎯 **Spec Kit `107`：A8 的「仍空缺什么」改为****从台账生成**** —— 因为手写的那一节****已腐坏******（轮 187）——
               起因：一份外部评审引用 `docs/harvest-report.md` 的 **§三（仍然空缺什么、为什么）** 得缺口结论。
               ★ 回代码核 ⇒ **本节已腐坏**：
               ```
               · §3.1 末行：「拓扑优化 10 个约束接口 … 本轮未逐个核签名，不做半成品」
                 ⇒ ★ 而它们**现在已经实现**（scripts/sw_topology.py；台账里 ICWTopology*Constraint 均已 used>=1）
               · §3.1 标题：「Simulation 域：84 接口只覆盖 7 个载荷方法」
                 ⇒ ★ 而台账现在显示仿真域 **84/84 触及**；ICWForce / ICWPressure / ICWHeatFlux /
                   ICWTemperature / ICWConvection / ICWRadiation / ICWContactSet 等**均有直接调用**
               ```
               ★★ 与 §二 正文停在「截至第 12 轮」**同一个病**：**手写状态必腐坏**。
            599 ★★★ **修法：复用**既有**生成器（一个门禁都没新增）** ——
               `tools/gen_harvest_digest.py` → `docs/harvest-digest.md` **§4.3**：
               ```
               数据源 docs/family-coverage.json（生成物）
               881 族 / 15,466 成员 · 编目录 15,466(100%) · 护栏 10,579(68%) · 直接调 2,721(18%)
               ⇒ **编进目录但从未直接调 = 256 族 / 2,114 成员**（按域 10 行 + 最大 10 族）
               ★ 附「读这一段的四条纪律」：① 三列不可合并 ② used=0 ≠ 没实现（反例 IGtolFrame）
                 ③ 静态解析 ≠ 运行期 ④ **该不该做不在台账里**（不做的原因在 backend_catalog / §4.2）
               ```
               ★ **零新门禁**：该文件已有**逐字节**新鲜度门禁 `scripts/check_digest_freshness.py`
                 （已在 `release_check.py` 里）⇒ 直接受它保护。
            600 ★★★ **本轮收敛出的定则（比代码值钱）**：
               > **凡是「状态 / 数字」都要生成，凡是「判断 / 原因」才手写。**
               ```
               两者混在同一节里 ⇒ **数字会随判断一起腐坏**，而**读者分不出哪半是旧的**。
               §三 的病正是如此：它把「84 接口只覆盖 7 个」（数字）与
               「两个官方源同时失效」（原因）写在同一小节 ⇒ 原因**至今可能仍成立**、
               数字**早就过期** ⇒ 引用它的人**必然踩坑**。
               ⇒ 修法不是重写那一节，而是**把两半分开**：数字进生成物，原因留手写。
               ```
            601 ★ **手写的 §三 保留**（它承载**「为什么补不了」的判断** —— 那一半机器生成不了），
               但加了**更正块**：写明它已腐坏、数字以生成的 §4.3 为准、并点出它**两处具体错**。
               ★ 验证：生成器**两次输出 SHA256 相同**（逐字节可复现，门禁要求）。
               门禁 + `release_check` exit 0 · 回归 **1248 passed**。
               ⚑ **未查证**：⚠ 手写 §3.1–3.3 **只加更正块、没重写** ⇒ 可能还有别的过期数字没逐条核；
                 ⚠ §4.3 **继承台账的静态局限**（走变量传成员名的调用看不见；不证运行期）；
                 ⚠ 台账由**工作区仓库**的 `D:/AI/SW/tools/gen_family_coverage.py` 生成 ⇒ **跨仓库滞后风险**；
                 ⚠ **「哪些零调用族该做」未逐条判**（那是判断，留给后续轮）。
               下轮候选：① 逐条判审计 §八 那 25 个零调用族「该做 / 不做 + 原因」；
               ② 试 `comtypes` 后端能否驱动 `out` 形参（若能，轮 186 的「不做」要改写）；
               ③ 回到在上下文链（`SketchUseEdge3` 静默无效）。
"""
lines = R.read_text(encoding="utf-8").splitlines(keepends=True)
i = next((k for k, l in enumerate(lines) if l.startswith("阻塞:")), None)
assert i is not None, "找不到『阻塞:』锚点"
before = "".join(lines)
if re.search(r"^\s+598 ", before, re.M):
    print("  游标 598 已在")
else:
    new = "".join(lines[:i]) + B + "".join(lines[i:])
    assert new.replace(B, "") == before
    R.write_text(new, encoding="utf-8")
    print("  游标已加")
    assert re.search(r"^\s+601 ", R.read_text(encoding="utf-8"), re.M), "复核失败"
    print("  复核: 601 行已存在 ✓")
