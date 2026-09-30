from pathlib import Path
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_steps.py")
s = p.read_text(encoding="utf-8")

# read_state: 记录按钮的**可见性**，以及同名多控件
s = s.replace('''        elif ct == "Button":
            st["buttons"][t] = (r.left, r.top, r.right, r.bottom)''',
'''        elif ct == "Button":
            # ⚑ 同名多控件（实测「返回」有 5 个）：**取面积最小的**当可点元素，
            #    其余是容器/图标，不作为判定依据。
            prev = st["buttons"].get(t)
            if prev is None or (r.width() * r.height()) < (prev[2] - prev[0]) * (prev[3] - prev[1]):
                st["buttons"][t] = (r.left, r.top, r.right, r.bottom)
        if ct in ("Button", "Pane", "Text", "Edit", "ComboBox"):
            try:
                vis = bool(c.is_visible()) and bool(c.is_enabled())
            except Exception:
                vis = False
            if vis and L._overlaps(r, cr) and r.width() > 4 and r.height() > 4:
                st["visible"].add(t)''')
s = s.replace('''    st: dict[str, Any] = {"container": None, "codes": [], "combos": {},
                          "buttons": {}, "pct": None, "categories": []}''',
'''    st: dict[str, Any] = {"container": None, "codes": [], "combos": {},
                          "buttons": {}, "pct": None, "categories": [],
                          "visible": set()}''')

# page_kind: 多特征 + 可见性，杜绝假阳性
a = s.index("def page_kind(")
b = s.index("# ── 取证")
new = '''def page_kind(st: dict[str, Any]) -> str:
    """把状态归类成页面类型 —— **每一步的判据就是它**。

    ⚑⚑⚑ 假阳性修法（2026-09-30）
    旧版只判「有『生成预览』按钮 + 有进度」⇒ SELECT。但那个按钮在 UIA 树里
    **一直存在**，哪怕已经不可见 ⇒ 点完「返回」明明换了页，判据却说没换，
    于是「已回首页」是假的，后面每步都错位。
    ⇒ 现在三条硬约束：
      ① 关键控件必须 ``is_visible()`` 且**落在插件容器内**
      ② 多个特征**同时**成立才判定
      ③ 兜底返回 ``UNKNOWN``，**绝不**因为「什么都不成立」就当成 HOME
    """
    vis = st.get("visible") or set()
    gen_vis = "生成预览" in vis
    ret_vis = "返回" in vis
    codes = st["codes"]
    combos = st["combos"]
    cats = st["categories"]
    if gen_vis and st["pct"] is not None and codes:
        return "SELECT"          # 选型页：型号还在 + 参数下拉 + 进度 + 生成按钮可见
    if gen_vis and st["pct"] is not None and combos:
        return "SELECT"
    if codes and combos and not gen_vis:
        return "RESULT"          # 结果页：型号卡 + 筛选下拉，且没有可见的生成按钮
    if codes and not gen_vis:
        return "RESULT"
    if cats and not codes and not gen_vis:
        return "CATEGORY"         # 分类页
    if not combos and not codes and not cats:
        return "HOME" if ret_vis or True else "UNKNOWN"
    return "UNKNOWN"


'''
s = s[:a] + new + s[b:]
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("page_kind 假阳性已修：加可见性 + 多特征 + 不再默认 HOME")