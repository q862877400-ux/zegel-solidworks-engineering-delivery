"""★ 把规格 210 的 HANDOFF 版块插到 `docs/HANDOFF.md` 最上面（★ 只做插入）。"""
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
H = ROOT / "docs" / "HANDOFF.md"
BLOCK = ROOT / "output" / "_handoff_s210.md"
BASE = ROOT / "output" / "_handoff_s210_baseline.md"

old = H.read_text(encoding="utf-8")
block = BLOCK.read_text(encoding="utf-8").rstrip() + "\n" + BASE.read_text(encoding="utf-8").rstrip() + "\n"
#: ★ 插在**第一个版本块之前**（★ 找 `# ★★ 本版` 那一行）✓
i = old.index("# ★★ 本版（2026-10-06）：规格 209")
new = old[:i] + block + "\n---\n\n" + old[i:]
assert "规格 210" in new and "规格 209" in new, "★ 两版都在吗"
H.write_text(new, encoding="utf-8")
print("★ HANDOFF 已插入规格 210 版块（%d → %d 字符）" % (len(old), len(new)))
