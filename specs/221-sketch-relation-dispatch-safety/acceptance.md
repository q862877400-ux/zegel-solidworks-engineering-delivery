# 221 · 离线安全切片验收记录

日期：2026-10-08。结论：限定离线行为回归通过；runtime/product=not_run。未证明整体EC00、官方枚举正确性、真实COM或工程建模合格；不升级capabilities verified。

## 实际命令与读数

受管Python3.13.12，标准库unittest，无pytest/pydantic安装：

`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B "D:/AI/SW/tests/test_sw_sketch_relations_safety.py" -v`

原实现：12例中9失败，成功/无效关系/调用前兜底3例通过。异常场景两条关系出现24次管理器调用；单条无效果出现12次；改后抛错出现12次；verify=False非欠定义仍执行。均为FakeHost，未碰SW。

修复后：12例全通过，0.001秒；计数pass与完整effect_status=unknown分层增加断言后再次12例全通过。

AST：目标源码/新增测试均解析通过。独立hy4-worker限定只读核查未见异常后重放/批次停止/旧键兼容漏洞，未检查全部系统行为。

## 改动

- scripts/sw_sketch_relations.py：消除3轮、多payload、IAddRelation同签名误用及异常后兜底；管理器路线预先选择，复用既有_dispatch_array；准备包装失败在修改前拒绝。
- 每条关系至多一次修改派发；异常或后读数不可得标uncertain，未派后续标not_started。
- 前态计数不可读、选区不足拒绝；verify=False也不能绕草图欠定义状态。
- 保留ok/applied/total/results等旧字典键。新增execution_state、relation_count_status与effect_status；计数增不宣称完整几何效果pass。
- 新增tests/test_sw_sketch_relations_safety.py，所有sw_part/sw_sketch/SAFEARRAY包装均替身，不证明实际COM包装可行。
- 新正式切片specs/221-sketch-relation-dispatch-safety/，feature游标更新，ROADMAP加接续状态，不改旧完成规格/公共注册表/旧单位修复。

## 原基线与权属

HEAD仍为d072d0c79985f87e9d1f6278241b18fc1f26d713，master；未提交/未跟踪代码未丢弃。目标sw_sketch_relations.py原已未跟踪，原文件内容已读，仅替换明确风险段，保留其余旧工作。未全仓暂存/提交。

## 未过的门

- 官方swConstraintType_e与sw_sketch_relations.py、sketch_relations.py旧映射冲突：下一项须按出厂类型库/实际官方源裁决，不凭猜测改枚举。
- 计数增加无法验证关系类型、实体对应、几何、自由度及保存重开。
- 实际SAFEARRAY、SW护栏与公开MCP ToolSpec接线未测试；本次不是公开工具生产验收。
- 原全量收尾链含git add/关闭SW，未运行；发行快照同步与全门禁未运行，发布之前必须另收口。
- 跨客户端互斥/文档授权等EC00其余义务未实施。

下一动作：核对关系枚举和已存在的SAFEARRAY调用路径，限定公开注册契约及计数/几何独立验证；真机按明确授权与护栏执行，不盲重放或自动关用户文档。
