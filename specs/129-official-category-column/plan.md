# Implementation Plan: 接入官方接口分类（`category`）

**Branch**: `129-official-category-column` | **Date**: 2026-10-01 | **Spec**: 同目录 `spec.md`

## Summary
在 `D:\AI\SW\tools\gen_family_coverage.py`（生成器）里加：
① `CATEGORY_RX` + `official_categories()`（读 `C:\swapi\types\<接口>\*.md` 的 `category`）
② 每行加 `official_category` 字段
③ md 新增 `## 四、官方分类与「未认领」族的归位`（数字**全部现算**，不写死）

★ **不改**既有 `domain`（业务域）—— **并存**，不替换。

## Technical Context
Python 3.14.7 · 无新依赖 · 生成器产物落代码仓库 `docs/family-coverage.{md,json}`
**Constraints**: 铁律 4（三源互证）· 铁律 6（许可）· 事实 61（批量改文件先看 `diff --stat` 的 deletions）

## ★ 要查的官方源与裁决顺序（§II）
| 源 | 用途 | 本次查到 |
|---|---|---|
| `C:\swapi\types\<接口>\*.md` 的 `category` | **分类取值** | 481 个接口有该字段 · 39 个取值 |
| 出厂反射 `_raw/reflect*/iface_*.txt` | **互证** | ★ **没有 `category`** ⇒ 无法互证（如实记）|
| `tools/gen_family_coverage.py` 的 `_dedupe_domains()` | 「未认领」的定义 | 「一族只算一次」⇒ `全量索引/<程序集>` = 未被 14 域认领者 |
| 外部审计 `official-category-unused.md` | 线索（**非权威**）| 数全对；两处读法要纠正 |

**裁决顺序**：出厂类型库/反射 **>** `C:\swapi` markdown **>** 本项目既有口径 **>** 外部报告。
★ 本次的**特殊性**：分类字段**只有第二源有** ⇒ **不能用"三源互证"背书**，只能标注。

## ⚠ 两处核查命令（§III，**都排除本批产物 / 不碰新写的文件**，事实 147）
```
① 官方 category 覆盖率（可重跑）：
   python -c "import re;from collections import Counter;from pathlib import Path;c=Counter();n=0
   for p in Path(r'C:\swapi\types').rglob('*.md'):
       n+=1;m=re.search(r'(?im)^\s*\*{0,2}category\*{0,2}\s*[:：]\s*(.+)$',p.read_text(encoding='utf-8',errors='replace'))
       if m: c[m.group(1).strip()]+=1
   print('md',n,'有category',sum(c.values()),'种类',len(c))"
   期望：md 12123 有category 11703 种类 39
② 出厂反射**没有**该字段（可重跑，**期望两行都是 0**）：
   python -c "import sys;from pathlib import Path
   for f in (r'D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt', r'D:\AI\SW\_raw\reflect\iface_cosworks.txt'):
       t=Path(f).read_text(encoding='utf-8',errors='replace')
       print(Path(f).name, sum(1 for l in t.splitlines() if l.strip().lower().startswith('category')))"
```

## Constitution Check（§I–§V）
| 条 | 判据 | 本次 |
|---|---|---|
| §I 来源 | 每条需求有来源 | ✅（含"无许可来源"的如实标注）|
| §II 官方源 | 列源 + 裁决序 | ✅（含"只有第二源有该字段"的说明）|
| §III 查不到 | 附核查命令 | ✅ 两条，含"期望 0"的负例 |
| §IV license | 来源行带 license | ✅ |
| §V 可跑验收 | 每条任务带 `→ 验收:` | ✅ |

## Project Structure
```
D:\AI\SW\tools\gen_family_coverage.py          ← 生成器（**工作区仓库**）：+ 2 函数 + 1 字段 + §四
C:\swprojects\sw-skill-fork\docs\family-coverage.{md,json}  ← 产物（**代码仓库**）
```
★ 跨两仓库：生成器在工作区、产物在代码仓库 ⇒ **各自提交**。
