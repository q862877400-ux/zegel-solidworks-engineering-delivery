# vd50-A · assembly —— 「能力 level 与真机证据」逐条核对

> 范围：`capabilities.yaml` 里**装配域**的条目。判据三问：① `level: verified` 引的 evidence 文件**是否真的存在**；② **证据文件里的结论与条目写的是否一致**；③ 有没有「**证据否定、条目写成肯定**」（最严重，单列）。
> 只读核对，**未改动仓内任何文件**；本文件是本轮唯一写入。

---

## 0 · 核了哪些条目

装配域共 **4 条**带 evidence 的条目，全部 `level: verified`：

| id | label | level | evidence 条数 | 引用的文件是否都存在 |
|---|---|---|---|---|
| `assembly_and_mates` | 装配体与配合 | verified | 3 | ★ 2 在 · 1 在（**结论对不上**，见 F1） |
| `assembly_read` | 装配只读 | verified | 2 | ✔ 2 在（**结论一致**） |
| `motion_study` | 旋转马达 Motion Study | verified | 1 | ★ 在（**结论对不上**，见 F2） |
| `motion_validation_and_preconditions` | 运动算例的验收与前置检查 | verified | 1 | ✔ 在（**结论一致**） |

**核了 4 处条目 · 核了 8 个 evidence 引用 · 对不上 3 处。**

> ★ 说明：`custom_properties_and_bom` / `drawings_and_bom` / `weldments` 等虽也挂了 `solidworks_collect_assembly_bom` / `solidworks_weldment_create_profile_center_mate`，但其 `label` 属 BOM / 焊件域，按「本片只做装配域」**未纳入**。

---

## ★★★ F1 —— 最严重类：证据是否定结果，条目写成肯定

### 判定：**成立**

### 一句话依据
`assembly_and_mates` 标 `level: verified`、label 是「装配体与**配合**」，但它引的**唯一**真机证据 `output/in-context-reference-smoke.json` 顶层写着 `"verdict": "fail"`，而条目正文只把失败写成「⚠ 还没绿」的括注、**结论位仍留在 `verified`**。

### 仓内那一段（capabilities.yaml · `assembly_and_mates`）

```
"id": "assembly_and_mates",
"label": "装配体与配合",
"level": "verified",
```

同条 evidence 里的**失败**被降格成括注：

```
⚠ **判据①②（关系数 N→N+1 · 外部参考 0→≥1）还没绿**（`add_relation` 调用形态未解决）
⇒ **外部参考还没真的建立，未取证**（8/11）。
```

### 证据/目标那一段（`output/in-context-reference-smoke.json` · 文件实际写的）

```
"passed": 9,
"total": 12,
"verdict": "fail",
```

两条失败的判据在文件里是**带 `ok: false` 的实打实的 check 条目**：

```
"★★ 判据①：`GetRelationsCount` **N → N+1**（空操作不变）": {
  "ok": false,
  "detail": "0 → 0"
},
"★★ 判据②：外部参考计数 **0 → ≥1**（空操作不变）": {
  "ok": false,
  "detail": "0 → 0"
},
```

### 三点补充（都是可搜索的原文，不含推测）

1. ★ **分母也对不上**：条目写 **8/11**，文件写 **`"passed": 9, "total": 12`**。两处数字都不是对方的值。
2. ★ 该脚本按**自己写的**口径算分母 —— `tools/verify_in_context_reference_smoke.py` 里 `ev.update(passed=sum(1 for c in checks if c), total=len(checks),` ⇒ ★ 分母只能是 `len(checks)`，而文件里 `checks` 字典**逐条数得 12 项** ⇒ **「11」这个数在该脚本口径下不可能出现**。
3. ★★ **`mcp_tools` 里没有任何一个「建配合」的工具**：该条目挂的是
   ```
   "mcp_tools": ["solidworks_assembly_check_interference",
                 "solidworks_assembly_list_components",
                 "solidworks_assembly_list_mates"]
   ```
   ⇒ 三个**全是只读**；而全仓 `tests/` 与 `tools/` 里 grep 六个建配合函数名（`add_mate_coincident` / `add_mate_concentric` / `add_mate_distance` / `add_mate_parallel` / `add_mate5_checked` / `add_concentric_mate_by_cylinders`）**命中 0 处** ⇒ ★ label 里的「配合」二字，**本条目没有任何建成证据**。

> ★ 与「文件不存在」无关：`tools/verify_in_context_reference_smoke.py` 与 `output/in-context-reference-smoke.json` **都在**，问题只在**结论定性**。

---

## ★★★ F2 —— 同属最严重类：`motion_study` 的证据不含它自称的内容

### 判定：**成立**

### 一句话依据
`motion_study` 标 `verified`、label 是「**旋转马达** Motion Study」，evidence 自称是「（旋转马达创建与结果审计）」，但它引的 `tests/test_sw_motion_audit.py` **一次都没建过马达** —— 只调 `collect_motion_study_summary` 与 `validate_motion_study_summary`，且马达是文件自己造的 `FakeMotionFeature`。

### 仓内那一段（capabilities.yaml · `motion_study`）

```
"id": "motion_study",
"label": "旋转马达 Motion Study",
"level": "verified",
...
"evidence": [
  "pytest tests/test_sw_motion_audit.py（旋转马达创建与结果审计）"
],
```

### 证据/目标那一段（`tests/test_sw_motion_audit.py` · 文件实际写的）

被引作「旋转马达创建」的证据里，马达是**纯造假对象**：

```
class FakeMotionFeature:
    """@brief 模拟真实旋转马达 Motion Feature。"""
    Name = "旋转马达"
    GetType = 102
    GetTypeName2 = "AEMRotationalMotor"
```

该文件引用 `sw_motion` 的**全部**符号只有两个，**都不是建马达**：

```
sw_motion.collect_motion_study_summary
sw_motion.validate_motion_study_summary
```

### 三点补充（都可搜索）

1. ★★ 全仓 `tests/` 里 **0 处**调用 `add_constant_speed_rotary_motor` ⇒ evidence 所称的「旋转马达**创建**」在任何 pytest 里**都没有被覆盖**。
2. ★★★ 而仓里**自己的真机证据是反的** —— `output/motor-e2e-replica.json`：
   ```
   "motor_on_s1": {
     "ok": false,
     "error": "RuntimeError: 创建旋转马达 FeatureData 失败"
   },
   ```
   同一文件里 `"motor_on_s2": {"ok": true, "type": "CDispatch"}` ⇒ ★ **同一函数两个组件一个成一个败**。
3. ★★★ 同域另一条 `animation_export` 的 limitations 里，本仓**自己**已经把这个结论写死了：
   ```
   `add_constant_speed_rotary_motor_by_cylinders` **真机 `ok: false`**
   ```
   ⇒ ★★ **同一份 capabilities.yaml 里，一条记「真机 ok:false」、另一条把同族能力标 `verified` 并声称「旋转马达创建」已被 pytest 覆盖。**

> ★ 该条并非全无真机证据：`output/motion-evidence.json`（`ensure_type_library` / `study_manager` / `create_study` / `validate_studies` 五步全 `ok:true`、`verdict: pass`）是实的 —— 但那份证据**属于 `motion_validation_and_preconditions`**，**不含马达**。

---

## ★ F3 —— 数字与现状对不上（较轻，单列）

### 判定：**成立**

### 一句话依据
`assembly_read` 的第二条 evidence 写「两个『钉死数量』守卫已同步：**all_specs() 81 / 协议层 126**」，而这两个「钉死」现在分别是 **277** 与 **322** —— 守卫早已同步到别的数，条目里的数字停在旧值。

### 仓内那一段（capabilities.yaml · `assembly_read`）

```
"pytest tests（全量 0 failed；两个「钉死数量」守卫已同步：all_specs() 81 / 协议层 126）"
```

### 证据/目标那一段（当前实际值）

`tests/test_server_wiring.py` 里的硬编码守卫：

```
assert len(all_specs()) == 277
```

`tests/test_mcp_protocol_layer.py` 里的硬编码守卫（含它自己的演进史，`126 → 128 → 131 …`）：

```
assert n == 322, (
```

同一条目的 limitations 自己写着「★ 加了工具就要同时改这里」，⇒ ★ **这两个数都是设计为会变的**，而条目把旧值当现状陈述。

> ★ 本条**不影响** `assembly_read` 的主证据 —— 主证据 `output/assembly-evidence.json` 与条目**完全一致**（见下）。

---

## ✔ 核过且对得上的（不写进问题，但记明已核）

- **`assembly_read`**：`output/assembly-evidence.json` 顶层 `"verdict": "pass"`；`"overlap_case"` 的 `"interference_count": 1` 且 `"status": "warn"`；`"apart_case"` 的 `"interference_count": 0` 且 `"status": "pass"`；`"n_components": 2` ⇒ ★ 与条目写的「重叠 ⇒ 1 · 分开 ⇒ 0（status pass）· 回读 2 个组件」**逐字对得上**。★ **唯一对不上的是上面 F3 那两个守卫数字。**
- **`motion_validation_and_preconditions`**：`output/motion-evidence.json` 的 `"passed": 5, "of": 5, "verdict": "pass"`，且 `ensure_type_library` 的 `"preview"` 就是条目 limitations 里写的 `D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\swmotionstudy.tlb` ⇒ ★ 一致。
- ★ **8 个 evidence 引用文件全部真实存在**（逐个 `Test-Path` 过：`tests/test_sw_assembly_doc_contract.py` · `tests/test_sw_assembly_aliases.py` · `tools/verify_in_context_reference_smoke.py` · `tools/capture_assembly_evidence.py` · `tests/test_sw_motion_audit.py` · `output/assembly-evidence.json` · `output/motion-evidence.json`）⇒ ★ **本次没发现「引用了不存在的文件」**。

---

## 汇总

| # | 条目 | 判定 | 一句话依据 |
|---|---|---|---|
| **F1** | `assembly_and_mates` | **成立**（★ 最严重类） | 唯一真机证据顶层写 `"verdict": "fail"`，条目却仍定在 `level: verified` 且 label 含「配合」；分母 `8/11` 与文件的 `9/12` 也对不上 |
| **F2** | `motion_study` | **成立**（★ 最严重类） | evidence 自称「旋转马达创建」，实际文件里马达是 `FakeMotionFeature`、全仓 0 处真调建马达；同域 `animation_export` 已记「真机 `ok: false`」 |
| **F3** | `assembly_read` | **成立** | evidence 里的「all_specs() 81 / 协议层 126」与现值 277 / 322 不符（主证据本身一致） |

**核了 4 处条目（8 个 evidence 引用）· 对不上 3 处。**