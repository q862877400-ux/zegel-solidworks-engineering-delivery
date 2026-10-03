"""★ vd50-H 第二轮：接口感知的草图命令核（草图工具条命令的宿主是 ISketchManager / IModelDoc2 / IModelDocExtension）。"""
import json, os, re, glob, collections

OUT = r'D:/AI/SW/specs/202-user-coverage-gaps/recon/verify50/__OUT__'
official = json.load(open(os.path.join(OUT, '_official.json'), encoding='utf-8'))

# 所有含 Text / Project / Silhouette / Intersect / Picture 的官方成员（不限接口）
pat = re.compile(r'text|project|silhouette|intersect|picture|equation', re.I)
hits = collections.defaultdict(list)
for m, ifaces in official.items():
    if pat.search(m):
        for i in ifaces:
            hits[i].append(m)

for i in sorted(hits):
    print(i, '->', sorted(hits[i]))
