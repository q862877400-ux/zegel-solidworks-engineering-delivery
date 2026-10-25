"""SolidWorks 官方枚举常量（由 tools/gen_sw_enums.py 生成，勿手改）。

生成源：`C:/swapi/enums/*.md`。要改就改生成器并重跑；
`python -B tools/gen_sw_enums.py --check` 会拦住「手改了但没重新生成」。

★ 为什么生成而不是手抄：手抄 `swConstraintType_e` 曾把 7/8 抄错，把业主的
「平行/垂直」记录成「相切/同心」——假事实比读不到更危险。
"""
# 本文件是生成物：排版由生成器负责（下面这行只放 code，别加注释）
# ruff: noqa: I001
from __future__ import annotations

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身（常量层 · 官方枚举）
# 文件:   scripts/sw_enums.py —— 由 tools/gen_sw_enums.py 生成，勿手改
# 定位:   把官方枚举转成 Python 常量，杜绝手抄枚举抄错（根因 A）。
# 官方依据: `C:\swapi\enums\<枚举名>.md`（本仓铁律 4 的第二套离线源）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────


#: 源：`C:/swapi/enums/swConstraintType_e.md`（86 个取值）
CONSTRAINT_TYPE = {
    0: 'swConstraintType_INVALIDCTYPE',
    1: 'swConstraintType_DISTANCE',
    2: 'swConstraintType_ANGLE',
    3: 'swConstraintType_RADIUS',
    4: 'swConstraintType_HORIZONTAL',
    5: 'swConstraintType_VERTICAL',
    6: 'swConstraintType_TANGENT',
    7: 'swConstraintType_PARALLEL',
    8: 'swConstraintType_PERPENDICULAR',
    9: 'swConstraintType_COINCIDENT',
    10: 'swConstraintType_CONCENTRIC',
    11: 'swConstraintType_SYMMETRIC',
    12: 'swConstraintType_ATMIDDLE',
    13: 'swConstraintType_ATINTERSECT',
    14: 'swConstraintType_SAMELENGTH',
    15: 'swConstraintType_DIAMETER',
    16: 'swConstraintType_OFFSETEDGE',
    17: 'swConstraintType_FIXED',
    18: 'swConstraintType_ARCANG90',
    19: 'swConstraintType_ARCANG180',
    20: 'swConstraintType_ARCANG270',
    21: 'swConstraintType_ARCANGTOP',
    22: 'swConstraintType_ARCANGBOTTOM',
    23: 'swConstraintType_ARCANGLEFT',
    24: 'swConstraintType_ARCANGRIGHT',
    25: 'swConstraintType_HORIZPOINTS',
    26: 'swConstraintType_VERTPOINTS',
    27: 'swConstraintType_COLINEAR',
    28: 'swConstraintType_CORADIAL',
    29: 'swConstraintType_SNAPGRID',
    30: 'swConstraintType_SNAPLENGTH',
    31: 'swConstraintType_SNAPANGLE',
    32: 'swConstraintType_USEEDGE',
    33: 'swConstraintType_ELLIPSEANG90',
    34: 'swConstraintType_ELLIPSEANG180',
    35: 'swConstraintType_ELLIPSEANG270',
    36: 'swConstraintType_ELLIPSEANGTOP',
    37: 'swConstraintType_ELLIPSEANGBOTTOM',
    38: 'swConstraintType_ELLIPSEANGLEFT',
    39: 'swConstraintType_ELLIPSEANGRIGHT',
    40: 'swConstraintType_ATPIERCE',
    41: 'swConstraintType_DOUBLEDISTANCE',
    42: 'swConstraintType_MERGEPOINTS',
    43: 'swConstraintType_ANGLE3P',
    44: 'swConstraintType_ARCLENGTH',
    45: 'swConstraintType_NORMAL',
    46: 'swConstraintType_NORMALPOINTS',
    47: 'swConstraintType_SKETCHOFFSET',
    48: 'swConstraintType_ALONGX',
    49: 'swConstraintType_ALONGY',
    50: 'swConstraintType_ALONGZ',
    51: 'swConstraintType_ALONGXPOINTS',
    52: 'swConstraintType_ALONGYPOINTS',
    53: 'swConstraintType_ALONGZPOINTS',
    54: 'swConstraintType_PARALLELYZ',
    55: 'swConstraintType_PARALLELZX',
    56: 'swConstraintType_INTERSECTION',
    57: 'swConstraintType_PATTERNED',
    58: 'swConstraintType_ISOBYPOINT',
    59: 'swConstraintType_SAMEISOPARAM',
    60: 'swConstraintType_FITSPLINE',
    61: 'swConstraintType_EQUALCURVATURE',
    62: 'swConstraintType_EQUALTANGENT',
    63: 'swConstraintType_TANGENTFACE',
    64: 'swConstraintType_ALONGX3D',
    65: 'swConstraintType_ALONGY3D',
    66: 'swConstraintType_ALONGXPOINTS3D',
    67: 'swConstraintType_ALONGYPOINTS3D',
    68: 'swConstraintType_TRACTION',
    69: 'swConstraintType_BELTTRACTION',
    70: 'swConstraintType_BLOCKFIXEDLOCK',
    71: 'swConstraintType_BLOCKNORMALLOCK',
    72: 'swConstraintType_BLOCKROTATELOCK',
    73: 'swConstraintType_FAKESLOTCONSTRAINT',
    74: 'swConstraintType_FIXEDSLOT',
    75: 'swConstraintType_SAMESLOTS',
    76: 'swConstraintType_LINEARPATTCNT',
    77: 'swConstraintType_CIRCULARPATTCNT',
    78: 'swConstraintType_RADIALOFFSET',
    79: 'swConstraintType_PLANAROFFSET',
    80: 'swConstraintType_EQUALCURV3DALIGN',
    81: 'swConstraintType_FLANGEFACEDIST',
    82: 'swConstraintType_CONICRHO',
    83: 'swConstraintType_C3TOUCH',
    84: 'swConstraintType_DOUBLEANGLE',
    85: 'swConstraintType_SAMECURVELENGTH',
}

#: `CONSTRAINT_TYPE` 中文标签（只给已核过的值）
CONSTRAINT_TYPE_ZH = {
    1: '尺寸',
    2: '角度',
    3: '半径',
    4: '水平',
    6: '相切',
    7: '平行',
    8: '垂直',
    9: '重合',
    10: '同心',
    11: '对称',
    12: '中点',
    15: '直径',
    17: '固定',
    25: '水平点',
    27: '共线',
    32: '转换实体',
}


#: 源：`C:/swapi/enums/swMateType_e.md`（26 个取值）
MATE_TYPE = {
    0: 'swMateCOINCIDENT',
    1: 'swMateCONCENTRIC',
    2: 'swMatePERPENDICULAR',
    3: 'swMatePARALLEL',
    4: 'swMateTANGENT',
    5: 'swMateDISTANCE',
    6: 'swMateANGLE',
    7: 'swMateUNKNOWN',
    8: 'swMateSYMMETRIC',
    9: 'swMateCAMFOLLOWER',
    10: 'swMateGEAR',
    11: 'swMateWIDTH',
    12: 'swMateLOCKTOSKETCH',
    13: 'swMateRACKPINION',
    14: 'swMateMAXMATES',
    15: 'swMatePATH',
    16: 'swMateLOCK',
    17: 'swMateSCREW',
    18: 'swMateLINEARCOUPLER',
    19: 'swMateUNIVERSALJOINT',
    20: 'swMateCOORDINATE',
    21: 'swMateSLOT',
    22: 'swMateHINGE',
    23: 'swMateSLIDER',
    24: 'swMatePROFILECENTER',
    25: 'swMateMAGNETIC',
}

#: `MATE_TYPE` 中文标签（只给已核过的值）
MATE_TYPE_ZH = {
    0: '重合',
    1: '同心',
    2: '垂直',
    3: '平行',
    4: '相切',
    5: '距离',
    6: '角度',
    16: '锁定',
}


#: 源：`C:/swapi/enums/swMateAlign_e.md`（3 个取值）
MATE_ALIGN = {
    0: 'swMateAlignALIGNED',
    1: 'swMateAlignANTI_ALIGNED',
    2: 'swMateAlignCLOSEST',
}

#: `MATE_ALIGN` 中文标签（只给已核过的值）
MATE_ALIGN_ZH = {
    0: '对齐',
    1: '反向对齐',
    2: '最近',
}


#: 源：`C:/swapi/enums/swSketchSegments_e.md`（6 个取值）
SEGMENT_KIND = {
    0: 'swSketchLINE',
    1: 'swSketchARC',
    2: 'swSketchELLIPSE',
    3: 'swSketchSPLINE',
    4: 'swSketchTEXT',
    5: 'swSketchPARABOLA',
}

#: `SEGMENT_KIND` 中文标签（只给已核过的值）
SEGMENT_KIND_ZH = {
    0: '直线',
    1: '圆弧',
    2: '椭圆',
    3: '样条',
    4: '文字',
    5: '抛物线',
}


#: 源：`C:/swapi/enums/swDocumentTypes_e.md`（8 个取值）
DOC_KIND = {
    0: 'swDocNONE',
    1: 'swDocPART',
    2: 'swDocASSEMBLY',
    3: 'swDocDRAWING',
    4: 'swDocSDM',
    5: 'swDocLAYOUT',
    6: 'swDocIMPORTED_PART',
    7: 'swDocIMPORTED_ASSEMBLY',
}

#: `DOC_KIND` 中文标签（只给已核过的值）
DOC_KIND_ZH = {
    1: '零件',
    2: '装配',
    3: '图样',
}


#: 源：`C:/swapi/enums/swBodyType_e.md`（9 个取值）
BODY_TYPE = {
    -1: 'swAllBodies',
    0: 'swSolidBody',
    1: 'swSheetBody',
    2: 'swWireBody',
    3: 'swMinimumBody',
    4: 'swGeneralBody',
    5: 'swEmptyBody',
    6: 'swMeshBody',
    7: 'swGraphicsBody',
}


#: 源：`C:/swapi/enums/swExternalReferenceStatus_e.md`（5 个取值）
EXTERNAL_REF_STATUS = {
    0: 'swExternalReferenceBroken',
    1: 'swExternalReferenceLocked',
    3: 'swExternalReferenceInContext',
    4: 'swExternalReferenceOutOfContext',
    5: 'swExternalReferenceDangling',
}


#: 源：`C:/swapi/enums/swCustomInfoType_e.md`（7 个取值）
CUSTOM_INFO_TYPE = {
    0: 'swCustomInfoUnknown',
    3: 'swCustomInfoNumber',
    5: 'swCustomInfoDouble',
    11: 'swCustomInfoYesOrNo',
    30: 'swCustomInfoText',
    64: 'swCustomInfoDate',
    105: 'swCustomInfoEquation',
}


#: 源：`C:/swapi/enums/swCustomInfoGetResult_e.md`（3 个取值）
CUSTOM_INFO_GET_RESULT = {
    0: 'swCustomInfoGetResult_CachedValue',
    1: 'swCustomInfoGetResult_NotPresent',
    2: 'swCustomInfoGetResult_ResolvedValue',
}


#: 源：`C:/swapi/enums/swInsertPartOptions_e.md`（24 个取值）
INSERT_PART_OPTIONS = {
    1: 'swInsertPartImportSolids',
    2: 'swInsertPartImportSurfaces',
    4: 'swInsertPartImportAxes',
    8: 'swInsertPartImportPlanes',
    16: 'swInsertPartImportCosmeticThreads',
    32: 'swInsertPartImportAbsorbedSketchs',
    64: 'swInsertPartImportUnabsorbedSketchs',
    128: 'swInsertPartImportCustomProperties',
    256: 'swInsertPartImportCoordinateSystem',
    512: 'swInsertPartBreakLink',
    1024: 'swInsertPartImportModelDimensions',
    2048: 'swInsertPartImportCutListProperties',
    4096: 'swInsertPartImportHoleWzdData',
    8192: 'swInsertPartImportSMInfo',
    16384: 'swInsertPartImportIndProps',
    32768: 'swInsertPartImportCustomToFileProperties',
    65536: 'swInsertPartImportCustomToCutlistProperties',
    131072: 'swInsertPartImportDimXpertAnnotations',
    262144: 'swInsertPartDontZoomAll',
    524288: 'swInsertPartImportMaterial',
    1048576: 'swInsertPartImportPropagateVisualPropertiesFromOriginalPart',
    2097152: 'swInsertPartImportPoints',
    4194304: 'swInsertPartImportPartMaterial',
    8388608: 'swInsertPartImportGraphicBodies',
}


#: 源：`C:/swapi/enums/swEditPartCommandStatus_e.md`（7 个取值）
EDIT_PART_STATUS = {
    -5: 'swEditPartCompMustHaveWriteAccess',
    -4: 'swEditPartCompMustBeResolved',
    -3: 'swEditPartCompMustBeSelected',
    -2: 'swEditPartAsmMustBeSaved',
    -1: 'swEditPartFailure',
    0: 'swEditPartSuccessful',
    1: 'swEditPartCompNotPositioned',
}


#: 源：`C:/swapi/enums/swSketchPointType_e.md`（12 个取值）
SKETCH_POINT_TYPE = {
    -1: 'swSketchPointType_Unknown',
    0: 'swSketchPointType_Internal',
    1: 'swSketchPointType_User',
    2: 'swSketchPointType_Spline',
    3: 'swSketchPointType_Datum',
    4: 'swSketchPointType_VirtualSharp',
    5: 'swSketchPointType_Parabola',
    6: 'swSketchPointType_MidPoint',
    7: 'swSketchPointType_FramePoint',
    8: 'swSketchPointType_Origin',
    9: 'swSketchPointType_Ellipse',
    10: 'swSketchPointType_External',
}

#: `SKETCH_POINT_TYPE` 中文标签（只给已核过的值）
SKETCH_POINT_TYPE_ZH = {
    1: '用户点',
    8: '草图原点',
    10: '外部引用点',
}


#: 源：`C:/swapi/enums/swSmartDimensionDirection_e.md`（4 个取值）
SMART_DIM_DIRECTION = {
    0: 'swSmartDimensionDirection_Right',
    1: 'swSmartDimensionDirection_Up',
    2: 'swSmartDimensionDirection_Left',
    3: 'swSmartDimensionDirection_Down',
}
