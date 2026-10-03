"""★ vd50-H 第五轮：逐条看"看似 covered"的真实命中行（按文件名，不靠排序下标）。"""
import re, os, glob

D = r'D:/AI/SW/mcp-server'

def show(fname, pat, label):
    p = os.path.join(D, fname)
    print(f'\n--- {label}  [{fname}] ---')
    for l in open(p, encoding='utf-8').read().splitlines():
        if re.search(pat, l):
            print('   ', l.strip()[:160])

show('tool_specs_batch2.py',  r'InsertSketchPicture|sketch_picture', 'SketchPicture 命中')
show('tool_specs_batch71.py', r'InsertSplit|split_feature',       'InsertSplit 命中')
show('tool_specs_batch1.py',  r'InsertPart|insert_part',          'InsertPart 命中 batch1')
show('tool_specs_batch9.py',  r'InsertPart|insert_part',          'InsertPart 命中 batch9')
show('tool_specs_batch16.py', r'LinearPattern',                   'LinearPattern batch16')
show('tool_specs_batch32.py', r'LinearPattern',                   'LinearPattern batch32')
show('tool_specs_batch55.py', r'LinearPattern',                   'LinearPattern batch55')
show('tool_specs_batch56.py', r'LinearPattern',                   'LinearPattern batch56')
show('tool_specs_batch66.py', r'LinearPattern',                   'LinearPattern batch66')
