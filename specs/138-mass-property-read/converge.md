# Converge · Feature 138 读质量属性

## 一、交付了什么

| 层 | 文件 | 内容 |
|---|---|---|
| 探针 | `tools/probe_mass_property_reads.py`（新增） | 答三问（取法 / 单位 / 负例）⇒ `output/mass-property-reads.json` |
| 能力层 | `scripts/sw_mass_property.py`（**新模块**） | `mass_property_object` · `mass_properties` · ★ `require_mass_property_document` · `UNITS` |
| 工具层 | `mcp-server/tool_specs_batch24.py`（新增） | **1 个**工具：`solidworks_part_mass_properties` |
| 注册 | `mcp-server/register_capabilities.py` | `BATCH_MODULES` 加 `tool_specs_batch24` |
| 证据 | `tools/capture_mass_property_evidence.py`（新增） | **数字断言** ⇒ `output/mass-property-evidence.json` |
| 能力清单 | `capabilities.yaml` | 新增 `mass_property_read`（`verified` + evidence） |

`all_specs()` 从 **77 → 78**。

## 二、★ 补的又是一个「能写不能读」的真空白（与 `specs/133` 同型）

```
★ 有 `set_mass_property_override`（**改**）却**读不出实际值**
⇒ 而「这零件多重 / 体积多少 / 重心在哪」是**最常被问的问题之一**。
★ 两次同型出现在 W3 与 W5 ⇒ ★ 这说明**这类空白有规律**：
    能改的接口先被实现，**读的接口反而没人做**（因为"改"看起来更有用）。
```

## 三、★★★ 本特性最值钱的一处：**真机负例逼出来的判据升级**

```
★ 我最初的能力层只用**行为判据**（`hasattr(mp, "Mass")`）—— 那是**照事实 161/167 定则写的**
  （那条定则本身是对的：类型判据判不出 method 对象）。
★★ 而真机负例（在**工程图**上调用）**没有抛错**：
   工程图上的 `CreateMassProperty` **竟然也返回了一个带 `Mass`/`Volume` 的对象**
   ⇒ ★ **静默通过、返回无意义读数**。
⇒ ★★★ **教训：行为判据证明"这个成员存在"，不证明"这个读数是这个文档的"**
  ⇒ 它必须**配合文档类型判据**。
⇒ 修法：`require_mass_property_document`（`GetType()==3` ⇒ 报错）。
  ★ 这是 `specs/132` 的 `require_drawing` 的**镜像用法**（一个判"必须是"，一个判"不能是"）。
★ 过程：修完**重跑真机证据** ⇒ 负例命中（`RuntimeError`），`verdict` 由 **FAIL → pass**。
  ⇒ ★ **这就是"验不过的回退、不许留在柜台上"那条纪律的实战**：
    若当时把负例当成"测试太严"而放过去，柜台上就会多一个**会返回假数据**的工具。
```

## 四、★★★ 一个如实记录的**量纲疑点**（不猜单位）

```
读数：Volume = 8000（mm³）· Density = 1000.0 · **Mass = 7999999.999999999**
★ 而 **8000 × 1000 = 8,000,000** ⇒ `mass` **恰好等于** `volume(mm³) × density`
⇒ ⚠ 若 volume 是 mm³、density 是 kg/m³，质量应是 **8 g = 0.008 kg** ⇒ **不是 8e6**
⇒ ★★★ **量纲不成立** ⇒ **`mass` 的物理单位没有确证**。
★ 处置：**照实透传** + **工具说明写明"未确证"** + ★ **不猜、不换算、不给它安一个单位**。
⇒ ★ 这条是本项目的**一贯做法**（铁律 5：查不到就说查不到）在**数值**上的应用：
    **核不出来的单位，就不给它一个名字。**
```

## 五、收敛判据

| 判据 | 结果 |
|---|---|
| `all_specs()` | 78 |
| 门禁链（8 条） | 全 exit 0 |
| 全量 pytest | **0 failed** |
| 真机证据 `verdict` | `pass`（数字断言 3 项 + 负例 1 项 + 2 条如实记录） |
| 真机验证覆盖（`docs/metrics.md` 最窄口径） | 本轮**上涨** |

## 六、遗留（明确标注）

| # | 遗留 | 为什么留着 |
|---|---|---|
| L1 | ★ **`mass` 的单位未确证** | ★ 核不出来 ⇒ **如实标注**，不猜；★ 若要查清需另立专题（可能要看官方 Remark 或做不同密度的对照实验）|
| L2 | `density` 的 kg/m³ 未在本机确认 | 同上（只在说明里标"官方惯用"）|
| L3 | 惯性矩 / 主惯性轴**未暴露** | 能力层只读了 5 个成员 |
| L4 | ⑫inspect 其余缺口（`measure_distance` / `sensors` / `status` / `check_errors` / `reference_geometry` / `analyze_geometry` / `capture_screenshot`）未挂 | 留后续批次 |
| L5 | 装配上的质量属性**未真机验证** | ★ 类型守卫**允许**装配（1/2），但**没在装配上跑过** ⇒ 如实记 |

## 七、给下一批的可复用套路（增至 13 条）

```
① 先写真机探针答"对象怎么取" —— 但**先判断要不要探针**（已有证据就别重跑）
② **先核缺口本身**（缺口名是名字级匹配）③ 能力落 scripts/，不改生成物
④ 证据走工具真实路径 ⑤ 证据必带负例 ⑥ 期望值本身也要被怀疑
⑦ 长文本进源码立刻 ast.parse（含中文时**内层引号一律用「」**）
⑧ 判据用"行为"不用"类型" ⑨ 可用性看"封送形状"，不看"代数新旧"
⑩ 对外名与对内名不同时用 `param_alias`，别改能力层形参名
⑪ "不确定就不敢断言"是对的，但"不确定"先去核一分钟，别直接降级为记录
⑫ 读一个"官方没写"的语义时，设计**对照实验**去问真机，并事先规定"若两种情况相同就说明设计错了"
⑬ ★★ **行为判据要配"对象归属"判据** —— `hasattr` 只说"成员存在"，
   不说"这个读数是这个文档的"（本轮工程图的假读数就是这么来的）
```
