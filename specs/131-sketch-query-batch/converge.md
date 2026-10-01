# Converge · Feature 131 草图只读查询

## 一、交付了什么

| 层 | 文件 | 内容 |
|---|---|---|
| 能力层 | `scripts/sw_sketch.py`（追加） | `sketch_by_name` · `resolve_sketch` · `count_lines` · `count_arcs` · `count_segments` · 常量 `ELEMS_PER_LINE` / `ELEMS_PER_ARC` |
| 工具层 | `mcp-server/tool_specs_batch18.py`（新增） | 4 个只读工具，**全声明式** |
| 注册 | `mcp-server/register_capabilities.py` | `BATCH_MODULES` 加 `tool_specs_batch18` |
| 证据 | `tools/capture_sketch_evidence.py`（新增） | 真机验证，产出 `output/sketch-evidence.json` |
| 前置探针 | `tools/probe_sketch_object_routes.py`（上一轮） | ★ 定下"取草图对象只能按名取" |

`all_specs()` 从 **58 → 62**。

## 二、★ 本特性的核心价值：**真机验证抓到两件事，静态门禁一件都没抓到**

```
当时的状态：门禁全绿 · 同步 305 文件 · pytest 1274 passed · 62 个工具全部挂载成功
⇒ ★ 然后**第一次真机调用就失败**。
```

| # | 抓到什么 | 性质 | 处置 |
|---|---|---|---|
| **D1** | `sw_part.current_sketch_name` 在**草图已关闭**时回**英文 fallback**「Sketch1」，而中文 UI 下真名是「草图1」⇒ **必然找不到** | ★ **真 bug** | 新增 `resolve_sketch`：中英文候选名 → 特征树兜底 → 抛错 |
| **D2** | 我的**期望值写错了**：以为"画了 1 个圆"就不该有弧 ⇒ 断言 `count_arcs == 0` | ★ **判据错，不是代码错** | 改正期望值（**不是放宽判据**）+ 把「整圆算一段弧」写进工具说明 |

★ **D1 的意义**：这条纪律（A 与 B 必须配对）当场付了回报 ——
  **若只挂不验，柜台上会多 4 个"看起来对、一调就错"的工具。**

## 三、收敛判据（全会话级）

| 判据 | 结果 |
|---|---|
| `all_specs()` | 62 |
| 门禁链（8 条） | 全 exit 0 |
| 全量 pytest | 0 failed |
| 真机证据 `verdict` | `pass` |
| 真机证据含负例命中 | 是（2 条） |
| ★ 真机验证覆盖（`docs/metrics.md` 的最窄口径） | 本轮**上涨**（新增 4 个成员位次） |

## 四、遗留（明确标注，不假称已完成）

| # | 遗留 | 为什么留着 |
|---|---|---|
| L1 | `sw_sketch` 还有 **21 个**只读函数没挂（`get_sketch_contours` / `get_splines` / `get_sketch_points` …） | 本批只取了 4 个最有代表性的；其余同型，可照本批的包装层**直接扩展** |
| L2 | 草图的**写**操作（加几何 / 加约束 / 改尺寸）没做 | 需要另一套验证（要能断言"加完之后形状对不对"），另开特性 |
| L3 | `sw_part.current_sketch_name` 的 fallback 行为**本身没改** | ★ 改它会动到既有调用点；本批用 `resolve_sketch` **包住**它，风险更小。**建议后续单独开特性**评估（它的 fallback 语义在别的调用点里可能仍是对的） |

## 五、给下一批（W2 工程图）的可复用套路

```
① 先写真机探针回答"对象怎么取"（★ 本批证明：这一步会推翻按命名直觉做的设计）
② 能力逻辑落 scripts/（薄函数），工具声明只做参数搬运
③ 证据脚本**走工具真实路径**（import 批次的 helper），不是只调底层函数
④ 证据里**必须带负例**（错名字 / 错形状 —— 证明守卫真的在尽职）
⑤ ★ 期望值本身也要被怀疑：本批就错在期望值上
```
