from pathlib import Path
p = Path(r"D:\AI\SW\run_audit.py")
s = p.read_text(encoding="utf-8")
s = s.replace("A.main(PLAN)", "A.main(PLAN[:1])")
p.write_text(s, encoding="utf-8")