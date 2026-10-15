import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
GEN = Path(r"D:\AI\SW\tools\gen_family_coverage.py")
SEC = Path(r"D:\AI\SW\_section4.py")

src = GEN.read_text(encoding="utf-8")
sec = SEC.read_text(encoding="utf-8")

#: ① 插入 CATEGORY_RX + 两个函数（锚点 = _api_index_families 的结尾，唯一）
A1 = '        out[f"全量索引/{asm}"] = fams\n    return out\n'
assert src.count(A1) == 1, "锚点①不唯一/不存在: %d 次" % src.count(A1)
src = src.replace(A1, A1 + sec, 1)
print("  ✓ ① 已插入 CATEGORY_RX + official_categories + official_category_section")

#: ② main() 里取一次 cats
A2 = "    called, catalogued = repo_members()\n"
assert src.count(A2) == 1, "锚点②不唯一/不存在"
src = src.replace(A2, '    cats = official_categories()   #: ★ 官方分类（单一来源，见函数 docstring）\n' + A2, 1)
print("  ✓ ② 已在 main() 里取 cats")

#: ③ 每行加 official_category 字段
A3 = '                "note": "" if mems else "C:\\\\swapi 无该类型目录",\n'
assert src.count(A3) == 1, "锚点③不唯一/不存在: %d 次" % src.count(A3)
src = src.replace(
    A3,
    '                "note": "" if mems else "C:\\\\swapi 无该类型目录",\n'
    '                #: ★ 官方 category（**单一来源**：C:\\swapi 的 help 站点镜像；\n'
    '                #:   出厂反射**没有**该字段 ⇒ 无法三源互证）。读不到就是空串。\n'
    '                "official_category": cats.get(fam, ""),\n', 1)
print("  ✓ ③ 已给每行加 official_category")

#: ④ md 里插 `## 四`（锚点 = §三 那一节的开头，插在它**之前**? 不 —— 插在文件尾之前）
A4 = '    OUT_MD.write_text("\\n".join(L), encoding="utf-8")\n'
assert src.count(A4) == 1, "锚点④不唯一/不存在: %d 次" % src.count(A4)
src = src.replace(A4, '    L += official_category_section(rows, cats)\n\n' + A4, 1)
print("  ✓ ④ 已在写 md 之前追加 §四")

GEN.write_text(src, encoding="utf-8")
print("  ok 已写回")

import ast
try:
    ast.parse(src)
    print("  语法 OK")
except SyntaxError as e:
    print("  ⚠ 语法错 L%s: %s" % (e.lineno, e.text))
