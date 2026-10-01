# Tasks: 草图几何关系 + 镜像特征

- [x] T-12801 ★ 把 `sw_part` 的 14 个可注入孤立能力**按规则 2/3 精确分诊**
  `→ 验收:` `python -c "import json,re,sys;from pathlib import Path;d=json.loads(Path(r'D:/AI/SW/output/orphan-capabilities.json').read_text(encoding='utf-8'));rows=[r for r in d['orphans'] if r['module']=='sw_part.py' and r['first_param_is_injectable']];print(len(rows), [r['function'] for r in rows])"`
  （期望 14 个；★ 分诊结论见 `tool_specs_batch16.py` 头部那张表）
- [x] T-12802 ★ 核 `insert_composite_curve` **本来就坏**（事实 121/124）
  `→ 验收:` `python -c "import sys;from pathlib import Path;t=Path(r'D:\AI\SW\docs\known-facts.md').read_text(encoding='utf-8');print([l[:70] for l in t.splitlines() if 'InsertCompositeCurve' in l][:2])"`
- [x] T-12803 ★ 核 `relation_type` 的 12 个合法值来自 docstring
  `→ 验收:` `python -c "import sys;sys.path[:0]=[r'C:\swprojects\sw-skill-fork\scripts'];import sw_part as m;d=m.add_sketch_relation.__doc__ or '';print(sum(1 for s in ('sgFIXED','sgHORIZONTAL','sgVERTICAL','sgCOLINEAR','sgPARALLEL','sgPERPENDICULAR','sgTANGENT','sgCONCENTRIC','sgEQUAL','sgSYMMETRIC','sgMIDPOINT','sgCOINCIDENT') if s in d))"`
  （期望 **12**）
- [x] T-12804 写 `tool_specs_batch16.py` + 注册 + 查重名
  `→ 验收:` `python -c "import sys;sys.path[:0]=[r'C:\swprojects\sw-skill-fork\mcp-server',r'C:\swprojects\sw-skill-fork'];import register_capabilities as rc;from collections import Counter;s=rc.all_specs();print(len(s), [k for k,v in Counter(x.name for x in s).items() if v>1] or 'no-dup')"`
  （期望 `56 no-dup`）
- [x] T-12805 两处计数同步（54→56 · 99→101）
  `→ 验收:` `python -m pytest tests/test_server_wiring.py tests/test_mcp_protocol_layer.py -q`（0 failed）
- [x] T-12806 五处口径一致动 2（★ 本轮**缺口第一次动**：338→337）
  `→ 验收:` `python tools/probe_unexposed_functions.py` + `python tools/build_union_map.py`
- [x] T-12807 全链 + 回归
  `→ 验收:` `python scripts/release_check.py`（exit 0）· `python -m pytest tests -q`（0 failed）
