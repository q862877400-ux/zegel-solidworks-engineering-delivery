# vd50-B-features · 核「`06-features` 域置信度为高的核对表条目」

- **范围**：只核置信度为「**高**」的条目 —— `audit-06-features-A.md` #1 · `audit-06-features-B.md` #1 #2 #3 #4 · `audit-06-features-C.md` #1–#8 = **共 13 条**
- **★ 中/低置信度的条目（B#5、B#6、C#9）按纪律一律未碰**
- **两查**：① 「官方的原文」是否真在 `C:\swapi`；② 「我们的原文」是否真在被点名的仓内文件里（逐字片段能对上）
- **纪律**：给不出两段原文的不写；不写行号，只写片段；查不到就说查不到。

---

## 表

| 条目 | 文件 | 官方原文在不在 | 我们的原文在不在 | 判定 |
|---|---|---|---|---|
| A-1 | `sw_part.py` · `sketch_slot` | ✅ 在（3 源全中） | ✅ 在 | **成立** |
| B-1 | `sw_part.py` · `revolve_boss`/`revolve_cut` | ✅ 在 | ✅ 在 | **成立** |
| B-2 | `sw_part.py` · `linear_pattern` | ✅ 在 | ✅ 在 | **成立** |
| B-3 | `sw_part.py` · `linear_pattern_report` | ✅ 在 | ✅ 在 | **成立** |
| B-4 | `sw_part.py` · `auto_dimension_sketch` | ✅ 在 | ✅ 在 | **成立** |
| C-1 | `sw_part.py` · `fillet` | ✅ 在 | ✅ 在 | **成立** |
| C-2 | `sw_part.py` · `linear_pattern` + `linear_pattern_report` | ✅ 在 | ✅ 在 | **成立** |
| C-3 | `sw_part.py` · `circular_pattern` | ✅ 在 | ✅ 在 | **成立** |
| C-4 | `sw_part.py` · `sketch_spline` | ✅ 在 | ✅ 在 | **成立** |
| C-5 | `sw_part.py` · `auto_dimension_sketch` | ✅ 在 | ✅ 在 | **成立** |
| C-6 | `sw_part.py` · `auto_dimension_sketch` | ✅ 在 | ⚠ **只在注释里** | **不成立**（已过时） |
| C-7 | `sw_part.py` · `_require_active_sketch` | ✅ 在 | ❌ **不在该文件** | **不成立**（已过时＋文件不符） |
| C-8 | `sw_part.py` · `auto_dimension_sketch` | ✅ 在 | ✅ 在 | **成立** |

**核了 13 处 · 对不上 2 处（C-6、C-7）· 成立 11 处。**

---

## 逐条证据

### A-1 · `CreateSketchSlot` 第 2 实参类型不符 —— **成立**

**我们的原文（`scripts/sw_part.py`）**
```
    return model.SketchManager.CreateSketchSlot(
        0,  # swSketchSlotCreationType_e: 0=Straight
        radius, radius,  # 宽度
        x1, y1, 0,
```

**官方原文 ①（`C:\swapi\types\ISketchManager\CreateSketchSlot.md` · Signature）**
```
**Signature**: `SketchSlot CreateSketchSlot( System.int SlotCreationType, System.int SlotLengthType, System.double Width, System.double X1, ...
```

**官方原文 ②（`C:\swapi\examples\Insert_and_Resize_Sketch_Slot_Example_VB.md`）**
```
Set swSketchSlot = skManager.CreateSketchSlot(swSketchSlotCreationType_e.swSketchSlotCreationType_line, swSketchSlotLengthType_e.swSketchSlotLengthType_CenterCenter, 0.05, -0.05, 0, 0, 0.05, 0, 0, 0, 0, 0, 1, False)
```

**官方原文 ③（`D:\AI\SW\_raw\reflect_sldworks\iface_sldworks.txt`）**
```
SketchSlot CreateSketchSlot(Int32, Int32, Double, Double, Double, Double, Double, Double, Double, Double, Double, Double, Int32, Boolean)
```

**一句话依据**：核对表所引的 Signature 行逐字命中，且三源一致把第 2 形参写成 `System.int` / `swSketchSlotLengthType_CenterCenter` / `Int32`；我们把同一个浮点 `radius` 同时喂给第 2 位（`SlotLengthType`，int）与第 3 位（`Width`，double）⇒ 实参个数 14 = 形参个数 14，**分歧在类型不在个数**。

---

### B-1 · 旋转轴在选轮廓时被清空 —— **成立**

**我们的原文（`scripts/sw_part.py` · `revolve_boss`）**
```
    #: ★ **先轴、后轮廓**（★ 顺序照官方示例 —— 反了会建不成）
    if axis_sketch_name:
        _select_revolve_axis(model, str(axis_sketch_name))
    _ensure_sketch_selected(model, sketch_name)
    return model.FeatureManager.FeatureRevolve2(
```
同一函数的 docstring 还逐字写着：
```
    ⇒ ★★ **轴必须在轮廓之前进选择集**（`FeatureRevolve2` 靠"选择集里谁是轴"来解析）。
```
而 `_ensure_sketch_selected` → `_select_sketch_ref` 的第一句就是清空：
```
def _select_sketch_ref(model, sketch_ref, mark=0):
    ...
    model.ClearSelection2(True)
```
（`revolve_cut` 与 `revolve_boss` 逐字同形：`_select_revolve_axis(...)` → `_ensure_sketch_selected(...)` → `FeatureRevolve2(`。）

**官方原文（`C:\swapi\types\IFeatureManager\FeatureRevolve2.md` · Remarks）**
```
Before calling this method, call [[IModelDocExtension::SelectByID2]] to select:

- the sketch to revolve, using Mark = 0.

- the axis of revolution, using Mark = 4 or 16.
```

**一句话依据**：官方要求轮廓（mark 0）与旋转轴（mark 4/16）**同时留在**选择集里，我们选完轴后走 `_ensure_sketch_selected` 而它内部首句 `model.ClearSelection2(True)` 把选择集清空 ⇒ 调 `FeatureRevolve2` 时轴已不在；**仓内自己的 docstring 也写了「轴必须在轮廓之前进选择集」，与该实现自相矛盾**。

---

### B-2 · `linear_pattern` 从未选方向 —— **成立**

**我们的原文（`scripts/sw_part.py` · `linear_pattern`，全函数只有这一次选择）**
```
    _select_by_id(model.Extension, feature_name, "BODYFEATURE", mark=4)
    ...
    return model.FeatureManager.FeatureLinearPattern3(
```
（该函数体内**没有**任何第二次 `_select_by_id`，方向只以字符串实参出现：`f"{d1_x} {d1_y} {d1_z}",` / `f"{d2_x} {d2_y} {d2_z}",`）

**官方原文（`C:\swapi\types\IFeatureManager\FeatureLinearPattern3.md` · Remarks）**
```
Using [[IModelDocExtension::SelectByID2]] to select features and components, ordered selection of the features and components is required

- 1 and 2 to mark the directions

- 4 to mark the features to pattern
```

**一句话依据**：官方在「选特征」这一列同时要求用 **mark 1 / mark 2 标方向**、mark 4 标特征；我们只做了 mark=4 一次，**从未选过任何方向** ⇒ 与原文对不上。

---

### B-3 · `linear_pattern_report` 空选择集调用 —— **成立**

**我们的原文（`scripts/sw_part.py` · `linear_pattern_report`，函数体内无任何 SelectByID2 / Select）**
```
        get_com_member(get_com_member(model, "FeatureManager"), "FeatureLinearPattern3",
                       n1, s1, n2, s2, False, False, "", "", False, False)
```
形参 `feature_name` 在本函数里只被写进返回字典（`"feature_name": str(feature_name)[:60],`），**从未用于选择**。

**官方原文（同 B-2）**
```
Using [[IModelDocExtension::SelectByID2]] to select features and components, ordered selection of the features and components is required

- 1 and 2 to mark the directions

- 4 to mark the features to pattern
```

**一句话依据**：官方要求调用前必须**有序选择**，我们这个站点**连要阵列的特征都没选**（两个方向名还传的是空串 `"", ""`），选择集为空就调 ⇒ 对不上。

---

### B-4 · 只给一个基准仍调 `AutoDimension2` —— **成立**

**我们的原文（`scripts/sw_part.py` · `auto_dimension_sketch`）**
```
    for segment, mark in ((vertical, 2), (horizontal, 4)):
        if segment is None:
            continue
        try:
            if bool(segment.Select3(selected > 0, mark, _empty_callout())):
```
循环之后是**无条件**调用（两处基准无论缺几个都会走到）：
```
        status_code = int(get_com_member(active, "AutoDimension2", 1, 1, -1, 1, -1))
```

**官方原文（`C:\swapi\types\ISketch\AutoDimension2.md` · Remarks）**
```
You can supply datums for horizontal and vertical dimensioning schemes. ... It is an error to supply just one datum as indicated by the status value swAutodimStatus_DatumNotSupplied.
```

**一句话依据**：官方明写只给一个基准是**错误**，我们对缺失的那个基准 `continue` 跳过后仍无条件调 `AutoDimension2` ⇒ 对不上。（两个 mark 值 2/4 与官方一致，不算分歧。）

---

### C-1 · `FeatureFillet` 是 Obsolete —— **成立**

**我们的原文（`scripts/sw_part.py` · `fillet`）**
```
    return model.FeatureManager.FeatureFillet(
        195, radius, 0, 0, None, None, None
    )
```

**官方原文（`C:\swapi\types\IFeatureManager\FeatureFillet.md` 顶部 Obsolete 行 / `FeatureFillet2.md` 顶部 Obsolete 行）**
```
Obsolete. Superseded by [[IFeatureManager::FeatureFillet2]].
Obsolete. Superseded by [[IFeatureManager::FeatureFillet3]].
```

**一句话依据**：官方点名的后继 `FeatureFillet2` 自己也标 Obsolete ⇒ 现行入口是 `FeatureFillet3`，而我们调的正是被标 Obsolete 的 `FeatureFillet` ⇒ 对不上。

---

### C-2 · `FeatureLinearPattern3` 是 Obsolete（三级链）—— **成立**

**我们的原文（`scripts/sw_part.py`）**
```
    return model.FeatureManager.FeatureLinearPattern3(
        int(d1_count), float(d1_spacing),
```
```
        get_com_member(get_com_member(model, "FeatureManager"), "FeatureLinearPattern3",
                       n1, s1, n2, s2, False, False, "", "", False, False)
```

**官方原文（`FeatureLinearPattern3.md` → `…Pattern4.md` → `…Pattern5.md` 三页顶部 Obsolete 行）**
```
Obsolete. Superseded by [[IFeatureManager::FeatureLinearPattern4]].
Obsolete. Superseded by [[IFeatureManager::FeatureLinearPattern5]].
Obsolete. See [[IFeatureManager::CreateFeature]] and the Remarks in [[ILinearPatternFeatureData]] and [[ILocalLinearPatternFeatureData]].
```

**一句话依据**：两个调用点都调在**被官方标 Obsolete** 的成员上，官方点名链走到底是 `CreateFeature` + `ILinearPatternFeatureData` / `ILocalLinearPatternFeatureData`（三级 Obsolete）⇒ 对不上。

---

### C-3 · `FeatureCircularPattern4` 是 Obsolete（两级链）—— **成立**

**我们的原文（`scripts/sw_part.py` · `circular_pattern`）**
```
    return model.FeatureManager.FeatureCircularPattern4(
        count, angle_rad, False, "None", False, equal_spacing, False
    )
```

**官方原文（`FeatureCircularPattern4.md` → `…Pattern5.md` 顶部 Obsolete 行）**
```
Obsolete. Superseded by [[IFeatureManager::FeatureCircularPattern5]].
Obsolete. See [[IFeatureManager::CreateFeature]] and the Remarks in [[ICircularPatternFeatureData]] and [[ILocalCircularPatternFeatureData]].
```

**一句话依据**：我们调的成员被官方标 Obsolete，其点名后继 `FeatureCircularPattern5` 亦 Obsolete ⇒ 现行走 `CreateFeature` + 两个 `PatternFeatureData` ⇒ 对不上。

---

### C-4 · `CreateSpline2` 是 Obsolete —— **成立**

**我们的原文（`scripts/sw_part.py` · `sketch_spline`）**
```
    seg = get_com_member(model, "SketchManager").CreateSpline2(data, False)
```

**官方原文（`C:\swapi\types\ISketchManager\CreateSpline2.md` 顶部 Obsolete 行）**
```
Obsolete. Superseded by [[ISketchManager::CreateSpline3]].
```
（同一页的 `## Examples` 指向 `CreateSpline3`；本函数 docstring 里也已逐字记了这条，但**调用点仍未换**。）

**一句话依据**：我们调的 `ISketchManager.CreateSpline2` 逐字带 Obsolete 行，官方点名后继 `CreateSpline3` ⇒ 对不上。

---

### C-5 · `ISketch.AutoDimension2` 是 Obsolete —— **成立**

**我们的原文（`scripts/sw_part.py` · `auto_dimension_sketch`）**
```
        status_code = int(get_com_member(active, "AutoDimension2", 1, 1, -1, 1, -1))
```

**官方原文（`C:\swapi\types\ISketch\AutoDimension2.md` 顶部 Obsolete 行）**
```
Obsolete. Superseded by [[ISketchManager::FullyDefineSketch]].
```

**一句话依据**：我们调的 `ISketch.AutoDimension2` 逐字带 Obsolete 行，官方点名后继为 `ISketchManager::FullyDefineSketch`，而调用点未换 ⇒ 对不上。

---

### C-6 · `IModelDoc2.GraphicsRedraw2` 是 Obsolete —— **不成立（已过时）**

**官方原文（`C:\swapi\types\IModelDoc2\GraphicsRedraw2.md` 顶部 Obsolete 行）· ✅ 在**
```
Obsolete. Superseded by [[IModelView::GraphicsRedraw]] and [[IModelView::IGraphicsRedraw]].
```

**我们在 `scripts/sw_part.py` 里能搜到的 `model.GraphicsRedraw2()` · ⚠ 只以注释形式出现，且注释本身说明它已被换掉**
```
        #: ★★★ 2026-10-03（接手轮）**换成后继入口** —— 原来是 `model.GraphicsRedraw2()`。
```

**那段位置现在的活代码是后继入口**
```
        _view = get_com_member(model, "ActiveView")
        if _view is not None:
            get_com_member(_view, "GraphicsRedraw", None)
```
（另一处 `scripts/sw_import_mesh_reference.py` 里的同名片段同样**只在注释里**。）

**一句话依据**：官方 Obsolete 行确实存在，但**我们调用 `GraphicsRedraw2` 的那个事实已经不存在了** —— 活代码早已改成 `IModelView.GraphicsRedraw`，`model.GraphicsRedraw2()` 只作为「原来是…」的注释残留 ⇒ 核对表的分歧点已过时，不成立。

---

### C-7 · `IModelDoc2.GetActiveSketch2` 是 Obsolete —— **不成立（已过时＋文件不符）**

**官方原文（`C:\swapi\types\IModelDoc2\GetActiveSketch2.md` 顶部 Obsolete 行）· ✅ 在**
```
Obsolete. Superseded by [[SketchManager::ActiveSketch]].
```

**我们的原文（核对表点名 `scripts/sw_part.py` · `_require_active_sketch` 包装体内）· ❌ 不在该文件**
- 全仓逐字搜 `sk = get_com_member(model, "GetActiveSketch2")`，**只命中 `scripts/sw_sketch_edit.py`**，`sw_part.py` **没有**这一行；
- `sw_part.py` 里 `GetActiveSketch2` 只剩两类非调用文字：一行注释 + 一行文档依据
```
            #: ★★★ 2026-10-03（接手轮）**换走后继入口** —— 原来是 `get_com_member(model, "GetActiveSketch2")`。
```
```
# 官方依据: `IModelDoc2.GetActiveSketch2`（★ 读活动草图；★ 只用于**判在不在**）·
```
**那个位置的活代码是后继入口**
```
            from sw_sketch import active_sketch as _active_sketch
            sk = _active_sketch(model)
```

**一句话依据**：官方 Obsolete 行在，但核对表引用的「我们的原文」在被点名的 `sw_part.py` 里**根本不存在**（只在注释里，且注释说已换掉）；活代码走的是后继 `sw_sketch.active_sketch` ⇒ 不成立。★ 附注：`sw_sketch_edit.py` 里那条活调用**不在本次核对声明的三份文件范围内**，本条不据此翻案。

---

### C-8 · `ISketchSegment.Select3` 是 Obsolete —— **成立**

**我们的原文（`scripts/sw_part.py` · `auto_dimension_sketch`）**
```
            if bool(segment.Select3(selected > 0, mark, _empty_callout())):
                selected += 1
        except Exception:
            try:
                if bool(segment.Select4(selected > 0, _empty_callout())):
```
（与核对表描述一致：`Select4` 兜底确实存在，但**只在 `Select3` 抛异常时**才走到。）

**官方原文（`C:\swapi\types\ISketchSegment\Select3.md` 顶部 Obsolete 行）**
```
Obsolete. Superseded by [[ISketchSegment::Select4]].
```

**一句话依据**：我们优先调的 `Select3` 逐字带 Obsolete 行，官方点名后继正是下一行那个兜底分支里的 `Select4` ⇒ 对不上。

---

## 口径与「查不到」记录

- **未碰**：`audit-06-features-B.md` #5（`fillet` 无 mark 约定）、#6（`shell` 无 mark 约定）与 `audit-06-features-C.md` #9（`ISketchSegment.Select2`）在源表里是**中**置信度，按任务纪律**一律未核、未写**。
- **本轮无「查不到」条目**：13 条的官方侧引用（`C:\swapi\types\...` 与 A-1 的 example / 反射）**全部逐字命中**；对不上的是**我们这一侧**（C-6、C-7 已过时）。
- **对不上的性质**：C-6 / C-7 都不是「核对表写错了原文」，而是**核对表写完之后仓内已自行改掉**（两处源码注释都带「2026-10-03（接手轮）**换成/换走后继入口** —— 原来是 …」）。
- **未改动仓内任何文件**（铁律 1）；本文件是本轮**唯一**写入。