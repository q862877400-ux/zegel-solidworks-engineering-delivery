# S3 真机验证 · E1 判据能看见真实坏样件

**日期**: 2026-10-25

**对应任务**: `specs/350-first-part-delivery/tasks.md` T012（第 3 条前半句）

**依据**: `docs/ENGINEERING-PATH.md` 第六节 S3 第 3 条

> 先核官方签名、Remarks、示例和死路限制，再做限定真机试验。
> **先验证检查器能看见真实坏样件，再验证生成方法。**

---

## 一、结论

**成立。** 判据对真机的两个状态分别给出正确结论：

| 真机状态 | `GetConstrainedStatus()` | 判据结论 |
|---|---:|---|
| 欠约束矩形（4 段，无关系） | **2** | **fail**（状态 2：欠定义） |
| 对 4 段全加 `sgFIXED` 后 | **3** | **pass**（状态 3：完全定义） |

读数与官方表逐字吻合：`2 = swUnderConstrained`、`3 = swFullyConstrained`。

证据：`output/s3-e1-real-machine-evidence.json`（`ok: true`）与
[`source-verification.md`](source-verification.md) 的三源互证。

## 二、为什么这个顺序不能反

`ENGINEERING-PATH.md` 把「先验证检查器」写在「再验证生成方法」前面，理由是：

> 否则做出来的东西没有任何东西能验它。

具体到本项目：如果我先把板件生成改造成「尺寸与关系驱动」，再去想怎么验，
那「验」的标准就会被**已知的生成结果**牵着走 —— 这正是
`docs/state/facts/R-engineering-path.md` 记的四个伪造手法的成因
（判据是照着已有输出写的，所以它总说「合格」）。

所以本轮的顺序是：

1. 先查官方签名与枚举表（三源互证，见 `source-verification.md`）
2. **先证明判据能拒绝真机上的真实坏样件**（本文件）
3. 再谈改造生成方法（S3 后续）

## 三、怎么做的（可重跑）

```powershell
python -B tools\sw_guard.py --timeout 300 -- python tools\probe_s3_e1_real_machine.py
```

探针步骤：

1. `connect_solidworks()` → 新建零件
2. `start_sketch("Front Plane")` → `CreateCornerRectangle` 画 20×20 mm 矩形
3. 读 `ISketch.GetConstrainedStatus()` ⇒ **2**
4. 把读数喂给 `judge_sketch_constraint` ⇒ **fail**
5. 选中全部 4 段 → `add_sketch_relation("sgFIXED")`
6. 再读 ⇒ **3**
7. 再喂给判据 ⇒ **pass**
8. 收尾关掉**自己开的**文档

实测输出（护栏日志里的子进程 stdout）：

```
① 欠约束草图：GetConstrainedStatus = 2
   → 判据结论：fail（★ 状态 2：欠定义 ⇒ 未满足 E1）
② 草图段数 = 4
   选中段数 = 4
③ 全固定后：GetConstrainedStatus = 3
   → 判据结论：pass（★ 状态 3：完全定义 ⇒ 满足 E1）
```

## 四、这次验证覆盖了什么、没覆盖什么

### 覆盖了

- `GetConstrainedStatus()` 在真机上调得动，返回 `int`
- 该读数**有区分度**（2 与 3 不同，不是常量）
- 读数与官方枚举表的语义**对得上**（不是「读了但不知道是什么」）
- `judge_sketch_constraint` 的枚举分支在真机数据上**两态都对**

### 没覆盖（如实）

| 项 | 为什么没覆盖 |
|---|---|
| `swOverConstrained`（4）的真机验证 | 本轮只造了欠约束与全约束两态 |
| `swNoSolution`（5）/ `swInvalidSolution`（6） | 需要构造病态草图，本轮未做 |
| `swAutosolveOff`（7） | 需要关自动求解，本轮未做 |
| **数值自由度** | 三源确认 API 无此入口，**验不了**（见 `source-verification.md`） |
| 「有意保留自由度」 | 同上，无法从模型反读，只能靠需求声明 |

★ 上表后两行是**确认的限制**，不是待办。
★ 前三行是**待补的验证**，S3 后续可以补，但它们不影响本轮结论 ——
  本轮要证的是「判据能看见真实坏样件」，用 2 与 3 两态就够了。

## 五、一个连带发现：`S3` 不受 `S2` 需求冻结阻断

先前我把 S3 判成「被 S2 需求冻结阻断」，**这是错的**，本轮更正。

`ENGINEERING-PATH.md` 第六节 S3 的五步逐条核对：

| S3 步 | 需要 S2 的八项吗 |
|---|---|
| 1 尺寸与关系驱动（位置/方向/大小完整约束） | ❌ |
| 2 稳定语义引用 + 孔型孔位逐项回读 | ❌ |
| 3 官方签名 → 限定真机试验 | ❌ |
| 4 同一交付件副本改主参数 | ❌ |
| 5 E5 最难的一个必需尺寸/基准标注小验证 | ❌ |

S3 验的是**几何与参数化行为**；八项（材料/载荷/安全等级/工艺/基准/接口/图样范围/交付目的）
影响的是 **E6 工艺**、**E4 基准**、**E5 图样**、以及**强度** —— 属 **S4 及以后**。

⇒ 阻断的是 S4，不是 S3。本轮据此推进了 S3 真机。

## 六、下一步（S3 剩余）

| # | 做什么 | 为什么还没做 |
|---|---|---|
| 1 | 板件改成尺寸与关系驱动的方法 | 需要改生成路径并真机验证 |
| 2 | 三处 `index:0` 改成语义选择器 | 要先改工具层 `selection` 支持语义形态 |
| 3 | 同一交付件副本改主参数（E2/E3 的核心） | 需要已交付件，且要在副本上做 |
| 4 | 孔型从特征参数回读接上 | `judge_hole_readback` 目前对孔型回 `unknown` |
| 5 | E5 最难标注的小验证 | 需先确认图样 API 到不到得了 |

★ 第 2、4 项**必须真机验证**，不能只看代码改对了。
★ 第 3 项是 E2 的关键：`run_stage2_plate.py` 的 `run_change` 现在是**新建文档重跑**，
  按 `R-engineering-path.md` R-10，那不叫「改已交付件」。
