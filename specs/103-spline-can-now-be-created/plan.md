# 103 · Plan

## 步骤
1. 轮 182 查明「样条建不出」挡着 `composite_curve` ⇒ 本轮攻它
2. ★ 读官方 md ⇒ **CreateSpline 的 Remarks 写明 PointData 是**扁平的 X,Y,Z 序列****
3. ★★ 真机逐形态判别（扁平 list / tuple / VARIANT / list of tuples）
4. ★★★ ⇒ **只有 `VARIANT(VT_ARRAY|VT_R8)` 成**（段数 0 → 1）
5. ⚠ 修的时候踩到第二处：`CreateSpline` 取不到（Obsolete）⇒ `TypeError`（**指不出真因**）
6. ★ 修 `create_spline`（摊平 + VARIANT + 走 `CreateSpline2`）⇒ **三种写法全成**
7. 事实 123 → 门禁 + 回归 → 收工

## 风险与对策
| 风险 | 对策 |
|---|---|
| 把"形态不对"读成"接口到不了" | ★ **读官方 Remarks + 逐形态实测** |
| 只试一种形态就下结论 | ★ **四种形态都试**（含现状做对照）|
| 报错看不出真因 | ★ 打 **traceback** 定位到 `member(*args)` |
| 顺手去修 `composite_curve` | ★ **不顺手**（本轮只修上游，它的复验留给下轮）|
