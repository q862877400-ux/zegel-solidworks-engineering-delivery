from pathlib import Path
p = Path(r"D:\AI\SW\shape_loc.py")
s = p.read_text(encoding="utf-8")
s = s.replace('''#: 插件主题蓝（按钮底色）。取自截图：分类/搜索按钮均为蓝底白字。
THEME_BLUE = (43, 107, 228)
BLUE_TOL = 46          # 各通道容差''',
'''#: 插件主题蓝。⚠ 本机实测（截图采样，2026-09-30）真实值是
#:   ``RGB(48,80,224)`` 为主、``RGB(0,144,224)`` 次之 ——
#:   **不是**我一开始凭印象写的 (43,107,228)，那个阈值太严导致一个都找不到。
THEME_BLUES = ((48, 80, 224), (0, 144, 224))
BLUE_TOL = 40          # 各通道容差''')
s = s.replace('''def _is_blue(p) -> bool:
    r, g, b = p[0], p[1], p[2]
    return (abs(r - THEME_BLUE[0]) <= BLUE_TOL
            and abs(g - THEME_BLUE[1]) <= BLUE_TOL
            and abs(b - THEME_BLUE[2]) <= BLUE_TOL)''',
'''def _is_blue(p) -> bool:
    """蓝底判定：命中任一主题蓝，且**明显偏蓝**（排除浅蓝边框/文字）。"""
    r, g, b = p[0], p[1], p[2]
    if b < 130 or b - r < 60 or b - g < 30:
        return False
    return any(abs(r - t[0]) <= BLUE_TOL and abs(g - t[1]) <= BLUE_TOL
               and abs(b - t[2]) <= BLUE_TOL for t in THEME_BLUES)''')
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("颜色阈值已按实测值修正")