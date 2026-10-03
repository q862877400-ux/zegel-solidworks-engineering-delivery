

# ── 24h 计划 段 6 续（Spec Kit `169`）：**扫描（sweep）** ────────────────────────────
# ★★★★★ 2026-10-01（轮 315）**这是"四家有我们没有"里核实的第二个真缺**：
#   ★ 全仓 grep `sweep` ⇒ **工具 0 · 函数 0**（★ 与 `loft` 一样）——
#   ★★ 而**扫描与放样是 SolidWorks 最基本的两种特征**。四家并集里有 **`sweep`**（Slacker-LLC）。
#
# ★★★ **而入口不是 `InsertProtrusionSwept*`** —— ★ 官方 Remarks 第一句就写明：
#   > 「SOLIDWORKS 2018 introduces a **new sweep architecture**, making this method **obsolete**.
#   >  See **Sweep Features and SweepFeatureData Objects**」
#   ⇒ ★★ 现代入口是 **`IFeatureManager.CreateDefinition(swFmSweep)` → `ISweepFeatureData` → `CreateFeature`**
#     （★ 常量值 **17** —— ★ 反射 `swFmSweep = 17` × 官方 `CreateDefinition.md` 的「swFmSweep (boss sweep)」两源一致）
#
# ★★ **官方调用序与 mark**（★ §5.0：判据先找后搓 —— ★ 读的是官方专文，不是自己猜）：
#   源：`C:\swapi\docs\Programming with the SOLIDWORKS API\Sweep Features and SweepFeatureData Objects.md`
#   ```
#   ① 轮廓：★ 草图轮廓 ⇒ **Mark = 1**（闭合草图）· ★ 圆形轮廓 ⇒ **Mark = 4** · ★ 实体轮廓 ⇒ 1 + 2048
#   ② 路径：★ **Mark = 4**  ← ★ 而「**路径的起点必须落在轮廓所在平面上**」（1 方向扫描）
#   ③ 引导线 ⇒ Mark = 2（只与草图轮廓配）· ④ 方向向量 ⇒ Mark = 128
#   ⑤ CreateDefinition(swFmSweep) ⇒ ISweepFeatureData ⇒ 设属性 ⇒ CreateFeature
#   ```
#
# ★★★ **判据用**特征类型名**（★ 事实 242 的教训：挑只依赖被测对象的那个）——
#   ★ 真机：放样 = `Blend` · 拉伸 = `Extrusion` · ★ **而扫描应为 `Sweep`**（★ 本次真机核）。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_sweep.py —— 本文件（新）
# 定位:   24h 段 6 续：扫描（★ 补「四家有我们没有」的真缺）。
# 官方签名依据: `C:\swapi\docs\Programming with the SOLIDWORKS API\Sweep Features and SweepFeatureData Objects.md` ·
#   `C:\swapi\types\IFeatureManager\CreateDefinition.md`（swFmSweep = 17）·
#   `C:\swapi\types\ISweepFeatureData\`（54 个成员：`AccessSelections` / `CircularProfile` / `Direction` / …）·
#   ★ 反射 arity 表 `scripts/sw_api_sldworks.py`（`swFmSweep = 17` · `swFmSweepCut = 18`）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────

from sw_connect import get_com_member, set_com_member
from sw_feature_readback import feature_names

#: ★ `swFeatureNameID_e` 的取值（★ 反射来的，★ 事实 43：数值必须去反射）
SW_FM_SWEEP = 17
SW_FM_SWEEP_CUT = 18
#: ★★ 2026-10-03（轮 486）**曲面扫描的常量**：
#:   官方 `CreateDefinition.md` 的**合法常量表**里有一条逐字是
#:   「**`swFmRefSurface` (surface sweep)**」；★ 而反射转储给出
#:   **`swFmRefSurface = 62`** ⇒ 两源一致 ✓
SW_FM_REF_SURFACE = 62


def _feature_type_name(model, name):
    """★ 读特征类型名（★ 事实 242：那是**只依赖 API 对不对**的硬判据）。"""
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


def create_sweep_report(model, cut: bool = False) -> dict:
    """★ **用选中的「轮廓（mark=1）+ 路径（mark=4）」建扫描特征**。

    ★ 走官方**现代入口**：★ `CreateDefinition(swFmSweep=17)` → `ISweepFeatureData` → `CreateFeature`
      （★ `InsertProtrusionSwept*` 已被 SOLIDWORKS 2018 标为 obsolete）。
    ★ 官方约束（★ 原文）：★ **路径的起点必须落在轮廓所在平面上**（1 方向扫描）。
    ★ 判据（★ 事实 242）：★ **特征树多了新特征** **且** **类型名 = `Sweep`**
      （★ 而不是拿"体积期望"当判据 —— ★ 那会依赖我造几何的能力）。
    """
    if model is None:
        return {"ok": False, "error": "model 为 None"}
    sel = {}
    for mark, label in ((1, "profile"), (4, "path"), (2, "guide")):
        try:
            sel[label] = int(get_com_member(get_com_member(model, "SelectionManager"),
                                            "GetSelectedObjectCount2", mark))
        except Exception:                                      # noqa: BLE001
            sel[label] = -1
    if sel.get("profile", 0) < 1 or sel.get("path", 0) < 1:
        return {"ok": False, "stage": "selection", "selected_by_mark": sel,
                "error": "扫描要选 **轮廓（mark=1）** 与 **路径（mark=4）**（★ 官方专文给的 mark）；"
                         "★ 当前 mark1=%r · mark4=%r" % (sel.get("profile"), sel.get("path"))}
    before = feature_names(model)
    #: ★ 官方调用序：CreateDefinition ⇒ ISweepFeatureData ⇒ CreateFeature
    try:
        fm = get_com_member(model, "FeatureManager")
        data = get_com_member(fm, "CreateDefinition", SW_FM_SWEEP_CUT if cut else SW_FM_SWEEP)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "stage": "CreateDefinition", "selected_by_mark": sel,
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:200])}
    if data is None:
        return {"ok": False, "stage": "CreateDefinition", "selected_by_mark": sel,
                "error": "CreateDefinition(swFmSweep=%d) 回了 None（★ 与事实 43 的 35 常量表有关？）"
                         % (SW_FM_SWEEP_CUT if cut else SW_FM_SWEEP)}
    #: ★ 认领选择（★ `AccessSelections` 是官方要求的第二步）
    #: ★★★ 2026-10-01（轮 315）**第二个参数要传空 Dispatch物件**（★ **事实 33**）——
    #:   传 `None` ⇒ `com_error: (-2147352571, '类型不匹配。', None, **2**)`（★ 位置 2）。
    #:   ★ 而真机实测：**即使这一步报错，特征仍然建成了**（`扫描1` · type=`Sweep`）
    #:   ⚠⚠ **2026-10-03（轮 488）更正**：上面那句**在本轮的前置下不成立** ⚠
    #:     ★ 一次**A/B**（`tools/prove_sweep_ab.py`，★ 同一套几何 + 同一套选区 `{1:1, 4:1}`，只改常量）：
    #:       `const=17`（实体）⇒ **不成** · `access = 0x80010105` · `CreateFeature = None`；
    #:       `const=62`（曲面）⇒ **不成** · 同上。
    #:     ⇒ ★★ **两路都卡在 `AccessSelections`**，★ 故「它不是必需的」这半句**至少在这套前置下不成立**；
    #:     ★ 而轮 315 那次能成，说明**当时的前置与本轮不同**（★ 而差在哪尚未查）。
    #:   ⇒ ★ 所以它**不是必需的**；★ 而本包装仍然试它（★ 因为官方步骤里有）、**而不把它当判据**。
    access = None
    try:
        from sw_part import _empty_callout as _ec
        access = bool(get_com_member(data, "AccessSelections", model, _ec()))
    except Exception as exc:                                   # noqa: BLE001
        access = "ERR %s: %s" % (type(exc).__name__, str(exc)[:110])
    try:
        feat = get_com_member(fm, "CreateFeature", data)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "stage": "CreateFeature", "selected_by_mark": sel, "access": access,
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:200])}
    #: ★★★★ 2026-10-03（接手轮）**补上成功路径的 `return`** —— ★★ 由 bunny 的
    #:   `recon/precall-cand/precall-verdict.md` 报出、★ **我复核确认**（M3）。
    #:   ★★ **病灶**：原函数**最后一个语句就是上面那个 `except` 的 `return`**
    #:     ⇒ ★★★ **`CreateFeature` 不抛异常时，函数直接掉出末尾、返回 `None`**
    #:     ⇒ ★★ 而**调用方看到的是 `ret_type=None`**、★ 于**分不清"没建成"与"没返回值"**。
    #:   ★ 后果（★ 已发生、如实记）：★ 我第 32 轮据此写下
    #:     「失败已越过前置、卡在扫描 API 自身」⇒ ★★ **那个结论是错的** ——
    #:     ★ 真相是**我们根本没拿到返回值**，★ 所以"建成没建成"当时**无从判断**。
    #:   ★★ 而且本函数 docstring 逐字写着判据：
    #:     「**特征树多了新特征** **且** **类型名 = `Sweep`**（★ 事实 242：挑只依赖被测对象的那个）」
    #:     ⇒ ★★★ **那个"类型名"检查从来没实现过** —— ★ 典型的"文档承诺了、代码没做"。
    after = feature_names(model)
    new = [n for n in after if n not in before]
    tname = ""
    if feat is not None:
        try:
            tname = str(get_com_member(feat, "GetTypeName2") or "")
        except Exception:                                      # noqa: BLE001
            tname = ""
    return {"ok": bool(new) and (tname == "Sweep"), "stage": "done",
            "feature_name": (new[-1] if new else None), "new_features": new,
            "tree_before": len(before), "tree_after": len(after),
            "type_name": tname, "access": access, "selected_by_mark": sel,
            "cut": bool(cut),
            "★": "判据 = **特征树多了新特征** **且** **类型名 = `Sweep`**（★ 事实 242：挑只依赖被测对象的那个）"}
def create_sweep_surface_report(model) -> dict:
    """★ **曲面扫描**：`CreateDefinition(**swFmRefSurface = 62**)` → `ISweepFeatureData` → `CreateFeature`。

    ★★★ 2026-10-03（轮 486）**为什么是 62**（★ 三源互证）：
      · ★ 官方 `C:\\swapi\\types\\IFeatureManager\\CreateDefinition.md` 的**合法常量表**里有一条逐字是
        「**`swFmRefSurface` (surface sweep)**」 ✓
      · ★ 而反射转储 `_raw/enum_values_sldworks.txt` 给出 **`swFmRefSurface = 62`** ✓
      · ★ 而 `ISweepFeatureData.SweepType` 是 **get-only**、回的正是 `swFeatureNameID_e` 的值
        ⇒ ★★ **即：同一个 `ISweepFeatureData` 可承载 "swept boss"(17) 或 "surface sweep"(62)**
        ⇒ **`CreateDefinition(62)` 就是把它初始化成曲面扫描** ✓

    ★★ **为什么不是台账给的那个名字**：台账写 `InsertProtrusionSwept4(Surface)`（★ 一轮前刚核过）——
      ★ 而 `IModelDoc2.InsertSweepRefSurface` 与 `…RefSurface2` **两个都标 Obsolete**，
      ★ 且都把继任者指向 `IFeatureManager::InsertProtrusionSwept3`（★ **实体**那族）⚠
      ⇒ ★★ **正解是 `CreateDefinition` 那条现代入口**（★ 与本模块既有的两条同族）✓

    ★ 判据与 `create_sweep_report` 同口径（★ 事实 242）：**特征树多了新特征** **且** **类型名 = `Sweep`**。
    ⚠⚠ **2026-10-03（轮 486）真机**：本函数**尚未建成** —— 卡在**最后的选区 mark**上。
      ★ 而三个真因都**定位到了**（★ 已写进 `output/sweep-surface-evidence.json`）：
        ① `IFeatureManager.FeatureName` 是**属性**，★★ 而**取特征的真名是 `IModelDoc2.FeatureByName(name)`**（**方法**）—— 两个名字极像，用错**不报错、只是选不上**（**事实 383**）；
        ② `sw_part._select_sketch_feature_by_name` 内部用 **`append=False`**（`sw_part.py` L350）⇒ **调两次只剩第二次**；
        ③ 开**第二个草图**前要先 `ClearSelection2`，★ 否则 `start_sketch` 选不中基准面、**草图根本不建成**。
      ★ 下一轮：`append=True` 后变成 `{1:1, 4:0}`（**反过来了**）⇒ 去查**扫描自己的**官方专文（而不是照搬 `sw_loft` 里那张针对 `InsertProtrusionBlend2` 的 mark 表）。
    ★ ★★ **按 A4 不登记成工具、不写 verified** —— ★ **不假装做到**。
    ⚠ ★ 调用前同样要选好**轮廓（mark=1）+ 路径（mark=4）**（★ 官方专文给的 mark）。
    """
    if model is None:
        return {"ok": False, "error": "model 为 None"}
    sel = {}
    for mark, label in ((1, "profile"), (4, "path"), (2, "guide")):
        try:
            sel[label] = int(get_com_member(get_com_member(model, "SelectionManager"),
                                            "GetSelectedObjectCount2", mark))
        except Exception:                                      # noqa: BLE001
            sel[label] = -1
    if sel.get("profile", 0) < 1 or sel.get("path", 0) < 1:
        return {"ok": False, "stage": "selection", "selected_by_mark": sel,
                "error": "曲面扫描要选 **轮廓（mark=1）** 与 **路径（mark=4）**；"
                         "★ 当前 mark1=%r · mark4=%r" % (sel.get("profile"), sel.get("path"))}
    before = feature_names(model)
    try:
        fm = get_com_member(model, "FeatureManager")
        data = get_com_member(fm, "CreateDefinition", SW_FM_REF_SURFACE)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "stage": "CreateDefinition", "selected_by_mark": sel,
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:200])}
    if data is None:
        return {"ok": False, "stage": "CreateDefinition", "selected_by_mark": sel,
                "error": "CreateDefinition(swFmRefSurface=%d) 回了 None" % SW_FM_REF_SURFACE}
    access = None
    try:
        from sw_part import _empty_callout as _ec
        access = bool(get_com_member(data, "AccessSelections", model, _ec()))
    except Exception as exc:                                   # noqa: BLE001
        access = "ERR %s: %s" % (type(exc).__name__, str(exc)[:110])
    try:
        feat = get_com_member(fm, "CreateFeature", data)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "stage": "CreateFeature", "selected_by_mark": sel, "access": access,
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:200])}
    after = feature_names(model)
    new = [n for n in after if n not in before]
    tname = _feature_type_name(model, new[-1]) if new else None
    return {"ok": bool(new) and (tname == "Sweep"), "feature_name": (new[-1] if new else None),
            "new_features": new, "type_name": tname, "tree_before": len(before),
            "tree_after": len(after), "selected_by_mark": sel, "access_selections": access,
            "sw_fm_const": SW_FM_REF_SURFACE,
            "★": "曲面扫描走 CreateDefinition(swFmRefSurface=62) → ISweepFeatureData → CreateFeature"
                 "（★ 而台账给的 InsertSweepRefSurface* 两个都 Obsolete）；"
                 "★ 判据 = 特征树多了 **且** 类型名 = `Sweep`（事实 242）"}
