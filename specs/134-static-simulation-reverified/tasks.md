# Tasks: 静力学真机复验

- [x] T-13401 确认只有一个 SolidWorks 实例（事实 24）
  `→ 验收:` `Get-Process -Name SLDWORKS | Select-Object Id`（**恰好 1 个**）
- [x] T-13402 ★ 跑静力学真机验收
  `→ 验收:` `python tools/capture_simulation_evidence.py`（**exit 0 · `verdict: pass`**）
- [x] T-13403 复核判据是**回读**而不是返回码
  `→ 验收:` `python -c "import json;from pathlib import Path;d=json.loads(Path('output/simulation-evidence.json').read_text(encoding='utf-8'));print(d['verdict'], d['steps']['solve']['plot_names'], d['steps']['solve']['run_analysis_return_is_trustworthy'])"`
  （期望 `pass ['品质1','应力1','位移1','应变1'] False`）
- [x] T-13404 全链 + 回归
  `→ 验收:` `python scripts/release_check.py`（exit 0）· `python -m pytest tests -q`（0 failed）
