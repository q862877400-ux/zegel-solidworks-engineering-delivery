from pathlib import Path
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_cards.py")
s = p.read_text(encoding="utf-8")
# visible_codes 是旧的分类卡定位（现已被 sw_jlcfa_search 的结构判据取代）
a = s.index("def visible_codes(")
b = s.index("def locate_code(")
s = s[:a] + '''def visible_codes(win) -> list[tuple[str, int, int]]:
    """⚠ **已废弃**：改用 ``sw_jlcfa_search.result_cards()``（结构判据）。

    旧实现用「容器顶部 +150 / 底部 -60」这种**相对偏移**判断卡片是否在视口内，
    侧边栏拉宽或 DPI 变化后不成立。保留仅为兼容旧调用。
    """
    return []


''' + s[b:]
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("visible_codes 已废弃化")