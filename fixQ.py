import re, sys
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
T = Path(r"C:\swprojects\sw-skill-fork\tests\test_official_names_only_contract.py")
s = T.read_text(encoding="utf-8")

# 1) _official_members 改为按程序集分别取
old = re.search(r"def _official_members\(\).*?\n    return out\n", s, re.S).group(0)
new = '''def _official_members(asm: str | None = None) -> set[str] | None:
    """某程序集（或全部）的官方成员名。

    ⚑⚑ 必须**按程序集**分别取，不能混成一锅 ——
      本任务明确不收录 sustainability / sw3dprinter / swbrowser，
      混起来比就会把「故意不收」误报成「漏抄」。
    """
    files = ([REFLECT_DIR / f"iface_{asm}.txt"] if asm
             else list(REFLECT_DIR.glob("iface_*.txt")))
    files = [f for f in files if f.is_file()]
    if not files:
        return None
    out: set[str] = set()
    for f in files:
        for line in f.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if line.startswith("## "):
                continue
            m = SIG.match(line)
            if m:
                out.add(re.sub(r"^(get|set)_", "", m.group(1)))
    return out
'''
s = s.replace(old, new, 1)

# 2) 逐个索引文件用它自己的程序集名去比
s = s.replace('''def test_every_registered_name_is_official():
    official = _official_members()
    if official is None:
        print("  (跳过：反射清单不在本机)")
        return
    total = 0
    for p in sorted(SCRIPTS.glob("sw_api_*.py")):
        src = p.read_text(encoding="utf-8")
        for name in re.findall(r"^        '([A-Za-z_]\\w*)': \\d+,$", src, re.M):
            total += 1
            assert name in official, f"{p.name}: {name} 不在官方反射里"
        for name in re.findall(r"^        '([A-Za-z_]\\w*)',$", src, re.M):
            total += 1
            assert name in official, f"{p.name}: 属性 {name} 不在官方反射里"
    assert total > 10000, f"只扫到 {total} 条，清单不该这么小"''',
'''def test_every_registered_name_is_official():
    """⚑ **逐程序集**比对 —— 每个索引只跟它自己那个 DLL 的反射比。"""
    total = 0
    for p in sorted(SCRIPTS.glob("sw_api_*.py")):
        asm = re.search(r"ASSEMBLY = '(\\w+)'", p.read_text(encoding="utf-8")).group(1)
        official = _official_members(asm)
        if official is None:
            print(f"  (跳过：{asm} 反射清单不在本机)")
            continue
        src = p.read_text(encoding="utf-8")
        for name in re.findall(r"^        '([A-Za-z_]\\w*)': \\d+,$", src, re.M):
            total += 1
            assert name in official, f"{p.name}: {name} 不在 {asm} 反射里"
        for name in re.findall(r"^        '([A-Za-z_]\\w*)',$", src, re.M):
            total += 1
            assert name in official, f"{p.name}: 属性 {name} 不在 {asm} 反射里"
    assert total > 10000, f"只扫到 {total} 条，清单不该这么小"''')

# 3) 完整性比对也改成逐程序集
s = s.replace('''def test_index_is_complete_against_reflection():
    """6 份索引合起来 == 反射里的全部族与全部成员。"""
    official = _official_members()
    if official is None:
        print("  (跳过：反射清单不在本机)")
        return
    seen: set[str] = set()
    fams = 0
    for p in sorted(SCRIPTS.glob("sw_api_*.py")):
        src = p.read_text(encoding="utf-8")
        m = re.search(r"FAMILIES: tuple\\[str, \\.\\.\\.\\] = \\((.*?)\\n\\)", src, re.S)
        if m:
            fams += len(re.findall(r"'(\\w+)'", m.group(1)))
        seen |= set(re.findall(r"^        '([A-Za-z_]\\w*)': \\d+,$", src, re.M))
        seen |= set(re.findall(r"^        '([A-Za-z_]\\w*)',$", src, re.M))
    # ⚑ 族数**不写死** —— 写死就会在新增程序集时悄悄过期
    assert fams > 700, f"族数 {fams} 异常偏少，反射清单可能没读全"
    # ⚑ 比对时**同样要剥掉 COM 内部分发口**
    absent = {n for n in official - seen if not re.match(r"^I[A-Z][a-z]", n)}
    assert not absent, f"反射里有、索引里没有: {sorted(absent)[:8]}"''',
'''def test_index_is_complete_against_reflection():
    """**逐程序集**：该 DLL 反射里的成员，索引里必须一个不少。"""
    checked = 0
    for p in sorted(SCRIPTS.glob("sw_api_*.py")):
        src = p.read_text(encoding="utf-8")
        asm = re.search(r"ASSEMBLY = '(\\w+)'", src).group(1)
        official = _official_members(asm)
        if official is None:
            print(f"  (跳过：{asm} 反射清单不在本机)")
            continue
        seen = set(re.findall(r"^        '([A-Za-z_]\\w*)': \\d+,$", src, re.M))
        seen |= set(re.findall(r"^        '([A-Za-z_]\\w*)',$", src, re.M))
        # ⚑ 同样要剥掉 COM 内部分发口（`IGetXxx` 之类）——
        #   索引刻意不收它们，比对时也不能算成「缺」。
        absent = {n for n in official - seen if not re.match(r"^I[A-Z][a-z]", n)}
        assert not absent, f"{asm}: 反射里有、索引里没有: {sorted(absent)[:8]}"
        checked += 1
    assert checked >= 10, f"只比对了 {checked} 个程序集，清单可能没读全"''')
T.write_text(s, encoding="utf-8")
import ast; ast.parse(s)
print("  [ok] 门禁改为逐程序集比对")