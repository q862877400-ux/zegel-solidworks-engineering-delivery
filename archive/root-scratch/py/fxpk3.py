from pathlib import Path
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_steps.py")
s = p.read_text(encoding="utf-8")

# 1) categories 只收**卡片形状**（实测分类卡 100x100），不再什么都收
s = s.replace('''        elif (r.top >= cr.top + 120 and r.bottom <= cr.bottom - 20
              and r.width() >= 40 and r.height() >= 20
              and t not in C.SKIP_NAMES):
            st["categories"].append(t)''',
'''        elif (80 <= r.width() <= 220 and 80 <= r.height() <= 220
              and r.top >= cr.top + 120 and r.bottom <= cr.bottom - 20
              and t not in C.SKIP_NAMES):
            # ⚑ 只收**近似正方形的卡片**（实测分类卡 100x100）。
            #   早前的宽过滤（w>=40,h>=20）把整页文字都算成「分类卡」，
            #   导致 counts 在任何页面都是几十，判据失去区分力。
            st["categories"].append(t)''')

# 2) page_kind 用**实测特征**，不再靠推断
a = s.index("def page_kind(")
b = s.index("# ── 取证")
new = '''def page_kind(st: dict[str, Any]) -> str:
    """把状态归类成页面类型 —— **每一步的判据就是它**。

    ⚑⚑⚑ 特征全部来自**实测可见控件名**（2026-09-30 抓了四页的真实清单）：
        SELECT(选型页)   参数筛选器 · 个备选型号 · 生成预览/插入/保存/选型PDF
                         参数值以**纯文字**出现（合金钢/四方型/短型/低组装…）
                         填满 100% 后 ComboBox 会消失，只剩文字 ⇒ 不能靠 combos 判
        生成完成        额外出现 **建模完成！**
        RESULT(结果页)  「代码：<型号>」标签 + 搜索 + 全部商品分类，无参数筛选器
        CATEGORY/HOME   100x100 卡片，无「代码：」标签、无参数筛选器
    ⇒ 判据用**互斥的独占特征**，并要求**可见**。
    """
    vis = st.get("visible") or set()
    has = lambda n: n in vis
    # 生成完成是 SELECT 的子状态，先判它
    if has("建模完成！"):
        return "GENERATED"
    if has("参数筛选器") and has("个备选型号"):
        return "SELECT"
    if st["codes"]:
        return "RESULT"
    if st["categories"]:
        return "CATEGORY"
    if has("全部商品分类") and not st["categories"]:
        return "HOME"
    return "UNKNOWN"


'''
s = s[:a] + new + s[b:]
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("page_kind 已按实测特征重写")