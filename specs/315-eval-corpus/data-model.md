# Data Model: 评测语料（315）

**对应**：`specs/315-eval-corpus/spec.md` §3 Key Entities

---

## §1 三份语料的共同形状

三份都是 YAML 列表，每个元素是一个**条目对象**。共同字段：

| 字段 | 类型 | 必填 | 说明 |
|---|---|---|---|
| `id` | string | ✅ | `L1-001` / `L2-001` / `L3-001` |
| `needs_owner_judgment` | bool | ✅ | **true = 有字段需要业主判**（不许 AI 冒充定论） |
| `notes` | string | | 起草说明 / 不确定处 |

---

## §2 L1 · 主干局部任务

```yaml
- id: L1-001
  product_class: 板件            # 板件 | 轴件 | 夹具 | 平口钳 | 连杆 | 箱体
  task: 在一块 100×60×20 的板上，四角各打一个 M6 通孔，孔心距边 10mm
  tools:                          # ★ 链的列表：允许多条正确链
    - [solidworks_sketch_start, solidworks_sketch_add_rectangle,
       solidworks_sketch_end, solidworks_extrude_boss,
       solidworks_hole_wizard, solidworks_part_mass_properties]
  readback:                       # ★ 必填：回读判据
    - 孔数 = 4
    - 孔径 = 6mm
    - 体积 = 100×60×20 − 4×π×3²×20
  difficulty: easy                # easy | medium | hard
  needs_owner_judgment: true      # 工具链对不对要业主判
  notes: 工具链是候选，需业主确认是否等价
```

### 字段约束

| 字段 | 约束 |
|---|---|
| `product_class` | 必须是 6 类之一 |
| `tools` | **非空**；每条的每个工具名**必须存在于真实工具面** |
| `tools` 的链 | 每条链**非空**；允许多条链（方案逐字：「同一任务允许多个正确工具链」） |
| `readback` | **非空**；至少 1 条 |
| `difficulty` | `easy` / `medium` / `hard` |

---

## §3 L2 · 长尾覆盖任务

```yaml
- id: L2-001
  target_group: 模具              # ★ L2 独有：本条要覆盖的工具组
  task: 对已建好的分型件做拔模分析，报出需要拔模的面
  tools:
    - [solidworks_mold_draft_analysis, solidworks_mold_evidence]
  expected_groups: [模具]         # ★ 首选链应命中的组（防误召回）
  forbidden_groups: [草图, 工程图] # ★ 明确不该被召回到的组
  readback:
    - 返回的面数 ≥ 0
    - 证据文件已生成
  needs_owner_judgment: true
  notes: 模具组 7 个工具，本条覆盖其中 2 个
```

### 字段约束

| 字段 | 约束 |
|---|---|
| `target_group` | 必须是**工程任务组**之一（见 §6） |
| `expected_groups` | **非空** |
| `forbidden_groups` | 可空；用于**防误召回**判据 |

---

## §4 L3 · 语义案例

```yaml
- id: L3-001
  requirement: 给我设计一台台式平口钳
  category: missing_input          # solvable | missing_input | capability_boundary | adversarial
  split: dev                       # dev | blind
  labels:
    function: 夹持工件、可开合、可锁紧
    interface: 底座固定孔位
    question: 缺开口度、缺夹紧力、缺行程
    result: WAITING_INPUT          # 期望的结果状态
  needs_owner_judgment: true
  notes: 标签是 AI 起草，需业主确认「缺的项对不对」
```

### 字段约束

| 字段 | 约束 |
|---|---|
| `category` | 4 类之一；**总量必须精确 24/12/12/12** |
| `split` | `dev` 或 `blind`；**总量必须精确 20/40** |
| `labels` | 四类**全必填**：`function` / `interface` / `question` / `result` |
| `labels.result` | 必须是受控词表之一（见 §5） |
| **近似变体不跨组** | 若两条是近似变体，`split` 必须相同 |

---

## §5 `labels.result` 的受控词表

| 值 | 含义 |
|---|---|
| `READY_FOR_REVIEW` | 自动流程完成，待人工审核 |
| `WAITING_INPUT` | 缺关键输入，等用户回答 |
| `REJECTED_OUT_OF_SCOPE` | 能力圈外，应拒 |
| `REJECTED_UNSUPPORTED` | 能力圈内但工具做不到 |
| `REJECTED_AMBIGUOUS` | 需求歧义，需澄清 |

> ⚠️ **这份词表是 AI 起草的** —— 若业主认为该改，改这里。

---

## §6 工具组清单（L2 的覆盖目标）

**来源**：按工具名首词分组（`register_capabilities.all_specs()`）。

| 组 | 工具数 | 组 | 工具数 |
|---|---|---|---|
| 其他 | 110 | 配置 | 8 |
| 仿真 | 53 | 导出 | 8 |
| 草图 | 45 | 运动 | 8 |
| 工程图 | 31 | 模具 | 7 |
| 装配 | 25 | 拉伸 | 5 |
| 视图 | 22 | 会话 | 5 |
| 成本 | 19 | 证据收集 | 4 |
| 拓扑 | 17 | 属性 | 4 |
| 焊件 | 15 | 方程 | 4 |
| 钣金 | 13 | Toolbox | 4 |
| 零件 | 12 | 旋转 | 3 |
| 选择 | 11 | 交付 | 3 |
| 曲面 | 8 | 圆角 / 读回 / 截面 | 各 2 |
| 孔 / 特征 | 各 8 | 单工具组（12 个） | 各 1 |

> ⚠️ **「其他」110 个工具是最大的组** —— 说明**按首词分组不足以表达任务域**。
> 这本身是一个发现（对应外部方案 Q4「任务域该按什么维度划」）。
> **本规格的做法**：L2 对「其他」组**按二级词再分**，避免 110 个工具只被 1 条覆盖。
