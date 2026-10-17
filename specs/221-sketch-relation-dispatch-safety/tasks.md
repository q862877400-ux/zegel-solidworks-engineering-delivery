# 221 · 任务（ROADMAP对应：草图关系派发安全切片）

- [x] T001 核官方AddRelation/计数/调用序与本仓SAFEARRAY实现，固定唯一写面。→ 验收: `"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -c "from pathlib import Path; assert Path('scripts/sketch_relations.py').is_file(); assert Path('C:/swapi/types/ISketchRelationManager/AddRelation.md').is_file()"`；签名/Remarks/行为结论另由实际阅读记录，不把文件存在当正确性证明。
- [x] T002 创建12例标准库离线回归，验证原路径失败。→ 验收: `"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B "tests/test_sw_sketch_relations_safety.py" -v`；原实现12例中9失败，已记录，不执行COM。
- [x] T003 改一次派发/uncertain停止/前置拒绝，保留旧结果键。→ 验收: `"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B "tests/test_sw_sketch_relations_safety.py" -v`；12例全绿才完成。
- [x] T004 静态语法与副作用审计、独立核查、记录离线/真机等级，更新ROADMAP及交接。→ 验收: `"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -c "import ast,pathlib; [ast.parse(pathlib.Path(p).read_text(encoding='utf-8')) for p in ['scripts/sw_sketch_relations.py','tests/test_sw_sketch_relations_safety.py']]"`；无COM、无全仓暂存；发行全门禁/真机不伪称通过。

依赖：T001→T002→T003→T004。正式化的是最小修复，EC00其他任务不自动勾完。未解决官方枚举冲突、实际管理器/SAFEARRAY行为、完整工程效果与生产注册是后续门。
