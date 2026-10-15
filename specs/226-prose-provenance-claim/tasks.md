# Tasks — 散文式出处自称的收口（spec 226）

**Feature**: `specs/226-prose-provenance-claim/`
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

## T-001 · 先量：到底有多少张散文自称（**先量后改**）

```bash
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B output/_probe_prose_claim.py
```

- [x] 读数：`总表 101 · 已覆盖 33 · 未覆盖 68 = 盲区 54 + 非盲区 14`；**非盲区 14 张里带散文出处线索 = 1 张**
- [x] 那 1 张 = `sw_import_mesh_reference.py:69 SW_LENGTH_UNITS`，注释 `# 本机 SolidWorks 2024 swconst.dll 验证值`
- [x] 结论：**量 = 1**（★ 不是「无从下手」，也不是「全仓要改造」）

## T-002 · 先量爆炸半径（★ 225 的教训：放宽会拖一堆表进来）

```bash
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B -c "
import importlib.util,sys,re
from pathlib import Path
ROOT=Path(r'D:\AI\SW'); G=ROOT/'scripts'/'check_enum_values_vs_reflection.py'
s=importlib.util.spec_from_file_location('g',G); m=importlib.util.module_from_spec(s); sys.modules['g']=m; s.loader.exec_module(m)
cov={}
for fn,ln,*_ in m.parse_code(): cov.setdefault(fn,[]).append(ln)
unc=[]
for fn,lo,hi,name,n in m.find_int_tables():
    if any(lo<=x<=hi for x in cov.get(fn,[])): continue
    L=(ROOT/'scripts'/fn).read_text(encoding='utf-8',errors='replace').splitlines()
    unc.append((fn,lo,name,n,'\n'.join(L[max(0,lo-15):hi])))
rx=re.compile(r'本机|本地|实测|真机|观测|\.dll|swconst|手册|帮助|文档|摘自|取自')
print('新增', [(t[0],t[1],t[2]) for t in unc if rx.search(t[4]) and not m.CLAIM.search(t[4])])
"
```

- [x] 读数：**新增 1 张**（`sw_import_mesh_reference.py:69 SW_LENGTH_UNITS`）⇒ 盲区 54 → **55**
- [x] 逐词量：`本机` 1 · `\.dll` 1 · `验证值` 1 · `swconst` 1 · `手册\|文档\|帮助\|参考\|摘自\|取自` **0**
- [x] 结论：**爆炸半径 = 1**，安全

## T-003 · 写判据并**证明它红**（FR-003）

```bash
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B tests/test_gate_prose_provenance_claim.py
```

- [x] 判据文件：`tests/test_gate_prose_provenance_claim.py`（9 例）
- [x] ★ **改动前读数：`Ran 9 tests · FAILED (failures=5)`** ⇒ 判据真的能红 ✓
- [x] 5 例红 = ① 认不出散文自称 · ② 该表没进盲区清单 · ③ 该表没声明 ·
      ④ 盲区 54 < 基线 55 · ⑤ 端到端负例（合成树散文自称却未表态，门禁却 exit 0）
- [x] 4 例绿 = 歧义边界（`参考` 不命中）· 旧探针不丢 · 已声明⇒门禁绿 · 错值⇒门禁红
      ⇒ ★ 红/绿**同时**存在，说明判据不是恒红也不是恒绿

## T-004 · 改 `CLAIM` 正则（FR-001）

```bash
grep -n "CLAIM = re.compile" -A2 scripts/check_enum_values_vs_reflection.py
```

- [x] 追加：`本机|本地|实测|真机|观测|\.dll|swconst|手册|帮助|文档|摘自|取自`（**12 词**）
- [x] ★ **只追加、不删**（旧词 `官方|swapi|sws?[A-Z]\w+|反射|转储|CHM|_raw` 原样保留，FR-005）
- [x] 附**语义分类注释**（四类）+ **有意排除**说明（`参考`/`据`/`按`）

## T-005 · 给 `SW_LENGTH_UNITS` 补声明（FR-002）

```bash
sed -n '56,78p' scripts/sw_import_mesh_reference.py
```

- [x] 表起始行正上方插入 **4 行**（3 行出处注释 + `#: enum-gate: enum swLengthUnit_e`），**纯插入零删除**
- [x] 官方依据两源逐条核过：`C:\swapi\enums\swLengthUnit_e.md` · `_raw/enum_values_sldworks.txt` 959–970
- [x] 值集 `{0,1,2,3,4}` ⊆ 官方取值集 ⇒ `check_dispositions()` 的「值集包含」通过

## T-006 · 判据转绿

```bash
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B tests/test_gate_prose_provenance_claim.py
```

- [x] 读数：**`Ran 9 tests · OK`**（改动前 5 红）

## T-007 · 门禁本体（★ 四读数必须全不变）

```bash
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B scripts/check_enum_values_vs_reflection.py
```

- [x] `覆盖清单 · 扫描 189 · 模块级整数表 101 · 已覆盖 33 · 未覆盖 68`（★ **四读数全不变**）
- [x] `已表态 **55** · 未表态 **0**` · `[PASS] **175**` · **exit 0**
- [x] 查不到 **2** · 两源冲突 **3**（均不变）

## T-008 · 回归 223 / 224 / 225 / 222

```bash
P=C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe
$P -B tests/test_enum_table_disposition.py        # 224
$P -B tests/test_gate_blind_spot_claim.py         # 225
$P -B tests/test_gate_boundary_transparency.py    # 223
$P -B tests/test_relation_enum_alignment.py       # 222
$P -B tests/test_pattern_enum_alignment.py        # 222
```

- [x] 224 **8/8 OK** · 225 **11/11 OK** · 223 **7/7 passed** · 222 **18/18 OK** + **12/12 passed**
- [x] ★ 224 的 `BASELINE_BLIND=44` 与 225 的 `BASELINE_BLIND=54` 都是**下界** ⇒ 55 ≥ 54 ✓

## T-009 · 打包副本同步 + 新鲜度

```bash
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B scripts/sync_bundled_skill.py
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -B tests/test_bundled_skill_enum_freshness.py
```

- [x] `{"status": "pass", "files": 461, "pruned": []}`
- [x] 新鲜度 **3/3 passed**（含 `test_bundled_py_copies_are_byte_identical_to_source`）

## T-010 · 生成器 + 门禁全套（★ 3.14.7）

```bash
P=C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe
$P -B scripts/gen_level_audit.py && $P -B tools/gen_metrics.py && $P -B tools/gen_harvest_digest.py \
  && $P -B tools/build_union_map.py && $P -B tools/gen_dead_ends.py
C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe scripts/release_check.py; echo "EXIT=$?"
```

- [x] 生成器全绿（`union-level-audit.md` 140 条能力 · 并集 808 操作 · 死路 75 条 / 46 能力）
- [x] ★ `release_check` **EXIT=0** · `"missing": []`

## T-011 · 收口（文档与状态）

- [x] `specs/226-prose-provenance-claim/{spec,plan,tasks,acceptance}.md` 四件齐
- [x] `docs/ROADMAP.md` §一 追加 226 段 + 更新游标
- [x] `.specify/feature.json` → `specs/226-prose-provenance-claim`
- [x] `.workbuddy-ai/memory/2026-10-09.md`（append）
- [x] `output/AUTO_HANDOFF.md`（覆盖写）
- [x] `output/AUTO_RUN_2026-10-09-<HHMM>.md`
- [x] ★ 更新自身排下一轮（`mode="update"`，**绝不 `mode="create"`**）
- [x] 未提交 / 未部署 / 未打 tag / 未调 COM / 未删任何文件
