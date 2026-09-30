from pathlib import Path
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_fill.py")
s = p.read_text(encoding="utf-8")
a = s.index("def model_line(win) -> str:")
b = s.index("def set_front(")
new = '''def _container_texts(win) -> list[str]:
    """插件容器内所有控件的文字（去空）。"""
    allc = S.controls_cached(win)
    cr = S._container_from(allc)
    if cr is None:
        return []
    out = []
    for c in allc:
        try:
            t = (c.window_text() or "").strip()
            r = c.rectangle()
        except Exception:
            continue
        if t and L._overlaps(r, cr):
            out.append(t)
    return out


def model_line(win) -> str:
    """插件里含 ``【去填写】`` 或看着像型号的那一行。

    ⚠ 不要用「必须以 X-Y 开头」这类正则卡 —— 实测把 ``EGH25SAZ0C``
      这种**无连字符**的型号全滤掉了，于是校验恒失败（假阴性），
      反而把先前能过的件判死。
    ⚑ 改用**整容器文字**里挑最像型号的那一条。
    """
    best = ""
    for t in _container_texts(win):
        if PLACEHOLDER in t:
            return t                      # 有缺口行，就是它
        if 6 < len(t) < 90 and "：" not in t and " " not in t:
            if any(ch.isdigit() for ch in t) and any(ch.isalpha() for ch in t):
                if len(t) > len(best):
                    best = t
    return best


def code_present(win, code: str) -> bool:
    """容器文字里是否出现目标型号（前 8 位，宽松匹配）。"""
    key = (code or "").split("-")[0][:8].lower()
    if not key:
        return False
    return any(key in t.lower() for t in _container_texts(win))


def unfilled(win) -> int:
    """插件容器里 ``【去填写】`` 的个数 == 还差几个参数。"""
    return sum(t.count(PLACEHOLDER) for t in _container_texts(win))


'''
s = s[:a] + new + s[b:]
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("model_line/unfilled 改为扫容器文字，并加 code_present")