from pathlib import Path
p = Path(r"D:\AI\SW\verify_appid.py")
s = p.read_text(encoding="utf-8")
s = s.replace('(r.text or "")[:80]', '(r.status_code == 200 and "200-OK" or (r.json().get("errorList") or [{}])[0].get("errorCode", "?"))')
s = s.replace('print("  核 ①', 'print("  核 ①').replace('print("     -> %d  %s" % (r.status_code', 'print("     -> %d  %s" % (r.status_code')
p.write_text(s, encoding="utf-8")
print("ok")