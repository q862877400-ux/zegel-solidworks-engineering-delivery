# Acceptance — `Name` 的逐宿主表达式表态

**Feature**: `specs/248-name-host-adjudication/`
**日期**: 2026-10-09
**结论**: ✅ **四件齐 · 判据 6/6 绿 · 红基线三组全红 · 门禁全套 `status pass` · `EXIT 0` · `missing []`**

---

## 一、逐条验收（对应 `spec.md` 的 FR）

| # | 需求 | 判据 | 读数 |
|---|---|---|---|
| FR-001 | 每个**宿主表达式**必须表态 | `test_every_host_expression_is_adjudicated` | ✅ **16 宿主 / 51 站点**全部进表，纯函数问题数 **0** |
| FR-002 | 表态必须与**接口**自洽 | 同上（纯函数第 ③ 查项） | ✅ `real-hit` ⟺ 接口 ∈ {`IComponent2`, `IView`}，**0 矛盾** |
| FR-003 | 判据**必须能红**（合成负例） | `test_criterion_catches_unadjudicated_host` | ✅ **三组负例全部被判出** |
| FR-004 | 证据站点与重算**逐字相等** | `test_every_host_expression_is_adjudicated` | ✅ 16 宿主的站点集合**逐一相等** |
| FR-005 | 下界（只增不减） | `test_real_and_false_site_lower_bounds` | ✅ 宿主 **16** · 站点 **51** · 真 **4** · 假 **47** |
| FR-006 | 与 245 跨规格一致 | `test_consistent_with_245_host_review` | ✅ 245 判 `mixed`；证据站点全在本表内、且**至少 1 个真命中** |
| FR-007 | 调用口径与互锁**逐条一致** | `test_scan_parity_with_interlock` | ✅ 全部 `scripts/sw_*.py` 的 `(行号, 成员名)` **逐条相等** |
| FR-008 | 不许改索引生成器 / 靶子表 | mtime 核（见 §三） | ✅ 四个文件 mtime **全部早于** 开工时刻 |

---

## 二、★★ 红基线（★ 本仓纪律：不能红的判据 = 空判据）

| 变异 | 期望 | 实测 |
|---|---|---|
| **清空表态表** | 16 个宿主全部报「未表态」 | ✅ **`清空表 => 16 条未表态`** |
| **删掉 `av` 一条** | 报 `av` 未表态 | ✅ **`["宿主 'av' 未表态（真树上有 1 处）"]`** |
| **把 `view` 翻成 `false-hit`** | 报「表态与接口矛盾」 | ✅ **判出** |

★ 命令（★ 可复制）：
```bash
cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B -c "
import sys, importlib.util
sys.path.insert(0,'D:/AI/SW'); sys.path.insert(0,'D:/AI/SW/scripts'); sys.path.insert(0,'D:/AI/SW/tests')
s=importlib.util.spec_from_file_location('t','D:/AI/SW/tests/test_obsolete_name_host_adjudication.py')
m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
h=m._host_sites()
print('清空表 =>', len(m._adjudication_failures(h, {})), '条未表态')
print('删 av   =>', m._adjudication_failures(h, {k:v for k,v in m._NAME_HOST_REVIEW.items() if k!='av'}))
"
```

---

## 三、★ 未改动证明（★ 用 mtime，**不用 `git status`**）

★ **理由**：本仓工作树是「**已 staged 的整树基线**」⇒ `git status --short` 里 `release_check.py` /
`gate-classification.json` / `sw_com_traps.py` **都带 `M` 标记** —— ★ 那是**历轮**留下的，**不代表本轮改过**。

| 文件 | mtime | 早于 22:38？ |
|---|---|---|
| `tools/build_obsolete_index.py` | `10-03 23:28` | ✅ |
| `scripts/release_check.py` | `10-09 14:41` | ✅ |
| `docs/gate-classification.json` | `10-09 14:41` | ✅ |
| `scripts/sw_com_traps.py` | `10-09 19:46` | ✅ |

★ **本轮（22:38 之后）改过的文件**：
```bash
cd "D:/AI/SW" && find . -maxdepth 2 -newermt "2026-10-09 22:38" -type f -not -path "./.git/*" -not -name "*.pyc" -not -path "./__pycache__/*"
```
实测输出：`output/_gate248.log` · `output/_probe248_name_sites.py` · `output/_probe248_name_sites.txt` ·
`tests/test_obsolete_multi_successor_impact.py` · `tests/test_obsolete_name_host_adjudication.py`
（★ `specs/248-*/` 在 `maxdepth 3`，未列 —— 已另行确认存在）。
⇒ ★ **`scripts/` 与 `tools/` 一个文件都没动**。

---

## 四、门禁全套 @3.14.7

```bash
cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -B scripts/release_check.py > output/_gate248.log 2>&1
```
| 项 | 读数 |
|---|---|
| `status` | **`pass`** |
| `EXIT` | **`0`** |
| `missing` | **`[]`** |
| `gate_details` 条数 | **47**（★ 与 247 同 —— 本轮**未新增门禁**） |
| 耗时 | 约 **2m40s**（★ 后台跑，落盘日志） |

★ 三套口径（★ 别混）：`gate_details` **47** · `check_*.py`（`gate_wiring`）**44** · `gate-classification.json` **48**
—— ★ **三者都不变**（本轮未加门禁）。

---

## 五、相关族回归

```bash
cd "D:/AI/SW" && "C:/Users/Zegel/AppData/Local/Python/pythoncore-3.14-64/python.exe" -m pytest tests/test_obsolete_name_host_adjudication.py tests/test_obsolete_multi_successor_impact.py tests/test_obsolete_multi_successor.py tests/test_deprecated_multi_successor_adjudication.py tests/test_deprecated_table_admission.py tests/test_deprecated_entry_interlock.py -q
```
**读数：`46 passed`**（248 的 6 + 245 的 7 + 244 的 4 + 247 的 11 + 243 的 12 + 互锁 6）。

★ **生成器链**：★ **未跑** —— 本轮**没改 `scripts/`**（★ 与 247 不同：247 改了 `sw_com_traps.py` ⇒ 跑了 7 步）。
★ 依据：见 §三 的 mtime 表。

---

## 六、★★ 核心发现（本轮的价值）

### 发现一：245 漏了一条真命中

| 宿主 | 站点 | 赋值来源 | 官方 Returns | 接口 |
|---|---|---|---|---|
| **`av`** | `sw_review.py:637` | `get_com_member(model, "ActiveView")` | `IModelDoc2/ActiveView.md` → 「Current active [[model view]]」 | ★ **IView** |

⇒ ★ 与废弃条目 `IView::Name` **同接口** ⇒ **真命中**（245 只写了 `view` 的 3 处，**漏了这 1 处**）。

### 发现二：51 处 = 4 真 + 47 假，16 个宿主表达式全部判完

★ 判读方法：★ 每个宿主表达式**读同函数内的赋值来源**，由来源的**官方 `## Returns`** 定接口。
★ **不按变量名猜** —— `f` / `x` / `av` / `cfg` / `entry` 这些名字**不携带接口信息**。

### 发现三：判据口径下沉

| 项 | 245 | 248 |
|---|---|---|
| 粒度 | 名 | ★ **宿主表达式**（16） |
| 证据 | 2 站点 | ★ **51 站点** |
| 新增宿主 | 不报 | ★★ **即红** |
| 自洽性 | 无 | ★★ `real-hit` ⟺ 接口 ∈ {`IComponent2`, `IView`} |

---

## 七、未过门（如实登记，★ 未完成项不因本切片收口而消失）

1. **4 处真命中未换路由** —— ★ `IView::Name`（属性）→ `IView::GetName2`（方法）**非 drop-in**；
   ★ 且三处 `view` 站点**已有 `GetName2` 兜底在前** ⇒ ★ 换法**必须真机验**。
2. **245 的其余 13 条命中名**仍只登记**名**级结论 ⇒ ★ 未按宿主表达式逐条展开（★ 与 248 同法的尾巴，可按需立项）。
3. **6 条索引错后继仍未修**（改生成器 = 独立工作）。
4. **16 条 `Superseded by A and B`** 仍表达不了「两个后继」（★ 需先立项改表形态 + 兼容公开工具签名）。
5. **真机未验**；**223 的 8 条 `HEAD` 即红既有失败未修**；**未提交 / 未部署**。
6. **未调 COM / 真机**；**未删任何文件**；**未派任何成员**；**未 create 或 update 任何自动任务**。
