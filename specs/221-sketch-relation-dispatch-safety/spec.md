# 221 · 草图关系创建不确定执行防重放

Created: 2026-10-08。Scope: EC00的最小离线修复切片；不是整个EC00获批或完成。用户最新允许主代理推进实质工作，机械核对才委派；本次不执行COM、部署或提交。保持master，不为脏工作树自动切分支。

## 用户故事与验收场景

US1/P1：关系创建可能已生效后报错、回读失败或返回无效果时，不再换实参形态、IAddRelation或兜底重复修改。离线假宿主可验证修改次数、批次停止和旧返回字段。
US2/P1：选区不足、前态计数不可读、草图非欠定义时在修改前拒绝；verify=False不绕状态门。
US3/P2：已有管理器不可用时只在调用前选择既有SketchAddConstraints路线，一条关系最多一次修改调用；成功路径保持ok/applied/total/results。

| 需求 | 来源（license） | 可测判据 |
|---|---|---|
| FR-001 | 本项目既有模式：scripts/sw_sketch_relations.py多轮/多形态重试；scripts/sw_connect.py:get_com_member_raw；license=MIT | 异常后计数改变/不变/不可读均不重放；后续关系not_started |
| FR-002 | 官方资料C:/swapi/types/ISketchRelationManager/AddRelation.md签名/Remarks；本项目specs/081-add-relation-safearray/spec.md及scripts/sketch_relations.py:_dispatch_array，license=MIT；官方资料仅参考 | 使用已有SAFEARRAY包装，不把IAddRelation当同签名替代品 |
| FR-003 | 本项目既有工具的状态/Select4/前后关系计数纪律，license=MIT；官方GetRelationsCount页仅参考 | 非欠定义、选择不足、前读数unknown不调用修改成员 |
| FR-004 | EC00现有uncertain/unknown设计与旧字典返回模式，license=MIT | 新增execution_state；异常/后读数不可得时ok=False且停止批次，保持旧字段 |

边界：计数增加只是计数证据，不证明关系类型/对象/几何/自由度/持久性。既有数值关系映射与官方枚举存在冲突，本次不默默改公共枚举，登记待核，不启用生产路径或认证COM成功。调用前选择兜底不等于证明兜底几何正确。

成功标准：离线12例全部通过；旧源码至少9例失败证明用例可抓原缺陷；源码无sleep/多payload创建重放；无依赖安装或实际COM调用。
