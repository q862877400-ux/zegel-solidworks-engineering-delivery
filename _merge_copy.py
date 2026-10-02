"""★ 把代码仓 B 的追踪文件并进工作区 A（★ 跳过 2 个同名文件，交给人工）。"""

import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
A = Path(r"D:\AI\SW")
B = Path(r"C:\swprojects\sw-skill-fork")
SKIP = {".gitignore", "README.md"}          #: ★ 绝不覆盖 A 的这两份


def tracked(root: Path) -> list:
    out = subprocess.run(["git", "-C", str(root), "-c", "core.quotePath=false", "ls-files", "-z"],
                         capture_output=True)
    return [p for p in out.stdout.decode("utf-8", "replace").split("\0") if p]


rels = tracked(B)
copied = skipped_existing = skipped_named = missing = 0
problems = []
for rel in rels:
    if rel in SKIP:
        skipped_named += 1
        continue
    src, dst = B / rel, A / rel
    if not src.is_file():
        missing += 1
        continue
    if dst.exists():
        skipped_existing += 1
        problems.append("已存在(未覆盖): " + rel)
        continue
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        dst.write_bytes(src.read_bytes())
        copied += 1
    except Exception as exc:                                   # noqa: BLE001
        problems.append("复制失败 %s: %s" % (rel, str(exc)[:80]))

print("  B 追踪文件        : %d" % len(rels))
print("  ★ 已复制          : %d" % copied)
print("  ★ 按名单跳过      : %d  (.gitignore / README.md)" % skipped_named)
print("  已存在而未覆盖    : %d" % skipped_existing)
print("  源缺失            : %d" % missing)
for p in problems[:12]:
    print("      " + p)
