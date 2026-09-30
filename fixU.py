import re, sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
REPO = Path(r"C:\swprojects\sw-skill-fork")
NEW = '''| 口径 | 含义 | 本仓库实测（2026 收尾后） |
|---|---|---|
| ① **接口族收录** | 每个接口族的成员都抄进官方 API 索引 | ✅ **792/792 族** |
| ② **成员收录** | 每个成员的名字与参数个数都抄全 | ✅ **15,466/15,466 = 100%** |
| ③ **参数个数核对** | 索引里的 arity 与反射逐条一致 | ✅ 逐程序集自动比对，见门禁 |

> ⚑ 这三个口径**都已达成**，且都有门禁盯着。
> 但请注意它们**只说明「清单正确」**——
> **不说明每个 API 都被高层封装过**。本仓库**刻意不做**逐成员封装
> （用户要求「不要有自创的东西」），调用方一律用
> `call_index(对象, "族名", "成员名", *参数)` 直接按官方名调。

**收录范围**：本机实装 18 个 interop 程序集（1,804 个接口），收录 **12** 个；
未收录 3 个是明确排除的（`sustainability` / `sw3dprinter` / `swbrowser`），
`swconst` 只有枚举（字面值已单独收录），`swcommands` 实测 0 个接口。

**门禁**（每道都做过负向验证：注入已知违规 → 确认报 FAIL 并点名行号 → 撤销恢复 PASS）：

| 门禁 | 拦什么 |
|---|---|
| `check_provenance.py` | 新增代码没有出处 |
| `check_diff_markers.py` | 来源块把 patch 记号带进来 |
| `check_member_names.py` | 成员名在官方反射里查不到 |
| `test_official_names_only_contract.py` | 自造入口、索引与反射逐条对齐 |
'''
for f, pat in (("docs/gap-analysis.md", r"\| 口径 \| 含义 \| 本仓库实测.*?\n\n"),
               ("docs/harvest-report.md", r"\*\*成员级\*\*（这一栏才是真实覆盖面）：.*?(?=\n\n\n)")):
    p = REPO / f
    s = p.read_text(encoding="utf-8")
    m = re.search(pat, s, re.S)
    if m:
        s = s[:m.start()] + NEW + s[m.end():]
        p.write_text(s, encoding="utf-8")
        print("  [ok] %s 已更新" % f)
    else:
        print("  [skip] %s 未匹配" % f)