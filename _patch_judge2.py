import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
p = Path(r"C:\swprojects\sw-skill-fork\tools\judge_naked_batch2.py")
t = p.read_text(encoding="utf-8")

#: ★ 把第三层的**子串匹配**改成**全词/词边界**（★ `THEME` 含 `HEM` 是假阳性）
OLD = """            for m2 in re.finditer(r'"([A-Z_]{3,})"', src2):
                name2 = m2.group(1)
                if any(k.lower() in name2.lower() for k in keys):
                    enumish.append("%s:%s" % (p2.name, name2))"""
NEW = """            for m2 in re.finditer(r'"([A-Z_]{3,})"', src2):
                name2 = m2.group(1)
                #: ★★ **按 `_` 切词后做全词匹配** —— ★ 否则 `THEME_BLUES` 里的 `HEM`
                #:   会被当成 `hem`（★ 假阳性；与 `close` 含 `lose` 同族）。
                words2 = [w for w in name2.split("_") if w]
                if any(k.upper() in words2 for k in keys):
                    enumish.append("%s:%s" % (p2.name, name2))"""
if "按 `_` 切词后做全词匹配" not in t:
    t = t.replace(OLD, NEW, 1)
    p.write_text(t, encoding="utf-8")
    print("  已改为全词匹配")
try:
    compile(p.read_text(encoding="utf-8"), str(p), "exec")
    print("  ok-compile")
except SyntaxError as e:
    print("  **错 L%s**: %s" % (e.lineno, str(e.msg)[:80]))
