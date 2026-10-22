"""★ 组 T0-3 的裁判输入：把我的头条数字 + 口径声明交给三个独立裁判挑毛病。"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/build_t0_judge_inputs.py
# 定位:   组 T0-3 的裁判输入：把我的头条数字 + 口径声明交给三个独立裁判挑毛病。
# 官方依据: 不适用（本仓工具，不调 COM）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(Path(__file__).resolve().parents[1])

scope = json.loads((ROOT / "output" / "metric-scope-report.json").read_text(encoding="utf-8"))

#: ★★ 我这一路报过的头条数字（★ 逐条附"它是在哪一轮、对谁说的"）
CLAIMS = [
    {"id": "C1", "scope": "zero_han_surface", "value": "205 / 433 = 47.3%",
     "text": "433 个工具里，模型可见文本（name+title+doc）完全不含汉字的有 205 个 = 47.3%",
     "where": "支撑「中文查询与工具面词元重叠恒为 0」的论断"},
    {"id": "C2", "scope": "official_term_alignment", "value": "248 / 273 = 90.8%",
     "text": "能取到官方成员名的 273 个里，工具面与官方成员名有词交集的有 248 个 = 90.8%",
     "where": "回答业主「是不是很多英文词和官方文档没对应」"},
    {"id": "C3", "scope": "bm25_topk", "value": "CN top-5 33% · EN-nat top-5 88%",
     "text": "朴素 BM25：中文查询 top-5 命中 33%、自然英文 top-5 命中 88%、名字反推 92%",
     "where": "第一次中英对照"},
    {"id": "C4", "scope": "bm25_topk", "value": "冷门 CN 44% / EN 67% · 热门 CN 5% / EN 74%",
     "text": "分层抽样后：C1 冷门 CN 44% EN 67%；C3 自研层 CN 25% EN 72%；H 热门 CN 5% EN 74%",
     "where": "回答业主「你测的肯定是常见功能」的批评"},
    {"id": "C5", "scope": "lens_replica_topk", "value": "CN top-5 23% · EN-nat top-5 62%",
     "text": "换成 dsh-mcp-lens 的检索算法，在同一目录同一批 48 题上：中文 top-5 23%、英文 62%",
     "where": "核「1000 个工具都能精准找回」能否推广到我们"},
    {"id": "C6", "scope": "model_pick_correct", "value": "41/47 = 87%（A）· 43/47 = 91%（B）",
     "text": "真模型挑工具：盲判裁判判 yes 的占 87%（主判）/ 91%（复核）；前二至少一个 yes = 96%",
     "where": "回答业主「别给命中率，要看挑出来的到底对不对」"},
    {"id": "C7", "scope": "model_pick_correct", "value": "C1 冷门 94% > H 热门 90%",
     "text": "同一批 48 题里分层：冷门 94%、热门 90%、自研层 76%（以主判为准）",
     "where": "支持「模型能跨语言读懂描述，而词法检索器不能」"},
    {"id": "C8", "scope": "lens_replica_topk", "value": "字段贡献 name 2.76 vs 中文 description 0.162",
     "text": "按 lens 公式算字段贡献：name 2.7586、中文 description 0.1617 ⇒ 差约 17 倍",
     "where": "解释 lens 在我们目录上为何更差"},
]

OUT = ROOT / "output" / "t0-judge"
OUT.mkdir(parents=True, exist_ok=True)
N = 3
for i in range(N):
    (OUT / ("judge-in-%d.json" % i)).write_text(json.dumps({
        "judge_index": i,
        "task": "审查下列「头条数字 + 其口径声明」是否存在六类缺陷",
        "scopes": scope["scopes"],
        "claims": CLAIMS,
    }, ensure_ascii=False, indent=1), encoding="utf-8")
print("★ 写出 %d 份裁判输入（每份含 %d 条口径 + %d 条头条数字）" % (N, len(scope["scopes"]), len(CLAIMS)))
print("★ 目录: %s" % OUT)
