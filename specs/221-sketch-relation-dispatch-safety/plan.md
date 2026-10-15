# 221 · 实施计划

## 技术选择

Python标准库unittest，以importlib加载目标模块；sw_part/sw_sketch只用sys.modules假宿主，不导入真实COM模块。受管Python无pytest/pydantic，故不安装或依赖它们。真实SW未接入本测试。

只改scripts/sw_sketch_relations.py；新增tests/test_sw_sketch_relations_safety.py。不改sw_part旧单位修复、注册表、capabilities等级或旧完成Spec。采用get_com_member_raw式只取不调用的语义，预先选择可调用AddRelation或原字符串兜底；真正修改一旦开始，任何异常或后读数不可得标uncertain并停止后续项。无sleep，不试IAddRelation/tuple/list轮换。复用scripts/sketch_relations.py:_dispatch_array的已存在包装；包装失败发生在派发前时拒绝，不伪称已执行。

verify=False保留参数，但不允许绕欠定义状态/完整选择/可读前态。为兼容旧verify=False不确认applied，此路径不提供效果通过断言。

## 来源、官方核对与许可

- license=MIT：本仓LICENSE；源码sw_sketch_relations.py、sketch_relations.py、sw_connect.py及specs/081。复用本仓模式，保留许可，不复制第三方实现。
- license=reference-only：C:/swapi/types/ISketchRelationManager/AddRelation.md（Object,Int32，活动草图）、ISketchSegment/GetRelationsCount.md；Constrain_Sketch_Example_CSharp.md及IModelDoc2/SketchAddConstraints.md（选择→添加→清选区）。仅读签名/Remarks/示例顺序，不复制官方文本。
- license=reference-only：D:/AI/SW/_raw/reflect_sldworks/iface_sldworks.txt，已核AddRelation(Object,Int32)；IAddRelation(Int32,Object&,Int32)不可当同签名替换。
- CHM解包入口：D:/AI/SW/AI Solidworks/官方文档/SWhelp；本切片未另读CHM全文，不宣称全三源语义验证。签名冲突以出厂类型库为准；未解决枚举/语义冲突不启用真机。

官方swConstraintType_e与旧两个关系映射表存在冲突：属于下个明确任务，当前只防重放，不宣称合法类型已经全面正确。

## 宪法与批准边界

每FR有来源和license；每任务有可跑标准库命令。新221是独立安全切片，不覆盖原已完成081或把此前交接所称缺目录的221冒充历史正式编号。无extensions.yml检出。ROADMAP新增本切片唯一WIP引用；feature.json指向本切片但不修改旧目录。用户21:28允许主代理实质推进；仅离线修复，COM/部署/提交未执行。

## 写入/验收

测试先红后绿；12个FakeHost用例记录每次修改调用，覆盖可能已修改再抛错、返回true无效果、后态unknown、批次停止、兜底异常与状态绕行。静态检查仅核语法，不代替行为测试。收尾链有git add/关闭SW副作用，本轮不执行整链；发行生成物与全门禁未运行，记录为后续发布门。
