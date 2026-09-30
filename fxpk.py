from pathlib import Path
p = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_jlcfa_steps.py")
s = p.read_text(encoding="utf-8")
# page_kind 补 MODEL 与 SELECT 的区分：进详情页后代码标签会消失、出现参数下拉
s = s.replace('''def page_kind(st: dict[str, Any]) -> str:
    """把状态归类成页面类型 —— **每一步的判据就是它**。"""
    if st["codes"]:
        return "RESULT" if st["combos"] else "MODEL"
    if st["pct"] is not None and ("生成预览" in st["buttons"] or
                                  (set(st["combos"]) - {"每页"})):
        return "SELECT"
    if st["categories"]:
        return "CATEGORY"
    return "HOME" if not st["combos"] else "UNKNOWN"''',
'''def page_kind(st: dict[str, Any]) -> str:
    """把状态归类成页面类型 —— **每一步的判据就是它**。

    ⚑ 判据只用「读得到的状态」，不靠截图（实测踩过的坑）：
       结果页与选型页都有「代码：xxx」，靠**参数 ComboBox 变多**区分。
    """
    has_gen = "生成预览" in st["buttons"]
    param_combos = {k for k in st["combos"] if k != "每页"}
    if has_gen and st["pct"] is not None:
        return "SELECT"          # 选型页：参数下拉 + 进度条 + 生成按钮
    if st["codes"] and st["combos"]:
        return "RESULT"          # 结果页：型号卡 + 筛选下拉
    if st["codes"]:
        return "MODEL"
    if st["categories"]:
        return "CATEGORY"
    if not st["combos"]:
        return "HOME"
    return "UNKNOWN"''')
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("page_kind 已细分 RESULT/SELECT")