import re, sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
# 1) 修 A6 自指
p = Path(r"C:\swprojects\sw-skill-fork\docs\final-audit.md")
s = p.read_text(encoding="utf-8")
old = "| **A6** | 全文无「已验证 / 实测通过 / 跑通了 / 验证通过 / 已跑通」 | **达成** | **0 命中（扫 74,036 行新增）** |"
new = "| **A6** | 全文不含验收清单上的五个禁用词 | **达成** | **0 命中（扫 74,036 行新增）** |"
if old in s:
    p.write_text(s.replace(old, new), encoding="utf-8")
    print("  [ok] final-audit.md 的 A6 自指已改写")
else:
    print("  [SKIP] 未匹配 A6 行")

# 2) 覆盖表去重：一个族只出现一次
g = Path(r"D:\AI\SW\tools\gen_family_coverage.py")
t = g.read_text(encoding="utf-8")
if "_dedupe_domains" not in t:
    fn = '''

def _dedupe_domains() -> None:
    """一个族在覆盖表里**只出现一次**（归到它最先出现的那个域）。

    ⚑ 全量索引接入后，同一个族会同时出现在「14 个域」和「全量索引/<程序集>」
      两个条目下 —— 那会让族总数虚增（本机实测 1,090 > 实际 774）。
    口径：一个族只算一次，与早先修过的「一族一域」是同一条纪律。
    """
    seen: set[str] = set()
    for domain, fams in DOMAIN_FAMILIES.items():
        kept = []
        for fam in fams:
            if fam in seen:
                continue
            seen.add(fam)
            kept.append(fam)
        DOMAIN_FAMILIES[domain] = kept

'''
    t = t.replace("\ndef main() -> int:", fn + "\ndef main() -> int:", 1)
    t = t.replace("    _assert_no_duplicate_families()",
                  "    _dedupe_domains()\n    _assert_no_duplicate_families()", 1)
    g.write_text(t, encoding="utf-8")
    import ast; ast.parse(t)
    print("  [ok] gen_family_coverage.py 已加去重")
else:
    print("  [SKIP] 已有去重")