import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
S = Path(r"D:\AI\SW\specs\024-sketch-edit-from-true-missing")
S.mkdir(parents=True, exist_ok=True)

spec = """# 024 · 从「真缺」再补两条：草图倒角 / 草图镜像

**Status**: Implemented（轮 105）

## 背景
`023` 从「真缺」档补了螺旋线。本轮接着补 **`sketch_chamfer`** 与 **`sketch_mirror`**
（`022` 的核样确认这两条确实没有实现）。

## ★★ 本轮最重要的发现：**枚举值两源冲突**（铁律 4 的活例）
```
swSketchChamferType_e
  成员                              C:\\swapi 的 md    出厂反射（**采用**）
  swSketchChamfer_DistanceAngle          0               0
  swSketchChamfer_DistanceDistance     **-1**          **1**      ← 冲突
  swSketchChamfer_DistanceEqual          2               2
```
★ **铁律 4：冲突以出厂类型库为准** ⇒ 实现取 **1**。
⚠ 此前铁律 4 更像一条**预防性条款**；本轮它**第一次真正裁决了一次冲突**。
★ 契约测试把 **1** 独立抄一份 ⇒ 任何人改成 -1 都会红。

## 另一处：**走非废弃入口**
官方文档明写 `IModelDoc2.SketchChamfer` 是 **Obsolete**，被 `ISketchManager::CreateChamfer` 取代
⇒ 本模块用**后继**（`SketchSegment CreateChamfer(Int32, Double, Double)`，两源签名一致）。

## 判据
| ID | 判据 |
|---|---|
| SC-2001 | ★ 枚举**取出厂反射**（`distance_distance = 1`），不是 md 的 -1 |
| SC-2002 | ★ 走**非废弃**入口（`CreateChamfer`），来源块记下原因 |
| SC-2003 | 官方参数顺序与个数照抄（倒角 3 参；镜像**0 参**）|
| SC-2004 | 长度在**边界**换算（2.5 mm ⇒ 0.0025 m）|
| SC-2005 | 前置条件不满足时抛**带原因**的 `RuntimeError`（两条实体 / 草图编辑态 + 标记 1/2）|
| SC-2006 | 来源块写明等级 **`stitched`** 且**无本机运行证据** |
| SC-2007 | `capabilities.yaml` 新增 `sketch_edit_ops`（`stitched`），32 → **33** 条 |
| SC-2008 | 门禁 + 回归不退化（回归 **1064 passed**）|

## ⚠ 明确记下的限度
* **等级 `stitched`** —— 只有静态证据，**本机从未做过草图倒角/镜像**；
* **前置条件不代选**：倒角要两条实体、镜像要按官方标记（线段 1 / 中心线 2）选中；
* `CreateChamfer` 第三参 `AngleORdist` 的**单位随类型变，官方未写** ⇒ **不做换算**、原样传；
* 本轮**主动不做真机测试**（轮 98 的模态框教训）。
"""

plan = """# 024 · Plan

**不重造**：照 `023`（`sw_helix.py`）的模块形式与来源块写法。

## 步骤
1. 查 `sketch_chamfer` / `sketch_mirror` 是否真缺 ⇒ 确认缺
2. 两源取签名（反射 + swapi）⇒ 倒角 3 参一致；镜像 0 参一致
3. ★ 取枚举 `swSketchChamferType_e` ⇒ **发现两源冲突**（-1 vs 1）
4. ★ **按铁律 4 取出厂反射的 1**
5. 发现 `SketchChamfer` **已废弃** ⇒ 改走后继 `CreateChamfer`
6. 写 `scripts/sw_sketch_edit.py` + 契约测试（10 条）
7. 加 `capabilities.yaml` 条目（32 → 33）
8. 重生成地图/审计/digest + 同步数字 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| **枚举冲突随手取一个** | ★ 铁律 4 明文裁决 + 测试独立钉住 |
| 用已废弃的入口 | 官方文档明写 Obsolete ⇒ 走后继，且来源块记下原因 |
| 单位再出岔子 | 长度走 `mm()`；**官方未写单位的参数不做换算并声明** |
| 真机测试触发弹窗 | ★ 不做真机测试，等级写 `stitched` |
"""

tasks = """# 024 · Tasks（全部完成，轮 105）

- [x] T-2001 确认两条确实没实现
- [x] T-2002 两源取签名
- [x] T-2003 ★ 取枚举 ⇒ **发现两源冲突（-1 vs 1）** ⇒ 按铁律 4 取 **1**
- [x] T-2004 ★ 发现 `SketchChamfer` **已废弃** ⇒ 改走后继 `CreateChamfer`
- [x] T-2005 写 `scripts/sw_sketch_edit.py`
- [x] T-2006 契约测试 `tests/test_sw_sketch_edit_contract.py`（**10 passed**）
  `→ 验收:` `python -m pytest tests/test_sw_sketch_edit_contract.py -q`
- [x] T-2007 加能力条目（32 → **33**）
- [x] T-2008 重生成 + 门禁 + 回归 `→ 验收:` `python scripts/release_check.py`（exit 0）
"""

converge = """# 024 · Converge

**Converged**: 2026-10-01（轮 105）

## 一、结果
| 判据 | 结论 |
|---|---|
| SC-2001 枚举取出厂反射 | ✅ `distance_distance = 1`（测试独立钉住）|
| SC-2002 走非废弃入口 | ✅ `CreateChamfer`，来源块记下原因 |
| SC-2003 参数顺序与个数 | ✅ 倒角 3 参；镜像 0 参 |
| SC-2004 长度边界换算 | ✅ 2.5 mm ⇒ 0.0025 m |
| SC-2005 前置不满足时抛带原因的错 | ✅ 消息含「两条草图实体」/「草图编辑态」+「mark=1/2」|
| SC-2006 来源块写明 `stitched` | ✅ 测试钉住 |
| SC-2007 能力 32 → **33** | ✅ `sketch_edit_ops` |
| SC-2008 门禁 + 回归 | ✅ `release_check` exit 0 · 回归 **1064 passed** |

## 二、★ 铁律 4 第一次真正裁决了一次冲突
```
swSketchChamfer_DistanceDistance：swapi 的 md 写 -1 · 出厂反射写 1
⇒ 铁律 4「冲突以出厂类型库为准」⇒ 取 **1**
```
⚠ 此前四轮里，两源一直是**一致**的（`023` 的 `InsertHelix`、螺旋线枚举）。
本轮**第一次出现真冲突** ⇒ 那条铁律从"预防性条款"变成了**实际用上的规则**。

★ 若不是它，取值就只能靠"哪个看起来合理"——而 `-1` 看起来**并非不可能**
（有些枚举确实用负数表示变体），**光看值本身判不出来**。

## 三、连两轮的共同点：错都在**值**上，不在**名字**上
```
023：枚举值凭记忆写反（1 ↔ 2）—— 门禁抓不到
024：枚举值两源冲突（-1 vs 1）—— 门禁抓不到
```
★ **门禁查的是"名字在不在官方清单里"，不查"值对不对"**
⇒ 这两轮的错**都只能靠人查证**拦下。这是本项目一个**已知的覆盖缺口**，
两轮连着撞上，值得记进已知事实。

## 四、未查证
* **本机从未做过**草图倒角/镜像（等级 `stitched`）；
* 前置条件（选中两条实体 / 按标记选中）**未实测**；
* `CreateChamfer` 第三参 `AngleORdist` 的**单位随类型变，官方未写** ⇒ 未换算、未验证；
* 「真缺」档还有 **129 条**（`023`+`024` 共补了 3 条）。
"""

for name, text in (("spec.md", spec), ("plan.md", plan), ("tasks.md", tasks), ("converge.md", converge)):
    (S / name).write_text(text, encoding="utf-8")
    print("  written %s" % name)
