import sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
p = Path(r"D:\AI\SW\build_complete_index.py")
s = p.read_text(encoding="utf-8")
# 按用户指示收录：swdimxpert / swpublished / gtswutilities / dsgnchk /
#                sldtoolboxconfigureaddin
# 明确不收：sw3dprinter / swbrowser / sustainability
add_src = '    "swmotionstudy": Path(r"D:\\AI\\SW\\_raw\\reflect\\iface_swmotionstudy.txt"),\n}'
new_src = ('    "swmotionstudy": Path(r"D:\\AI\\SW\\_raw\\reflect\\iface_swmotionstudy.txt"),\n'
           '    "swdimxpert": Path(r"D:\\AI\\SW\\_raw\\reflect\\iface_swdimxpert.txt"),\n'
           '    "swpublished": Path(r"D:\\AI\\SW\\_raw\\reflect\\iface_swpublished.txt"),\n'
           '    "gtswutilities": Path(r"D:\\AI\\SW\\_raw\\reflect\\iface_gtswutilities.txt"),\n'
           '    "dsgnchk": Path(r"D:\\AI\\SW\\_raw\\reflect\\iface_dsgnchk.txt"),\n'
           '    "sldtoolboxconfigureaddin": Path(r"D:\\AI\\SW\\_raw\\reflect\\iface_sldtoolboxconfigureaddin.txt"),\n'
           '    # ⚑ 按用户指示**不收录**：sw3dprinter（只 1 个接口）、'
           'swbrowser（只 2 个）、\n'
           '    #   sustainability（绿色设计，非本任务目标）。\n'
           '    "swconst_only": None,\n}')
assert add_src in s
s = s.replace(add_src, new_src, 1)
# DLL 表
add_dll = '    "swmotionstudy": "SolidWorks.Interop.swmotionstudy.dll",\n}'
new_dll = ('    "swmotionstudy": "SolidWorks.Interop.swmotionstudy.dll",\n'
           '    "swdimxpert": "SolidWorks.Interop.swdimxpert.dll",\n'
           '    "swpublished": "SolidWorks.Interop.swpublished.dll",\n'
           '    "gtswutilities": "SolidWorks.Interop.gtswutilities.dll",\n'
           '    "dsgnchk": "SolidWorks.Interop.dsgnchk.dll",\n'
           '    "sldtoolboxconfigureaddin": "SolidWorks.Interop.sldtoolboxconfigureaddin.dll",\n'
           '    "swconst_only": "SolidWorks.Interop.swconst.dll",\n}')
assert add_dll in s
s = s.replace(add_dll, new_dll, 1)
# DESC 表
add_d = '    "swmotionstudy": "SolidWorks Motion —— 机构运动仿真（**需独立许可**）",\n}'
new_d = ('    "swmotionstudy": "SolidWorks Motion —— 机构运动仿真（**需独立许可**）",\n'
         '    "swdimxpert": "DimXpert —— 尺寸标注自动化 / GD&T 公差",\n'
         '    "swpublished": "加载项开发框架（属性管理页回调、消息栏）",\n'
         '    "gtswutilities": "几何分析 / 壁厚分析 / 图档比较 等独立工具",\n'
         '    "dsgnchk": "Design Checker —— 设计检查器",\n'
         '    "sldtoolboxconfigureaddin": "Toolbox 配置加载项",\n'
         '    "swconst_only": "（不收录）",\n}')
assert add_d in s
s = s.replace(add_d, new_d, 1)
# main 里跳过 None
s = s.replace("        if not path.is_file():\n            print(f\"[FATAL] 反射清单缺失: {path}\")\n            return 2",
              "        if path is None or not Path(path).is_file():\n            continue")
p.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("  [ok] 构建器已加入 5 个程序集（sw3dprinter / swbrowser / sustainability 按指示不收）")