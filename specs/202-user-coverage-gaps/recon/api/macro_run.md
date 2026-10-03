# 其他/宏·VBA（macro_run）

候选成员名：RunMacro / RunMacro2
命中页（2 份，同一接口 `ISldWorks`，**每份都抄**）：

- `C:\swapi\types\ISldWorks\RunMacro.md`
- `C:\swapi\types\ISldWorks\RunMacro2.md`

---

## 页头逐字段（逐字）

### 命中页 ① —— `C:\swapi\types\ISldWorks\RunMacro.md`（第 1–12 行）

```
---
type: ISldWorks
member: RunMacro
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Application Interfaces
---

# ISldWorks.RunMacro

Obsolete. Superseded by [[ISldWorks::RunMacro2]].
```

### 命中页 ② —— `C:\swapi\types\ISldWorks\RunMacro2.md`（第 1–12 行）

```
---
type: ISldWorks
member: RunMacro2
kind: method
assembly: SolidWorks.Interop.sldworks
namespace: SolidWorks.Interop.sldworks
category: Application Interfaces
---

# ISldWorks.RunMacro2

Runs a macro from a project file.
```

---

## Signature（逐字）

### 命中页 ① —— `RunMacro.md` 第 14 行

```
**Signature**: `System.bool RunMacro( System.string FilePathName, System.string ModuleName, System.string ProcedureName )`
```

- Obsolete: `Obsolete. Superseded by [[ISldWorks::RunMacro2]].`

★ **判为废弃** ⇒ 按要求去后继页抄，链条如下：

#### 后继链（逐级追到不再废弃）

| 级 | 成员 | 状态 | 依据 |
|---|---|---|---|
| 1 | `ISldWorks.RunMacro` | **Obsolete** | 页内 Obsolete 句 |
| 2 | `ISldWorks.RunMacro2` | **不再废弃**（页内无 Obsolete 句） | `RunMacro2.md` 全文无 Obsolete |

**链条终点 = `ISldWorks.RunMacro2`**（后继的 Signature 见下）。

#### 后继 ② —— `RunMacro2.md` 第 14 行（Signature 逐字）

```
**Signature**: `System.bool RunMacro2( System.string FilePathName, System.string ModuleName, System.string ProcedureName, System.int Options, out System.int Error )`
```

- Obsolete: 无

---

## Remarks（逐字）

★ 两页**都有** `## Remarks` 标题 ⇒ 按要求粘该段全文，不写「官方没写」。

### 命中页 ① —— `RunMacro.md` 第 24–25 行

```
## Remarks
See [SOLIDWORKS Macros](<../../docs/Types of SOLIDWORKS API Applications/SOLIDWORKS Macros/Overview.md>) for details.
```

### 命中页 ② —— `RunMacro2.md` 第 26–33 行

```
## Remarks
If you specify swRunMacroUnloadAfterRun for Options, then the macro is unloaded from the VBA IDE after running.

Use the path and filename of the compiled DLL for the FilePathName argument for a .NET macro. By default, the procedure is called **Main** in a C# macro. Because C# is case sensitive, you must specify **Main** for ProcedureName in this method.. See **Running a C# DLL from VBA** in the **Example** section.

Running a macro from an add-in application, standalone .exe, or VBA macro is supported. Running a .NET macro from a .NET macro is also supported, but only if both .NET macros were created using the same VSTA version.

See [SOLIDWORKS Macros](<../../docs/Types of SOLIDWORKS API Applications/SOLIDWORKS Macros/Overview.md>) for details.
```

（注：上面 `this method..` 的双句点是**原文照抄**，未改。）

---

## Examples

**无。**

- `RunMacro.md` 全文无 `## Examples` 标题。
- `RunMacro2.md` 全文无 `## Examples` 标题（★ 其 Remarks 正文里提到「See **Running a C# DLL from VBA** in the **Example** section」，但**本页不存在该段**，示例文件在官方 Example 页而非本页 ⇒ 不补、不猜）。

**AccessSelections 全文搜索结果**：

| 页 | `AccessSelections` 命中数 | 判定 |
|---|---|---|
| `RunMacro.md` | 0 | — |
| `RunMacro2.md` | 0 | — |

⇒ **非指针族**。

---

## 指针族 / 本仓现状

### 指针族

— （两页 `AccessSelections` 均为 0 命中 ⇒ **不是指针族**。）

### 本仓现状（`D:\AI\SW\scripts\` + `D:\AI\SW\mcp-server\`）

搜索模式 `RunMacro2?\b`，全文件类型（`*.py` / `*.md` / `*.json` / `*.yaml` / `*.yml` / `*.txt`）命中 2 个文件：

| 文件 | 命中 | 性质 | 是否算实现 |
|---|---|---|---|
| `D:\AI\SW\scripts\sw_api_sldworks.py` | L8884-8885 `'RunMacro': 3,` / `'RunMacro2': 4,`；L25581-25582 `'RunMacro': 177,` / `'RunMacro2': 270,` | **生成的反射索引**（`scripts/sw_api_*.py`，按纪律**排除**） | **否**（仅反射索引，不算实现） |
| `D:\AI\SW\scripts\sw_com_traps.py` | L115 注释 `ISldWorks.RunMacro2(..., Int32&)  5 参、末 1 个 [out] ✅`；L205 / L212 起 `RUN_MACRO_ERROR` 枚举常量字典 | 注释 + 第三方转录的枚举常量，**全文无 `.RunMacro(` / `.RunMacro2(` 调用** | **否**（无调用） |

补充核实：

- `D:\AI\SW\mcp-server\` —— 搜 `Macro` **0 命中**（无任何宏工具、无任何调用）。
- `D:\AI\SW\scripts\sw_macro_guard.py` —— 搜 `RunMacro` **0 命中**（该模块是 VBA **文本生成**防护层，与本成员无关）。
- `D:\AI\SW\scripts\*macro*` / `D:\AI\SW\tools\*macro*` —— 除 `sw_macro_guard.py` 外无同名模块。

⇒ **本仓无 `RunMacro` / `RunMacro2` 的实现**。

---

## 抄录纪律声明

- 全部内容逐字来自 `C:\swapi\types\ISldWorks\RunMacro.md`（34 行）与 `RunMacro2.md`（45 行）**全文**。
- 未改任何已有文件；未运行 SolidWorks；未运行 pytest。
- 拿不准处已在正文标注，未用相近名字替代、未补全。