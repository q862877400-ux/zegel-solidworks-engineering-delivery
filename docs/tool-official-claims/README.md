# 官方依据台账 · 格式与写者须知

> 门禁：`python -B scripts/check_tool_official_claims.py --report`
> 判据出处：`specs/353-mcp-tool-official-audit/spec.md` §二

**一句话**：每个 MCP 工具交一条记录，证明「它调用哪些官方 API、它那句模型可见的说明有出处」。
★ **锚点必须逐字出现在所指文件里**（只忽略 markdown 排版）——凭印象写的句子过不去。

## 一、一条记录长什么样

```json
{
  "tool": "solidworks_extrude_boss",
  "impl": "scripts/sw_part.py:extrude_boss",
  "claim": "Create a solid boss by extruding an existing sketch.",
  "claim_evidence": {
    "kind": "official",
    "path": "C:/swapi/types/IFeatureManager/FeatureExtrusion3.md",
    "anchor": "Creates an extruded feature."
  },
  "members": [
    { "interface": "IFeatureManager", "member": "FeatureExtrusion3",
      "path": "C:/swapi/types/IFeatureManager/FeatureExtrusion3.md",
      "anchor": "Creates an extruded feature." },
    { "interface": "IModelDoc2", "member": "ClearSelection2",
      "path": "C:/swapi/types/IModelDoc2/ClearSelection2.md",
      "anchor": "Clears the selection list." }
  ],
  "allowed_non_com": [],
  "verified": { "by": "lead", "at": "2026-11-01",
                "method": "read official page",
                "notes": "官方 Remarks 要求先 SelectByID2 选草图；工具已内置该前置。" }
}
```

### 字段规则

| 字段 | 规则 |
|---|---|
| `tool` | 必须与 `tools/list` 的工具名逐字一致 |
| `impl` | `相对路径:函数名`（相对仓库根）。写者**不要**改实现 |
| `claim` | **逐字等于**该工具 `doc` 的首句（门禁会比对） |
| `claim_evidence.kind` | `official`（官方页）/ `impl`（本仓实现）/ `runtime`（真机读数/测试） |
| `claim_evidence.path` + `anchor` | `anchor` 必须是该文件里的**原文片段**（可带 `**`，比对时会归一化） |
| `members[]` | 实现里调用的每个 COM 成员一条；`path` 给官方页；`anchor` 抄页里的原文 |
| `allowed_non_com` | 提取器误当成 COM 成员的（如 `items`），写 `{"name":"items","why":"…"}` |
| `verified` | `by` / `at` 必填；`notes` 写「读了哪页、确认了什么、有没有发现不符」 |

### 官方页确实查不到时（铁律 5）

**不许编页**。写：

```json
{ "interface": "ICWStudyManager", "member": "CreateNewStudy3",
  "documented": false,
  "gap": "C:\\swapi\\types 无此接口；已查 AI Solidworks\\官方文档\\SWhelp\\cosworks 与 sldworksapi，均无此成员页" }
```

门禁把它记为 `member-undocumented`（**报表项**），不拦发布，但**台账里看得见**。

## 二、一次核验的动作（每工具 5 分钟）

1. `python -B tools/gen_tool_official_claims.py --tools <名字> --out output/draft-<名字>.json`
   —— 拿到「实现调了哪些成员 + 官方页 + 页里的原始描述行」。
2. **打开每个官方页读**：Description / Parameters / Remarks。★ 只抄锚点不算核验。
3. 对照工具 `doc` 首句：它说的和官方页 + 实现**是不是同一件事**？
   - 是 ⇒ 填 `claim_evidence`（挑一句**支持这句**的原文）+ `verified`。
   - 不是 ⇒ 先改 `doc`（改完 `claim` 要跟着改），再填证据；
     若发现实现错了，**别在本规格改实现** —— 记进该批报告，另立规格。
4. 跑 `python -B scripts/check_tool_official_claims.py --only <名字> --report`。

## 三、写者纪律

- 一个批次一个文件（`B1.json` … `B8.json`），**不要动别的批次的文件**。
- 以 `_` 开头的文件是草稿，门禁不读；★ 别把草稿改名当成品提交。
- 核完一批，跑一次全量 `--report`，把该批的 `no-record` 清零，然后 `--write-baseline`
  让待核清单降下来（**只许降**）。

## 四、官方源清单（未登记成员必须逐棵查过）

| 源 | 覆盖 | 形态 |
|---|---|---|
| `C:\swapi\types\<接口>\<成员>.md` | sldworks / swconst（566 个接口） | 有 Description / Signature / Remarks |
| `C:\cworks_en\api\*.html` | **Simulation / Topology / 部分 Costing**（2704 页） | .NET 参考页，有描述句 |
| `AI Solidworks\官方文档\SWhelp\sldworksapi\*.html` | sldworks 老快照（11498 页） | ★ 多数**只有签名与语言过滤**，无散文说明 |
| `AI Solidworks\官方文档\SWhelp\cosworks\*.html` | ICWLoadsAndRestraintsManager（45 页） | 正文嵌在 script 里，抽取物见 `_raw/cosworks_pages/` |
| `C:\cworks_vb6\*.html` | VB6 声明（2842 页） | 只有签名 |
| `C:\cworks_manual\*.html` | 手册页（776 页） | 视页面而定 |
| `_raw/reflect*/iface_*.txt` | 出厂类型库（**冲突裁决者**） | 只有签名，**不能当语义锚点** |

★ **再查一遍**：`python -B tools/audit_undocumented_members.py --write`
  它会把「有描述页」的升级成正式证据（页 + 逐字锚点），把「只有签名 / 全无」的写进
  `gap`（含查过哪几棵源、出厂类型库的签名行）。★ 不跨接口兜底：同名成员在多个接口上
  有页时**不猜**，宁可判「查不到」。
