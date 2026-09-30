# 阻塞报告：`pilot` 有 13 条落在你 B1 规则的空档里（执行方 → 改 AGENTS.md 的对话）

> **结论**：你的 B1 写着「旧 `pilot` **无运行证据时**一律迁 `stitched`」——
> 但实测 19 条里 **13 条有运行证据**（非空 `verified_versions`）。**那一支你没定，我停在这里等你裁。**

---

## 一、先纠正一句我差点执行的错

我上一份回复里默认接受了「`pilot` 口径不清（跑过还是写了分不清）」这个前提。
**实测不是** —— `pilot` 在上游有明确定义，写在编排器的能力表里：

```python
"drawings_and_bom": _CapabilityDefinition(
    CapabilityLevel.PILOT,
    (MAIN_SKILL, "solidworks-engineering-drawing"),
    ("solidworks_generate_drawing", "solidworks_review_drawing", "solidworks_inspect_drawing"),
    "工程图处于 Pilot，GB/T 第一角图框、BOM、尺寸链和钣金展开证据必须人工复核，禁止无人值守宣称完成。",
),
```

**⇒ `pilot` = 「有实现、跑了，但证据不足以无人值守 ⇒ 必须人工复核」**
**⇒ `stitched` = 「代码已并入、从未运行」** —— **两者语义不重合，甚至方向相反。**

**⇒ 若按「一律迁 `stitched`」执行，13 条有版本证据的能力会被写成「从未运行」——
那不是保守，是假话。**（保守是「低报」，这是「错报」。）

---

## 二、`pilot` 编码了**两个**事实，而新五级只拆出了其中一个

### 实测的两个维度

```
level × allowed_modes 交叉（28 条）：
  verified         interactive+reviewed    8 条
  pilot            interactive+reviewed   18 条
  pilot            reviewed                1 条
  not_implemented  interactive             1 条
```

**⚠ 注意：`allowed_modes` 里根本没有 `unattended` 值** —— 它只有 `interactive` / `reviewed`。

### 那「能不能无人值守」靠什么判？靠 `level`

```python
# scripts/capabilities.py:213
def unattended_allowed(capability_ids, payload=None) -> bool:
    """@brief 判断一组能力是否允许无人值守执行。"""
    return all(capability_level(cid, payload) == "verified" for cid in capability_ids)
```

调用面（**这条安全属性是真的**）：

```
apps\desktop\cad_workbench\engineering_orchestrator.py:356   ← 桌面编排器
scripts\sw_capability_probe.py:142
tests\test_cad_reliability.py:15,41,42
tests\test_engineering_orchestrator.py:121,146
tests\test_sw_capability_probe.py:41
```

### ⇒ 所以 `pilot` 同时说的是两件事

| 事实 | 现在由谁编码 |
|---|---|
| **跑没跑 / 证据多强** | `level` |
| **允不允许无人值守** | **也是 `level`**（`verified` 才许） |

**新五级把「谁跑的」拆出来了（`source_verified`），但没把「允不允许无人值守」拆出来。**
**⇒ `pilot` 无处可去 —— 这是 schema 缺口，不是迁移选择问题。**

---

## 三、13 条有证据的 `pilot`，逐条摆出来

| capability_id | `verified_versions` | 迁 `stitched` 会说成 | 
|---|---|---|
| `external_spur_gear_geometry` | `["2026"]` | 从未运行 |
| `parameter_updates` | `["2024","2026"]` | 从未运行 |
| `custom_properties_and_bom` | `["2024","2026"]` | 从未运行 |
| `pack_and_go` | `["2024","2026"]` | 从未运行 |
| `motion_study` | `["2024"]` | 从未运行 |
| `drawings_and_bom` | `["2024","2026"]` | 从未运行 |
| `headless_open_format_writing` | `["OCP 7.9.3.1.1"]` | 从未运行 |
| `configurations_and_design_tables` | `["2026"]` | 从未运行 |
| `sheet_metal` | `["2026"]` | 从未运行 |
| `weldments` | `["2026"]` | 从未运行 |
| `simulation_and_fea` | `["CalculiX 2.23"]` | 从未运行 |
| `autocad_script_backend` | `["2024"]` | 从未运行 |
| `autocad_dotnet_backend` | `["2024"]` | 从未运行 |

**另 6 条 `verified_versions` 为空，你的规则覆盖得到，迁 `stitched` 没有异议**：
`dfm_checks` · `surface_modeling` · `mold_tools` · `autocad_headless_preview` · `dxf_preview_scene` · `routing`

---

## 四、三条可选解法（**裁断归你，我只给证据与后果**）

### 选项 A · `pilot` → `verified` + 把「不许无人值守」交给 `allowed_modes`

**做法**：
1. 13 条有证据的 → `verified`（跑过了，这是事实）
2. **给 `allowed_modes` 加合法值 `unattended`**
3. 迁移时：原 8 条 `verified` **补上** `unattended`；原 19 条 `pilot` **不补**
4. `unattended_allowed()` 从「看 level」改成「看 `allowed_modes` 含不含 `unattended`」

**后果**：
- ✅ 两条事实各归其位，新五级的语义边界干净
- ✅ 无人值守闸门**不放松**（13 条仍不许无人值守）
- ⚠ 改了一个**安全函数的语义** —— 要同步改它的 6 处调用与 3 个测试文件
- ⚠ 引入 `allowed_modes` 的第二个合法值集，多一处枚举

### 选项 B · 保留第六级

**做法**：枚举从五个变成六个，`pilot` 留作「跑过但不许无人值守」。

**后果**：
- ✅ 数据不用改，语义不丢
- ❌ **直接违反你定的「枚举恰好五个」**（提案 L26）
- ❌ 你反对过的「旧值腐坏」问题回来一半

### 选项 C · 按原案迁 `stitched`

**做法**：13 条也迁 `stitched`。

**后果**：
- ✅ 最保守，绝不高报，A7 稳过
- ❌ **13 条被写成「从未运行」= 与 `verified_versions` 自相矛盾**
      （同一份数据里说「跑过 2026」和「从未运行」）
- ❌ 后续要升回 `verified` 得重新补证据 —— 而那些证据**现在就在数据里**

---

## 五、我倾向 A，但理由说给裁断用

**倾向 A 的理由**：它让 `level` 只回答一个问题（证据强度），
无人值守回答另一个问题（授权）。**现在这两个问题被一个字段同时回答**，那本身就是腐坏的来源 ——
`pilot` 之所以无处可去，正是因为「跑过」和「不许无人值守」被焊在一起了。

**但我必须先说清 A 的风险**：它动的是**安全闸门的判据**。
如果 `allowed_modes` 的迁移漏了任何一条，那条就会**从「需复核」变成「可无人值守」或反过来**。
⇒ 所以 A 必须**同批**做三件事：加值、改函数、改 6 处调用 + 3 个测试文件，缺一即红。

**如果你判 C**，我也照做 —— **但请把「13 条与自身 `verified_versions` 矛盾」记成已知限制**，
不要让它悄悄存在。

---

## 六、我这边的状态

**已完成**：基线（`2 failed / 738 passed / 15 skipped`，2 个是已记录的上游基线失败）。

**已停在这里**：`level` 数据迁移 —— **因为一改数据，`scripts/capabilities.py:36-37` 的
`load_capabilities()` 立刻 `raise`，而 `pilot` 的目标值未定。**

**等你裁断后我一次做完**：`VALID_LEVELS` 换五级 + 删 pilot 豁免 + 迁数据 + 逐条过 13 个测试文件 + bump `schema_version`。

**另**：`provenance`（B2）现在**无处可加** —— 现有 28 条全是自研能力，没有一条是来源派生的。
它是给「并进来的 349 条」用的字段，落地要等 B 级并入开始。**这不是问题，是顺序。**
