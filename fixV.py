import sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
p = Path(r"C:\swprojects\sw-skill-fork\docs\harvest-report.md")
lines = p.read_text(encoding="utf-8").splitlines()
# 定位 72..100 区间（0-based 71..99）
s = 71
e = next((i for i in range(s, len(lines)) if lines[i].strip() == "" and i > 99), 100)
NEW = '''| 指标 | 数值 |
|---|---|
| 收录程序集 | **12** 个（本机实装 18） |
| 接口族 | **792** |
| 成员 | **15,466** |
| 抄进官方 API 索引 | **15,466 / 15,466 = 100%** |
| 未抄的族 | **0** |

> ⚑ 收录 12 个、未收录 3 个是**明确排除**的
> （`sustainability` 绿色设计 / `sw3dprinter` 3D 打印 / `swbrowser` PDM 浏览器）；
> `swconst` 只有枚举（1,963 个字面值已单独收录），`swcommands` 实测 0 个接口。

**本仓库刻意不做逐成员高层封装**（用户要求「不要有自创的东西」）：
调用方一律用 `call_index(对象, "族名", "成员名", *参数)` 按**官方名**直接调。
⇒ 所以**不存在**「封装率」这个指标 —— 早先版本的「16%」那个数字已经作废。

四道门禁（每道都做过负向验证）：

| 门禁 | 拦什么 |
|---|---|
| `check_provenance.py` | 新增代码没有出处（235 块 / 0 违规） |
| `check_diff_markers.py` | 来源块把 patch 记号带进来 |
| `check_member_names.py` | 成员名在官方反射里查不到 |
| `test_official_names_only_contract.py` | 自造入口、索引与反射逐程序集对齐 |

> ⚑ 「族总数」修过三次：① 6 个族同时登记在两个域（187→174）；
>   ② 174 那版只是 14 个域的范围（→701）；③ 接入 12 份全量索引后重排（→792）。'''
out = lines[:s] + NEW.splitlines() + lines[e:]
p.write_text("\n".join(out) + "\n", encoding="utf-8")
print("  [ok] harvest-report.md 指标段已重写")