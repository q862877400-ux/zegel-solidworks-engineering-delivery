# 示教器 L1–L4 实现状态（2026-10-26）

**一句话**：L1/L2/L4 已实现并有测试；**L3 打通 4/6 断言**，剩两条卡在同一个前提
（孔位草图缺可标注的参照），已定位、未伪装。

## 各层状态

| 层 | 文件 | 状态 | 判据 |
|---|---|---|---|
| L1 捕获 | `tools/demo_capture.py` + `scripts/sw_model_snapshot.py` | ✅ 完成 | 真机：PSR 276 步 + 录屏 + 模型语义（含关系/尺寸参照） |
| L2 提炼 | `scripts/sw_recipe.py` | ✅ 完成 | 16 条离线测试；真机从示范件提炼出配方 |
| L3 执行 | `scripts/sw_recipe_exec.py` | ⚠ **4/6** | 见下表 |
| L4 个人化 | `scripts/sw_habits.py` | ✅ 完成 | 未知键/类型错报错、不覆盖配方、id 防穿越 |
| 统一入口 | `tools/teach.py` | ✅ 完成 | `capture/derive/profile/run` 四子命令 |

## L3 真机读数（`teach/recipes/hole-4x-m6-gb.yaml`）

```
board      凸台-拉伸1                          ✓
孔特征      ok=True 数量=1                     ✓
进孔位草图  草图3                              ✓
加点后      4 点 (10,50)(90,50)(90,10)(10,10)  ✓
点关系      水平25 / 竖直26 / 水平25 / 竖直26    ✓ 四条全成
```

| 断言 | 结果 | 实测 | 期望 |
|---|---|---|---|
| `feature_count_hole` | **PASS** | 1 | 1 |
| `hole_standard_gb` | **PASS** | GB | 含 GB |
| `hole_size` | **PASS** | M6 | 非空 |
| `hole_fastener` | **PASS** | 螺钉间隙 | 非空 |
| `hole_sketch_constrained` | **FAIL** | 2 | 3 |
| `cylinder_count` | **FAIL** | 2 | 4 |

## 剩下的缺口（定位清楚，含证据）

**共同前提**：孔位草图里只有「点」，没有可标注的**线/边**。

实测证据：
- `IModelDocExtension.AddDimension(x,y,z,dir)` 对**圆**返回真 `IDisplayDimension`，
  对**草图点**返回 `None`（`output/probe_circle_dimension.py`、`probe_dims.py`）
- 只选点、或选「点 + 原点」都拿不到尺寸；`SelectByID2("Origin","SKETCHPOINT")` 在孔位草图里
  回 `False`（该草图**没有原点实体**）
- 参考案例的做法是「点到**板边**」，即那张草图里有板边（投影/转换实体）

⇒ 缺的一步是：**把板边投影进孔位草图**（`ISketchManager.SketchUseEdge3`）。
  已试两次：`SketchUseEdge3` 回 `True` 但草图线段数 = 0，射线选边的坐标基准还没校准
  （`solid_body_extent_mm.raw` 的单位在两次读数里不一致：一次米、一次毫米 ⇒ 必须先自证单位，
  不能靠猜）。

⇒ 一旦投影成功，补 4 个「点到边」尺寸（`AddDimension` + `SetSystemValue2(v, 2)` 直接设值，
  **不必碰界面**）⇒ 状态应到 3 ⇒ 圆柱面数随之到 4。

## 我这一轮踩到并修掉的（都写了注释与测试）

| 坑 | 后果 | 修法 |
|---|---|---|
| 孔特征取**最后**一张草图 | 那是轮廓草图 ⇒ 状态 3 是**假绿** | 取**第一**张（定位草图） |
| bbox `raw` 当毫米用 | 板厚写成 0.02mm ⇒ 建出一张纸片 | ×1000，并加测试锁住 |
| 孔位没归一化 | 示范件负 Y ⇒ 射线打空、孔建不出 | 减掉板草图最小角，并加测试 |
| 配方 YAML 回读不认 `- ` 列表 | 孔位读成 `{}`，配方静默丢数据 | 解析器加 `pending` 记录 |
| `_g(obj,name)` 不转发 `*args` | 带参调用全被静默吞掉 ⇒ 关系读成 0 | 转发 `*args` |
| `GetSystemValue2` 漏配置名 | 抛 `DISP_E_PARAMNOTOPTIONAL` | 传空串（当前配置） |

## 下一步（按顺序，不跳）

1. 校准 `solid_body_extent_mm` 单位：写一个自证探针（建已知 100×60×20 的板，读 bbox，比对）
2. 用校准后的坐标选 4 条板边 → `SketchUseEdge3(True, False)` → 断言草图线段 = 4
3. 逐点标「点到边」尺寸 → `SetSystemValue2` 设 10 → 断言状态 3
4. 复跑 `teach.py run` ⇒ 6/6


---

## 第 2 轮进展（2026-10-26 后半）

### 决定性判别（两条，都有读数）

`
① AddDimension 在**普通草图**里：
   点+线 → None   线+线 → None
   ⇒ 本机「成对实体」的尺寸创建**整体不可用**，与「点不能标」无关
② 孔位草图里 4 个点**逐个 sgFIXED**：
   点1→状态2  点2→状态2  点3→状态2  点4→**状态3**，圆柱面 = 4
   ⇒ 这是本机可用的全定义路径
`

### 因此实现的两种风格（hints.dimension_style）

| 风格 | 说明 | 状态 |
|---|---|---|
| ixed_points | 逐点 sgFIXED（等价于给绝对坐标） | ✅ **本机可用**，默认 |
| 	o_edge | 点到板边尺寸（业主示范的做法，参数化更好） | ❌ 被 AddDimension 阻塞 |

★ 取舍如实写进报告：ixed_points 拿不到参数化（改不了「10」这个尺寸），
  一旦尺寸 API 可用就应切回 	o_edge。habits.yaml 里可随时切换。

### 当前真机读数（	each.py run）

`
feature_count_hole      PASS (1)
hole_standard_gb        PASS (GB)
hole_sketch_constrained PASS (3)     ← 本轮打通
hole_size               PASS (M6)
hole_fastener           PASS (螺钉间隙)
cylinder_count          FAIL (2/4)   ← 仅剩这一条
`

### 仅剩的缺口：cylinder_count = 2

事实：同一套 4 个点，probe_isolate.py 里算到 **4** 个圆柱面，
而 	each.py run 里只有 **2**。两处差异待查（下一步，一次探针即可定）：
- 两处**首个孔位不同**：isolate 用 (10,10)，recipe 用 (10,50)
- recipe 路径多了一层 dimension_style 分支与 
ote() 记录

⇒ 判据：跑一个只改「首个孔位」的对照，看圆柱面数是否跟着变。
   这是可复算的取证，不靠猜。


---

## 第 3 轮：**6/6 达成**（2026-10-26）

### 定因（三组对照，一次探针）

| 组 | 首孔 | 点关系 | 点/FIXED | 状态 | 圆柱面 |
|---|---|---|---|---|---|
| A | (10,10) | **无** | 4/4 | 3 | **4** ✓ |
| B | (10,10) | **有** | 4/4 | 3 | **1** ✗ |
| C | (10,50) | **无** | 4/4 | 3 | **4** ✓ |

⇒ 真因**不是**首孔位置，而是「**点关系与逐点 FIXED 冲突**」：
  两者都在约束同样的事，SW 只能靠移动点去同时满足 ⇒ 孔被挤到一起。

### 修法

ixed_points 风格**不加点关系**（
elations_needed() 纯函数 + 测试锁住）；
	o_edge 风格靠尺寸定位置，才需要关系。

★ 上一版还把「风格降级」写在加关系**之后** ⇒ 先按 to_edge 加了 4 条关系、再降级，
  于是也踩了同一个冲突（圆柱面 2）。降级必须前移到加关系之前 —— 这条也写进注释。

### 最终真机读数（连跑 3 次，全部通过）

`
feature_count_hole      PASS (1)
hole_standard_gb        PASS (GB)
hole_sketch_constrained PASS (3)
cylinder_count          PASS (4)
hole_size               PASS (M6)
hole_fastener           PASS (螺钉间隙)
★ 结论：全部通过
`

### 现状：L1–L4 全部可用

`ash
python -B tools/teach.py capture --start/--stop      # L1 捕获
python -B tools/teach.py derive --snapshot … --out … # L2 提炼
python -B tools/teach.py profile --id owner --set …  # L4 个人化
python -B tools/teach.py run --recipe … --profile …  # L3 执行（6/6）
`

### 未尽事项（如实）

- 	o_edge 风格（点到边尺寸，参数化更好）**仍被 AddDimension 阻塞**：
  实测本机对「点+线」「线+线」一律返回 None ⇒ 保留代码，降级并记录。
  一旦尺寸 API 可用，切 habits.yaml 的 dimension_style: to_edge 即可。
- solid_body_extent_mm 的 
aw **单位不一致**（x/y 米、z 毫米）—— 已记录，
  未修（不在本目标范围，但影响任何靠 bbox 推尺寸的代码）。
