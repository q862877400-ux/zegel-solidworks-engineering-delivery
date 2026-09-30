# -*- coding: utf-8 -*-
"""修 17 处「归一化名」错误：arity 表与调用点统一到 COM 名。

⚑ 根因：反射清单里属性形态写作 ``get_Xxx``（.NET interop 约定），
  但 ``get_com_member`` 走 ``getattr(obj, name)`` ⇒ 传的必须是 **COM 名** ``Xxx``。
  我在 arity 表里写成了 ``GetXxx``（大写 G）—— 那是第三种形式，谁都不认。
"""
from __future__ import annotations

import importlib.util
import io
import re
import sys
import types
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass

REPO = Path(r"C:\swprojects\sw-skill-fork")

# ── 1) sw_model_doc_extension.py ────────────────────────────────────
MDE_OLD = '''MDE_ARITY: dict[str, int] = {
    "SelectByID2": 9,          # ⚑ .NET interop 11 参，末 2 参为 out/Callout
    "SelectAll": 0,
    "GetCustomPropertyManager": 1,
    "GetWhatsWrongCount": 0,
    "GetPersistReference3": 1,
    "GetObjectByPersistReference3": 1,
    "GetDependencies": 5,
    "RunCommand": 4,
    "EditRebuild3": 2,
    "GetMassProperties": 1,
}'''
MDE_NEW = '''MDE_ARITY: dict[str, int] = {
    # ⚑⚑⚑ **键必须是 COM 名，不是反射原名。**
    #   反射写 ``get_CustomPropertyManager(String)``（.NET interop 的属性写法），
    #   而 ``get_com_member`` 走 ``getattr(obj, name)`` ⇒ 实际要传 ``CustomPropertyManager``。
    #   我初稿写成 ``GetCustomPropertyManager``（大写 G）—— **第三种形式，谁都不认**，
    #   运行时会直接 AttributeError。由 tests/test_app_and_section_contract.py 抓出。
    "SelectByID2": 9,                    # 反射整行 11 参；末 2 参为 out/Callout
    "SelectAll": 0,                      # 反射: Void SelectAll()
    "CustomPropertyManager": 1,          # 反射: CustomPropertyManager get_CustomPropertyManager(String)
    "GetWhatsWrongCount": 0,             # 反射: Int32 GetWhatsWrongCount()
    "GetPersistReference3": 1,           # 反射: Object GetPersistReference3(Object)
    "GetObjectByPersistReference3": 2,   # ⚑ 反射是 **2 参**，初稿写了 1 —— 已更正
    "GetDependencies": 5,
    "RunCommand": 2,                     # ⚑ 反射是 **2 参**，初稿写了 4 —— 已更正
    "Rebuild": 1,                        # ⚑ 初稿写的 EditRebuild3 **不存在**
    "GetMassProperties": 2,              # ⚑ 反射是 **2 参**，初稿写了 1 —— 已更正
}'''

# ── 2) sw_section_view.py ───────────────────────────────────────────
SEC_OLD = '''SECTION_VIEW_ARITY: dict[str, int] = {
    "AccessSelections": 2,
    "ReleaseSelectionAccess": 0,
    "GetFeatures": 0,
    "GetBodies": 0,
    "GetComponents": 0,
}'''
SEC_NEW = '''SECTION_VIEW_ARITY: dict[str, int] = {
    # ⚑⚑⚑ 初稿写的 AccessSelections / ReleaseSelectionAccess / GetFeatures /
    #   GetBodies / GetComponents **五个成员在 ISectionViewData 上全部不存在**
    #   —— 那是**凭印象从别的 FeatureData 族搬过来的**。
    #   反射实测该接口**只有 set_* 属性**（FirstPlane / FirstOffset /
    #   FirstReverseDirection / FirstRotationX/Y / FirstColor /
    #   ExcludeSelectedItems …）加三个 Get*PlaneParameters 方法。
    #   ⇒ **本族没有选区事务**，也不提供「取特征/体/组件」——那些在别的接口上。
    "GetFirstPlaneParameters": 2,
    "GetSecondPlaneParameters": 2,
    "GetThirdPlaneParameters": 2,
    "GetDynamicCenterTransform": 1,
}'''

ANN_OLD = '''ANNOTATION_VIEW_ARITY: dict[str, int] = {
    "Activate": 0,
    "ActivateAndReorient": 0,
    "GetAnnotationCount": 0,
    "GetAnnotations": 0,
}'''
ANN_NEW = '''ANNOTATION_VIEW_ARITY: dict[str, int] = {
    "Activate": 0,
    "ActivateAndReorient": 0,
    # ⚑ COM 名是 AnnotationCount / Annotations（反射原名 get_AnnotationCount /
    #   get_Annotations，是 .NET 的属性写法）——初稿写成 GetXxx，COM 层不认。
    "AnnotationCount": 0,
    "Annotations": 0,
    "GetAnnotations2": 2,
}'''

MVM_OLD = '''    "AddSnapShot": 1,
    "GetSnapShotCount": 0,
    "GetSnapShotNames": 0,
    "DeleteSnapShot": 1,
    "DeleteAllSnapShots": 0,
}'''
MVM_NEW = '''    # ⚑ 初稿写的 GetSnapShotCount / GetSnapShotNames / DeleteAllSnapShots
    #   **三个都不存在**。反射实测只有：AddSnapShot(1) / DeleteSnapShot(1) /
    #   GetSnapShot(1) / GetSnapShots(0)。
    "AddSnapShot": 1,
    "DeleteSnapShot": 1,
    "GetSnapShot": 1,
    "GetSnapShots": 0,
}'''

# ── 3) sw_table_annotations.py ──────────────────────────────────────
TBA_OLD = '''    "IHoleTableAnnotation": {
        "GetHoleTable": 0,      # 反射: HoleTable get_HoleTable()
        "Sort": 2,              # 反射: Boolean Sort(Int32, Boolean)
    },
    "IBendTableAnnotation": {
        "GetBendTable": 0,      # 反射: BendTable get_BendTable()
    },
    "IFamilyTableAnnotation": {
        "GetFamilyTableFeature": 0,   # 反射: Object get_FamilyTableFeature()
        "GetSheet": 0,                # 反射: Object GetSheet()
    },
    "IGeneralTableAnnotation": {
        "GetGeneralTable": 0,   # 反射: GeneralTableFeature get_GeneralTable()
        "Sort": 2,              # 反射: Boolean Sort(Int32, Boolean)
    },
    "IGeneralToleranceTableAnnotation": {
        "GetGeneralToleranceTableFeature": 0,   # 反射: GeneralToleranceTableFeature get_...
    },
}'''
TBA_NEW = '''    # ⚑⚑⚑ 五个「取底层特征」的键，COM 名都**没有 Get 前缀** ——
    #   反射原名是 ``get_HoleTable``（.NET 属性写法），COM 名是 ``HoleTable``。
    #   初稿一律写成 ``GetHoleTable``，COM 层不认。
    "IHoleTableAnnotation": {
        "HoleTable": 0,         # 反射: HoleTable get_HoleTable()
        "Sort": 2,              # 反射: Boolean Sort(Int32, Boolean)
    },
    "IBendTableAnnotation": {
        "BendTable": 0,         # 反射: BendTable get_BendTable()
    },
    "IFamilyTableAnnotation": {
        "FamilyTableFeature": 0,        # 反射: Object get_FamilyTableFeature()
        "GetSheet": 0,                  # 反射: Object GetSheet() —— 这个是真方法，带 Get
    },
    "IGeneralTableAnnotation": {
        "GeneralTable": 0,      # 反射: GeneralTableFeature get_GeneralTable()
        "Sort": 2,              # 反射: Boolean Sort(Int32, Boolean)
    },
    "IGeneralToleranceTableAnnotation": {
        "GeneralToleranceTableFeature": 0,   # 反射: ... get_GeneralToleranceTableFeature()
    },
}'''

# 调用点要跟着改
CALLS = [
    ("sw_model_doc_extension.py", '"GetCustomPropertyManager"', '"CustomPropertyManager"'),
    ("sw_model_doc_extension.py", 'f"IModelDocExtension.{member} 官方签名是', 'f"IModelDocExtension.{member} 官方签名是'),
    ("sw_section_view.py", '"GetAnnotationCount"', '"AnnotationCount"'),
    ("sw_section_view.py", '"GetAnnotations"', '"Annotations"'),
    ("sw_section_view.py", '"GetSnapShotNames"', '"GetSnapShots"'),
    ("sw_section_view.py", '"DeleteAllSnapShots"', '"DeleteSnapShot"'),
    ("sw_table_annotations.py", "GetHoleTable", "HoleTable"),
    ("sw_table_annotations.py", "GetBendTable", "BendTable"),
    ("sw_table_annotations.py", "GetFamilyTableFeature", "FamilyTableFeature"),
    ("sw_table_annotations.py", "GetGeneralTable", "GeneralTable"),
    ("sw_table_annotations.py", "GetGeneralToleranceTableFeature", "GeneralToleranceTableFeature"),
]

BLOCKS = {
    "sw_model_doc_extension.py": [(MDE_OLD, MDE_NEW)],
    "sw_section_view.py": [(SEC_OLD, SEC_NEW), (ANN_OLD, ANN_NEW), (MVM_OLD, MVM_NEW)],
    "sw_table_annotations.py": [(TBA_OLD, TBA_NEW)],
}

for filename, pairs in BLOCKS.items():
    p = REPO / "scripts" / filename
    src = p.read_text(encoding="utf-8")
    for old, new in pairs:
        if old not in src:
            print(f"  [FATAL] {filename}: 表块未匹配")
            sys.exit(2)
        src = src.replace(old, new, 1)
    p.write_text(src, encoding="utf-8")
    print(f"  [ok] {filename}: 能力表已改为 COM 名")

for filename, old, new in CALLS:
    if old == new:
        continue
    p = REPO / "scripts" / filename
    src = p.read_text(encoding="utf-8")
    if old in src:
        p.write_text(src.replace(old, new), encoding="utf-8")
        print(f"  [ok] {filename}: 调用点 {old} -> {new}")
print("完成")
