# Converge · Feature 133 读文件自定义属性

## 一、交付了什么

| 层 | 文件 | 内容 |
|---|---|---|
| 探针 | `tools/probe_custom_property_reads.py`（新增） | 答三个未知 + 决定性用例；产物 `output/custom-property-reads.json` |
| 能力层 | `scripts/sw_custom_property.py`（**新模块**） | `custom_property_manager` · `custom_property_count` · `custom_property_names` · `custom_property` · `custom_properties` · `SW_CUSTOM_INFO_TYPES` |
| 工具层 | `mcp-server/tool_specs_batch20.py`（新增） | **2 个**只读工具：`..._custom_property_get` / `..._custom_property_list` |
| 注册 | `mcp-server/register_capabilities.py` | `BATCH_MODULES` 加 `tool_specs_batch20` |
| 证据 | `tools/capture_custom_property_evidence.py`（新增） | 真机验证 ⇒ `output/custom-property-evidence.json` |
| 能力清单 | `capabilities.yaml` | 新增 `file_custom_property_read`（`verified` + evidence） |

`all_specs()` 从 **65 → 67**。

## 二、★ 本特性补的是一个**真空白**，而且它很典型

```
★ 本仓库**早就能写**自定义属性（`solidworks_set_custom_properties`，上游工具），
  却**读不回来**（能力层里没有读的实现；`sw_pdm` 那条路要 PDM 许可证）
⇒ ★★ **"能写不能读" = 写了属性没法验。** 这类空白比"少一个功能"更值得补。
★ 而真机验证的第一条就是**先写再读回来** —— 直接对着这个空白验。
```

## 三、★★★ 探针又抓到我自己一个**假阳性判据**（本轮最值钱的一条）

```
第一版判据： "拿到对象" if (ok and v is not None and not isinstance(v, (str, int, float)))
真机表现：   mgr_obtained = **true**，然后**每个读都 AttributeError: 'function' object ...**
真因：       pywin32 把 `Extension.CustomPropertyManager` 封成了一个 **method 对象**，
             而 method **恰好不是** str/int/float ⇒ **判据说"拿到了"**。
修法：       判据改成**行为** —— `hasattr(obj, "Count") and hasattr(obj, "GetNames")`
```
★ 这与**事实 155**（"恒等于分母"的假指标）同族：
  **判据本身不可靠时，它会伪装成"成功"**，而下游错误信息（`'function' object has no attribute`）
  指向的是**症状**，不是判据。

## 四、★★ 一条可复用的定则（本轮新得出）

```
★ **"官方标了 Obsolete 就换后继"这条不总对** —— 可用性判据是**封送形状**，不是**代数新旧**：
    · `Get(FieldName) → string`      **Obsolete**，但**单返回值** ⇒ ★ **实测能读** ✓
    · `Get2..Get6(…, out Val, out ResolvedVal)` 更新，但**带 by-ref out** ⇒ ★ **实测报类型不匹配**
  ⇒ ★ 本特性**故意用 Obsolete 那个**，并把这个理由写进了 `spec.md` 的 R7 与代码注释。
★ 同族先例：事实 8（`AddSelectionListObject` 的 bool 不可信）· 事实 33（`Callout` 必须传 VARIANT）
  · 事实 47（`I` 前缀指针变体 pywin32 到不了）。
```

## 五、收敛判据

| 判据 | 结果 |
|---|---|
| `all_specs()` | 67 |
| 门禁链（8 条） | 全 exit 0 |
| 全量 pytest | **0 failed** |
| 真机证据 `verdict` | `pass`（1 决定性用例 + 2 负例） |
| 真机验证覆盖（`docs/metrics.md` 最窄口径） | 本轮**上涨** |

## 六、遗留（明确标注，不假称完成）

| # | 遗留 | 为什么留着 |
|---|---|---|
| L1 | `editable`（`IsCustomPropertyEditable`）**没读到**，回 `null` | ★ 实测没成功 ⇒ **如实留空**，已写进 capability 的 limitations |
| L2 | 只验了**默认配置**（`config_name=""`） | 按配置读的路径**未真机验证**（需要一个多配置文档） |
| L3 | **PDM** 那一族（引用文档、PDM 自定义属性）没做 | ★ `sw_pdm` 需 **PDM 许可证**，且官方 swapi 里 `IPDMDocument` **0 命中** ⇒ 本机做不了（记为「不做 + 原因」） |
| L4 | 保存类（`save_as` / `save_all` / 模板库）没做 | 计划明写本阶段不碰高风险写操作 |

## 七、给下一批（W4）的可复用套路（增至 9 条）

```
① 先写真机探针回答"对象怎么取" ② **先核缺口本身**（缺口名是名字级匹配）
③ 能力落 scripts/，不改生成物 ④ 证据走工具真实路径 ⑤ 证据必带负例
⑥ 期望值本身也要被怀疑 ⑦ 长文本进源码立刻 ast.parse
⑧ ★ **判据要用"行为"，不要用"类型"**（本批的假阳性就是这么来的）
⑨ ★ **可用性看"封送形状"，不看"代数新旧"**（Obsolete 的反而能用）
```
