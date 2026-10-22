"""特征树名清单的单一实现（原先在 4 个模块里各有一份）。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   scripts/sw_feature_tree.py
# 定位:   ★ 2026-10-22（仓库统一化 · 待办「同一功能多份实现」）：`_tree_names` 原先在
#         `sw_curve_and_split.py` / `sw_ref_geometry.py` / `sw_surface_edit_ops.py` /
#         `sw_surface_ref_ops.py` 里**各有一份**
#         （四份逻辑逐字相同，只差 docstring 措辞）。
#         本模块给出**唯一实现**，四者改为导入本模块的同名函数（别名 `_tree_names`）。
#         判据：`tools/find_duplicate_functions.py` 的跨文件同函数体组数下降。
# 官方依据: 无（本模块本身不调 COM；它转调本仓已验证的 `sw_part.feature_names`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────
from __future__ import annotations

try:
    from .sw_connect import get_com_member
except ImportError:
    from sw_connect import get_com_member


def tree_names(model):
    """★ 特征树的**有序特征名清单**（★ 判据用：调用前后比它）。

    ★★ **必须用本仓已验证的 `sw_part.feature_names`** —— ⚠ 轮 473 我自己拼过一条
      （`FeatureManager.GetFeatureCount(True)` + `FeatureByPositionReverse(i)`）⇒
      ★ **真机上它回 `None`** ⇒ 5 条能力**全被记成"不能"/"树无增量"**，
      ★ 而**真因是判据坏了、不是能力不行** ⚠
    ★ `sw_part.feature_names` 是本仓已验证过的：★ **两层过滤**
      （① `GetTypeName2` 非空 ⇒ 排除容器、与 UI 语言无关 ② 再排 `_CONTAINER_NODES`）
      ⇒ ★ 那种过滤正是"按名找特征"不假通过的前提 ✓
    ⚠ 取不到 ⇒ 回 `None`（★ 调用方写 `tree_delta: null`，**不猜**）。
    """
    try:
        from .sw_part import feature_names as _fn
    except ImportError:
        from sw_part import feature_names as _fn
    try:
        return list(_fn(model) or [])
    except Exception:                                                     # noqa: BLE001
        return None


def new_features(before, after) -> list[str] | None:
    """★ 新增的特征名（★ 任一侧为 `None` ⇒ 量不到 ⇒ 回 `None`，★ **判据降级、不猜**）。

    ★★ 2026-10-22（仓库统一化）：这段逻辑原先有 **5 份、2 个名字** ——
      `sw_curve_and_split` / `sw_ref_geometry` / `sw_surface_edit_ops` /
      `sw_surface_ref_ops` 里叫 `_delta`（★ 名字说的是「差」，实际返回的是**列表差**，
      不是在算数），而 `sw_sheet_metal_weld_entry` 里叫 `_new_features`
      （★ 这个名字才是对的）。
    ★ 更危险的是：`sw_sheet_metal_weld_entry` 里还有**另一个** `_delta`，
      ★ 那个才是**数值差**（`after - before`）⇒ ★ **同一个名字在同一个仓里指两件事** ✗
      ⇒ 本轮把列表版统一成本函数、把数值版**改名**为 `_numeric_delta` ✓
    """
    if before is None or after is None:
        return None
    return [x for x in after if x not in before]


def feature_count(model) -> int:
    """★ 特征树计数 —— ★ 本 COM 绑定里 `GetFeatureCount` 是**属性**
    （★ 调 `()` 会报 `TypeError: 'int' object is not callable`）⇒ ★ 两种形态都吃 ✓
    ★ 取不到 ⇒ 回 `-1`（★ 不猜、不抛）。

    ★ 2026-10-22（仓库统一化）：原先在 `sw_cosmetic_weld_bead.py` / `sw_net_blend.py` /
      `sw_weld_bead.py` **各有一份**（逻辑逐字相同，只差 docstring 措辞）⇒ 收敛到这里 ✓
    """
    attr = getattr(model, "GetFeatureCount", None)
    if attr is None:
        return -1
    if callable(attr):
        try:
            return int(attr())
        except TypeError:
            pass
    try:
        return int(attr)
    except (TypeError, ValueError):
        return -1



def feature_type_name(model, name):
    """★ 读特征类型名（★ 事实 242：那是**只依赖 API 对不对**的硬判据）。

    ★ 2026-10-22（仓库统一化）：原先在 `sw_sweep.py` / `sw_wrap.py` **各有一份**
      （逻辑逐字相同，只差 docstring 措辞）⇒ 收敛到这里 ✓
    ★ 取不到 ⇒ 回 `None`（★ 不猜）。
    """
    try:
        f = get_com_member(model, "FeatureByName", name)
        for meth in ("GetTypeName2", "GetTypeName"):
            try:
                return str(get_com_member(f, meth))
            except Exception:                                  # noqa: BLE001
                continue
    except Exception:                                          # noqa: BLE001
        pass
    return None
