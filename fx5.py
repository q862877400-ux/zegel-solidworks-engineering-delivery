from pathlib import Path
p = Path(r"D:\AI\SW\probe_part.py")
s = p.read_text(encoding="utf-8")
s = s.replace('parts = sorted(BF.glob("*.SLDPRT")) or sorted(BF.glob("*.sldprt"))',
              '# ⚠ ~$ 开头是 SolidWorks 的锁文件（不是零件本体），必须排除\n'
              'parts = [p for p in BF.iterdir()\n'
              '         if p.is_file() and p.suffix.lower() == ".sldprt"\n'
              '         and not p.name.startswith("~$")]')
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("  已排除 ~$ 锁文件")