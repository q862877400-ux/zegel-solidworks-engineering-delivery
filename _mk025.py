import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"D:\AI\SW\specs\025-enum-value-gate")
S.mkdir(parents=True, exist_ok=True)

spec = """# 025 · 补上「值级」覆盖缺口：枚举值必须与出厂反射对得上

**Status**: Implemented（轮 106）

## 背景：连着两轮的错**都在「值」上，而门禁一个都抓不到**
```
023：螺旋线枚举**凭记忆写反**      height_and_pitch 1 ↔ 2
024：swSketchChamfer_DistanceDistance **两源冲突**   md −1 / 反射 1
```
★ 当时的门禁（`check_member_names` / `interface_member_ownership` / `audit_call_arity`）
查的都是「**名字**在不在官方清单里」，**没有一个查「值对不对」**。
⇒ 这是一个**已知的覆盖缺口**，两轮连着撞上 ⇒ 本轮把它补成**机器判据**。

## 做法
`scripts/check_enum_values_vs_reflection.py`（**第 16 道门禁**）：
1. 在 `scripts/sw_*.py` 找形如 `"<key>": <整数>,   # <swMember>` 的行
   （本仓库广泛使用的写法：**值 + 官方成员名**，共 **91** 条）；
2. 从**出厂反射转储**解析 `{成员名: 值}`（**8216** 个成员）；
3. 逐条比对 —— **对不上即 `[FAIL]`**（就是 023 那类）；
4. **顺带报出两源冲突**（就是 024 那类）—— ⚠ **冲突不判失败**
   （铁律 4 已定：冲突取反射），但**必须让人看得见**；
5. 转储里查不到的成员归「查不到」（铁律 5：不猜），**不判失败**。

## ★★ 门禁自己也有过一处漏点（当场抓到并修）
第一版正则要求**成员名后即行尾** ⇒ 漏掉 `sw_sketch_edit.py` 那行
（它写成 `# swSketchChamfer_DistanceDistance（⚠ md 写 -1…）`）
⇒ ⚠ **门禁会漏掉 024 那个冲突本身**。
★ 这正是**已知事实 62** 的又一例：「门禁**写了**不等于它**有效**」——
**判据对了，匹配范围没跟上**。

## 实跑结果
```
出厂反射转储 8216 个成员 · 代码里「值 + 官方成员名」91 条
  15 条有据可查的值全部与反射一致
  75 条在转储里查不到（多为 Simulation 的 sws* 枚举，属另一程序集）
   1 处两源冲突  ← swSketchChamfer_DistanceDistance（反射 1 · md −1）
⇒ [PASS]
```

## 判据
| ID | 判据 |
|---|---|
| SC-2101 | ★ **负例**：值写错被抓出并报出反射里的正确值（造 023 的真实错法）|
| SC-2102 | ★ **负例**：两源冲突**被报出来**，但**不判失败**（024 的真实形态）|
| SC-2103 | ★ **负例**：成员名后**有注释文字**的行也能解析（**门禁第一版的漏点**）|
| SC-2104 | `swDefaultTemplatePart` 那类 `Enum.member` 前缀写法也能解析 |
| SC-2105 | 转储里查不到的成员 ⇒ 归「查不到」，**不判失败** |
| SC-2106 | 对着**真实仓库**跑：无值错，且**报得出** `swSketchChamfer_DistanceDistance` 那处冲突 |
| SC-2107 | 拿不到转储时 **SKIP 并 exit 0**（便携性）|
| SC-2108 | 接进 `release_check.py`（**硬门禁**）+ 登记进 `gate-classification.json` |
| SC-2109 | 门禁数 **15 → 16**；回归不退化（**1072 passed**）|

## ⚠ 明确记下的覆盖面边界
* 它判「写出的**值**与反射一致」，**不判**「成员名挂的是不是对的枚举」；
* 它**不判**「值的语义对不对」（例如某个参数该传 0 还是 1）；
* 转储本身是**纯元数据读取**（非实测），它反映的是**出厂声明**，不是运行时行为。
"""

plan = """# 025 · Plan

**不重造**：复用仓库既有的门禁形式（`check_*.py` + `release_check` 接线 + 分类登记 + 负例测试）。

## 步骤
1. 确认缺口的证据：列出旧门禁查的都是「名字」而非「值」
2. 写 `scripts/check_enum_values_vs_reflection.py`
3. ★ 跑一次 ⇒ **发现自己的正则漏了带尾注的行**（即会漏掉 024 那个冲突）⇒ 修
4. 重构出 `compare()` 便于负例测试
5. 写 `tests/test_enum_values_gate.py`（8 条，含 3 个负例）
6. 接进 `release_check.py`（硬门禁）+ `gate-classification.json`
7. ★ **门禁接线元门禁当场报出两处漏登记**（汇总体 + 分类表）⇒ 补
8. 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| **新门禁自己也"写了但没用"** | ★ 3 个负例（值错 / 冲突 / 带尾注的行）；且**对着真实仓库**断言它报得出 024 的冲突 |
| 把冲突判成失败 ⇒ 误伤正确实现 | 明写**冲突不判失败**（铁律 4 已定取反射），只报 |
| 75 条"查不到"被当成失败 | 按铁律 5 归「查不到」，单独列出、**不判失败** |
| 转储路径不可移植 | `DSH_ENUM_DUMP` 可覆盖；拿不到 ⇒ SKIP exit 0 |
"""

tasks = """# 025 · Tasks（全部完成，轮 106）

- [x] T-2101 写 `scripts/check_enum_values_vs_reflection.py`
- [x] T-2102 ★ 首跑即发现**自己的正则漏了带尾注的行** ⇒ 修
  `→ 验收:` `python scripts/check_enum_values_vs_reflection.py`
- [x] T-2103 重构出 `compare()`（为负例可测）
- [x] T-2104 负例测试 `tests/test_enum_values_gate.py`（**8 passed**）
  `→ 验收:` `python -m pytest tests/test_enum_values_gate.py -q`
- [x] T-2105 接进 `release_check.py`（硬门禁）
- [x] T-2106 登记 `docs/gate-classification.json`
  `→ 验收:` `python scripts/check_gate_wiring.py`（**16 个门禁全部已接线**）
- [x] T-2107 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 025 · Converge

**Converged**: 2026-10-01（轮 106）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-2101 值错被抓 | ✅ 负例测试 |
| SC-2102 冲突被报但不判失败 | ✅ 负例测试（用 024 的真实形态）|
| SC-2103 带尾注的行能解析 | ✅ 负例测试（**第一版真的漏了**）|
| SC-2104 `Enum.member` 前缀可解析 | ✅ |
| SC-2105 查不到不判失败 | ✅ |
| SC-2106 真实仓库上无值错且报得出 024 冲突 | ✅ 1 处冲突 |
| SC-2107 拿不到转储则 SKIP | ✅ |
| SC-2108 接线 + 登记 | ✅ 硬门禁 · 16 道全部接线 |
| SC-2109 门禁 15 → **16** · 回归 | ✅ `release_check` exit 0 · **1072 passed** |

## 二、★ 修的是「**值从来没人查**」这个结构性缺口
```
旧门禁查什么：名字在不在官方清单里     （check_member_names / interface_member_ownership
                                      / audit_call_arity）
新门禁查什么：**写出的值与出厂反射是否一致** + 两源冲突
```
★ 两轮（023/024）的错**都从这个缺口漏过去**，而**两轮都是靠人查证才拦下的**。
⇒ 本轮把它变成**机器判据** —— 同类错**以后会在门禁上红**，不再依赖我恰好停下来查。

## 三、★ 门禁自己也踩了同一个坑（当场抓到）
第一版正则要求**成员名后即行尾** ⇒ **漏掉 `sw_sketch_edit.py` 那行**
（它后面有括号注释）⇒ **门禁会漏掉 024 那个冲突本身**。
★ 又是**已知事实 62**：**判据对了，匹配范围没跟上**。
⇒ 这正是为什么 SC-2106 要求**对着真实仓库断言它报得出那一处冲突** ——
不能只测"逻辑对不对"，还要测"它在我们这堆代码上真的看得见"。

## 四、实跑的数字（可复算）
```
出厂反射转储 8216 个成员
代码里「值 + 官方成员名」的行 91 条
  ├─ 15 条与反射一致
  ├─ 75 条转储里查不到（多为 Simulation 的 sws*，属另一程序集）
  └─  1 处两源冲突（swSketchChamfer_DistanceDistance：反射 1 · md −1）
```

## 五、未查证
* **75 条"查不到"未逐条核** —— 它们多半来自 `swsimulation` 程序集（不在本转储里），
  **未验证**是否有对应的反射源可查；
* 新门禁**不判**「成员名挂的是不是对的枚举」，也**不判**值的语义；
* 转储是**纯元数据读取**（非实测）⇒ 它反映**出厂声明**，不是运行时行为。
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
