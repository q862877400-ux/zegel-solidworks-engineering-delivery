"""只读：查 GVINPUT 设备的硬件 ID + 罗技 macros.db 里有哪些宏。"""
import json
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

print("═" * 70)
print("① GVINPUT 设备的硬件 ID / 制造商（它是什么牌子）")
print("═" * 70)
ps = r"""
Get-PnpDevice -ErrorAction SilentlyContinue |
  Where-Object { $_.InstanceId -match 'GVINPUT' } |
  Select-Object -First 1 |
  ForEach-Object {
    $id = $_.InstanceId
    "  FriendlyName : $($_.FriendlyName)"
    "  InstanceId   : $id"
    $hdw = (Get-PnpDeviceProperty -InstanceId $id -KeyName 'DEVPKEY_Device_HardwareIds' -ErrorAction SilentlyContinue).Data
    "  HardwareIds  : $($hdw -join ' | ')"
    $mfg = (Get-PnpDeviceProperty -InstanceId $id -KeyName 'DEVPKEY_Device_Manufacturer' -ErrorAction SilentlyContinue).Data
    "  Manufacturer : $mfg"
    $svc = (Get-PnpDeviceProperty -InstanceId $id -KeyName 'DEVPKEY_Device_Service' -ErrorAction SilentlyContinue).Data
    "  Service      : $svc"
    $parent = (Get-PnpDeviceProperty -InstanceId $id -KeyName 'DEVPKEY_Device_Parent' -ErrorAction SilentlyContinue).Data
    "  Parent       : $parent"
  }
"""
r = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                   capture_output=True, text=True, encoding="utf-8", errors="replace")
print(r.stdout or r.stderr)

print("═" * 70)
print("② 罗技 macros.db（只读 SQLite）")
print("═" * 70)
db = Path(os.environ["LOCALAPPDATA"]) / "LogiOptionsPlus" / "macros.db"
print("  %s  (%d KB)" % (db, db.stat().st_size // 1024))
try:
    con = sqlite3.connect("file:%s?mode=ro" % db.as_posix(), uri=True)
    tabs = [row[0] for row in con.execute("select name from sqlite_master where type='table'")]
    print("  表: %s" % tabs)
    for t in tabs:
        try:
            n = con.execute('select count(*) from "%s"' % t).fetchone()[0]
            print("    %-30s %d 行" % (t, n))
        except Exception as exc:  # noqa: BLE001
            print("    %-30s ✗ %s" % (t, exc))
    # 把每个表的前几行打出来找「按键序列」
    for t in tabs:
        try:
            rows = con.execute('select * from "%s" limit 5' % t).fetchall()
            cols = [d[0] for d in con.execute('select * from "%s" limit 1' % t).description]
            print("\n  ── %s ──" % t)
            print("     列: %s" % cols)
            for row in rows:
                s = str(row)
                print("     %s" % (s[:200]))
        except Exception:  # noqa: BLE001
            pass
except Exception as exc:  # noqa: BLE001
    print("  打不开: %s" % exc)

print()
print("═" * 70)
print("③ Listary Preferences.json（热键）")
print("═" * 70)
pref = Path(os.environ["APPDATA"]) / "Listary" / "UserProfile" / "Settings" / "Preferences.json"
try:
    d = json.loads(pref.read_text(encoding="utf-8"))
    hits = []

    def walk(o, path=""):
        if isinstance(o, dict):
            for k, v in o.items():
                kl = k.lower()
                if any(t in kl for t in ("hotkey", "key", "shortcut", "trigger", "ctrl", "double")):
                    hits.append("%s%s = %r" % (path, k, v))
                walk(v, path + k + ".")
        elif isinstance(o, list):
            for i, v in enumerate(o):
                walk(v, path + "[%d]." % i)

    walk(d)
    for h in hits[:30]:
        print("  %s" % h)
    if not hits:
        print("  （没找到含 hotkey/key/trigger 的字段；顶层键：%s）" % list(d)[:20])
except Exception as exc:  # noqa: BLE001
    print("  读不了: %s" % exc)
