# Tasks: 接入官方接口分类（`category`）

- [x] T-12901 ★ 核官方 `category` 的覆盖率与种类数（复现外部审计的数）
  `→ 验收:` 见 plan.md §查证命令 ① ⇒ 期望 `md 12123 有category 11703 种类 39`
- [x] T-12902 ★★ 核「出厂反射**有没有**该字段」—— **这是"能不能三源互证"的判据**
  `→ 验收:` 见 plan.md §查证命令 ② ⇒ 期望**两行都是 0** ⇒ 结论：**只能标"单一来源"**
- [x] T-12903 ★ 核「未认领族」的定义（读 `_dedupe_domains()` 的 docstring）
  `→ 验收:` `Set-Location D:\AI\SW; python -c "from pathlib import Path;t=Path('tools/gen_family_coverage.py').read_text(encoding='utf-8');i=t.find('def _dedupe_domains');print(t[i:i+400])"`（★ 生成器在**工作区仓库**，跨仓库）
  ⇒ 期望看到「**一个族只算一次**」与「1,090 > 实际 774」
- [x] T-12904 ★★ 把**九个** `全量索引/*` 桶加总（审计只数了最大那个）
  `→ 验收:` `python -c "import json,sys;from collections import Counter;from pathlib import Path;rows=json.loads(Path(r'docs\family-coverage.json').read_text(encoding='utf-8'));c=Counter(r['domain'] for r in rows);u={k:v for k,v in c.items() if str(k).startswith('全量索引/')};print(len(rows), sum(u.values()), sorted(u.items(), key=lambda x:-x[1]))"`
  ⇒ 期望 `881 507 [...]`（**不是 385**）
- [x] T-12905 加 `official_categories()` + 行字段 + `## 四`（**纯插入**，事实 61）
  `→ 验收:` `Set-Location D:\AI\SW; git diff --numstat -- "tools/gen_family_coverage.py"` ⇒ **deletions 应为 0 或仅那一行表头改写**（★ 跨仓库：在工作区仓库里查）
- [x] T-12906 跑生成器 + **核对落盘**（事实 48 定则②）
  `→ 验收:` `Set-Location D:\AI\SW; python "tools/gen_family_coverage.py"` 后再核对：
  `python -c "import json,sys;from pathlib import Path;rows=json.loads(Path(r'C:\swprojects\sw-skill-fork\docs\family-coverage.json').read_text(encoding='utf-8'));print(len(rows), sum(1 for r in rows if 'official_category' in r), sum(1 for r in rows if r.get('official_category')))"`
  ⇒ 期望 `881 881 477`
- [x] T-12907 ★ 修一处**我自己读错的证据**：把 §一 那句打印加上标签
  （我一度把 stdout 的 `327/385` 当成分类覆盖率 —— 那其实是**既有**的「触及成员数」）
  `→ 验收:` `Set-Location D:\AI\SW; python "tools/gen_family_coverage.py" 2>&1 | Select-String '触及的成员数'`（**有命中**）
- [x] T-12908 五处口径不受影响（本批**不加工具**，只改分类产物）
  `→ 验收:` `python tools/probe_unexposed_functions.py` + `python tools/build_union_map.py`（数应与上批**相同**）
- [x] T-12909 全链 + 回归
  `→ 验收:` `python scripts/release_check.py`（exit 0）· `python -m pytest tests -q`（0 failed）
- [x] T-12910 两仓库各自提交（生成器在工作区、产物在代码仓库）
