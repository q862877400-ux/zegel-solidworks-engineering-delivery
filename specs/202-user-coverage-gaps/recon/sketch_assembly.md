<!-- domain: 草图/装配 -->

# 草图 / 装配 —— 官方成员逐字抄录

抄录规则：官方签名整行照抄；抄不到写「官方没写」；本仓现状 = `D:\AI\SW\scripts\` 与 `D:\AI\SW\mcp-server\` 内 grep 该成员名的命中（`__pycache__\*.pyc` 为编译产物，未列入）。

| 功能 | 官方成员 | 签名 | 官方例子 | 本仓现状 | 指针族 |
|---|---|---|---|---|---|
| 样条曲线 | `ISketchManager.CreateSpline2` | `**Signature**: \`SketchSegment CreateSpline2( System.object PointData, System.bool SimulateNaturalEnds )\`` | 无 | `scripts\sketch_relations.py:222`、`:240`、`:274`、`:277`、`:281`、`:283`、`:284`；`scripts\sw_api_sldworks.py:8438`、`:25135`；`scripts\sw_part.py:568`、`:574`、`:587`、`:590`；`mcp-server\tool_specs_batch54.py:14` | — |
| 完全定义检查 | `ISketch.GetConstrainedStatus` | `**Signature**: \`System.int GetConstrainedStatus()\`` | 无 | `scripts\sw_api_sldworks.py:2565`、`:2612`、`:8240`、`:19466`、`:19513`、`:24937` | — |
| 爆炸视图 | `IAssemblyDoc.CreateExplodedView` | `**Signature**: \`System.bool CreateExplodedView()\`` | 无 | `scripts\sw_assembly_doc.py:110`；`scripts\sw_api_sldworks.py:1780`、`:7272`、`:18703`、`:23999` | — |

## 逐项溯源事实（搜索过程原文）

### ① 候选成员名递归搜 `C:\swapi\types\`

| 功能 | 候选（按顺序试） | 结果 |
|---|---|---|
| 样条曲线 | `CreateSpline2` | 存在 → `C:\swapi\types\ISketchManager\CreateSpline2.md`（**采用**） |
| 样条曲线 | `CreateSpline` | 存在 → `C:\swapi\types\IModelDoc2\CreateSpline.md`、`C:\swapi\types\ISketchManager\CreateSpline.md`（**未采用**：前一个候选已命中） |
| 完全定义检查 | `GetConstrainedStatus` | 存在 → `C:\swapi\types\IComponent2\GetConstrainedStatus.md`、`C:\swapi\types\ISketch\GetConstrainedStatus.md`（**采用** `ISketch` 那一份 —— 功能域为「草图」） |
| 爆炸视图 | `CreateExplodedView` | 存在 → `C:\swapi\types\IAssemblyDoc\CreateExplodedView.md`（**采用**）、`C:\swapi\types\IPartDoc\CreateExplodedView.md` |
| 爆炸视图 | `AutoExplode` | 存在 → `C:\swapi\types\IAssemblyDoc\AutoExplode.md`（**未采用**：前一个候选已命中） |

**「完全定义检查」与「爆炸视图」两栏的官方成员名同名存在于两个接口下** —— 上面写的是按功能域选定的那一份，另一份的存在如实记在此处。

### ② 未采用的同族成员（仅备查，未抄签名）

- `C:\swapi\types\IModelDoc2\CreateSpline.md`
- `C:\swapi\types\ISketchManager\CreateSpline.md`
- `C:\swapi\types\IComponent2\GetConstrainedStatus.md`
- `C:\swapi\types\IPartDoc\CreateExplodedView.md`
- `C:\swapi\types\IAssemblyDoc\AutoExplode.md`

### ③ 官方例子目录搜索

`C:\swapi\examples\` 存在，递归共 **2839** 个文件；按「文件名含成员名」逐个查 `CreateSpline2` / `CreateSpline` / `GetConstrainedStatus` / `CreateExplodedView` / `AutoExplode` —— **全部 0 命中**，故三栏「官方例子」均写「无」。

（注：被采用的三份 md 的 `## Examples` 段各自列了若干 `../../examples/*.md` 链接，如 `Get_Sketch_Constraints_Example_VB.md`、`Create_Exploded_Views_Example_VB.md`、`Insert_a_Composite_Curve_Example_VB.md` —— 但这些**文件名里不含成员名**，按本任务「文件名含即可」的口径仍算「无」。）

### ④ `AccessSelections` 全文串搜

对被采用的三份 md 全文各搜一次 `AccessSelections`：

| md | `AccessSelections` |
|---|---|
| `ISketchManager\CreateSpline2.md` | 无 → `—` |
| `ISketch\GetConstrainedStatus.md` | 无 → `—` |
| `IAssemblyDoc\CreateExplodedView.md` | 无 → `—` |

⇒ 三栏「指针族」均为 `—`，无一项是 `⚠ 指针族`。

### ⑤ 本仓 grep 命中行原文（抽样，非全部）

```
scripts\sw_part.py:568         ① `CreateSpline2(arr, False)` ⇒ 返回 **None** ⇒ `get_sketch_segments` = **0**
scripts\sw_part.py:590         "ISketchManager.CreateSpline2 返回 None ⇒ **样条没建出来**（本机实测，轮 141）。"
scripts\sketch_relations.py:222  #           SketchSegment CreateSpline2(Object Points, Boolean Simulate)  ← 2 参
mcp-server\tool_specs_batch54.py:14  #       `CreateSpline2` 返回 None（且此前是静默的）· 重绘后仍 0 段（排除了官方那句"必须重绘"）·
scripts\sw_api_sldworks.py:2565      'GetConstrainedStatus': 0,
scripts\sw_api_sldworks.py:19466     'GetConstrainedStatus': 51,
scripts\sw_assembly_doc.py:104       'AutoExplode': 0,
scripts\sw_assembly_doc.py:110       'CreateExplodedView': 0,
```

⇒ 三项在本仓**均有命中**，故三栏「本仓现状」都不是「无」。

### 未执行

- 未运行 SolidWorks，未运行 pytest。
- 未修改任何已有文件；本文件为本次唯一新建文件（`D:\AI\SW\specs\202-user-coverage-gaps\recon\` 目录此前不存在，随本文件一并创建）。