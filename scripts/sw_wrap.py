

# ── 24h 计划 段 6 续（Spec Kit `171`）：**包覆（wrap）** ─────────────────────────────
# ★★★★★ 2026-10-01（轮 329）**这是"四家有我们没有"里核实的真缺之一**：
#   ★ 全仓 grep `wrap` ⇒ **工具 0 · 函数 0**（★ 同批核出的另外三条：`sensor` / `units` / `undo`）。
#   ★★ 而**官方有明确入口**：`IFeatureManager.InsertWrapFeature2`（**5 参**，★ 反射 arity = 5）。
#
# ★★★ **调用序与 mark 来自官方**（★ §5.0：判据先找后搓）：
#   `C:\swapi\types\IFeatureManager\InsertWrapFeature2.md` 的 Remarks + 官方示例
#   `C:\swapi\examples\Create_Wrap_Feature_on_Multiple_Faces_Example_VB.md`：
#   ```
#   ① 选中基准面 ⇒ SelectByID2("Plane8", "PLANE", …)
#   ② SketchManager.InsertSketch True ⇒ CreateCircle(...) ⇒ InsertSketch True（收草图）
#   ③ 选草图：★ SelectByID2("Sketch30", "SKETCH", 0,0,0, False, **4**, …)   ← 官网 mark = 4
#   ④ 选面：  ★ 逐个 SelectByRay(...)                                        ← 官网 mark = 1
#      （★ 面**没有名字** ⇒ 官方示例用的是"射线选" —— 事实 32 的第三条路；
#        ★ 本模块改用 `IEntity.Select4`（★ 事实 32 的第一条路，★ 我们更熟、更稳））
#   ⑤ FeatureManager.InsertWrapFeature2(Type, Thickness, ReverseDir, Method, MeshFactor)
#   ```
# ★ `swWrapSketchType_e`（★ 官方枚举 × 反射**两源一致**）：
#   **0 = `swWrapSketchType_Emboss`**（凸起）· **1 = `swWrapSketchType_Engrave`**（★ UI 叫 Deboss，凹陷）
#   · **2 = `swWrapSketchType_Scribe`**（划痕/印记）
#
# ★★★ **判据用**特征类型名**（事实 242：挑只依赖被测对象的那个）——
#   ★ 真机读出来的名字写在 `WRAP_TYPE_NAME_CANDIDATES` 里（★ 首次跑先记录，★ 再钉死）。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_wrap.py —— 本文件（新）
# 定位:   24h 段 6 续：包覆（★ 补「四家有我们没有」的真缺）。
# 官方签名依据: `C:\swapi\types\IFeatureManager\InsertWrapFeature2.md`（5 参 · mark 1/2/4）·
#   `C:\swapi\enums\swWrapSketchType_e.md` + 反射 `enum_values_sldworks.txt`（0/1/2）·
#   `C:\swapi\examples\Create_Wrap_Feature_on_Multiple_Faces_Example_VB.md`（★ 调用序）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from sw_connect import get_com_member
from sw_feature_readback import feature_names

#: ★ `swWrapSketchType_e`（★ 官方枚举与反射两源一致）
WRAP_EMBOSS = 0    # 凸起
WRAP_ENGRAVE = 1   # 凹陷（★ UI 里叫 Deboss）
WRAP_SCRIBE = 2    # 划痕/印记

WRAP_TYPES = {"emboss": WRAP_EMBOSS, "deboss": WRAP_ENGRAVE, "engrave": WRAP_ENGRAVE,
              "scribe": WRAP_SCRIBE}

#: ★ `Method` / `MeshFactor` 的默认（★ 官方那两个参数在本文件里**没有查到取值表** ⇒
#:   ★ 按铁律 5 处理：**不猜**，★ 用 0 并在限制里写明"未核"。★ 5 参里它们排第 4/5。）
WRAP_METHOD_DEFAULT = 0
WRAP_MESH_FACTOR_DEFAULT = 0


#: ★ 2026-10-22（仓库统一化）：`_feature_type_name` 原在本文件与 `sw_sweep.py` 各有一份
#:   （逻辑逐字相同，只差 docstring）⇒ 收敛到 `scripts/sw_feature_tree.py` ✓
try:
    from .sw_feature_tree import feature_type_name as _feature_type_name
except ImportError:
    from sw_feature_tree import feature_type_name as _feature_type_name


def create_wrap_report(model, wrap_type: str = "emboss", thickness_mm: float = 1.0,
                       reverse: bool = False) -> dict:
    """★ **对已选中的「草图（mark=4）+ 面（mark=1）」建包覆特征**。

    ★ 走官方 `IFeatureManager.InsertWrapFeature2`（**5 参**）。
    ★ 官方要求（★ Remarks + 示例）：★ **草图 mark = 4**（★ 且**必须是 2D 草图**，官方原话
      "3D sketches are invalid"）· ★ **面 mark = 1** · ★ 拔模方向 mark = 2（★ 仅 Emboss/Engrave 用）。
    ★ **单位**（规则 2）：★ 入参是 **mm**，★ 换算成米在这里**只做一次**。
    ★ 判据（★ 规则 6 + 事实 242）：★ **特征树多了新特征** **且** **类型名里含 `Wrap`**
      （★ 具体串以真机读到的为准，★ 记在 `type_name`）。
    """
    if model is None:
        return {"ok": False, "error": "model 为 None"}
    key = str(wrap_type or "").strip().lower()
    if key not in WRAP_TYPES:
        return {"ok": False, "stage": "validate",
                "error": "wrap_type 只能是 %s（swWrapSketchType_e）；收到 %r"
                         % (sorted(set(WRAP_TYPES)), wrap_type)}
    try:
        thickness_m = float(thickness_mm) / 1000.0     # ★ 规则 2：换算只在边界做一次
    except (TypeError, ValueError):
        return {"ok": False, "stage": "validate", "error": "thickness_mm 要是数，收到 %r" % (thickness_mm,)}
    if thickness_m <= 0:
        return {"ok": False, "stage": "validate", "error": "thickness_mm 必须 > 0，收到 %r" % (thickness_mm,)}
    sel = {}
    for mark, label in ((4, "sketch"), (1, "face")):
        try:
            sel[label] = int(get_com_member(get_com_member(model, "SelectionManager"),
                                            "GetSelectedObjectCount2", mark))
        except Exception:                                      # noqa: BLE001
            sel[label] = -1
    if sel.get("sketch", 0) < 1 or sel.get("face", 0) < 1:
        return {"ok": False, "stage": "selection", "selected_by_mark": sel,
                "error": "包覆要选 **草图（mark=4，★ 必须是 2D 草图）** 与 **面（mark=1）**"
                         "（★ 官方 Remarks 与示例给的 mark）；★ 当前 mark4=%r · mark1=%r"
                         % (sel.get("sketch"), sel.get("face"))}
    before = feature_names(model)
    obj = None
    try:
        fm = get_com_member(model, "FeatureManager")
        obj = get_com_member(fm, "InsertWrapFeature2", WRAP_TYPES[key], thickness_m, bool(reverse),
                             WRAP_METHOD_DEFAULT, WRAP_MESH_FACTOR_DEFAULT)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "stage": "call", "selected_by_mark": sel, "args_count": 5,
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:200]),
                "★": "若报 DISP_E_BADPARAMCOUNT ⇒ 参数个数不对（官方 5 个）"}
    #: ★★★★★ 2026-10-01（轮 330）**判据改成「读返回对象」** —— 真机证明：
    #:   ★ 包覆**真的建成了**（返回对象的 `Name` = `包覆1` · `GetTypeName2()` = **`Emboss`**），
    #:   而 **`feature_names()` 的前后 diff 是空的**（before=8 / after=8 / new=[]）。
    #:   ⇒ ★★ **"树 diff"依赖遍历的完整性**；★ 而**返回值自带 Name 与类型名**，★ 更直接。
    #:   ⇒ ★★★ **顺带纠了一个错的预期**：★ 包覆的类型名是 **`Emboss`**（★ 与 `Type` 同名，
    #:     ★ **不是** `Wrap`）—— ★ 这正是"真机读出来的才算数"（事实 242）。
    ret_name, ret_type = None, None
    if obj is not None:
        try:
            ret_name = str(get_com_member(obj, "Name"))
        except Exception:                                      # noqa: BLE001
            ret_name = None
        for meth in ("GetTypeName2", "GetTypeName"):
            try:
                ret_type = str(get_com_member(obj, meth))
                break
            except Exception:                                  # noqa: BLE001
                continue
    after = feature_names(model)
    new = [n for n in after if n not in before]
    tname = ret_type or (_feature_type_name(model, new[-1]) if new else None)
    ok = bool(ret_name) and str(tname or "").lower() in ("emboss", "engrave", "deboss", "scribe")
    return {"ok": ok, "feature_name": ret_name or (new[-1] if new else None),
            "new_features": new, "type_name": tname, "returned_name": ret_name,
            "returned_type_name": ret_type,
            "tree_before": len(before), "tree_after": len(after), "wrap_type": key,
            "wrap_type_code": WRAP_TYPES[key], "thickness_mm": float(thickness_mm),
            "selected_by_mark": sel,
            "★": "官方 5 参 · 草图 mark=4（2D）· 面 mark=1 · ★ 判据 = **读返回对象的 Name 与 "
                 "GetTypeName2**（★ 真机：返回 `包覆1` / 类型 `Emboss`；★ 而 `feature_names()` 的 "
                 "前后 diff **是空的** ⇒ ★ 树 diff 不可靠）；⚠ `Method` / `MeshFactor`（第 4/5 参）"
                 "**取值表没查到** ⇒ 用 0，未核"}
