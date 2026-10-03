"""★ vd50-H 第三轮（修正）：仓内覆盖核，纯 Python 走文件（不依赖 grep 可执行文件）。"""
import os, re, json

REPO_DIRS = [r'D:/AI/SW/mcp-server', r'D:/AI/SW/scripts', r'D:/AI/SW/tools', r'D:/AI/SW/tests']

def py_files():
    for d in REPO_DIRS:
        for root, _, fs in os.walk(d):
            if '__pycache__' in root:
                continue
            for f in fs:
                if f.endswith('.py'):
                    yield os.path.join(root, f)

FILES = list(py_files())
CACHE = {p: open(p, encoding='utf-8', errors='replace').read() for p in FILES}
print('N_FILES', len(CACHE))

def find(pat):
    rx = re.compile(pat)
    return sorted(p for p, t in CACHE.items() if rx.search(t))

def snippet(pat, limit=2):
    rx = re.compile(pat)
    out = []
    for p, t in CACHE.items():
        for i, ln in enumerate(t.splitlines()):
            if rx.search(ln):
                out.append((p, ln.strip()[:170]))
                if len(out) >= limit:
                    return out
    return out

CAND = [
    ('swCommands_Text',                'InsertSketchText',         r'\bInsertSketchText\b'),
    ('swCommands_InsertSketchEQCurve', 'CreateEquationSpline',     r'\bCreateEquationSpline2?\b'),
    ('swCommands_SplitEntities',       'SplitOpenSegment',         r'\bSplit(Open|Closed)Segment\b'),
    ('swCommands_IntersectionCurve',   'IntersectCurves',          r'\bIntersectCurves\b'),
    ('swCommands_SketchPicture',       'InsertSketchPicture',      r'\bInsertSketchPicture2?\b'),
    ('swCommands_ProjectCurve',        'InsertProjectedSketch',    r'\bInsertProjectedSketch2?\b'),
    ('swCommands_RevolvedCut',         'FeatureRevolveCut',        r'\bFeatureRevolveCut\b'),
    ('swCommands_TableDrivenPattern',  'InsertTableDrivenPattern', r'\bInsertTableDrivenPattern\b'),
    ('swCommands_Flex',                'InsertFlexFeature',        r'\bInsertFlexFeature\b'),
    ('swCommands_GridFeature',         'InsertGridFeature',        r'\bInsertGridFeature\b'),
    ('swCommands_InsertFeatureMoveFace', 'InsertMoveFace2',        r'\bInsertMoveFace2\b'),
    ('swCommands_InsertLiveSection',   'InsertLiveSectionPlane',   r'\bInsertLiveSectionPlane\b'),
    ('swCommands_MoveCopyBodies',      'InsertMoveCopyBody2',      r'\bInsertMoveCopyBody2\b'),
    ('swCommands_InsertPart',          'InsertPart',               r'\bInsertPart\b'),
    ('swCommands_FillPattern',         'InsertFillPattern2',       r'\bInsertFillPattern2\b'),
    ('swCommands_DimensionPattern',    'InsertDimensionPattern',   r'\bInsertDimensionPattern\b'),
    ('swCommands_Deform',              'InsertDeformFeature',      r'\bInsertDeformFeature\b'),
    ('swCommands_Indent',              'InsertIndentFeature',      r'\bInsertIndentFeature\b'),
    ('swCommands_CurveDrivenPattern',  'InsertCurveDrivenPattern', r'\bInsertCurveDrivenPattern\b'),
    ('swCommands_SketchDrivenPattern', 'InsertSketchDrivenPattern',r'\bInsertSketchDrivenPattern\b'),
    ('swCommands_ImportedGeometry',    'InsertImportedGeometry',   r'\bInsertImportedGeometry\b'),
    ('swCommands_HealEdges',           'InsertHealEdges',          r'\bInsertHealEdges\b'),
    ('swCommands_MateReference',       'InsertMateEntity',         r'\bInsertMateEntity\b'),
    ('swCommands_CutWithSurface',      'InsertSurfaceCut4',        r'\bInsertSurfaceCut4\b'),
    ('swCommands_PushPull',            'InsertFreeformFeature',    r'\bInsertFreeformFeature\b'),
    ('swCommands_HoleSeries',          'InsertHoleSeries4',        r'\bInsertHoleSeries4?\b'),
    ('swCommands_InsertSplitFeat',     'InsertSplit',              r'\bInsertSplit\b'),
    ('swCommands_Join',                'InsertJoinFeature',        r'\bInsertJoinFeature\b'),
    ('swCommands_LinearPattern',       'InsertLinearPattern5',     r'\b(InsertLinearPattern5|FeatureLinearPattern)\b'),
    ('swCommands_SilhouetteEntities',  'InsertSilhouetteSketch',   r'\b(Silhouette|InsertSilhouette)\w*\b'),
]

print('=' * 110)
res = {}
for cmd, member, pat in CAND:
    h = find(pat)
    res[cmd] = {'member': member, 'hits': h}
    mark = 'HIT ' if h else 'ZERO'
    print(f'{mark}  {cmd:38s} {member:28s} {len(h)} file(s)')
    for p in h[:4]:
        print('        ', p)
