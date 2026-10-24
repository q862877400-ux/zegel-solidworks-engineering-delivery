# EC00 Tasks 草案——按证据拆开的施工任务

- 日期：2026-10-08；状态：DRAFT／全部施工任务未执行。
- [Spec](ENGINEERING_P0_SPEC_DRAFT.md)｜[Plan](ENGINEERING_P0_PLAN_DRAFT.md)｜[Contracts](ENGINEERING_P0_CONTRACTS_DRAFT.md)｜[Acceptance](ENGINEERING_P0_ACCEPTANCE_DRAFT.md)
- 工作包EC00不是正式特性编号。批准后按本仓tasks-template落入正式目录。
- `[ ]`表示未完成；阻塞另列。不得因本清单写完将任何实现、测试或真机任务勾完成。
- 表中的文件名为责任落点或正式施工待确定的新测试名，不宣称新文件已存在。
- 每项任务带字面 `→ 验收:` 行（宪法 §V 要求每项有可跑验法），标签与命令索引见 §10。当前状态：**32 个验收入口已登记，现有／拟新增／真机未授权三类命令分开列出，全部未执行，正式验收未通过**；登记入口不等于判据可跑，更不等于已通过。

## 1. 任务纪律

每个任务要有依赖、产物、验法和完成判据。只有全部产物与规定证据齐全才勾选。

- 文档、离线测试、真机验证分任务；不以一个大勾掩盖环境阻塞。
- `[P]`仅代表可并行的纯离线工作，前置输入必须冻结，写入面必须独立。
- 对公共schema、ToolSpec注册、执行包装和capabilities实行单责任人合并。
- 真机任务全部串行；使用自有测试工件和既有护栏，从公开契约调用。
- 当前清单未估工时；正式施工记录实际工时与返工，不用拍脑袋日历承诺。

## 2. 阶段A——立项、基线与需求冻结

- [ ] T001 [SETUP] 确认本仓分支/编号/游标/工作树及本轮写入范围。依赖：无。产物：正式`baseline.md`的权属记录。验法：明确哪些旧改动属于他人，创建流程会改什么；未明确不创建特性。支持FR-015。 → 验收:【已有且路径已核】`C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -c "import json,pathlib;d=json.loads(pathlib.Path(r'D:/AI/SW/output/ENGINEERING_PARALLEL_ROSTER.json').read_text(encoding='utf-8'));b=d['baseline'];print(b['head'],b['branch'],b['original_changes_to_preserve']);assert len(b['head'])==40 and b['branch']=='master' and d['business_build_authorized'] is False"`（只核字段存在与授权位，不证明权属）。【人工门】dirty 基线、`sw_part.py` 已修改与 `sw_sketch_relations.py` 未跟踪的权属及他人改动边界必须人工确认并留责任人；机器校验不得代替权属结论。
- [ ] T002 [SETUP] 按本仓流程创建一个正式特性，将六份草案整理为spec/plan/tasks及配套文件，不复制zcode脚手架。依赖：T001和用户批准。产物：正式目录及编号映射。验法：不覆盖旧规格；引用均指向正确正式目录。 → 验收:【已有且路径已核，拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_spec_acceptance_paths_gate.py::test_current_tree_passes" -q`（核 spec 验收路径可解析；函数名已核，pytest 依赖未探明，本轮未执行、环境未核）。【拟新增，文件不存在，当前不可执行，实施后拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_ec00_spec_pointer_anchor.py" -q`（本轮不存在／未运行；文件缺失时结论为 blocked。正式编号与目录确定后必须重新锚定，本轮路径为准备文件 `output/ENGINEERING_P0_*_DRAFT.md`）。【人工门】编号与 `.specify/feature.json` 游标冲突、旧规格未被覆盖需人工核对；创建流程会改哪些文件须书面列出。
- [ ] T003 [US6] 建旧任务→新任务迁移表，重点关联210效应、212单位及草图关系/关窗欠账。依赖：T001。产物：baseline中的历史状态/证据/责任。验法：每项写明复用、补验或延期，不能自动勾旧任务。FR-001/015。 → 验收:【拟新增，文件不存在，当前不可执行，实施后拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_ec00_legacy_migration_mapping.py" -q`（覆盖旧项→新任务、210效应、212单位、关系/关窗欠账映射；本轮该文件不存在、未运行，文件缺失时结论为 blocked，不得当成已执行）。【人工门】旧任务与台账权属不得按 git 作者自动认领；旧状态不得被新任务自动清空；未知归属保持 unknown。
- [ ] T004 [US1/US6] 冻结代表工具集和公开ToolSpec名称，静态盘点注入/参数/单位/风险/效果/来源/等级/测试。依赖：T003。产物：范围表。验法：范围100%有字段，未知具名；静态盘点不连接COM。FR-001/002，SC-001。 → 验收:【已有且路径已核，拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_tool_registry.py" -k "rule1 or rule3 or missing_body or duplicate_param or declaring_response_format" -q`、`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_registry_wiring.py::test_every_inject_name_has_a_resolver" -q`、`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_inject_binding_gate.py::test_current_repo_passes" -q`（ToolSpec 字段/命名/注入解析器的静态判据；函数名已核，本轮未执行、依赖未探明）。【人工门】范围100%有字段与"未知具名"需人工签署；静态盘点不连接 COM，不等于真机验证。
- [ ] T005 [US1～US6] 冻结D-001～D-005的阶段性决定及非目标，完成G1。依赖：T002/T004。产物：spec澄清与requirements checklist。验法：代表工具/旧默认/关键阻塞明确；runtime环境可仍未就绪但不能被写成通过。 → 验收:【已有且路径已核，仅结构检查】V1＋V2（§10.2：只校验 T001～T032 保持未勾与 FR→任务映射15行存在，**不证明本任务完成**）。【人工门】D-001～D-005 冻结与 G1 通过、每条 FR 来源具名需人工评审；runtime 环境未就绪只能写 not_run/unknown，不得写成通过。本文档只登记验收入口与命令形式，不保证判据可跑性，也不宣称宪法判据已满足。

## 3. 阶段B——限定研究与契约冻结

- [ ] T006 [US2] 对关系调用和回读核对官方签名、Remarks、Example、冲突索引与对应limitations；必要时设计限定探针但不先运行。依赖：T004。产物：research官方依据和待验证包装。验法：来源可定位，未知不编造API签名。FR-004/005。 → 验收:【已有且路径已核，拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_signature_audit_freshness_gate.py::test_current_table_is_fresh" -q`（核签名审计表新鲜度；函数名已核，本轮未执行）。【拟新增，文件不存在，当前不可执行，实施后拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_ec00_sketch_relation_official_source.py" -q`（本轮不存在／未运行；文件缺失时结论为 blocked）。【人工门】官方签名/Remarks/Example 与冲突索引来源必须可定位（如 `C:/swapi/types/...`）；不可读则记 unknown，禁止凭印象或编造 API 签名。
- [ ] T007 [US3/US4] 明确上下文/内存指纹/保存指纹/配置/互斥/护栏边界以及round_chain副作用。依赖：T004。产物：research与能力边界。验法：不把文件哈希当内存版本，不把既有脚本当纯只读。FR-006/010/012。 → 验收:【静态已核】`tools/round_chain.ps1` 第84/117/150行含 `git add -A`、第199行含 `reclaim_solidworks.py --close`，已由本轮 Read 核实 ⇒ 收尾链不是纯只读脚本。【已有且路径已核，拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_domain_evidence_status.py" -q`（人工复核门与环境失败阻断；函数名已核，本轮未执行）。【拟新增，文件不存在，当前不可执行，实施后拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_ec00_round_chain_side_effect_inventory.py" -q`（本轮不存在／未运行；文件缺失时结论为 blocked）。【人工门】内存/保存状态区分、可靠版本检测降级边界需人工确认。
- [ ] T008 [US1] 冻结Quantity、公开/规范化/COM单位、旧默认与重复转换防护契约。依赖：T005。产物：contracts/data-model单位定义和迁移表。验法：每个字段有量纲、允许域、默认依据和拒绝语义。FR-002/003/014。 → 验收:【已有且路径已核，拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_document_unit_scale.py" "D:/AI/SW/tests/test_rule2_length_suffix_is_enforced.py" "D:/AI/SW/tests/test_rule3_bare_coord_boundary.py" "D:/AI/SW/tests/test_linear_pattern_units.py" -q`（量纲、长度/角度后缀、裸坐标、无二次换算；函数名已核，本轮未执行）。【拟新增，文件不存在，当前不可执行，实施后拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_ec00_quantity_contract.py" -q`（本轮不存在／未运行；文件缺失时结论为 blocked）。【人工门】公开/规范化/COM 单位、旧默认依据与重复转换防护的拒绝语义需人工签署。
- [ ] T009 [US2/US5] 冻结EffectObservation、ExecutionOutcome、EvidenceManifest及容差来源。依赖：T006/T007/T008。产物：contracts/data-model。验法：API返回与effect/执行/等级分开；未知/过期不可放行。FR-008/011/013。 → 验收:【已有且路径已核，拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_verified_evidence_gate.py::test_real_tree_is_clean" -q`、`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_job_evidence_fields.py" -q`（证据字段门；函数名已核，本轮未执行）。【拟新增，文件不存在，当前不可执行，实施后拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_ec00_effect_observation_contract.py" -q`（本轮不存在／未运行；文件缺失时结论为 blocked）。【人工门】容差来源必须是外部参考值，不得取自被测实现；unknown/过期不得放行。
- [ ] T010 [US3/US4] 冻结文档/配置/版本/引用及uncertain恢复策略；定义EC04衔接字段而不重建租约系统。依赖：T007/T009。产物：状态机和错误/恢复契约。验法：超时不能直接重试；无可靠版本检测明确降级。FR-006/007/009/010。 → 验收:【已有且路径已核，拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_sw_guard_dialog_tiers.py" "D:/AI/SW/tests/test_modal_dialogs_single_source.py" -q`（护栏分级与单点委托；函数名已核，本轮未执行）。【拟新增，文件不存在，当前不可执行，实施后拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_ec00_uncertain_recovery_policy.py" -q`（本轮不存在／未运行；文件缺失时结论为 blocked）。【人工门】超时不得直接重放、无可靠版本检测须明确降级、EC04 衔接字段边界需人工签署；uncertain/busy 不得被当作成功重试依据。
- [ ] T011 [FOUNDATION] 完成Constitution Check及spec/plan/tasks/contracts一致性分析，过G2/G3。依赖：T005/T008/T009/T010。产物：检查记录、FR→任务→测试→证据矩阵。验法：无未解释冲突，无关键需求孤岛，无环依赖；关键实现依赖待决定则阻塞。 → 验收:【已有且路径已核，仅结构/图一致性检查】V1＋V2＋V3（§10.2：任务未勾、FR映射15行、依赖图无环；**不能证明 G2/G3 通过**）。【已有且路径已核，拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_spec_acceptance_paths_gate.py::test_current_tree_passes" -q`（本轮未执行）。【人工门】Constitution Check §I–§V、责任归属、批准与来源许可不可机器核验，需逐条人工审核；关键实现依赖待决定则阻塞，不得用结构完整冒充一致性通过。

## 4. 阶段C——先建离线负例和参考值

- [ ] T012 [P] [US1] 建单位等价/量纲错误/NaN无穷/域边界/重复转换/旧入口对照测试。依赖：T011。落点：`tests/`独立单位测试与参考数据。完成判据：测试能捕获旧错误；非法输入修改调用计数为0。FR-002/003/014，SC-002/007。 → 验收:【拟新增，文件不存在，当前不可执行，实施后拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_ec00_unit_boundary_negative.py" -q`（覆盖单位等价、错误量纲、NaN/无穷、域边界、重复转换、旧入口对照；本轮不存在／未运行，文件缺失时结论为 blocked）。【已有且路径已核，拟执行，仅作对照不作本任务判据】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_document_unit_scale.py::test_negative_case_falls_back_to_1000" "D:/AI/SW/tests/test_rule3_bare_coord_boundary.py::test_bare_coordinates_are_still_flagged" -q`（本轮未执行）。【判据】非法输入必须使修改调用计数为0，需调用桩计数证据；不允许用测试文件存在性检查或关键词 grep 冒充本判据。
- [ ] T013 [P] [US2/US5] 建返回true但无效果、关系未持久、回读错误/不可用、旧证据错版本负例。依赖：T011。落点：`tests/`独立效果测试。完成判据：故障样例均不能effect pass，参考值不取自被测实现。FR-004/008/011/013，SC-003。 → 验收:【拟新增，文件不存在，当前不可执行，实施后拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_ec00_effect_false_success_negative.py" -q`（覆盖true无效果、关系未持久、回读缺失/不可用、旧证据错版本；本轮该文件不存在、未运行，文件缺失时结论为 blocked）。【人工门】参考值不得取自被测实现；故障样例均须 fail 或 unknown，不得 effect pass。
- [ ] T014 [P] [US3] 建错文档/配置/版本、持久引用失效/歧义、未保存文档身份冲突测试。依赖：T011。落点：`tests/`上下文/引用测试。完成判据：错误对象在修改前被拒绝；0或多候选不返回成功。FR-006/007，SC-006。 → 验收:【已有且路径已核，拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_sw_entity_reference.py::test_semantic_reference_reports_ambiguity" "D:/AI/SW/tests/test_sw_entity_reference.py::test_semantic_reference_resolves_without_face_number" -q`（歧义报告与无面号解析；函数名已核，本轮未执行）。【拟新增，文件不存在，当前不可执行，实施后拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_ec00_context_reference_negative.py" -q`（覆盖错文档/配置/版本、未保存文档身份冲突、0或多候选；本轮不存在／未运行，文件缺失时结论为 blocked）。
- [ ] T015 [P] [US4/US5] 建非幂等超时、部分执行、竞争、护栏分级、脱敏及自有写入范围测试。依赖：T011。落点：`tests/`执行状态与证据测试。完成判据：uncertain无判断不重放；危险弹窗不自动确认；不输出凭据。FR-009/010/015，SC-005。 → 验收:【已有且路径已核，拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_sw_guard_dialog_tiers.py::test_needs_llm_or_forbidden_never_auto_dismiss" "D:/AI/SW/tests/test_sw_guard_dialog_tiers.py::test_destructive_text_is_forbidden_even_with_single_ok" "D:/AI/SW/tests/test_domain_evidence_status.py::test_domain_evidence_requires_manual_review" -q`（危险弹窗不自动确认、人工复核门；函数名已核，本轮未执行）。【拟新增，文件不存在，当前不可执行，实施后拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_ec00_nonidempotent_uncertain_negative.py" "D:/AI/SW/tests/test_ec00_secret_redaction.py" -q`（本轮不存在／未运行；文件缺失时结论为 blocked）。

## 5. 阶段D——实施边界与公开路由

- [ ] T016 [US1] 实现唯一单位规范化入口及旧契约适配，接入纳入范围的调用边界。依赖：T012。落点：现有单位/`sw_part.py`/ToolSpec边界。完成判据：单位对照全通过，原始与规范化类型隔离，无重复转换。FR-002/003。 → 验收:【已有且路径已核，拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_document_unit_scale.py::test_no_hardcoded_thousand_in_module" "D:/AI/SW/tests/test_linear_pattern_units.py::test_two_paths_agree_on_units" "D:/AI/SW/tests/test_linear_pattern_units.py::test_no_raw_mm_passthrough_left" -q`（无硬编码1000、双路径单位一致、无裸 mm 透传；函数名已核，本轮未执行）。【拟新增，文件不存在，当前不可执行，实施后拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_ec00_unit_normalization_entry.py" -q`（本轮不存在／未运行；文件缺失时结论为 blocked）。【人工门】原始与规范化类型隔离、旧契约适配范围需人工评审。
- [ ] T017 [US2] 完成草图关系正式注册、参数注入/包装和类型/数量/上下文预检。依赖：T006/T011。落点：`sw_sketch_relations.py`及实际注册位置。完成判据：公开ToolSpec调用通过离线桩，错误实体/关系在COM前拒绝；不声称包装已真机验证。FR-004/005。 → 验收:【已有且路径已核，拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_sw_sketch_primitives_contract.py" "D:/AI/SW/tests/test_registry_wiring.py::test_every_declared_spec_actually_reaches_all_specs" "D:/AI/SW/tests/test_param_binding_inject_key.py" "D:/AI/SW/tests/test_inject_binding_gate.py" -q`（注意 `test_sw_sketch_primitives_contract.py` 是**草图图元**参数/命名对照，不是"草图关系已注册或关系生效"的证据；注入键与到达 all_specs 才对应注册/接线判据。函数名已核，本轮未执行、依赖未探明）。【拟新增，文件不存在，当前不可执行，实施后拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_ec00_sketch_relation_precheck.py" -q`（本轮不存在／未运行；文件缺失时结论为 blocked）。【人工门】不得声称包装已真机验证；错误实体/关系在 COM 前拒绝须有调用计数证据。
- [ ] T018 [US2/US5] 实现关系/几何效果回读与pass/fail/unknown映射，禁止return true直通。依赖：T013/T017。落点：既有效应与回读模块。完成判据：假成功及不可回读负例成立；容差未定的义务不得pass。FR-004/008。 → 验收:【拟新增，文件不存在，当前不可执行，实施后拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_ec00_effect_readback_mapping.py" -q`（覆盖 pass/fail/unknown 映射与不可回读负例；本轮该文件不存在、未运行，文件缺失时结论为 blocked）。【人工门】代码评审确认无 `return true` 直通；容差未定义的义务不得 pass。【阻塞】真机未测，真机回读结论本轮不产出，不得用离线桩升级为 COM 验证。
- [ ] T019 [US3] 接上下文核验与引用语义/几何复核，区分内存/保存状态。依赖：T014。落点：选择规范、文档指纹及调用包装。完成判据：错文档/配置/引用歧义拒绝；无可靠版本保证返回明确降级。FR-006/007。 → 验收:【已有且路径已核，拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_sw_entity_reference.py" -q`（稳定签名/无面号解析/歧义报告；函数名已核，本轮未执行）。【拟新增，文件不存在，当前不可执行，实施后拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_ec00_context_fingerprint_negative.py" -q`（覆盖内存/保存状态区分、错文档/配置拒绝；本轮不存在／未运行，文件缺失时结论为 blocked）。
- [ ] T020 [US4] 接入现有互斥/护栏和uncertain恢复，限制非幂等重试。依赖：T015/T018/T019。落点：调用包装、`tool_caller.py`、`sw_guard.py`的必要扩展。完成判据：公开入口不能绕过；超时无效果判断不重放。FR-009/010。 → 验收:【已有且路径已核，拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_modal_dialogs_single_source.py::test_every_modal_dialogs_delegates_to_the_shared_impl" "D:/AI/SW/tests/test_sw_guard_dialog_tiers.py" -q`（护栏单点委托、不自动确认；函数名已核，本轮未执行）。【拟新增，文件不存在，当前不可执行，实施后拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_ec00_guardrail_bypass_negative.py" -q`（覆盖公开入口绕行与超时无判断不重放；本轮不存在／未运行，文件缺失时结论为 blocked）。
- [ ] T021 [US5] 实现证据字段、错误脱敏、版本失效与等级记录；必要时扩展现有schema。依赖：T009/T018/T019/T020。落点：既有证据模块/单一权威schema。完成判据：unknown、not_run和expired不变成通过；hash未实填不生成真实证据。FR-011/013/015。 → 验收:【已有且路径已核，拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_verified_level_has_runtime_evidence.py::test_every_verified_has_a_runtime_evidence" "D:/AI/SW/tests/test_verified_level_has_runtime_evidence.py::test_pytest_only_evidence_is_flagged_in_text" "D:/AI/SW/tests/test_verified_evidence_gate.py::test_catches_verified_without_evidence" "D:/AI/SW/tests/test_job_evidence_fields.py" -q`（等级与证据字段门；函数名已核，本轮未执行）。【拟新增，文件不存在，当前不可执行，实施后拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_ec00_evidence_manifest_versioning.py" -q`（本轮不存在／未运行；文件缺失时结论为 blocked）。【人工门】hash 未实填不得生成真实证据；unknown/not_run/expired 不得变通过；schema 变更必须是单一权威 schema 的单点修改。
- [ ] T022 [US6] 完成旧入口迁移与双路径回归，更新弃用说明。依赖：T016/T017/T020/T021。落点：公开工具适配层。完成判据：旧调用保持已登记语义或明确拒绝，无单位静默漂移，不绕硬门禁。FR-014。 → 验收:【已有且路径已核，拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_deprecated_entry_interlock.py::test_no_new_calls_to_deprecated_entries" "D:/AI/SW/tests/test_deprecated_entry_interlock.py::test_interlock_fires_on_deprecated_and_passes_on_successor" "D:/AI/SW/tests/test_deprecated_entry_interlock.py::test_target_table_entries_all_have_successors" -q`（函数名已核，本轮未执行）。【拟新增，文件不存在，当前不可执行，实施后拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_ec00_legacy_entry_hard_gate.py" -q`（本轮不存在／未运行；文件缺失时结论为 blocked）。【分层声明，不得误读】互锁只覆盖弃用登记表内入口；新工程路径硬门禁与未迁移旧入口必须分层，未迁移旧入口本轮不在"已改好"范围，须明确拒绝或保持已登记语义，不得写入"所有旧入口已迁移"。
- [ ] T023 [FOUNDATION] 运行公开路由集成桩和聚焦测试，完成离线验收。依赖：T016～T022。产物：测试记录及FR/SC映射。完成判据：按真实ToolSpec注入/参数调用；所有规定离线正负例通过；runtime仍可not_run。 → 验收:【已有且路径已核，拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_registry_wiring.py" -q`（批次/声明/到达 all_specs/注入解析器/无幽灵批次；函数名已核，本轮未执行）。【拟新增，文件不存在，当前不可执行，实施后拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_ec00_public_route_integration.py" -q`（按真实 ToolSpec 注入与参数调用；本轮不存在／未运行，文件缺失时结论为 blocked）。【判据】所有规定离线正负例通过，runtime 仍记 not_run；离线集成桩不得升级为真机验证。

## 6. 阶段E——受控真机验证，全部串行

- [ ] T024 [RUNTIME SETUP] 确认SW/COM/MCP环境、许可、插件、版本、护栏、单会话责任人、自有样例和允许操作。依赖：T023和执行授权。产物：environment/写入清单。完成判据：不靠猜测就绪；无用户文档被纳入关闭/重启；环境不满足则阻塞T025～T028。 → 验收:【真机另授权，本轮不执行任何命令】不运行 pytest、不运行 COM、不运行 `tools/round_chain.ps1`。未来拟新增（文件不存在，真机授权前不可执行，结论 blocked）：`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_ec00_runtime_environment.py" -q`。只做人工登记与证据收集要求：SW/COM/MCP 版本与许可、插件、护栏、单会话责任人、自有样例根目录、允许操作清单、busy/占用状态。【人工门】环境就绪必须实测确认，不得用文档就绪或准备完成冒充；任一条件不满足则 T025～T028 全部保留 blocked/not_run。
- [ ] T025 [US1/US2] 从正式工具路径验证尺寸/角度和关系正负例，记录实际传参/回读及未知。依赖：T024。产物：工具证据及工件。完成判据：正确单位与合法关系可验证，true无效果不可通过；不稳定情形保留失败或unknown。FR-003/004/005/008，SC-004。 → 验收:【真机另授权，本轮不执行】未来拟新增（文件不存在，真机授权前不可执行，结论 blocked）：`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_ec00_runtime_units_relations.py" -q`。待授权后按正式目录锚定真机用例；正式编号未定前引用准备文件 `output/ENGINEERING_P0_ACCEPTANCE_DRAFT.md` §5.2。要求记录实际传参、单位、回读值与 unknown 清单；正确单位与合法关系可验证，true 无效果不可通过；不稳定情形保留 fail 或 unknown。【阻塞】真机未测，本轮不产出真机证据。
- [ ] T026 [US3/US5] 验证重建、配置切换、保存重开、对象引用和尺寸/关系持久效果。依赖：T025。产物：自有工件前后版本与回读。完成判据：指定模型/配置没有串文档；重开效果与义务一致。FR-006/007/012，SC-006。 → 验收:【真机另授权，本轮不执行】未来拟新增（文件不存在，真机授权前不可执行，结论 blocked）：`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_ec00_runtime_persistence.py" -q`。要求自有工件前后版本与机器可读回读：重建、配置切换、保存重开、对象引用、尺寸/关系持久效果；指定模型/配置不得串文档。【人工门】重开效果与义务一致需人工比对；截图只作辅助，不能代替回读。
- [ ] T027 [US4] 安全验证单会话竞争及受控超时/弹窗恢复路径。依赖：T026。产物：竞争/恢复记录。完成判据：最多一个修改者；不故意破坏用户会话，不盲重试/危险确认；无安全复现条件则保留阻塞，不造证据。FR-009/010，SC-005。 → 验收:【真机另授权，本轮不执行】未来拟新增（文件不存在，真机授权前不可执行，结论 blocked）：`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_ec00_runtime_recovery.py" -q`。要求安全可复现的竞争/恢复样例与单会话互斥记录；禁止盲重试、禁止自动确认危险弹窗、禁止关闭不属于本轮的用户文档/会话。【人工门】无安全复现条件则保留 blocked，不造证据；资源所有权须人工确认。
- [ ] T028 [US6] 在冻结迁移样例上验证新旧公开入口、错误和证据语义。依赖：T027。产物：兼容验证记录。完成判据：原单位语义和硬门禁一致；明确不支持路径。FR-014，SC-007。 → 验收:【真机另授权，本轮不执行】未来拟新增（文件不存在，真机授权前不可执行，结论 blocked）：`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_ec00_runtime_legacy.py" -q`。在冻结迁移样例上做新旧公开入口、错误与证据语义对照，明确不支持或不稳定路径。【人工门】原单位语义与硬门禁一致需人工确认；不稳定路径保留限制说明，不解释为通过。

## 7. 阶段F——收口与交接

- [ ] T029 [FOUNDATION] 先将收尾链的生成/验证与全量暂存/关闭SW等副作用拆开；增加显式文件白名单和自有工件校验，再做聚焦测试、适用生成器/门禁及来源检查。依赖：T007/T023；若要runtime收口还依赖T028。产物：受控收尾入口、负例与机器门禁记录。完成判据：验证阶段不暂存他人改动、不关闭用户文档；危险阶段需独立授权；失败未解决不勾；全量仅按本仓规定；离线与runtime结论分开。 → 验收:【静态已核】`tools/round_chain.ps1` 第84/117/150行 `git add -A`、第199行 `reclaim_solidworks.py --close` 已由 Read 核实 ⇒ 禁止把整条收尾链当纯只读验证命令直接跑；第一动作是副作用拆分，不是执行链。【已有且路径已核，拟执行，且不跑整链】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_release_check.py::test_release_check_passes_current_tree" -q`（单条聚焦门禁测试；函数名已核，本轮未执行）。【拟新增，文件不存在，当前不可执行，实施后拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_ec00_round_chain_side_effect_split.py" "D:/AI/SW/tests/test_ec00_closeout_whitelist.py" -q`（核生成/验证与全量暂存/关闭SW拆分、显式文件白名单与自有工件校验；本轮不存在／未运行，文件缺失时结论为 blocked）。【人工门】危险阶段独立授权；他人改动不得被暂存；失败未解决不勾；全量仅按本仓规定。
- [ ] T030 [US5/US6] 完成acceptance证据矩阵、旧台账/能力状态的权属内更新与负面事实清单。依赖：T029。产物：正式acceptance、迁移/limitations。完成判据：每个完成任务有证据，未运行真机不升级等级；范围外旧欠账仍保留。FR-001/011/013/015，SC-001/008。 → 验收:【已有且路径已核，仅结构检查】V4（§10.2：只校验验收矩阵15条 FR 的结论列不出现 pass/通过字样，**不证明证据矩阵完成**）。【已有且路径已核，拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_verified_evidence_gate.py::test_real_tree_is_clean" "D:/AI/SW/tests/test_verified_level_has_runtime_evidence.py::test_pytest_only_evidence_is_flagged_in_text" -q`（本轮未执行）。【拟新增，文件不存在，当前不可执行，实施后拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_ec00_acceptance_matrix_completeness.py" -q`（本轮不存在／未运行；文件缺失时结论为 blocked）。【人工门】旧台账/能力状态更新须在权属内；未运行真机不升级等级；范围外旧欠账保留。
- [ ] T031 [DOCS] 完成quickstart与交接：实际可用入口、环境/权限、失败恢复、未解决项、下一轮动作。依赖：T030。产物：quickstart/交接。完成判据：没有伪造命令或就绪声明；指明EC01/EC04接口和边界。 → 验收:【拟新增，文件不存在，当前不可执行，实施后拟执行】`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/test_ec00_quickstart_entry_paths.py" -q`（核 quickstart 中入口路径真实存在、无伪造命令；本轮该文件不存在、未运行，文件缺失时结论为 blocked）。【人工门】环境/权限、失败恢复、未解决项与下一轮动作需人工核对；须指明 EC01/EC04 接口与边界，不得写就绪声明。
- [ ] T032 [CLOSEOUT] 做跨文档converge与G5评审；提交/发布另行授权。依赖：T030/T031。产物：结论和批准/阻塞记录。完成判据：需求/契约/任务/证据一致；他人改动未暂存；缺runtime证据只交离线阶段成果，不写整个EC00完成。 → 验收:【已有且路径已核，仅结构检查】V1＋V2＋V3（§10.2；不证明收口或 converge 通过）。【人工门，不可脚本代替】跨文档 converge 与 G5 评审、他人改动未暂存（人工核对 `git status --porcelain`，本轮不执行也不暂存）、缺 runtime 证据只交离线阶段成果、提交/发布另行授权。

## 8. 依赖与并行摘要

```text
T001 → T002
T001 → T003 → T004 → T005
T004 → T006/T007
T005 → T008
T006/T007/T008 → T009 → T010
T005/T008/T009/T010 → T011
T011 → T012/T013/T014/T015（独立离线可并行）
T012 → T016
T006/T011 → T017；T013/T017 → T018
T014 → T019；T015/T018/T019 → T020
T009/T018/T019/T020 → T021
T016/T017/T020/T021 → T022
T016～T022 → T023 → T024 → T025 → T026 → T027 → T028
T023（runtime收口还需T028）→ T029 → T030 → T031 → T032
```

T011前需要的文档分析与T032收口分析不是重复门禁：前者防止带冲突施工，后者检查实际实现、证据和变更是否偏离。

## 9. 需求到任务映射

| FR | 主任务 |
|---|---|
| FR-001 | T003/T004/T030 |
| FR-002 | T004/T008/T012/T016 |
| FR-003 | T008/T012/T016/T025 |
| FR-004 | T006/T013/T017/T018/T025 |
| FR-005 | T006/T017/T025 |
| FR-006 | T007/T010/T014/T019/T026 |
| FR-007 | T010/T014/T019/T026 |
| FR-008 | T009/T013/T018/T025 |
| FR-009 | T010/T015/T020/T027 |
| FR-010 | T007/T010/T015/T020/T027 |
| FR-011 | T009/T013/T021/T030 |
| FR-012 | T007/T026 |
| FR-013 | T009/T013/T021/T030 |
| FR-014 | T008/T012/T022/T028 |
| FR-015 | T001/T003/T015/T021/T030 |

## 10. 验收命令索引与静态校验

### 10.1 标签含义与纪律

- 【已有且路径已核】：测试文件与函数名已由本轮 Read/Grep 核实存在（见 §10.3）；但 pytest 命令一律写作"拟执行"，依赖未探明、运行环境未核，本轮未运行。
- 【拟新增，文件不存在，当前不可执行，实施后拟执行】：`tests/test_ec00_*.py` 本轮不存在、未运行；命令形式照写以便实施后直接执行，**文件缺失时结论为 blocked，不得当成已执行或通过**。
- 【已有且路径已核，拟执行】：命令指向现有测试，但本轮不执行；执行前须先探明依赖与环境。
- 【真机另授权】：T024～T028 及 `test_ec00_runtime_*.py` 本轮不执行任何命令；真机授权前结论为 blocked，只设计实际调用与证据验证要求。
- 【人工门】：责任归属、批准、dirty 权属、来源许可、COM/真机证据、危险授权不可由脚本核验。
- 命令形式：所有 pytest 一律用受管绝对路径与绝对路径参数——`"C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe" -B -m pytest -p no:cacheprovider "D:/AI/SW/tests/<file>.py[::test_x]" -q`；不写裸 `pytest`。
- 文档里写出命令形式、参数标志（flags）或测试名**不构成任何证据**；证据只能来自实际执行记录与回读/工件。禁止用测试文件存在性检查或关键词 grep 冒充业务验收判据。
- 基线 HEAD/分支/哈希位置：`output/ENGINEERING_PARALLEL_ROSTER.json` 的 `baseline` 块（`head`、`branch`、`file_sha256`）。正式编号未定，本文命令一律指向准备文件实际路径；迁移到正式目录时必须重新锚定。

### 10.2 静态校验脚本 V1～V4（受管 python，标准库只读）

V1 — T001～T032 全部存在且保持未勾：

```bash
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -c "import pathlib; t=pathlib.Path(r'D:/AI/SW/output/ENGINEERING_P0_TASKS_DRAFT.md').read_text(encoding='utf-8'); ids=[f'T{i:03d}' for i in range(1,33)]; miss=[i for i in ids if f'- [ ] {i}' not in t]; assert not miss, miss; print('T001..T032 全部存在且未勾', len(ids))"
```

V2 — FR→任务映射 15 行且每行有任务：

```bash
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -c "import pathlib,re; t=pathlib.Path(r'D:/AI/SW/output/ENGINEERING_P0_TASKS_DRAFT.md').read_text(encoding='utf-8'); rows=re.findall(r'^\| (FR-\d{3}) \| ([^|]+) \|$', t, re.M); assert len(rows)==15, len(rows); assert all(v.strip() for k,v in rows); print('FR 映射行数', len(rows))"
```

V3 — 逐任务"依赖："字段解析（展开 `T016～T022` 区间与 `T006/T007` 列表）后做无环检查。§8 的简写箭头图只作阅读辅助：它省略了区间内的中间任务与部分依赖，本校验**不读该简图、不称"32 节点"来自简图**；正式 DAG 以 32 条任务行的"依赖："字段为准，未逐条人工复核前不得宣称依赖无环已确认。

```bash
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -c "
import pathlib, re
from collections import defaultdict
t = pathlib.Path(r'D:/AI/SW/output/ENGINEERING_P0_TASKS_DRAFT.md').read_text(encoding='utf-8')
g = defaultdict(set); nodes = set(); deps = {}
for m in re.finditer(r'^- \[ \] (T\d{3}) .*?依赖：([^。]+)。', t, re.M):
    tid, dep = m.group(1), m.group(2)
    nodes.add(tid); deps[tid] = dep.strip()
    for tok in re.finditer(r'T(\d{3})(?:～T(\d{3}))?', dep):
        ids = [f'T{i:03d}' for i in range(int(tok.group(1)), int(tok.group(2) or tok.group(1)) + 1)]
        for d in ids:
            g[d].add(tid); nodes.add(d)
assert len(nodes) == 32, sorted(nodes)
indeg = {n: 0 for n in nodes}
for s, ds in g.items():
    for d in ds: indeg[d] += 1
q = [n for n in nodes if indeg[n] == 0]; seen = 0
while q:
    n = q.pop(); seen += 1
    for d in g.get(n, ()):
        indeg[d] -= 1
        if indeg[d] == 0: q.append(d)
assert seen == len(nodes), sorted(n for n in nodes if indeg[n] > 0)
print('依赖字段解析: 节点', len(nodes), '边', sum(len(v) for v in g.values()), '无环')
"
```

V4 — acceptance 矩阵 15 条 FR 的当前结论列不得出现 pass/通过：

```bash
C:/Users/Zegel/.workbuddy-ai/binaries/python/versions/3.13.12/python.exe -c "import pathlib,re; t=pathlib.Path(r'D:/AI/SW/output/ENGINEERING_P0_ACCEPTANCE_DRAFT.md').read_text(encoding='utf-8'); rows=re.findall(r'^\| (FR-\d{3}) [^|]*\|[^|]*\|[^|]*\|[^|]*\|\s*([^|]+?)\s*\|', t, re.M); assert len(rows)==15, len(rows); bad=[k for k,v in rows if v.strip() not in ('not_run','blocked/not_run')]; assert not bad, bad; print('15 条 FR 当前结论均为 not_run/blocked')"
```

### 10.3 已核实存在的聚焦测试（函数名已核，pytest 拟执行）

| 文件 | 已核函数名 | 支持的判据 |
|---|---|---|
| tests/test_tool_registry.py | test_rule1_bad_names_rejected／test_rule3_bare_coordinates_rejected／test_missing_body_rejected／test_duplicate_param_rejected／test_declaring_response_format_rejected | ToolSpec 字段、命名与单位规则 |
| tests/test_registry_wiring.py | test_every_declared_spec_actually_reaches_all_specs／test_every_inject_name_has_a_resolver／test_no_ghost_batches_declared | 公开路由、注入解析器、批次接线 |
| tests/test_inject_binding_gate.py | test_current_repo_passes／test_negative_missing_inject_is_caught | 注入绑定门禁 |
| tests/test_param_binding_inject_key.py | test_gate_catches_undeclared_required_param／test_gate_catches_inject_key_mismatch | 参数与 inject 键 |
| tests/test_document_unit_scale.py | test_mm_document_scale_is_one／test_meter_document_scale_is_1000／test_no_hardcoded_thousand_in_module／test_negative_case_falls_back_to_1000 | 量纲与无硬编码换算 |
| tests/test_rule2_length_suffix_is_enforced.py | test_rule2_length_suffix_is_now_enforced／test_angle_suffix_constant_is_used_now | 长度/角度后缀 |
| tests/test_rule3_bare_coord_boundary.py | test_bare_coordinates_are_still_flagged／test_unit_carrying_coordinates_are_not_bare | 裸坐标边界 |
| tests/test_linear_pattern_units.py | test_linear_pattern_converts_mm_to_m／test_no_raw_mm_passthrough_left／test_two_paths_agree_on_units | 无二次换算、双路径一致 |
| tests/test_sw_sketch_primitives_contract.py | test_all_five_specs_declared／test_spec_alias_targets_real_parameters／test_length_parameters_are_mm_named／test_resolve_sketch_rejects_non_empty_unknown_name | 草图**图元**声明/别名/mm命名对照；**不是**"草图关系已注册或关系生效"的证据（关系判据归 T017 的注入/注册与 T018 的回读） |
| tests/test_sw_entity_reference.py | test_semantic_reference_reports_ambiguity／test_semantic_reference_resolves_without_face_number／test_geometry_signature_is_stable_for_rounded_values | 引用歧义与稳定签名 |
| tests/test_sw_guard_dialog_tiers.py | test_needs_llm_or_forbidden_never_auto_dismiss／test_destructive_text_is_forbidden_even_with_single_ok／test_question_dialog_is_forbidden | 护栏分级、不自动确认 |
| tests/test_modal_dialogs_single_source.py | test_every_modal_dialogs_delegates_to_the_shared_impl | 护栏单点委托 |
| tests/test_domain_evidence_status.py | test_domain_evidence_requires_manual_review／test_domain_evidence_blocks_environment_failures | 人工复核门、环境失败阻断 |
| tests/test_verified_evidence_gate.py | test_catches_verified_without_evidence／test_real_tree_is_clean | 证据字段门禁 |
| tests/test_verified_level_has_runtime_evidence.py | test_every_verified_has_a_runtime_evidence／test_pytest_only_evidence_is_flagged_in_text | 等级不升级 |
| tests/test_job_evidence_fields.py | test_worker_promotes_drawing_and_bom_evidence_to_job | 证据字段提升 |
| tests/test_deprecated_entry_interlock.py | test_no_new_calls_to_deprecated_entries／test_interlock_fires_on_deprecated_and_passes_on_successor／test_target_table_entries_all_have_successors | 旧入口互锁（仅覆盖登记表内入口） |
| tests/test_spec_acceptance_paths_gate.py | test_current_tree_passes | spec 验收路径可解析 |
| tests/test_signature_audit_freshness_gate.py | test_current_table_is_fresh | 签名审计表新鲜度 |
| tests/test_release_check.py | test_release_check_passes_current_tree | 聚焦门禁（不跑整条收尾链） |

### 10.4 拟新增测试（本轮不存在／未运行／blocked）

所有条目命令形式同 §10.1 的受管绝对路径 pytest；文件缺失时结论为 blocked，不得当成已执行。真机一族（`test_ec00_runtime_*.py`）另需真机授权，授权前不可执行。

| 拟用测试名 | 服务任务 | 当前状态 |
|---|---|---|
| tests/test_ec00_spec_pointer_anchor.py | T002 | 本轮不存在／未运行 |
| tests/test_ec00_legacy_migration_mapping.py | T003 | 本轮不存在／未运行 |
| tests/test_ec00_sketch_relation_official_source.py | T006 | 本轮不存在／未运行 |
| tests/test_ec00_round_chain_side_effect_inventory.py | T007 | 本轮不存在／未运行 |
| tests/test_ec00_quantity_contract.py | T008 | 本轮不存在／未运行 |
| tests/test_ec00_effect_observation_contract.py | T009 | 本轮不存在／未运行 |
| tests/test_ec00_uncertain_recovery_policy.py | T010 | 本轮不存在／未运行 |
| tests/test_ec00_unit_boundary_negative.py | T012 | 本轮不存在／未运行 |
| tests/test_ec00_effect_false_success_negative.py | T013 | 本轮不存在／未运行 |
| tests/test_ec00_context_reference_negative.py | T014 | 本轮不存在／未运行 |
| tests/test_ec00_nonidempotent_uncertain_negative.py | T015 | 本轮不存在／未运行 |
| tests/test_ec00_secret_redaction.py | T015 | 本轮不存在／未运行 |
| tests/test_ec00_unit_normalization_entry.py | T016 | 本轮不存在／未运行 |
| tests/test_ec00_sketch_relation_precheck.py | T017 | 本轮不存在／未运行 |
| tests/test_ec00_effect_readback_mapping.py | T018 | 本轮不存在／未运行 |
| tests/test_ec00_context_fingerprint_negative.py | T019 | 本轮不存在／未运行 |
| tests/test_ec00_guardrail_bypass_negative.py | T020 | 本轮不存在／未运行 |
| tests/test_ec00_evidence_manifest_versioning.py | T021 | 本轮不存在／未运行 |
| tests/test_ec00_legacy_entry_hard_gate.py | T022 | 本轮不存在／未运行 |
| tests/test_ec00_public_route_integration.py | T023 | 本轮不存在／未运行 |
| tests/test_ec00_round_chain_side_effect_split.py | T029 | 本轮不存在／未运行 |
| tests/test_ec00_closeout_whitelist.py | T029 | 本轮不存在／未运行 |
| tests/test_ec00_acceptance_matrix_completeness.py | T030 | 本轮不存在／未运行 |
| tests/test_ec00_quickstart_entry_paths.py | T031 | 本轮不存在／未运行 |
| tests/test_ec00_runtime_environment.py | T024 | 本轮不存在／未运行；真机另授权，当前 blocked |
| tests/test_ec00_runtime_units_relations.py | T025 | 本轮不存在／未运行；真机另授权，当前 blocked |
| tests/test_ec00_runtime_persistence.py | T026 | 本轮不存在／未运行；真机另授权，当前 blocked |
| tests/test_ec00_runtime_recovery.py | T027 | 本轮不存在／未运行；真机另授权，当前 blocked |
| tests/test_ec00_runtime_legacy.py | T028 | 本轮不存在／未运行；真机另授权，当前 blocked |

### 10.5 文件责任域与共享单点合并

公共文件按单一责任人合并，不由多路并行改写；下表责任域名取自 `output/ENGINEERING_PARALLEL_ROSTER.json` 的 `merge_roles`，本轮全部 `assigned_agent` 为空。

| 责任域 | 路径 | 涉及任务 | 当前责任人 |
|---|---|---|---|
| M0 ToolSpec/Param 与新工程入口兼容 | mcp-server/tool_registry.py | T004/T016/T017/T020/T021/T022 | 未指派 |
| M1 批次及唯一注册表 | mcp-server/register_capabilities.py | T017/T022/T023 | 未指派 |
| M2 能力/ROADMAP 台账 | capabilities.yaml、docs/ROADMAP.md | T003/T030 | 未指派 |
| M3 旧草图修复接续 | scripts/sw_part.py、scripts/sw_sketch_relations.py | T003/T016/T017/T025 | 未指派 |
| M4 规格与常驻纪律 | AGENTS.md、.specify/feature.json | T002/T010/T011/T032 | 未指派 |
| M5 生成物与收尾链副作用 | tools/round_chain.ps1 | T007/T029 | 未指派 |
| M6 基线/候选区/执行合并 | — | T001/T003/T029/T032 | 未指派 |

## 11. 当前阻塞与第一动作

- B01：未正式批准编号/工具范围/写入面；先完成T001～T005。
- B02：API参数包装与回读依据未在本特性闭合；T017/T018不能跳过T006。
- B03：本会话运行环境及接入未视为就绪；T024前不得运行T025～T028。
- B04：可靠内存版本检测需研究；不满足时明确保守边界，不假装版本强一致。
- B05：文件责任域未指派、共享单点合并人未定；`merge_roles` M0～M6 的 `assigned_agent` 全部为空，公共 schema、ToolSpec 注册、执行包装、capabilities 不得多路并行改写。
- B06：unknown／busy／uncertain 与真机未测阻塞必须显式保留：unknown 不得当假、busy 不得盲重试、uncertain 无判断不重放、真机未测不得写成 pass 或 not_applicable；T024～T028 本轮只设计调用与证据要求，不执行。
- B07：dirty 基线（`sw_part.py` 已修改、`sw_sketch_relations.py` 未跟踪）与未提交文件权属待正式确认；HEAD/分支/哈希以 `output/ENGINEERING_PARALLEL_ROSTER.json` 的 `baseline` 块为当前已核位置，不代表权属已确认。

**下一轮第一动作是T001，不是继续画齿轮，也不是全仓运行测试。**本轮仅写出草案，T001～T032全部保持未完成；32 个验收入口虽已登记，但现有测试未执行、拟新增测试不存在、真机命令未授权，正式验收未通过。
