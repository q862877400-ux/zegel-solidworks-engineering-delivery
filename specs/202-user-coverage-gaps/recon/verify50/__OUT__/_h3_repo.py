"""★ vd50-H 第三轮：仓内覆盖核（双证：ToolSpec 名 + 能力层 API 调用）。"""
import subprocess, os, re, sys

REPO_DIRS = [r'D:/AI/SW/mcp-server', r'D:/AI/SW/scripts', r'D:/AI/SW/tools']

CANDIDATES = [
    # (命令, 官方成员, 该命令的仓内工具名 token)
    ('swCommands_Text',                'InsertSketchText',        ['sketch_text', 'sketch_add_text', 'insert_sketch_text']),
    ('swCommands_InsertSketchEQCurve', 'CreateEquationSpline',    ['equation_spline', 'sketch_eq', 'eq_curve']),
    ('swCommands_SplitEntities',       'SplitOpenSegment',        ['split_open_segment', 'sketch_split']),
    ('swCommands_IntersectionCurve',   'IntersectCurves',         ['intersect_curves', 'intersection_curve']),
    ('swCommands_SketchPicture',       'InsertSketchPicture',     ['sketch_picture']),
    ('swCommands_ProjectCurve',        'InsertProjectedSketch',   ['projected_sketch', 'project_curve']),
    ('swCommands_RevolvedCut',         'FeatureRevolveCut',       ['revolve_cut']),
    ('swCommands_TableDrivenPattern',  'InsertTableDrivenPattern',['table_driven']),
    ('swCommands_Flex',                'InsertFlexFeature',       ['flex']),
    ('swCommands_GridFeature',         'InsertGridFeature',       ['grid']),
    ('swCommands_InsertFeatureMoveFace', 'InsertMoveFace2',       ['move_face']),
    ('swCommands_InsertLiveSection',   'InsertLiveSectionPlane',  ['live_section']),
    ('swCommands_MoveCopyBodies',      'InsertMoveCopyBody2',     ['move_copy']),
    ('swCommands_InsertPart',          'InsertPart',              ['insert_part']),
    ('swCommands_FillPattern',         'InsertFillPattern2',      ['fill_pattern']),
    ('swCommands_DimensionPattern',    'InsertDimensionPattern',  ['dimension_pattern']),
    ('swCommands_Deform',              'InsertDeformFeature',     ['deform']),
    ('swCommands_Indent',              'InsertIndentFeature',     ['indent']),
    ('swCommands_CurveDrivenPattern',  'InsertCurveDrivenPattern',['curve_driven']),
    ('swCommands_SketchDrivenPattern', 'InsertSketchDrivenPattern',['sketch_driven']),
    ('swCommands_ImportedGeometry',    'InsertImportedGeometry',  ['imported_geometry']),
    ('swCommands_HealEdges',           'InsertHealEdges',         ['heal']),
    ('swCommands_MateReference',       'InsertMateEntity',        ['mate_entity']),
    ('swCommands_CutWithSurface',      'InsertSurfaceCut4',       ['surface_cut']),
    ('swCommands_InsertSplitFeat',     'InsertSplit',             ['split']),
    ('swCommands_PushPull',            'InsertFreeformFeature',   ['freeform']),
    ('swCommands_HoleSeries',          'InsertHoleSeries4',       ['hole_series']),
    ('swCommands_MateReference2',      'InsertMateReference',     ['mate_reference']),
    ('swCommands_Join',                'InsertJoinFeature',       ['join']),
    ('swCommands_InsertLiveSection2',  'InsertLiveSectionPlane2', ['live_section']),
]

def rg(pat, label):
    hits = []
    for d in REPO_DIRS:
        if not os.path.isdir(d):
            continue
        try:
            p = subprocess.run(['grep', '-rIlE', pat, d, '--include=*.py'],
                               capture_output=True, text=True, encoding='utf-8',
                               errors='replace', timeout=180)
            hits += [h for h in p.stdout.splitlines() if h]
        except Exception as e:
            print('  ERR', d, e)
    return sorted(set(hits))

print('=' * 100)
for cmd, member, toks in CANDIDATES:
    print(f'\n### {cmd}   <-> {member}')
    print('  [A] 官方成员在仓内任何 .py 被提到:')
    ha = rg(member, member)
    print('      ', ha if ha else '—— 0 命中')
    print('  [B] 工具名 token:')
    for t in toks:
        hb = rg(r'\b%s\b' % re.escape(t), t)
        print(f'      {t}: ', hb if hb else '—— 0 命中')
