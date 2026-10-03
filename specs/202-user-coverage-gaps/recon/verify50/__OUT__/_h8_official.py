"""★ vd50-H 第八轮：候选的官方侧逐条核（存在性 + 签名逐字）。"""
import os, glob, re

NEED = [
    'IFeatureManager/FeatureLinearPattern3', 'IFeatureManager/FeatureLinearPattern4',
    'IFeatureManager/InsertTableDrivenPattern', 'IFeatureManager/FeatureFillPattern',
    'IFillPatternFeatureData/_overview', 'IFeatureManager/FeatureCurvePattern',
    'ICurveDrivenPatternFeatureData/_overview', 'IFeatureManager/FeatureSketchDrivenPattern',
    'IModelDoc2/InsertProjectedSketch', 'ISketchManager/IntersectCurves',
    'ISketchManager/InsertSketchPicture', 'IModelDoc2/InsertSketchText',
    'ISketchManager/SplitOpenSegment', 'ISketchManager/CreateEquationSpline2',
    'IFeatureManager/FeatureRevolveCut',
]

for rel in NEED:
    p = os.path.join('C:/swapi/types', rel + '.md')
    if not os.path.exists(p):
        print(f'\n### {rel}  ==> 【官方源里没有这一页】')
        continue
    t = open(p, encoding='utf-8').read()
    sig = re.search(r'\*\*Signature\*\*:\s*`?([^`\n]+)', t)
    print(f'\n### {rel}.md   存在')
    print('   Signature:', (sig.group(1).strip()[:190] if sig else '(页里没有 **Signature** 行)'))
    # Obsolete 行
    ob = re.findall(r'^.*Obsolete.*$', t, re.M)
    for o in ob[:2]:
        print('   Obsolete :', o.strip()[:190])
