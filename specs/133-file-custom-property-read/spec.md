# Feature 133 · 读文件自定义属性（砌墙 W3）

> 状态与进度不写在这里（宪法：那在 `ROADMAP.md` §一 游标 / `capabilities.yaml` / `docs/metrics.md`）。

## 一、要解决的问题：**能写却不能读**

```
· `solidworks_set_custom_properties`（**写**）—— 上游 45 个工具之一，早就在。
· ★ 能力层里**没有任何"读文件自定义属性"的实现**：
    `sw_pdm.get_custom_property_names_and_values` 要 **PDM 许可证**
    （`sw_pdm` 模块头自述「域 14 · 路由 / Composer / PDM（**需许可证**）」）——不是这条路。
⇒ ★★ **结果：能写属性，却读不回来验。** 本特性补的就是这个空白。
```

## 二、★ 本特性的范围是**核过缺口本身之后**定的（照 W2 的教训）

①会话/文档/文件在矩阵里"缺 37/41"。逐个核完分四类：

| 类 | 内容 | 判断 |
|---|---|---|
| 保存类（写） | `save_document` `save_as` `save_all` `save_as_copy` `save_file` `save_part` `save_*_template_library` | **本阶段不做**（计划明写） |
| 导出类 | `export_pdf/step/stl/iges/dwg/image` `convert_file_format` `export_with_options` | ★ **已有**（`solidworks_export_active` / `batch_export_files` / `cadstudio_write_open_format`） |
| 打开/关闭/新建 | `open_document` `close_document` `new_document` `activate_document` `rebuild_model` `part` … | ★ **已有**（上游 `open/close/new` + `sw_connect` 一族） |
| ★ **读自定义属性** | `manage_file_properties`（读那一半） | ★★ **真空白**（见 §一） |

## 三、★★★ 调用形态由真机探针定死（不是照文档猜的）

**决定性的两个坑**（`tools/probe_custom_property_reads.py`，轮 227）：

```
① ★★ `model.Extension.CustomPropertyManager` **必须当方法调用**：
     正确：  model.Extension.CustomPropertyManager("")        ← 传配置名，"" = 默认
     错误：  model.Extension.CustomPropertyManager            ← 拿到 **method 对象**
             之后每个调用都报 `AttributeError: 'function' object has no attribute 'Count'`
② ★★ 读值**只能用 `Get(name)`**（单返回值，实测能读 ✓）：
     `Get2..Get6(name, …, out Val, out ResolvedVal)` 实测报 `类型不匹配`
     （`com_error: (-2147352571)`）—— ★ 与**已知事实 8 / 33** 同族：pywin32 下 by-ref 出参不通。
```

## 四、需求（各带来源）

| # | 需求 | 来源 |
|---|---|---|
| R1 | 能读**一个**自定义属性的值 | 官方 `ICustomPropertyManager.Get`（**单返回值**）；官方示例 `Add_and_Get_Custom_Properties_Example_VB` 里 `swCustPropMgr.Get(vName)` 就是单返回值用法 |
| R2 | 能给属性的**类型**（`swCustomInfoType_e`） | 官方 `GetType2`；枚举值照官方示例 `Get_Custom_Properties_Example_VB` 逐字列出（0/3/11/30/64） |
| R3 | 能读**全部**属性（名 + 值 + 类型 + 条数） | 官方 `Count` / `GetNames` + 逐个 `Get` |
| R4 | 能按**配置**读（自定义属性可以按配置不同） | 官方 `CustomPropertyManager(ConfigName)` 的参数语义 |
| R5 | 读**不存在**的属性名 ⇒ 值回空串，**不抛** | 官方 `Get` 的对不存在名字的行为（实测如此） |
| R6 | 属性名为**空** ⇒ 必须**报错** | 本项目一贯纪律（入参不合法要报错） |
| R7 | ★ **不使用** `Get2..Get6` | 实测它们在 pywin32 下报 `类型不匹配`（见 §三 ②） |

## 五、不做什么（有据）

| 不做 | 原因 |
|---|---|
| **不写**自定义属性 | 上游 `solidworks_set_custom_properties` 已经承担；本特性只补"读"这一半 |
| 不挂 `custom_property_count` / `custom_property_names` 为**独立工具** | ★ 它们的结果**已被「读全部」包含**（后者同时回 `count` 与逐条 `name`）⇒ 挂出去只会让 AI 多调一次拿同一件事 |
| 不做 **PDM** 那一族（`get_all_external_references` 等） | ★ `sw_pdm` 需 **PDM 许可证**，且官方 swapi 里 `IPDMDocument` **0 命中** ⇒ 本机做不了（记为「不做 + 原因」） |

## 六、验收

```
① 静态：`all_specs()` 里出现 2 个新工具，且门禁全绿
② ★ 真机：`D:\AI\SW\output\custom-property-evidence.json` 的 `verdict` == "pass"，且含：
   · ★ **决定性用例**：先 `Add3` 写一个再读回来（`count` +1 且读回写入值）
   · `count_read == count_reported`
   · **两个负例**命中（不存在的名字回空不抛 / 空名字抛 ValueError）
```
