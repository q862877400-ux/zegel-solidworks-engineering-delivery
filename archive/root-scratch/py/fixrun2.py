from pathlib import Path
p = Path(r"D:\AI\SW\run_audit.py")
s = p.read_text(encoding="utf-8")
s = s.replace("A.main(PLAN[:1])", "A.main(PLAN)")
p.write_text(s, encoding="utf-8")