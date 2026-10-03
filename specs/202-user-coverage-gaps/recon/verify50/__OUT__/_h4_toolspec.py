"""★ vd50-H 第四轮：只认 mcp-server/tool_specs_batch*.py 的 ToolSpec（判据收紧）。"""
import os, re, glob, json

BATCH = sorted(glob.glob(r'D:/AI/SW/mcp-server/tool_specs_batch*.py'))
BT = {p: open(p, encoding='utf-8').read() for p in BATCH}
# 能力模块名（module= 字段）
MODS = set()
for t in BT.values():
    for m in re.finditer(r'module\s*=\s*["\']([A-Za-z0-9_]+)["\']', t):
        MODS.add(m.group(1))
    for m in re.finditer(r'from\s+scripts\.([A-Za-z0-9_]+)\s+import', t):
        MODS.add(m.group(1))
    for m in re.finditer(r'import\s+scripts\.([A-Za-z0-9_]+)', t):
        MODS.add(m.group(1))
# 函数名（function= 字段）
FUNCS = set()
for t in BT.values():
    for m in re.finditer(r'function\s*=\s*["\']([A-Za-z0-9_]+)["\']', t):
        FUNCS.add(m.group(1))
TOOLNAMES = set()
for t in BT.values():
    for m in re.finditer(r'name\s*=\s*["\']([A-Za-z0-9_]+)["\']', t):
        TOOLNAMES.add(m.group(1))

print('N_BATCH_FILES', len(BATCH), ' N_TOOLNAMES', len(TOOLNAMES),
      ' N_MODULES', len(MODS), ' N_FUNCS', len(FUNCS))
print()
print('MODULES:', sorted(MODS))
print()

CAND = [
    ('swCommands_Text',                'IModelDoc2.InsertSketchText',      r'InsertSketchText|sketch_text'),
    ('swCommands_InsertSketchEQCurve', 'ISketchManager.CreateEquationSpline2', r'CreateEquationSpline|equation_spline|eq_curve'),
    ('swCommands_SplitEntities',       'ISketchManager.SplitOpenSegment',  r'SplitOpenSegment|split_open|sketch_split'),
    ('swCommands_IntersectionCurve',   'ISketchManager.IntersectCurves',   r'IntersectCurves|intersect_curves'),
    ('swCommands_SketchPicture',       'ISketchManager.InsertSketchPicture', r'InsertSketchPicture|sketch_picture'),
    ('swCommands_ProjectCurve',        'IModelDoc2.InsertProjectedSketch', r'InsertProjectedSketch|projected_sketch|project_curve|projection_curve'),
    ('swCommands_RevolvedCut',         'IFeatureManager.FeatureRevolveCut', r'FeatureRevolveCut|revolve_cut'),
    ('swCommands_TableDrivenPattern',  'IFeatureManager.InsertTableDrivenPattern', r'InsertTableDrivenPattern|table_driven'),
    ('swCommands_LinearPattern',       'IFeatureManager.InsertLinearPattern5',  r'InsertLinearPattern5|FeatureLinearPattern|linear_pattern'),
    ('swCommands_FillPattern',         'IFeatureManager.InsertFillPattern2',r'InsertFillPattern2|fill_pattern'),
    ('swCommands_DimensionPattern',    'IFeatureManager.InsertDimensionPattern', r'InsertDimensionPattern|dimension_pattern'),
    ('swCommands_Deform',              'IFeatureManager.InsertDeformFeature', r'InsertDeformFeature|deform'),
    ('swCommands_Indent',              'IFeatureManager.InsertIndentFeature', r'InsertIndentFeature|indent'),
    ('swCommands_SketchDrivenPattern', 'IFeatureManager.InsertSketchDrivenPattern', r'InsertSketchDrivenPattern|sketch_driven'),
    ('swCommands_CurveDrivenPattern',  'IFeatureManager.InsertCurveDrivenPattern', r'InsertCurveDrivenPattern|curve_driven'),
    ('swCommands_ImportedGeometry',    'IFeatureManager.InsertImportedGeometry', r'InsertImportedGeometry|imported_geometry'),
    ('swCommands_HealEdges',           'IFeatureManager.InsertHealEdges',   r'InsertHealEdges|heal_edge'),
    ('swCommands_MateReference',       'IFeatureManager.InsertMateEntity',  r'InsertMateEntity|mate_entity|mate_reference'),
    ('swCommands_CutWithSurface',      'IFeatureManager.InsertSurfaceCut4', r'InsertSurfaceCut4|surface_cut|cut_with_surface'),
    ('swCommands_PushPull',            'IFeatureManager.InsertFreeformFeature', r'InsertFreeformFeature|freeform'),
    ('swCommands_HoleSeries',          'IFeatureManager.InsertHoleSeries4', r'InsertHoleSeries|hole_series'),
    ('swCommands_InsertSplitFeat',     'IFeatureManager.InsertSplit',     r'InsertSplit|split_feature'),
    ('swCommands_Join',                'IFeatureManager.InsertJoinFeature',r'InsertJoinFeature|join_feature'),
    ('swCommands_Flex',                'IFeatureManager.InsertFlexFeature',r'InsertFlexFeature|flex'),
    ('swCommands_GridFeature',         'IFeatureManager.InsertGridFeature',r'InsertGridFeature|grid_feature'),
    ('swCommands_InsertFeatureMoveFace', 'IFeatureManager.InsertMoveFace2',r'InsertMoveFace2|move_face'),
    ('swCommands_InsertLiveSection',   'IFeatureManager.InsertLiveSectionPlane', r'InsertLiveSectionPlane|live_section'),
    ('swCommands_MoveCopyBodies',      'IFeatureManager.InsertMoveCopyBody2', r'InsertMoveCopyBody2|move_copy'),
    ('swCommands_InsertPart',          'IPartDoc.InsertPart',             r'InsertPart|insert_part'),
    ('swCommands_SilhouetteEntities',  'IModelDoc2.InsertSilhouetteSketch', r'Silhouette'),
]

print('=' * 108)
for cmd, api, pat in CAND:
    rx = re.compile(pat)
    hitfiles = sorted({os.path.basename(p) for p, t in BT.items() if rx.search(t)})
    tools = sorted(n for n in TOOLNAMES if rx.search(n))
    funcs = sorted(f for f in FUNCS if rx.search(f))
    mods = sorted(m for m in MODS if rx.search(m))
    verdict = 'GAP' if not hitfiles else 'covered'
    print(f'[{verdict:7s}] {cmd:36s} {api}')
    print(f'          batch_files={hitfiles}')
    print(f'          tool_names={tools}')
    print(f'          funcs={funcs}  modules={mods}')
