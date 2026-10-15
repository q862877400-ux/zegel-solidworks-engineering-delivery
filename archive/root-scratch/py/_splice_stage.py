"""★ 用文件里的那行替换 goal-bar 的「阶段：」行（★ 事实 48：长文本先落文件）。"""
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
g = ROOT / "specs" / "210-declarative-effects" / "goal-bar.md"
line = (ROOT / "output" / "_s210_stage_line.txt").read_text(encoding="utf-8").strip()
s = g.read_text(encoding="utf-8")
i = s.index("阶段：")
j = s.index("\n", i)
s = s[:i] + line + s[j:]
g.write_text(s, encoding="utf-8")
print("★ 阶段行已替换；新行含「五批全部收口」= %s" % ("五批全部收口" in s))

t = ROOT / "specs" / "210-declarative-effects" / "tasks.md"
ts = t.read_text(encoding="utf-8")
old = "- [~] **B3-1** 存活驱动"
if old in ts:
    k = ts.index(old)
    e = ts.index("\n", k)
    ts = (ts[:k] + "- [x] **B3-1** 存活驱动（**全量已跑**：★ 448 条 = `empty` 47 + "
          "`nonempty` 135 + `null` 266；★ 按 `inject|doc_type` 分组；★ 分块跑）" + ts[e:])
    t.write_text(ts, encoding="utf-8")
    print("★ B3-1 已勾")
else:
    print("★ B3-1 那行没找到（★ 可能已勾）")
