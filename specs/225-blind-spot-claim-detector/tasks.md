# Tasks — 门禁盲区探测器的漏网（spec 225）

**Feature**: `specs/225-blind-spot-claim-detector/`
**日期**: 2026-10-09
**纪律**：每条任务的验收命令**可直接复制执行**；★ 改实现前必须先证明判据能红。

---

## 环境（每轮固定）

```
判据解释器 : C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B
门禁解释器 : C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe   ← ★ 必须
```

★ 为什么门禁必须换解释器：受管 3.13.12 **缺 `comtypes`/`win32com`** ⇒「参数绑定门禁」会触发
`sw_part.py` 的**交互式**询问「是否授权自动安装 [Y/N]」⇒ 提示文本被当门禁输出 ⇒ **假红 + 挂死风险**。

---

## T-001 · 量出探测器漏了谁（**先量后改**）

```bash
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B -c "
import re, importlib.util
spec = importlib.util.spec_from_file_location('g', 'scripts/check_enum_values_vs_reflection.py')
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
disp = g.parse_dispositions()
for pat, label in [(r'官方|swapi|sw[A-Z]\w+','现状'),
                   (r'官方|swapi|sws?[A-Z]\w+','+sws'),
                   (r'官方|swapi|sws?[A-Z]\w+|反射|转储|CHM|_raw','+反射/转储/CHM')]:
    g.CLAIM = re.compile(pat)
    b = g.find_uncovered_claimed_tables()
    und = [t for t in b if (t[0],t[1]) not in disp]
    print('%-14s 盲区=%-3d 未表态=%-3d' % (label, len(b), len(und)))
"
```

- [x] 读数：**现状 44/0 → +sws 47/3 → +反射/转储/CHM 54/10**（新暴露 10 张全未表态）
- [x] 结论：`sw[A-Z]\w+` 要求 `sw` 后紧跟大写 ⇒ **`sws*` 全族不命中**

## T-002 · 写判据并**证明它红**（FR-004）

```bash
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B tests/test_gate_blind_spot_claim.py
```

- [x] 判据文件：`tests/test_gate_blind_spot_claim.py`（11 例）
- [x] ★ **改动前读数：`Ran 11 tests · FAILED (failures=8)`** ⇒ 判据真的能红 ✓
- [x] ★ 其中 `test_undeclared_sws_claim_makes_the_gate_red`（端到端负例）改动前**必红** ——
      这是「放宽正则」这件事**唯一**能红的判据（未覆盖本来就不判罪 ⇒ 没有它=空判据）

## T-003 · 放宽 `CLAIM` 正则（FR-001 / FR-002）

```bash
grep -n '^CLAIM = ' scripts/check_enum_values_vs_reflection.py
```

- [x] `官方|swapi|sw[A-Z]\w+` → **`官方|swapi|sws?[A-Z]\w+|反射|转储|CHM|_raw`**
- [x] 同处补注释：写明**为什么**（`sws*` 全族 300+ 名）与**诚实边界**（仍是启发式，散文自称仍看不见）
- [x] 模块 docstring §5 同步追加一段（记录本次放宽与实测影响）

## T-004 · 新暴露的 10 张表逐张表态（FR-003）

- [x] 三张 `enum`（★ 枚举名逐条从**出厂反射转储**节头抄，不靠记忆）：

| 文件（**改动后**行） | 表 | 声明 |
|---|---|---|
| `sw_simulation.py:1565`（表在 1566） | `SWS_SOLVER_TYPES` | `#: enum-gate: enum swsSolverType_e` |
| `sw_topology.py:185`（表在 186） | `SWS_TOPOLOGY_DEMOLD_DIRECTIONS` | `#: enum-gate: enum swsTopologyDemoldDirectionOption_e` |
| `sw_topology.py:194`（表在 195） | `SWS_TOPOLOGY_ACTIVATION` | `#: enum-gate: enum swsTopologyActivationOption_e` |

- [x] 六张 `not-enum arity`：`sw_costing.py:75 COSTING_ARITY` · `sw_featureworks.py:75 FEATUREWORKS_ARITY` ·
      `sw_pdm.py:94 DOCUMENT_ARITY` · `sw_pdm.py:109 TABLE_ARITY` · `sw_routing.py:84 ROUTING_ARITY` ·
      `sw_selection.py:99 SELECTION_ARITY`
- [x] 一张 `not-enum index`：`sw_simulation_loads.py:304 _REFGEOM_POSITIONS`
- [x] ★ 全部**纯插入、零删除**；★ **不逐行补 `# swXxx`**（键是本地语义键 —— 224 已判）

## T-005 · 三源核对（铁律 0 / 铁律 4）

```bash
grep -A6 '^## swsSolverType_e$' _raw/reflect/enum_cosworks.txt
grep -A5 '^## swsTopologyDemoldDirectionOption_e$' _raw/reflect/enum_cosworks.txt
grep -A4 '^## swsTopologyActivationOption_e$' _raw/reflect/enum_cosworks.txt
ls C:/swapi/enums/ | grep -i "SolverType\|DemoldDirection\|ActivationOption"
```

- [x] 转储（③）：三枚举名**逐条查到**，值集 `{0,1,2,5,6,7,8}` / `{0,1,2}` / `{0,1}`
- [x] swapi（①）：`C:\swapi\enums\` **没有**这三个页（142 个 `sws*` 页全是 `swS*`/`swSF*`/`swSM*` 等）
- [x] CHM 解包（②）：`_raw/chm_cosworks/` 存在，作交叉核对
- [x] **三源不冲突** ⇒ 无需动用裁决顺序（★ 是「查了、不冲突」，不是「没查」）

## T-006 · 判据全绿 + 门禁 exit 0

```bash
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B tests/test_gate_blind_spot_claim.py
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B scripts/check_enum_values_vs_reflection.py
```

- [x] 判据 **Ran 11 tests · OK**
- [x] 门禁 **`已表态 54 · 未表态 0 · [PASS] 175 · exit 0`**
- [x] 四读数**不变**：`ok 175` · 查不到 2 · 两源冲突 3 · 覆盖清单 189 文件 / 101 表 / 已覆盖 33 / 未覆盖 68

## T-007 · 回归（223 / 224 / 222）

```bash
for t in test_enum_table_disposition test_gate_boundary_transparency test_relation_enum_alignment test_pattern_enum_alignment; do
  C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B tests/$t.py; done
```

- [x] 224 `test_enum_table_disposition` **8/8 OK**（★ `BASELINE_BLIND=44` 是**下界**断言 ⇒ 54 ≥ 44 ✓）
- [x] 223 `test_gate_boundary_transparency` **7/7**（★ 明细行数按 `min(未表态,20)` ⇒ 仍 0 ✓）
- [x] 222 `test_relation_enum_alignment` **18/18** · `test_pattern_enum_alignment` **12/12**

## T-008 · 打包副本同步 + 新鲜度

```bash
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B scripts/release_check.py
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B
```

- [x] `sync_bundled_skill` → `{"status":"pass","files":461,"pruned":[]}`（★ **未删任何文件**）
- [x] 新鲜度 **3/3 passed**

## T-009 · 门禁全套（★ 必须 3.14.7）

```bash
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe scripts/release_check.py
```

- [x] **exit 0**（18 道门禁全绿；`missing: []`）

## T-010 · 收口（ROADMAP / feature.json / memory / 交接单 / AUTO_RUN）

- [x] `docs/ROADMAP.md` §一 追加 225 段 + 新「下一 WIP」（★ 同时**订正** 224 遗留的「D 类 42 张」误读）
- [x] `.specify/feature.json` → `specs/225-blind-spot-claim-detector`
- [x] `.workbuddy-ai/memory/2026-10-09.md`（append）· `MEMORY.md`（append 纪律）
- [x] `output/AUTO_HANDOFF.md`（覆盖写）· `output/AUTO_RUN_2026-10-09-0125.md`
- [x] `specs/225-.../acceptance.md`（**第 4 件**）

---

## 未做（明确划界，见 spec §三）

- [ ] 用**散文**（不含 `反射/转储/CHM/_raw`）自称出处的表 —— **仍看不见**，登记为未过门
- [ ] 逐行补 `# swXxx` · 把「未覆盖」判红 · 改 code 词表 · 修 223 的 8 条既有红
- [ ] `HEM_POSITIONS` 真机复核（需授权 COM）· 提交 / 部署 / 打 tag · 删文件
