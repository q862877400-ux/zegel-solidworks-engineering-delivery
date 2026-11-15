# Quickstart · 造环节验证指南

**Feature**: `354-make-side-generation` | **Date**: 2026-11-06

本文件只写「怎么跑、跑出什么算通过」。实现细节在 tasks.md。

---

## 前置

| 项 | 要求 | 怎么确认 |
|---|---|---|
| Python | ≥3.11（本机 3.14.7） | `python -V` |
| pytest | 已装（本机 9.1.1） | `python -m pytest --version` |
| SolidWorks | 2026，能启动 | `python -B tools\guard_run.py --timeout 60 -- python scripts\sw_connect.py --probe` |

---

## 场景 1 · 离线：参数推导（不需要 SolidWorks）

```powershell
cd research\text-to-cad-and-parametric-plugins\proto
python -m pytest test_gear_method.py -q
```

**通过判据**：`9 passed`

**看什么**：

```powershell
python -c "from gear_method import GearRequest, derive, render; print(render(derive(GearRequest(ratio=3.0, center_mm=40.0))))"
```

期望看到 13 行参数表，每行有「问/算/选/查/锁」标记，末尾有【未覆盖】段。

---

## 场景 2 · 离线：计划生成（不需要 SolidWorks）

```powershell
cd research\text-to-cad-and-parametric-plugins\proto
python -m pytest test_build_plan.py -q
```

**通过判据**：`8 passed`

**看什么**：

```powershell
python build_plan.py
```

期望：
```
SpurGear_m1_z20｜单位=mm｜草图实体 200 个
  拉伸 10 mm（送 SolidWorks 时转成 0.01 m）
  预期体积 3064.56 mm³｜预期包围盒 22.00 × 22.00 × 10.00 mm
```

> ⚠ 草图实体数从 700 改为 200（research §U5 的决策），体会跟着变一点。

---

## 场景 3 · 离线：分流决策

```powershell
python -m pytest test_dispatcher.py -q
```

**通过判据**：`7 passed`

---

## 场景 4 · ★ 真机：齿轮建出来且量得准（本特性的核心）

```powershell
cd research\text-to-cad-and-parametric-plugins\proto
python -B ..\..\..\tools\guard_run.py --timeout 300 -- python execute.py --gear i=3 a=40
```

**通过判据（三条全绿才算过）**：

| # | 判据 | 期望 |
|---|---|---|
| 1 | 体积偏差 | **< 1.0%** |
| 2 | 包围盒 | 22.00 × 22.00 × 10.00 mm，每向偏差 **< 0.5 mm** |
| 3 | 三视图 | `output\views\` 下 4 个文件，都非空 |

**期望输出**（形如）：

```
execute: SpurGear_m1_z20  草图实体 200
verify: 体积 3064.6 mm³（预期 3064.56，偏差 0.00%）✓
verify: 包围盒 22.00×22.00×10.00（偏差 0.00/0.00/0.00）✓
verify: 三视图 4/4 ✓
VERDICT: OK
```

**失败时**：

```
VERDICT: DIALOG <弹窗文字>
```
或 `output\execute_failures\<ts>.json` 里有 `failure` 字段。

---

## 场景 5 · 真机：第二族（轴）

```powershell
python -B ..\..\..\tools\guard_run.py --timeout 300 -- python execute.py --shaft T=120 span=300 shock=light
```

**通过判据**：体积偏差 <1%、包围盒对上、三视图 4/4。

**这条的意义**：证明「参数→计划→执行→验证」这套骨架**不是齿轮专用**。

---

## 场景 6 · 标准号现行版核验

```powershell
cd research\text-to-cad-and-parametric-plugins\_evidence\scan
python _recheck.py
```

**通过判据**：错误率 **0%**（当前 1.4%，有 1 条待清）

---

## 人工目视（不可自动化，必须单独做）

**上面场景 4/5 的「三视图 4/4」只证明图生成了，不证明图是对的。**

目视要看三件事：

1. **有没有悬空草图**（蓝色线框）
2. **有没有缺面**
3. **齿形是不是渐开线**（对照直边 vs 曲线）

**做完在报告里如实写**：`已目视，无异常` 或 `automated checks passed; not visually reviewed`。
**不许把「自动过了」写成「验收过了」。**

---

## 通过标准汇总

| 场景 | 判据 | 现在 |
|---|---|---|
| 1 参数推导 | 9 passed | ✅ |
| 2 计划生成 | 8 passed | ✅ |
| 3 分流决策 | 7 passed | ✅ |
| **4 齿轮真机** | **体积 <1% + 包围盒 + 三视图** | ❌ **未做** |
| **5 轴族真机** | 同上 | ❌ 未做 |
| 6 国标核验 | 错误率 0% | ⚠️ 1.4% |
| 人工目视 | 无悬空草图/缺面 | ❌ 未做 |

**场景 4 通过 = 造环节成立。其余是加固。**
