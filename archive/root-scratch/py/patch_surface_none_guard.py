"""把 `sw_surface` 的**静默失败**变成**响亮失败**：返回 None 就抛带原因的错。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机实测结论，非第三方移植）
# 文件:   D:\\AI\\SW\\probe_surface2_correct_arity.py（2026-10-01 证据）
#         D:\\AI\\SW\\probe_surface_generations.py（官方 Obsolete 标注的核实）
# 定位:   真机实测把 `IModeler.Create*Surface` 的行为定了性：
#
#   **① 该族有一半被官方标过时**：`CreateConicalSurface` / `CreateCylindricalSurface` /
#      `CreatePlanarSurface` / `CreateSphericalSurface` 都写着
#      「Obsolete. Superseded by …2」。**而 `sw_surface.py` 包装的正是这一代。**
#
#   **② `*2` 那代**可达**（错从「属性不可设」变成「非选择性的参数」= 缺参数），
#      它多一个 `RefDirection`。**但按正确 arity 调，**仍然返回 None**。**
#
#   **③ 最关键：同一个调用的成功与否**跨探针不一致**：
#        · 第 13 轮 `probe_surface_array_shape.py`：`CreateCylindricalSurface` **成功**
#        · 第 26 轮：`spherical` / `toroidal` 成功，`cylindrical` / `conical` 失败
#        · 第 27 轮：**只有** `spherical`（非-2）成功
#      **⇒ 返回值**不可靠** —— 不是「有些能有些不能」，而是**同一个也会变**。**
#
#   **⇒ 修法（本补丁）：`None` 就是「什么都没建出来」⇒ 必须**抛带原因的错**，
#     而不是把 `None` 悄悄交给调用方。**静默失败是本项目反复踩的头号敌人。**
#
#  ⚠ 为什么这是**正确的**修法而不是「改用 `*2`」：
#    `*2` 实测**也不可靠**（同样返回 None）⇒ 换一代**解决不了**。
#    能解决的只有「**让失败可见**」 —— 那是唯一不依赖 COM 不稳定行为的改进。
#
# 官方签名依据: `IModeler.Create*Surface` 家族（`C:\\swapi\\types\\IModeler\\`）
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 一次性脚本：跑完即可删。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SURF = Path(r"C:\swprojects\sw-skill-fork\scripts\sw_surface.py")

OLD = '''    require_runtime_available("%s")
    return _invoke('''
NEW = '''    require_runtime_available("%s")
    return _checked(_invoke('''

# 更稳的做法：在 _invoke 里做返回值检查（所有包装器都经过它）
OLD_INVOKE = '''    return get_com_member(modeler, method, *args)'''
NEW_INVOKE = '''    surface = get_com_member(modeler, method, *args)
    # ⚠⚠ **返回 None = 什么都没建出来** ⇒ **抛带原因的错，不把 None 交给调用方**。
    #   真机实测（2026-10-01）：本族**返回值不可靠** —— 同一个调用在不同次之间
    #   会成功或返回 None（证据见 `probe_surface2_correct_arity.py` 与
    #   `probe_surface_generations.py`）。**换用官方 `*2` 新一代也**不解决**
    #   （实测同样返回 None）⇒ 唯一不依赖 COM 不稳定行为的改进就是**让失败可见**。
    #   **⇒ 静默失败是本项目反复踩的头号敌人（已知事实 8 / 30 / 40）。**
    if surface is None:
        raise RuntimeError(
            "%s 返回 None —— **什么都没建出来**。"
            "本族（`IModeler.Create*Surface`）真机实测**返回值不可靠**："
            "同一调用跨次会成功或返回 None，且官方 `*2` 新一代同样如此。"
            "⇒ **不要把它当成功**；换个思路（如先建草图/特征再转曲面），或重试一次再判。"
            % method
        )
    return surface'''


def main() -> int:
    t = SURF.read_text(encoding="utf-8")
    if OLD_INVOKE not in t:
        print("  ✗ 未匹配 _invoke 的返回行")
        return 1
    t = t.replace(OLD_INVOKE, NEW_INVOKE, 1)
    print("  ✓ _invoke 现在对 None 返回值**抛带原因的错**（把静默失败变响亮）")
    # 文档串同步（教训：文档串必须与代码同步）
    old_doc = "    ⚠ 本函数**只做一件事**：**参数个数自检**（签名表照官方反射抄的，传错个数立刻抛"
    new_doc = ("    ⚠ 本函数做**两件事**：① **参数个数自检**（传错个数抛带方法名的 `TypeError`）；\n"
               "    ② **返回值检查** —— 拿到 `None` 就抛带原因的 `RuntimeError`\n"
               "    （见下方来源块：本族返回值真机实测**不可靠**，静默交给调用方是错的）。\n\n"
               "    ⚠ 原文档串曾只写① —— **文档串必须与代码同步**。\n"
               "    ⚠ 原本还写了：**参数个数自检**（签名表照官方反射抄的，传错个数立刻抛")
    if old_doc in t:
        t = t.replace(old_doc, new_doc, 1)
        print("  ✓ 文档串已同步（现在写的是它真正做的两件事）")
    SURF.write_text(t, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
