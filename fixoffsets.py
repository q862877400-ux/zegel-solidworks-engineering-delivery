from pathlib import Path
# ① fill.py 加 _has_cjk
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_fill.py")
s = p.read_text(encoding="utf-8")
if "_has_cjk" not in s.split("def model_row")[0]:
    s = s.replace("def model_row(win):",
'''def _has_cjk(s: str) -> bool:
    """含中日韩字符？用于区分「型号值」与「中文说明/标签」。"""
    return any("\\u4e00" <= ch <= "\\u9fff" for ch in s)


def model_row(win):''', 1)
    p.write_text(s, encoding="utf-8")
    print("① fill.py 已加 _has_cjk")

# ② steps.py read_state 去掉 y 偏移
p2 = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_steps.py")
s2 = p2.read_text(encoding="utf-8")
old = '''        elif (80 <= r.width() <= 220 and 80 <= r.height() <= 220
              and r.top >= cr.top + 120 and r.bottom <= cr.bottom - 20
              and t not in C.SKIP_NAMES):'''
new = '''        elif (80 <= r.width() <= 220 and 80 <= r.height() <= 220
              and t not in C.SKIP_NAMES):'''
assert old in s2, "steps 未找到目标片段"
s2 = s2.replace(old, new, 1)
s2 = s2.replace('''            # ⚑ 只收**近似正方形的卡片**（实测分类卡 100x100）。
            #   早前的宽过滤（w>=40,h>=20）把整页文字都算成「分类卡」，
            #   导致 counts 在任何页面都是几十，判据失去区分力。''',
'''            # ⚑ 只收**近似正方形的卡片**（实测分类卡 100x100）。
            #   早前的宽过滤（w>=40,h>=20）把整页文字都算成「分类卡」，
            #   导致 counts 在任何页面都是几十，判据失去区分力。
            # ⚑ 已去掉 `r.top >= cr.top+120 / r.bottom <= cr.bottom-20` 这两个
            #   **相对容器偏移**：侧边栏拉宽或 DPI 变化时它们会失效。
            #   现在只按**尺寸 + 非结构名**收，位置由控件树给。''')
p2.write_text(s2, encoding="utf-8")
print("② steps.py 已去掉 y 偏移阈值")

# ③ cards.py 的 category_cards 同样去掉
p3 = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_cards.py")
s3 = p3.read_text(encoding="utf-8")
s3 = s3.replace('''        if r.top < cr.top + 120 or r.bottom > cr.bottom - 20:
            continue''',
'''        # ⚑ 去掉相对容器偏移（拉宽/DPI 变化会失效）''')
p3.write_text(s3, encoding="utf-8")
import ast; ast.parse(s3)
print("③ cards.py 已去掉 y 偏移阈值")
import ast as _a
_a.parse(p.read_text(encoding="utf-8"))
_a.parse(s2)