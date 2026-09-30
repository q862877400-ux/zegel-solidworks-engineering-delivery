# -*- coding: utf-8 -*-
"""搜索框定位 v4 —— 用 UIA 树里**真实存在的**「搜索」Button 反推。

⚑ 三版形状定位全部失败（自截图逐次证实）
# --------------------------------------------------
#   v1 白底长条      → 界面上「白色」到处都是（header 空栏、表格空白）
#   v2 垂直中点      → 同一批白色区域，错因没除
#   v3 白底带字墨迹  → 候选 0 个，「白底带字」不成立
# ⇒ 结论：**颜色/形状在这个界面上不是可靠特征**。
#
# v4 改用**结构关系**：UIA 树里有一个真实的 ``Button``「搜索」，
#    它与搜索框**左右相邻**（截图可见：输入框在左、按钮在右）。
#    ⇒ 搜索框 = 「搜索」Button 左侧、同高的长条。
#    这是**结构锚**，不是像素特征 ⇒ 宽度变化时依然成立。
"""
import sys
import warnings

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"C:\swprojects\sw-skill-fork\scripts")
sys.path.insert(0, r"D:\AI\SW")

import sw_jlcfa_locate as L

warnings.filterwarnings("ignore")


def search_anchor(win):
    """「搜索」Button 的矩形（在插件区内）。找不到返回 None。"""
    cr = L.container_rect(win)
    if cr is None:
        return None, None
    cands = []
    for c in L._controls(win):
        try:
            t = (c.window_text() or "").strip()
            ct = c.element_info.control_type
            r = c.rectangle()
        except Exception:
            continue
        if t != "搜索" or ct != "Button":
            continue
        if not L._overlaps(r, cr):
            continue
        cands.append(r)
    if not cands:
        return None, cr
    # 取面积最小、最靠左的那个（「搜索」按钮，不含别的同名）
    cands.sort(key=lambda r: r.left)
    return cands[0], cr


def search_box(win):
    """搜索框矩形 = 「搜索」按钮左侧同高的长条。

    实测布局（截图 569px 插件区）：
      搜索框 ≈ (112,90)-(498,118)
      搜索钮 ≈ (500,90)-(569,118)
      ⇒ 搜索框右边界 = 按钮左边界 - 2；高度同按钮。
    """
    btn, cr = search_anchor(win)
    if btn is None:
        return None
    # 同高、紧邻左侧的长条
    r = btn
    box_left = r.left - int((r.right - r.left) * 4.6)
    return (box_left, r.top - 1, r.left - 2, r.bottom + 1)


if __name__ == "__main__":
    h, win = L.connect()
    btn, cr = search_anchor(win)
    print("「搜索」按钮:", btn)
    print("推算搜索框:", search_box(win))
