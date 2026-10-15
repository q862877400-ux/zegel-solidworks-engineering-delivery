import sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
p = Path(r"D:\AI\SW\build_complete_index.py")
s = p.read_text(encoding="utf-8")
# SRC / DLL / DESC 三处加 swmotionstudy（按用户指示：sustainability 不要）
s = s.replace('    "fworks": Path(r"D:\\AI\\SW\\_raw\\reflect\\iface_fworks.txt"),\n}',
              '    "fworks": Path(r"D:\\AI\\SW\\_raw\\reflect\\iface_fworks.txt"),\n'
              '    "swmotionstudy": Path(r"D:\\AI\\SW\\_raw\\reflect\\iface_swmotionstudy.txt"),\n}')
s = s.replace('    "fworks": "SolidWorks.Interop.fworks.dll",\n}',
              '    "fworks": "SolidWorks.Interop.fworks.dll",\n'
              '    "swmotionstudy": "SolidWorks.Interop.swmotionstudy.dll",\n}')
s = s.replace('    "fworks": "SolidWorks.Interop.fworks.dll",\n}',
              '    "fworks": "SolidWorks.Interop.fworks.dll",\n'
              '    "swmotionstudy": "SolidWorks.Interop.swmotionstudy.dll",\n}')
s = s.replace('    "fworks": "SolidWorks Factory / 其它辅助接口",\n}',
              '    "fworks": "SolidWorks Factory / 其它辅助接口",\n'
              '    "swmotionstudy": "SolidWorks Motion —— 机构运动仿真（**需独立许可**）",\n}')
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("  [ok] 构建器已加入 swmotionstudy（sustainability 按用户指示不加入）")