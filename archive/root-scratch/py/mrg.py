from pathlib import Path
S = Path(r"D:\AI\SW")
head = Path(r"D:\AI\SW\_head.txt")
parts = ["jlc_auto.py", "shot.py"]
out = []
for n in parts:
    src = (S / n).read_text(encoding="utf-8")
    out.append(src)
Path(r"D:\AI\SW\_merged_gui.txt").write_text("\n".join(out), encoding="utf-8")
print("  合并 %d 个文件，共 %d 行" % (len(parts), sum(x.count(chr(10)) for x in out)))