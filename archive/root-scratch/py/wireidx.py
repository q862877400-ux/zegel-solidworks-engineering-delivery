import re, sys, io
from pathlib import Path
for _s in (sys.stdout, sys.stderr):
    try: _s.reconfigure(encoding="utf-8")
    except Exception: pass
# 把 sw_api_* 里的族纳入覆盖表归因：登记表字面量本就能被 LITERAL 认出，
# 关键是让「域映射」包含这些族
f = Path(r"D:\AI\SW\tools\gen_family_coverage.py")
s = f.read_text(encoding="utf-8")
if "_unmapped_sldworks" in s and "sw_api_" not in s:
    add = '''

def _api_index_families() -> dict[str, list[str]]:
    """从 sw_api_<程序集>.py 的 FAMILIES 常量里取族名，按程序集分域。

    ⚑ 这 6 份是**全量索引**（774 族），比之前分散在各模块的登记表更全 ——
      覆盖表必须认它们，否则会说「没覆盖」，而实际上清单已经抄全了。
    """
    out: dict[str, list[str]] = {}
    for p in sorted((REPO / "scripts").glob("sw_api_*.py")):
        asm = p.stem[len("sw_api_"):]
        txt = p.read_text(encoding="utf-8")
        m = re.search(r"FAMILIES: tuple\\[str, \\.\\.\\.\\] = \\((.*?)\\n\\)", txt, re.S)
        if not m:
            continue
        fams = re.findall(r"'(\\w+)'", m.group(1))
        out[f"全量索引/{asm}"] = fams
    return out

'''
    s = s.replace("\ndef main() -> int:", add + "\ndef main() -> int:", 1)
    s = s.replace("    unmapped = _unmapped_sldworks()",
                  "    for _d, _f in _api_index_families().items():\n"
                  "        DOMAIN_FAMILIES.setdefault(_d, []).extend(_f)\n"
                  "    unmapped = _unmapped_sldworks()", 1)
    f.write_text(s, encoding="utf-8")
    import ast; ast.parse(s)
    print("  [ok] gen_family_coverage.py 已接入 sw_api_* 全量索引")
else:
    print("  已接入或无需改动")
