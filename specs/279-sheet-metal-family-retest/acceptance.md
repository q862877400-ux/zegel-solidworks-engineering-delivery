# Acceptance — 用带折弯的钣金件复测族成员

**Feature**: `specs/279-sheet-metal-family-retest/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 4/4 绿 · 红基线成立 · 生成器链 7/7 · 真机无残留 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★ 业务结论**: ★★ **两条「未决」都被量清了** —— ★ **开放折线是支持的**（★ 状态表那条**被证伪**）；
★★ **`create_edge_flange` 的「Mark 1」假设被证伪**（★ 三臂一样），★ 真报文是★「**无法为此特征找到适当的钣金实体**」。

## 一、逐条验收

| # | 需求 | 判据 | 读数 |
|---|---|---|---|
| FR-001 | ★★★ 开放折线的带折弯件建成 | `test_bent_part_builds_from_an_open_polyline` | ✅ `has_base_flange=True` |
| FR-002 | ★★★ 「Mark 1」假设被证伪 | `test_the_mark_one_hypothesis_is_falsified` | ✅ 三臂全失败 |
| FR-003 | ★★★ 状态表两处确实订正 | `test_status_table_is_corrected` | ✅ 按 key 取块核过 |
| FR-004 | ★★ 判据必须能红 | `test_pure_function_is_red_able` | ✅ 六组负例全红 |

## 二、★★★ 真机读数（SolidWorks **34.4.1** · ★ 走 `sw_guard` · ★ 临时零件用完关闭不保存）

### 2.1 ★★★ **开放**折线**建成了** ⇒ 状态表第 1 条**被证伪**

★ 夹具：★ **开放**折线（★ 3 段 U 形）· ★ **毫米**几何：

```
基体法兰 ⇒ '基体-法兰1'
证据：has_base_flange=True · all_solid_bodies_are_sheet_metal=True
实体 1 个 · 边 44 条 · 最长边长度 = 0.1000 m
```

⇒ ★★★ **「开放折线（轮廓法兰）真机失败」被证伪**（★ 278 与 279 **两次独立确认**）。
★ 当初失败的真因是**草图几何被 `mm()` 缩了 1000 倍**，★ **不是**「开放轮廓不被支持」。

### 2.2 ★★★ `create_edge_flange` 的「Mark 1」假设**被证伪**

★ **单变量：★ 只改「边的选择标记」**：

| 臂 | 选择 | `Select4` | 选中 | `create_edge_flange` | ★ 消息栈 |
|---|---|---|---|---|---|
| 1 | 不设 mark | `True` | 1 | ✗ | ★ **「边线-法兰1: 无法为此特征找到适当的钣金实体」** |
| 2 | **Mark 1** | `True` | 1 | ✗ | ★ **同上**（`边线-法兰2`） |
| 3 | Mark 0 | `True` | 1 | ✗ | ★ **同上**（`边线-法兰3`） |

⇒ ★★★ **三臂全失败且报文一致** ⇒ ★★ **阻塞不是选择标记** ⇒ ★★★ **「Mark 1」假设被证伪**；
★ 真阻塞在**边 / 实体的识别**（★ 那条边不被 SW 当作「可加边法兰的边」）。
★ 读数原文 `output/_probe279_family.txt`。

## 三、★★ 顺带踩的坑

★ `IEntity::Select4(Append, Callout)` 的 `Callout` **不能传 `None`**
（★ 报 `com_error: (-2147352571, '类型不匹配。', None, 2)` —— ★ **位置 2**）
⇒ ★ 用 `sw_part._empty_callout()`（★ 与 `SelectByID2` 同一个坑）。

## 四、★★★ 订正（★ `SHEET_METAL_RUNTIME_STATUS` 两条）

| 条目 | ★ 旧结论（留档） | ★ 订正 |
|---|---|---|
| `create_base_flange` | ★「开放折线（轮廓法兰）真机失败 ⇒ `True` 仅对闭轮廓成立」 | ★★ **被证伪** —— ★ 开放折线**建成了**（★ 278 + 279 两次）⇒ ★ `True` **对开放与闭轮廓都成立** |
| `create_edge_flange` | ★「剩最后一层：`CreateFeature` 需要选择状态（官方明写 with a Mark of 1）—— 未查明」 | ★★ **被证伪** —— ★ 三臂（不设 / 1 / 0）**全失败且报文一致** ⇒ ★ 阻塞**不是** mark，★ 而是**边 / 实体的识别** |

## 五、★★ 红基线（★ 六组负例）

| 变异 | 期望 | 实测 |
|---|---|---|
| 正常读数 | `[]` | ✅ `[]` |
| 件没建成 | 报错 | ✅ `['★ 带折弯的件没建成 ⇒ 夹具前提不成立']` |
| 某臂成功 | 报错 | ✅ `["★ 三臂应**全失败**…实测成功的是 ['Mark 1']", '★ 三臂报文应**一致**，实测 2 种…']` |
| 报文不一致 | 报错 | ✅ `['★ 三臂报文应**一致**，实测 2 种：{…, \'另一种\'}']` |
| 块没订正 | 报错 | ✅ `['★ 回源码核失败：create_edge_flange 那条**没有**写订正']` |
| 被证伪表不全 | 报错 | ✅ `['★ 被证伪的两句都要登记']` |

## 六、生成器链（★ 改了 `scripts/`）

| 步骤 | 结果 |
|---|---|
| `release_check.py` → `gen_level_audit.py` → `gen_metrics.py` → `gen_harvest_digest.py` → `build_union_map.py` → `gen_dead_ends.py` → `release_check.py` | **7/7 `exit 0`** |

## 七、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| 日志 | `output/_gate279.log` |

★ 真机预检前后均「**读到文档 0 个**」⇒ **无残留**。

## 八、未过门（如实登记）

1. ★★★ **`create_edge_flange` 仍未建成** —— ★ 但**阻塞已从「未查明」变成一条具体报文**
   ⇒ ★ 下一轮：★ **换边 / 核「那条边在 SW 眼里算不算钣金外轮廓」**（★ 279 只试了「最长边」一条）。
2. ★★ **`create_gusset` / `create_hem` 未复测**（★ 现在**有**带折弯的夹具了 ⇒ ★ 下一轮做）。
3. `create_one_bend`（★ 缺「选中折弯线 / 固定面」）· `create_draft`（★ 路径已改 `InsertMultiFaceDraft` · **未跑 COM**）。
4. 12 条 `arity` 接线 · 高危写盘 · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · 223 的 B1–B5 · 未提交未部署。
