import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
W = Path(r"D:\AI\SW")

#: ── ① 修 AGENTS.md 的排版：把 §5.0 从列表中间挪到列表之后 ────────────
A = W / "AGENTS.md"
t = A.read_text(encoding="utf-8")
start = t.find("### 5.0 ★★ 判据优先去开源项目里找")
assert start > 0, "找不到 §5.0"
end = t.find("\n4. 标等级与出处", start)
assert end > start, "找不到 §5.0 的结束锚点"
BLOCK = t[start:end]
t = t[:start] + t[end + 1:]                      #: 先摘出来（去掉多出的换行）
#: 重新插到「并入六条规则」那一段之前（即 §五 列表结束、新小节开始处）
anchor = "并入六条规则（全文 "
i = t.find(anchor)
assert i > 0, "找不到插入锚点"
t = t[:i] + BLOCK.rstrip() + "\n\n" + t[i:]
A.write_text(t, encoding="utf-8")

#: 核对：列表 1→5 应连续，§5.0 在其后
u = A.read_text(encoding="utf-8")
n1 = u.find("1. 建全景与对差")
n5 = u.find("5. 门禁与实测：")
n50 = u.find("### 5.0 ★★ 判据优先去开源项目里找")
nm = u.find(anchor)
print("  位置核对（应满足 1 < 2 < 3 < 4 < 5 < §5.0 < 并入六条规则）:")
print("    1=%d  5=%d  §5.0=%d  meta=%d" % (n1, n5, n50, nm))
print("  ✓ 排版已正:" , (n1 < n5 < n50 < nm))
print("  列表项 4 仍在:", "4. 标等级与出处" in u)

#: ── ② ROADMAP 游标（W6）──────────────────────────────────────────
p = W / "docs" / "ROADMAP.md"
lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
ADD = (Path(r"D:\AI\SW\_roadmap_w6.txt").read_text(encoding="utf-8")
       if Path(r"D:\AI\SW\_roadmap_w6.txt").is_file() else None)
print()
print("  ROADMAP: 待插入的 W6 段文件存在?", ADD is not None)
