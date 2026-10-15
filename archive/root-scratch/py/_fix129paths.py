import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"D:\AI\SW\specs\129-official-category-column\tasks.md")
t = P.read_text(encoding="utf-8")

REPL = [
    #: ① T-12903 原文（绝对路径直接当 token）
    ("`→ 验收:` `python -c \"import sys;from pathlib import Path;t=Path(r'D:\\AI\\SW\\tools\\gen_family_coverage.py').read_text(encoding='utf-8');i=t.find('def _dedupe_domains');print(t[i:i+400])\"`",
     "`→ 验收:` `Set-Location D:\\AI\\SW; python -c \"from pathlib import Path;t=Path('tools/gen_family_coverage.py').read_text(encoding='utf-8');i=t.find('def _dedupe_domains');print(t[i:i+400])\"`（★ 生成器在**工作区仓库**，跨仓库）"),
    #: ② git diff 那行
    ("`→ 验收:` `git -C D:\\AI\\SW diff --numstat -- tools/gen_family_coverage.py` ⇒ **deletions 应为 0 或仅那一行表头改写**",
     "`→ 验收:` `Set-Location D:\\AI\\SW; git diff --numstat -- \"tools/gen_family_coverage.py\"` ⇒ **deletions 应为 0 或仅那一行表头改写**（★ 跨仓库：在工作区仓库里查）"),
    #: ③ 跑生成器那行
    ("`→ 验收:` `python D:\\AI\\SW\\tools\\gen_family_coverage.py` 后再核对：",
     "`→ 验收:` `Set-Location D:\\AI\\SW; python \"tools/gen_family_coverage.py\"` 后再核对："),
    #: ④ 标签那行
    ("`→ 验收:` `python D:\\AI\\SW\\tools\\gen_family_coverage.py 2>&1 | Select-String '触及的成员数'`（**有命中**）",
     "`→ 验收:` `Set-Location D:\\AI\\SW; python \"tools/gen_family_coverage.py\" 2>&1 | Select-String '触及的成员数'`（**有命中**）"),
]
n = 0
for old, new in REPL:
    if old in t:
        t = t.replace(old, new, 1); n += 1
    else:
        print("  ⚠ 锚点未命中: %s" % old[:70])
P.write_text(t, encoding="utf-8")
print("  ok 替换 %d/4 处" % n)
print("  核对：还有直接以绝对路径点脚本的行吗 →",
      sum(1 for l in t.splitlines() if "python D:\\AI\\SW\\tools" in l))
