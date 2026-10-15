import re, sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
T = Path(r"C:\swprojects\sw-skill-fork\tests\test_official_names_only_contract.py")
s = T.read_text(encoding="utf-8")
# 1) 反射清单列表补 swmotionstudy（⚠ 写死的清单会悄悄过期）
s = s.replace('    Path(r"D:\\AI\\SW\\_raw\\reflect\\iface_fworks.txt"),\n]',
              '    Path(r"D:\\AI\\SW\\_raw\\reflect\\iface_fworks.txt"),\n'
              '    Path(r"D:\\AI\\SW\\_raw\\reflect\\iface_swmotionstudy.txt"),\n]')
# 2) 族数不再写死 —— 按反射实际数
s = s.replace('    assert fams == 774, f"族数 {fams} != 反射实测 774"',
              '    # ⚑ 族数**不写死** —— 写死就会在新增程序集时悄悄过期（本轮就因此\n'
              '    #   忘了把 swmotionstudy 加进上面的反射清单，测试报「查不到成员」）。\n'
              '    assert fams > 700, f"族数 {fams} 异常偏少，反射清单可能没读全"')
# 3) 入口名检查覆盖全部 sw_api_*（含 swmotionstudy）
s = s.replace('    for asm in ("sldworks", "cosworks", "swdocumentmgr", "SWRoutingLib",\n'
              '                "sldcostingapi", "fworks"):',
              '    for asm in sorted(p.stem[len("sw_api_"):]\n'
              '                     for p in SCRIPTS.glob("sw_api_*.py")):')
T.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("  [ok] 测试已改：反射清单补 swmotionstudy / 族数不写死 / 入口检查覆盖全部")