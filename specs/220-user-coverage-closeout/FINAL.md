# 规格 220 · 最终账（★ 13/14 轮，如实交代）

## 〇 · 一句话

★★ **目标未达成**：★ 地图**仍是 139/145 = 96%**（★ 与本规格开工时**同一读数**）✗
★★ 而**第 ④ 项已完成**（★ 3 格"不做 + 原因"），★ **①②③ 未完成**，★ 其中：
  ★ ① **验证债未还清**（★ 两个边界特征工具**如实留在 `stitched`**）✗
  ★ ②③ 未做（★ 但它们依赖的官方 API **已实查存在** ✓ ⇒ 可直接做）✓

## 一、★ 刚核实的纪律读数（★ 2026-10-07 收口时实测）

| 项 | ★ 读数 |
|---|---|
| ★ `all_specs()` | ★ **474**（★ 与开工时**一样** —— ★ 本规格**没加也没减**工具）✓ |
| ★ 地图 | ★ **139/145 = 96%**（★ 未动）|
| ★★ 台账 `level` 变更 | ★★ **0 行**（★ 红线⑥ 全程守住）✓ |
| ★★ 台账 diff | ★★ **空**（★ 本规格**没改台账一个字**）✓ |
| ★ `release_check` | ★ **exit 0** ✓（★ 收口前先重跑生成物 —— ★ 这是本规格第 3 次验到"改运行时文件 ⇒ 生成物过期 ⇒ 重跑即绿" ✓）|
| ★ 真机 | ★ **9 次**，★ 全走 `tools/sw_guard.py`，★ **0 弹窗** ✓ · ★ 每次都收尾 ✓ |
| ★ 工作区 | ★ 只剩既有的 `M AGENTS.md` / `output/*` / `.dsk` 备份（★ **不是本规格所为**）✓ |

## 二、★★ 本规格真正的产出（★ 比"地图没变"更重要）

★★ **边界特征（`InsertNetBlend`）的卡点链，四环全部有真机读数** ✓
★ 见 `recon-boundary-findings.md`：★ ① 成员是属性还是方法 → ② **迟到绑定要走 `get_com_member`**
→ ③ ★★ **选面必须走 `IEntity.Select4`（`SelectByID2` 按点对某些面永远选不上）** → ④ **试件要两个轮廓**

★ 其中 **③ 是决定性的**（★ 双臂判别探针一次定案）：★ 读数
  ★ `SelectByID2` 按点 ⇒ **0** ✗ · ★ **`face.Select4` ⇒ `[True, 1]`** ✓ · ★ **`Select4(Append=True)` ⇒ `[True, 2]`** ✓
⇒ ★★ **包装已按它改好** ✓ ⇒ ★ **选择这一环已经通了** ✓（★ 第 10 轮真机：★ 选面**不再报错** ✓）

## 三、★ 未还清的债（★ 只剩一环）

★ 第 10 轮真机：★ 选面通了、★ 流程走到 `InsertNetBlend`、★ **但它回 `None`、特征树 20 → 20** ✗
★★ **最可能的原因**：★ **试件不合法** —— ★ 官方示例 `Postconditions` 逐字是
  「② **Creates two boss-extrude features.** ③ **Selects a face on each boss-extrude feature.**」
  ⇒ ★ **两个轮廓/两个体**；★ 而我的试件是**同一块板的两个面** ✗

★★ **下一手的动作（★ 已写进 `goal-bar.md` §四）**：★ 建**两个拉伸** ⇒ ★ **每个体各取一个面**
  （★ `sw_selection_spec.entities_on_body(model, "FACE", body_index=…)` **已带该形参** ✓）⇒
  ★ 参数照官方（★ `Type` · ★ `NCurvesDir1=1` · ★ **`NCurvesDir2=2`**）⇒ ★ 跑 ⇒ ★ **判据：特征树增量 ≥ 1**
  ⇒ ★ **过了才**提 `level` ✓

## 四、★ 现状上限与现实上限的距离

| 项 | ★ 读数 |
|---|---|
| ★ 现在 | ★ **139/145 = 96%** |
| ★★ **现实上限** | ★★ **141/145 ≈ 97%**（★ 3 格官方无 API ⇒ `not-doing.md`）|
| ★ 差 | ★ **2 格**：★ **焊件/圆角焊缝** · ★ **装配/零部件阵列**（★ 都**已实查官方 API 存在** ✓）|
| ★ 另有 | ★ **2 格**在等验证：★ 边界凸台 · 边界曲面（★ 已暴露，★ 但 `level` 仍是 `stitched`）|

## 六、★ 轮次用尽（14/14）· 交接（★ 下一手照这条，一步可接）

★★ **状态**：★ 目标 `goal-6b9163d7` **轮次用尽而目标未达成** ⇒ ★ **保持 active**（★ 不标完成）✓
★ 地图 **139/145 = 96%** · ★ **现实上限 141/145 ≈ 97%** · ★ 台账**零改动** · ★ `level` **零变更** ✓

### ★★ 下一手（★ 唯一一件，照官方示例重建试件）

```powershell
# 1. 改 tools/probe_spec220_boundary.py 的建件部分：★ 建【两个拉伸】（★ 官方 Postconditions 逐字要求）
#    ★ 每个体各取一个面 ⇒ 用 sw_selection_spec.entities_on_body(model, "FACE", body_index=n)  ✓
# 2. 跑真机（★ 用完关 SolidWorks）
python tools/sw_guard.py --timeout 600 -- python tools/probe_spec220_boundary.py
# 3. ★★ 判据：特征树增量 >= 1（事实 8：不看布尔返回值）
#    ★ 过了 ⇒ 把 capabilities.yaml 的 surface_features（及其两条工具的 evidence）提到 verified
#    ★ 不成 ⇒ ★ 继续如实留 stitched，并把失败读数写进 limitations
```

★ 依据（★ 官方逐字）：`AI Solidworks\官方文档\…\Insert_Boundary_Feature_Example_VB.htm` 的
  `Postconditions`：「② **Creates two boss-extrude features.** ③ **Selects a face on each
  boss-extrude feature.** ④ Creates a boundary feature using the selected faces.」✓
★ 参数照官方（★ 第 74 行逐字）：★ `InsertNetBlend(1, 2, 0, False, 0.0001, …)` ⇒
  ★ `Type=1` · ★ `NCurvesDir1=1` · ★ **`NCurvesDir2=2`** ✓（★ 已设为包装默认 ✓）

### ★ 之后的两件（★ 官方 API 已实查存在，可直接做）

| 件 | ★ 官方入口 | ★ 判据 |
|---|---|---|
| ★ 焊件/圆角焊缝 ⇒ **焊件 7/7** | ★ `InsertFilletBeadFeature`（★ + `InsertCosmeticWeldBead2` · `GetWeldBeadFolder`）| ★ 特征树增量 ≥ 1 |
| ★ 装配/零部件阵列 ⇒ **装配 8/10** | ★ `DissolveComponentPattern` · `GetPatternComponentCount` | ★ 组件/特征计数增量 |

★ 做完这两件 ⇒ ★ 地图 **141/145 ≈ 97%** = ★ **本规格的目标上限** ✓
★ 另有 **3 格**已如实标注"不做 + 原因"（★ 见 `not-doing.md`）⇒ ★ **不硬凑** ✓

### ★★ 全程一句话（★ 给下一位）

★★ **本规格没让地图变绿，但它把"为什么不能变绿"查到底了** —— ★ 边界特征的卡点链**四环全有真机读数**
（★ 属性/方法 → 迟到绑定 → **`Select4` vs `SelectByID2`** → 试件），★ 而**最后一环是试件合法性**，
★ **有官方逐字依据**、★ **一步可改** ✓
★★ 而**没做到的事我一件都没粉饰**：★ `level` 零变更 · 台账零改动 · 地图零虚报 ✓


1. ★★ **误判 `Append` 不累加**（★ 真因是"0 号面根本选不上"）⇒ ★ 第 9 轮双臂探针定案后改账 ✓
2. ★★ **误判 `create_deformed_body` 是实体缩放**（★ 它是 Simulation 结果图）⇒ ★ 规格 219 第 2 轮改账 ✓
3. ★ **漏还原探针的 swap**（★ 导致第 8 轮"第 1 次=1"是必然）⇒ ★ 第 10 轮改账并还原 ✓
