# Plan · Feature 133 读文件自定义属性

## 一、要查的官方源与冲突裁决顺序

| 序 | 源 | 本特性用它查什么 |
|---|---|---|
| 1 | 出厂类型库反射（`D:\AI\SW\_raw\reflect_sldworks\`） | **裁决者**：`ICustomPropertyManager` 的成员名与 arity |
| 2 | `C:\swapi\types\ICustomPropertyManager\*.md` | 精确签名（★ 本特性**关键**：哪个 `Get*` 有 out 参数）|
| 3 | `C:\swapi\types\IModelDocExtension\CustomPropertyManager.md` | 取管理器的入口（★ 只写 `kind: property`，**没说**要不要参数）|
| 4 | `C:\swapi\examples\Add_and_Get_Custom_Properties_Example_VB.md` 等 | ★ **调用序列**（那里 `Get(vName)` 被当**单返回值**用）|
| 5 | 本机实测 | ★ **封送形状**（属性还是方法 / out 回不回写）|

**冲突裁决**：以**出厂类型库反射**为准（铁律 4）。

## 二、★★★ 三处"文档说了但不够用"的地方 —— 全部靠实测补齐

| 文档说 | 实测 | 影响 |
|---|---|---|
| `IModelDocExtension.CustomPropertyManager` 的 `kind: property` | ★ 当**属性**取会拿到一个 **method 对象**；**必须当方法调用** `("")` | ★ 不做这一步，第一轮全是 `AttributeError: 'function' object has no attribute 'Count'` |
| `Get(FieldName) → System.string`（标 Obsolete，后继 `Get2`） | ★ **单返回值那条实测能读**；而后继 `Get2..Get6` 都带 **by-ref out** | ★★ **"更新的一代"在这里反而不可用** ⇒ 必须用 Obsolete 的 `Get` |
| 未说 out 参数在 pywin32 下如何 | `Get6(name,False,'','')` ⇒ `com_error: (-2147352571, '类型不匹配')` | ★ 与**事实 8 / 33** 同族；能力层**一律不用 `Get2+`** |

★ ★ **教训（写进 docs）**：「官方标了 Obsolete 就换后继」这条**在这里是错的** ——
  后继带 by-ref out，而 pywin32 迟到绑定处理不了 ⇒ **可用性判据是"封送形状"，不是"代数新旧"**。

## 三、包装层的形状（由探针定死）

```
取管理器（★ 必须调用）：   model.Extension.CustomPropertyManager("")
读值（★ 单返回值）：       mgr.Get(name)
读名字 / 条数 / 类型：      mgr.GetNames() / mgr.Count / mgr.GetType2(name)
★ 不用：                   mgr.Get2 .. mgr.Get6（by-ref out 在 pywin32 下报类型不匹配）
```

## 四、分层落点

| 逻辑 | 落在哪 | 为什么 |
|---|---|---|
| 取管理器 / 读值 / 读全部 | `scripts/sw_custom_property.py`（**新模块**） | 能力落 `scripts/`；别的代码也能用 |
| 工具声明（参数搬运） | `mcp-server/tool_specs_batch20.py` | 只做声明；`inject` 用默认 `"model"` |

★ 为什么**不**动 `sw_pdm`：那一族首参是 COM 对象 `pdm_document` 且**需 PDM 许可证** ⇒ 不是这条路。

## 五、风险与对策

| 风险 | 对策 |
|---|---|
| 把管理器当属性取 ⇒ 拿到 method | ★ 判据用**行为**（它有没有 `Count`），不用类型 —— 见下 |
| 用了带 out 的 `Get2+` ⇒ 类型不匹配 | 只用 `Get`；`spec.md` R7 明写 |
| 属性名不存在 ⇒ 分不清"没这个属性"还是"读失败" | 官方 `Get` 原义就是回空串 ⇒ **照原义**（负例已验），但结果里同时给 `type_code`，`0` = unknown ⇒ 可区分 |
| 配置不同 ⇒ 属性不同 | `config_name` 参数（`""` = 默认配置） |

## 六、★ 探针第一版的判据错在哪（值得记）

```
第一版：  "拿到对象" if (ok and v is not None and not isinstance(v, (str, int, float)))
问题：    pywin32 返回的 **method 对象**恰好不是 str/int/float ⇒ **判据说"拿到对象了"** ⇒ 假阳性
真机表现：mgr_obtained = true，然后**每个读都 AttributeError**
修法：    判据改为**行为** —— `hasattr(obj, "Count") and hasattr(obj, "GetNames")`
```
★ 这与**事实 155**（"恒等于分母"的假指标）同族：**判据本身不可靠时，它会伪装成"成功"**。
