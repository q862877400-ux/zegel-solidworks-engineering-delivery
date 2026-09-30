import re, sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
T = Path(r"C:\swprojects\sw-skill-fork\tests\test_official_names_only_contract.py")
s = T.read_text(encoding="utf-8")
s = s.replace('REFLECTIONS = sorted(REFLECT_DIR.glob("iface_*.txt")) if REFLECT_DIR.is_dir() else []',
              '# ⚑ **递归**找 —— 最大的 sldworks 反射落在子目录里（_raw\\\\reflect_sldworks\\\\），\n'
              '#   只扫顶层会把 8,210 个方法整个漏掉（本轮实测：只扫到 7,610 条）。\n'
              'REFLECTIONS = sorted(REFLECT_DIR.rglob("iface_*.txt")) if REFLECT_DIR.is_dir() else []')
s = s.replace('    files = ([REFLECT_DIR / f"iface_{asm}.txt"] if asm\n             else list(REFLECT_DIR.glob("iface_*.txt")))',
              '    files = ([next(iter(REFLECT_DIR.rglob(f"iface_{asm}.txt")), None)] if asm\n             else list(REFLECT_DIR.rglob("iface_*.txt")))\n'
              '    files = [f for f in files if f is not None]')
# 计数断言：12 份索引、2 万多条
s = s.replace('    assert total > 10000, f"只扫到 {total} 条，清单不该这么小"',
              '    # ⚑ 阈值随收录程序集增长 —— 写死过小会在「少扫了一个程序集」时也不报\n'
              '    #   （本轮 7,610 < 10,000 正是靠这条抓出 sldworks 反射没被找到）。\n'
              '    assert total > 20000, f"只扫到 {total} 条，清单可能没读全"')
T.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("  [ok] 门禁改为递归发现反射清单")