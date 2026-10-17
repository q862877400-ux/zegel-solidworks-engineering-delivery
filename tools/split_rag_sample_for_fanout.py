"""★ 把抽样切成 60 份（每份 2 个工具），给 60 路 Bunny 各读一份 —— ★ 避免在提示里内联 105 条记录。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = Path(Path(__file__).resolve().parents[1])
sample = json.loads((ROOT / "output" / "rag-sample.json").read_text(encoding="utf-8"))
recs = sample["records"]
#: ★ 稳定顺序：按 tool 名排序（★ 可复现），并带上它属于哪一档（分层要在测量时用）
stratum_of = {t: k for k, v in sample["strata"].items() for t in v}
ordered = sorted(recs)
OUT = ROOT / "output" / "rag-queries"
OUT.mkdir(parents=True, exist_ok=True)
N = 2                                     #: ★ 每份 2 个工具
chunks = [ordered[i:i + N] for i in range(0, len(ordered), N)]
print("★ 共 %d 个工具 ⇒ 切 %d 份（每份 %d 个）" % (len(ordered), len(chunks), N))
for i, chunk in enumerate(chunks):
    payload = [{"tool": t, "stratum": stratum_of.get(t, "?"),
                "title": recs[t]["title"], "doc": recs[t]["doc"],
                "params": recs[t]["params"], "module": recs[t]["module"]} for t in chunk]
    (OUT / ("in-%02d.json" % i)).write_text(
        json.dumps(payload, ensure_ascii=False, indent=1), encoding="utf-8")
print("★ 切片写在 %s/in-XX.json（共 %d 个）" % (OUT, len(chunks)))
print("★ 最后一份：", chunks[-1])
