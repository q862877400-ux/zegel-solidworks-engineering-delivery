# 四家外部 MCP 项目 × 官方签名对账

> **这份文件做什么**：把四家外部开源 SolidWorks MCP 项目代码里**对官方 API 的调用**抽出来，
> 逐个与**官方源**对账，看调用形状与官方签名差在哪。
>
> ★★ **这份文件的头条结论被三裁判改写过一次** —— **原来的表按现状不可辩护**，
> 下面用的是**按裁判指正返工后**的数；裁判原话与 9 条缺陷全部留在 §五，**一条没删**。
>
> **来源与口径**
> - **四家**（克隆在 `C:\swprojects\`）：`Eduardof0nt`（MIT）· `andrewbartels1`（MIT）·
>   `vespo92/SolidworksMCP-TS`（MIT）· `Slacker-LLC`（Apache-2.0）。共 **307 个代码文件 / 5.01 MB**。
> - **官方源（三个，都只读）**：`C:\swapi\types\`（**8238** 个成员名）·
>   反射清单 `_raw\**\iface_*.txt`（**11117** 个）· CHM 解包（**28655** 份）。
> - **抽取**：Bunny（`opencode-zen` / `space-bunny-free`）**95 个 job**（每 job ≤6 文件 / ≤70 KB）。
> - **核验**：① 引文逐字回查（先原样、后归一化）；② 过两个结构化索引；③ 三个裁判。
> - ⚠ **本文件不含行号**。

## 一、★ 先说结论的**边界**（不改口径就没法读这张表）

| 事项 | 说明 |
|---|---|
| **措辞** | 只用「**在我们核过的三个源里查不到**」，**不说「与官方签名不一致」、更不说「他们错了」**。反射清单只覆盖 **15 个 interop 程序集** ⇒ 缺席 ≠ 不存在（铁律 5）。 |
| **分母有两个** | 「**真调用**」（剔除 docstring / VBA 字符串 / 伪代码）与「**含 `cannot_tell`**」两个口径**都报** —— 两者给出的率差最多 **近 3 倍**。 |
| **不可横比** | 四家的**调用/工具**比从 **1.22 到 3.91**（`Eduardof0nt` 只 2 个代码文件、大量委派）⇒ 按调用点加权会放大"重复封装"的一方。 |
| **CHM 那条已撤** | 我原先写「125 个里 37 个在 CHM 里有 ⇒ 我们源不全」—— **裁判逐名核：0/37 是成员页**（那 37 是**子串文件计数**，如 `SldWorks` 15673、`Item` 3304）⇒ **本条结论已撤回**。 |
| **★ 三源皆无的正确数** | 原写 **125**，**V2 独立复核后更正为 162** —— 那 37 个之所以不在 125 里，只因我的 `in_chm` 记的是**子串命中数**；**V2 重扫确认 37/37 在 swapi 与反射里同样查不到** ⇒ 应记「未判定」而非「源里有」。 |

## 二、统计

| 指标 | 数 |
|---|---|
| 四家代码文件 | **307**（2 / 231 / 59 / 15） |
| 抽出的调用点 | **1635** |
| —— 引文逐字命中（原样） | 1599 |
| —— **归一化空白后补回** | **+16** |
| —— 判定为**非调用**（docstring / VBA / 伪代码） | **258** |
| **可用的真调用** | **1360** |
| 回写后的 verdict | `match` 1148 · **`not_in_checked_sources` 185 行 = 162 个去重名字** · `cannot_tell` 187 · `argc_mismatch` 115 |

## 三、逐项目（**两个口径都报**）

| 项目 | 真调用 | 工具 | 调用/工具 | 缺陷数 | **率（真调用）** | **率（含 `cannot_tell`）** |
|---|---|---|---|---|---|---|
| `Eduardof0nt` | 228 | 187 | 1.22 | 86 | **37.7%** | 40.8% |
| `SolidworksMCP-TS` | 403 | 103 | 3.91 | 87 | **21.6%** | 33.5% |
| `andrewbartels1` | 486 | 128 | 3.80 | 53 | **10.9%** | **29.8%** |
| `Slacker-LLC` | 243 | 92 | 2.64 | 6 | **2.5%** | 5.3% |

★ **「缺陷」= + `argc_mismatch`**（名字查不到 + 实参个数与官方签名不同）。
★ **两个口径下排序都是** `Eduardof0nt` > `TS` > `andrewbartels1` > `Slacker-LLC`；
★ 但 **`andrewbartels1` 从 10.9% 跳到 29.8%（近 3 倍）**，
与 `TS` 几乎并拢 ⇒ **单报一个口径会误导**（这条是裁判 V3 预测、我返工后证实的）。

### 3.1 ★ 与 `AGENTS.md` §4.2 的独立事实**方向一致**（但**不当因果**用）

`AGENTS.md` 记着：工具最多的那家（187）**仓库内测试文件数为 0**；四家里**只有 `Slacker-LLC` 声明全工具真机跑过**，而它工具数最少（92）。
本表两个口径下 **`Eduardof0nt` 最高、`Slacker-LLC` 最低**。

⚠ **这只是方向一致，不是因果**：
① 分母是调用点不是工具；② `cannot_tell` 分布不均；③ 四家代码组织方式差异极大（2 个文件 vs 231 个）。
⇒ **要立因果需要按工具抽样、逐工具核**（本批没做，见 §六）。

## 四、`cannot_tell` 拆成三因（**返工项 2**）

| 原因 | 数 |
|---|---|
| `argc_unresolvable`（调用处实参个数数不出：`*args` / 模板变量） | 126 |
| `receiver_unresolved`（接收者归不到哪个接口） | 52 |
| `swapi_no_signature`（swapi 该页无 `Signature` 行） | 9 |

⇒ ★ **原来只有一个 `cannot_tell` 数字（187 / 11.4%），它其实混装了三种完全不同的东西** ——
这是裁判 V1 指出的判据缺陷，不是数据问题。

## 五、三裁判（**一条没删**）

**V1 审计者（`deepseek-official` / `deepseek-flash`）** · 抽检 12 条 · **不同意我 5 个数** · **8 条判据缺陷**
**V3 复算者（Bunny）** · 独立重算 · **6 处与我报告不一致** · **7 条方法学问题**
**V2 对抗者（Bunny）** · ⛔ **两次返回 NULL —— `space-bunny-free` 路由当时不可用，本件未过 V2**

### 5.1 V1 报出的判据缺陷（8 条）

1. cannot_tell 混装四种原因：125 条「调用处实参个数数不出来」（*args、模板变量）、52 条「接收者接口归不到」、9 条「swapi 页无 Signature」、1 条官方无页 ⇒ 11.4% 不是单一含义。
2. 官方源优先级有洞：swapi 页缺 **Signature** 行（或只有 front-matter）就直接 cannot_tell，而铁律 4 说冲突以出厂类型库为准 —— 反射里形参个数明明可用（GetCount、Sheet）。
3. 缺一档 verdict：「名字存在、但不是被调用接口的成员」（DimensionType→IDisplayDimension、ID→IEdmFolder5）无处可放、被塞进 member_not_found；这比「名字不存在」更常见。
4. argc_mismatch 不区分「只少传尾部 out 形参」：3 条 has_out_variant=true（SaveAs2 6vs8），少传 out 在 pywin32 下是常见写法；该标志也不可靠。
5. verdict 不随复核回写：22 条名字在官方源里查得到（3 条 swapi 有页 + 19 条只在反射）仍写 member_not_found，且被计入缺陷率 ⇒ 自审字段 _mnf_class 与 verdict 自相矛盾。
6. 抽取层把非调用当调用：${methodName} 这种模板占位、getattr/属性名元组探测、生成给 SW 跑的 VBA 字符串都进了账（TS 593 条里 192 条来自 vba-*.ts）⇒「一次调用」的口径没定义。
7. evidence 逐字判据太硬：36 条未命中里 16 条只是换行/空白差异（归一化后原样就在文件里）⇒「那些要作废」会连带作废 16 条其实站得住的记录。
8. 接收者归属没有独立判据：52 条「归不到接口」里多数在同一个函数上文就能定名（GetCount 的 eqn_mgr），且里面藏着 3 条实参个数真不等的（GetNames 1vs0、GetMaterial 1vs2、Edit 0vs3）。

### 5.2 V3 报出的方法学问题（7 条）

1. 分母是调用点不是工具：Eduardof0nt 187 工具/238 调用(1.27)，TS 103 工具/609 调用(5.9)，EditRebuild3 在 TS 出现 12 次；按调用点加权会放大重复封装的一方。
2. cannot_tell 187 条分布极不均（andrew 18.9%、TS 12.1%、另两家约 3%），其中 126 条是我方 argc 解不出；全算缺陷则 andrew 11.6%→30.5%、TS 24.6%→36.8%，排名翻转。
3. 缺陷率把源侧假阴性记成对方缺陷：206/207 条 mnf 只「不在 swapi 与反射清单」，而反射只覆盖 15 个程序集 ⇒ 只能写「我们核过的源里查不到」，不能写「与官方签名不一致」。
4. 分子混入非 COM 调用点：90 行 note 自述是 docstring / VBA / 伪代码（ev_ok 85），9 行被判 argc_mismatch（如 TS AddConfiguration 是往 VBA 宏 push 的串）。
5. argc 口径不统一：mnf 里 34 行 argc=None、62 行 argc=0（属性式）；66 行标 has_out_variant 却没说 out 是否计入 argc，属性与带默认值的长签名不能用单一 argc 判。
6. 两行 verdict 自相矛盾：1 条 argc_mismatch 的 official_argc 为 None 却判不一致；1 条 member_not_found 却 official_found=True，应退回。
7. 36 条 evidence 未命中剔除是对的，但剔除量按项目不均（TS 16 / Eduardof0nt 10 / andrew 10 / Slacker 0），四家基数因此不同，横比须一并注明。

### 5.3 裁判抽到的逐条实例（V1 的 12 条抽检里最关键的 4 条）

| 项目 | 成员 | 我们原判 | 裁判判 | 谁对 | 依据 |
|---|---|---|---|---|---|
| `Eduardof0nt` | `CreateMassProperty2` | member_not_found | match | **他们** | swapi types\IModelDocExtension\CreateMassProperty2 |
| `Eduardof0nt` | `StartRecordingMacro` | member_not_found | member_not_found | **我们** | sw_client.py:1454 逐字「app.StartRecordingMacro(outpu |
| `SolidworksMCP-TS` | `CreateNewStudy3` | member_not_found | match | **他们** | 反射 iface_cosworks.txt:2598 逐字「CWStudy CreateNewStu |
| `Slacker-LLC` | `ViewZoomtofit2` | member_not_found | match | **他们** | 反射 iface_sldworks.txt:10046 逐字「Void ViewZoomtofit2 |
| `Eduardof0nt` | `AddComponent5` | argc_mismatch | argc_mismatch | **我们** | sw_client.py:971 逐字「comp = doc.AddComponent5(file_ |
| `andrewbartels1` | `SaveAs2` | argc_mismatch | argc_mismatch（差的是尾部两个 out） | **我们** | pywin32_adapter.py:2387 逐字「ext.SaveAs2(resolved_pa |
| `SolidworksMCP-TS` | `CreateDetailViewAt4` | argc_mismatch | argc_mismatch | **我们** | vba-drawing.ts:126-132 逐字「Set swView = swDraw.Crea |
| `Eduardof0nt` | `GetCount` | cannot_tell | match | **他们** | sw_client.py:1305-1306 逐字「eqn_mgr = _get(doc, 'Get |
| `andrewbartels1` | `GetNames` | cannot_tell | cannot_tell | **我们** | docs_discovery.py:212 逐字「names = typeinfo.GetNames |
| `Slacker-LLC` | `SelectByID2` | match | match | **我们** | sw_core.py:654 逐字「return bool(target.SelectByID2(n |
| `andrewbartels1` | `ActiveDoc` | match | match（但这是它生成的 VBA 文本） | **我们** | vba_generation.py:268 逐字「vba_code = f"""Sub Create |


### 5.4 ★ V2 对抗者（Bunny）—— **它推翻了标题里的一个数**

V2 把攻击面**扩到全部 125 个名字**（不止我要求的 10 个），并用了**官方源的超集**
（`C:\swapi` 全部 **16254** 个 `.md` / **12364** 个唯一名 > 我用的 8238；`_raw` 全部 **15** 个 `iface_*.txt` /
**11120** 个裸成员名 > 我用的 11117）；另用 `Select-String` 独立复核 12 个名字。
**结论：125 这条推不翻（零反例）** —— 唯一疑似命中 `Depth2` 逐字是
`iface_cosworks.txt` 里 `Void SetIncludeRegionDepth2(Boolean)` 的**子串误报**。

★ **但它指出我标题那句话本身错了**：

| 我说的 | 实际 |
|---|---|
| 「**185 个名字**在三个官方源里都查不到」 | **185 是调用点行数**；去重后是 **162 个名字** |
| 「125 个三源皆无」 | 那 37 个只是 **CHM 子串命中**（噪声）；**V2 重扫确认 37/37 在 swapi 与反射里同样查不到** ⇒ **可辩护的三源皆无 = 162 个** |

V2 的 `argc_mismatch` 复核还指出：**8 条里有 5 条其实该判 `cannot_tell`**（官方同名有 0 参/多参重载，
判定器只取了其中一页的签名）⇒ **`argc_mismatch` 这一栏有高估**（已记入限度）。

## 六、⚠ 明确记下的限度

* ✅ **三裁判已齐**（V1 DeepSeek · V2 Bunny 对抗 · V3 Bunny 复算）；V2 **零反例**但**更正了标题里的名字数**（185 行 → 162 名 → 162 三源皆无）。
* ⚠ **`argc_mismatch` 有高估**：V2 复核 8 条里 **5 条该归 `cannot_tell`**（官方有同名重载，判定器只取了一页签名）⇒ 该栏 115 这个数**偏大**。
* ⚠ **不做因果**：缺陷率差异与"有没有测试 / 有没有真机跑过"**方向一致**，但本批**没有按工具抽样**，
  因此**不能**说"因为他们没测所以错得多"。
* ⚠ **反射清单只覆盖 15 个 interop 程序集** ⇒ 「查不到」只能是**我们核过的源里查不到**。
* ⚠ **未按工具抽样**：`Eduardof0nt` 187 个工具只有 228 个调用点（1.22/工具），
  `TS` 103 个工具 403 个调用点（3.91/工具）⇒ **两家的覆盖率不可比**。
* ⚠ **`argc_mismatch` 未区分「只少传尾部 `out` 形参」**（pywin32 的常见写法）——
  裁判点名要单列一档，本批**没做**（返工清单第 8 项，缺 V2 无法定稿）。
* ⚠ CHM 那条结论**已撤回**（§一）；CHM 在本件里**不再作为判据**。
* ⚠ 四家代码**只读，未执行**：本件判的是「调用形状 vs 官方签名」，**不是「能不能跑」**。
