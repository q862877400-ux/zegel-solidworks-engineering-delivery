# Acceptance — `create_draft` 首次真机验证

**Feature**: `specs/283-create-draft-machine-verified/`
**日期**: 2026-10-10
**结论**: ✅ **四件齐 · 判据 5/5 绿 · 红基线成立 · 生成器链 7/7 · 真机无残留 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**
**★★★ 业务结论**: ★★★ **`create_draft` 真机建出来了**（★ 新特征 **`拔模1`**）
⇒ ★ **规格 239 的路径改动（`IFeatureManager::InsertMultiFaceDraft`）是对的**；
★ 前提是**两个**选择：★ **方向项（mark 1 · 一个平面）** + ★ **待拔模面（mark 2）**。

## 一、逐条验收

| # | 需求 | 判据 | 读数 |
|---|---|---|---|
| FR-001 | ★★★ 只给面 ⇒ 18 臂全失败 | `test_face_only_always_fails` | ✅ 报文恒定 |
| FR-002 | ★★★ 加方向项 ⇒ 成功 | `test_adding_a_direction_reference_succeeds` | ✅ `拔模1` |
| FR-003 | ★★★ 282 假说的反例 | `test_it_is_a_counterexample_to_the_282_hypothesis` | ✅ |
| FR-004 | ★★★ 状态表升为 `True` | `test_status_entry_is_promoted_to_true` | ✅ |
| FR-005 | ★★ 判据必须能红 | `test_pure_function_is_red_able` | ✅ 六组负例全红 |

## 二、★★★ 真机读数 1（SW **34.4.1** · ★ 走 `sw_guard` · ★ 夹具 = 方块 60×40×20 mm）

| 臂 | 选择 | 结果 | ★ 消息栈 |
|---|---|---|---|
| 6 面 × 3 标记（`mark2` / `mark2+1` / 不设） | 面 | ✗ **全失败** | ★ **「此拔模方向尚未定义。」** |

⇒ ★★★ **排除「选错了面 / 选错了标记」** —— ★ 18 臂报**同一条**。

## 三、★★★ 真机读数 2（决定性）

```
★ Front Plane + 面#0 ⇒ 选中 2 · **成功** ✓（'拔模1'）
```

★★★ **`create_draft` 真机建出来了**：★ 新特征 **`拔模1`**，★ 选中 **2** 个（平面 + 面）。
★ 而 `create_draft` 的 docstring **本来就写着**「方向项 **mark 1**、待拔模面 **mark 2**、拔模边 **mark 4**」
⇒ ★★ **文档是对的，是**调用方**没照它选**（★ 与事实 503 同族：★ 选区必须由 `pre_call` 重建）。
★ 读数原文 `output/_probe283_draft.txt` · `output/_probe283_draft_dir.txt`。

## 四、★★★ 顺带：★ 282 那条假说的**反例**

★ 282 的假说：★「本机的特征创建 API **似乎吃不到「边 / 面」类选择**」（★ 只有 2 个样本）。
★★ 本轮：★ `InsertMultiFaceDraft` **吃得到面选择**（★ 只要同时给方向项）
⇒ ★★★ **假说被削弱** —— ★ 「吃不到」**不是普遍现象**，★ 而是**按 API 逐个**看的。

## 五、★★★ 订正（★ `SHEET_METAL_RUNTIME_STATUS["create_draft"]`）

| 项 | 内容 |
|---|---|
| ★ 旧值 | ★ **`(None, …)`** = **未测**（★ 239 是离线切片） |
| ★★★ 新值 | ★★ **`(True, …)`** = **真机验证可用**（★ 且写明**两个选择**的前提） |
| ★ 详细理由 | ★ 写在 `#:` **注释**里 —— ★ 吸取 **282 的教训**：★ 长文本写进**字符串**会推移预选门禁的否定窗口 |

## 六、★★ 红基线（★ 六组负例）

| 变异 | 期望 | 实测 |
|---|---|---|
| 正常读数 | `[]` | ✅ `[]` |
| 臂数不对 | 报错 | ✅ `['★ 应 18 臂，实测 6']` |
| 报文不对 | 报错 | ✅ `['★ 报文应是「此拔模方向尚未定义」']` |
| 没记特征名 | 报错 | ✅ `['★ 决定性那臂没记特征名']` |
| 需求不是两条 | 报错 | ✅ `['★ 需要**两个**选择（方向项 + 待拔模面）']` |
| 路径不对 | 报错 | ✅ `['★ 路径应是 `InsertMultiFaceDraft`']` |
| 表仍写「未测」 | 报错 | ✅ `['★ `create_draft` 那条**仍写着「未测」而没有订正**']` |

## 七、生成器链（★ 改了 `scripts/`）

| 步骤 | 结果 |
|---|---|
| `sync_bundled_skill.py` → `gen_level_audit.py` → `gen_metrics.py` → `gen_harvest_digest.py` → `build_union_map.py` → `gen_dead_ends.py` → `sync_bundled_skill.py` | **7/7 `exit 0`** |

★ 改完**先 `ast.parse`**（★ 282 的教训：★ 语法错会被下游门禁伪装成别的错）。

## 八、门禁全套 @3.14.7

| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| 日志 | `output/_gate283.log` |

★ 真机预检前后均「**读到文档 0 个**」⇒ **无残留**。

## 九、未过门（如实登记）

1. ★★★ **`SaveAs3` 未真机验证**（★ `sw_connect.py:1167` · ★ §三 C **已授权** · ★ **改错会直接坏掉写盘**）。
2. ★★★ **`create_profile_center_mate` 未真机验证**（★ §三 C **已授权**）。
3. ★★ **`create_draft` 的 `pre_call` 未接**（★ 要照 `tool_specs_batch74.py::_select_faces_for` 的形状）
   ⇒ ★ 否则 MCP 表面**仍然**建不出来（★ 事实 503）。
4. 12 条 `arity` 接线 · `DeleteRenderMaterial` · 4 处 `needs-feature-data` · 223 的 B1–B5 · 未提交未部署。
