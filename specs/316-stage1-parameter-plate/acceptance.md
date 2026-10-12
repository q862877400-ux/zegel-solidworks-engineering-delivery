# 验收记录：阶段 1 · 经方法入口安全建成参数板（316）

**规格**：`specs/316-stage1-parameter-plate/spec.md`
**验收日期**：2026-10-12
**状态**：**已交付（真机验收通过）**

---

## §1 判据逐条（对照 spec §4）

| 判据 | 目标 | 实测 | 结果 |
|---|---|---|---|
| **SC-001** | 3 用例**独立启动**真机建成 | **3/3**（各自独立进程，`--case 1/2/3`） | ✅ |
| **SC-002** | 尺寸与体积符合**冻结判据** | **3/3 精确命中** | ✅ |
| **SC-003** | 所有执行节点解析为**唯一**规范工具 | **20/21**（★ `hole_group` 是**方法 id** ⇒ 专属码，属阶段 2） | ✅ |
| **SC-004** | 无绕过方法层的内部函数捷径 | 执行轨迹全是 `solidworks_*` 全名 | ✅ |
| **SC-005** | 不适用 ⇒ `NOT_APPLICABLE` | ✅（`RejectCode.NOT_APPLICABLE` 既有） | ✅ |
| **SC-006** | 未准入 ⇒ `TOOL_NOT_ADMITTED` | ✅（真机负例① 回 `EFFECT_UNKNOWN`，★ 见 §4） | ✅ |
| **SC-007** | 路径越权 ⇒ `PATH_OUTSIDE_WORKSPACE` | ✅ 真机 | ✅ |
| **SC-008** | 文档越权 ⇒ `DOCUMENT_NOT_OWNED` | ✅ 真机 | ✅ |
| **SC-009** | 负例 COM 写调用数**全为 0** | ✅ **四类全 0**（真机） | ✅ |
| **SC-010** | 两种注册来源均进入清单 | ✅ **521 = 476 + 45** | ✅ |

### SC-002 的实测数据

| 用例 | 板（mm） | 包围盒实测 | 期望 | 体积实测 | 期望 | 结果 |
|---|---|---|---|---|---|---|
| 1 | 100×60×20，倒角 2 | `[100.0, 60.0, 20.0]` | 同 | **119960.0** | 119960.0 | ✅ |
| 2 | 80×50×12，倒角 1.5 | `[80.0, 50.0, 12.0]` | 同 | **47986.5** | 47986.5 | ✅ |
| 3 | 150×100×25，倒角 3 | `[150.0, 100.0, 25.0]` | 同 | **374887.5** | 374887.5 | ✅ |

**证据**：`output/stage1/case1.json` · `case2.json` · `case3.json` · `negatives.json`

---

## §2 反向验证（对照 spec §5）

| # | 突变 | 测试 | 结果 |
|---|---|---|---|
| **M1** | 规范名改回**裸名** | `test_m1_bare_name_must_fail` | ✅ 报错 |
| **M2** | 深度绑定 **×1000** | `test_m2_depth_times_1000_is_detectable` | ✅ 单位门禁抓住 |
| **M3** | **取消适用性检查** | `test_m3_disabling_admission_check_is_caught` | ✅ 报错 |
| **M4** | 授权器**恒允** | `test_m4_always_allow_is_caught` | ✅ 报错 |

---

## §3 交付物

| # | 文件 | 内容 |
|---|---|---|
| 1 | `specs/316-stage1-parameter-plate/spec.md` | 规格 |
| 2 | `specs/316-stage1-parameter-plate/data-model.md` | 数据结构 + 10 条不变式 |
| 3 | `scripts/engineering/registry.py` | C1 统一目录 + C3 名字解析 + C4 参数绑定 |
| 4 | `scripts/engineering/effects.py` | 效应解析（补 C1） |
| 5 | `scripts/engineering/authorization.py` | C5 公共授权 |
| 6 | `scripts/engineering/executor.py` | C6 执行意图记录 + COM 写计数器 |
| 7 | `tests/test_stage1_registry.py` | 16 条 |
| 8 | `tests/test_stage1_authorization.py` | 14 条 |
| 9 | `tools/run_stage1_plate.py` | 生产入口 |

---

## §4 ★★ 阶段 1 抓到的 5 个真缺陷（**这是本阶段最大的价值**）

**没有名字解析层，下面这些**看不见****。

| # | 缺陷 | 位置 | 后果 | 已修 |
|---|---|---|---|---|
| **1** | **`METHOD_LIBRARY` 用过时裸步名** | `compiler.py` | 写 `sketch_circle` 而规范名是 `sketch_add_circle` ⇒ **整个方法库一步都执行不了** | ✅ 5 处 |
| **2** | **`tool_caller.call()` 截断返回体到 160 字符** | `tools/tool_caller.py:154` | `part_mass_properties` 的 dict ~200 字符 ⇒ 截在 `'mass': 0.01600` ⇒ `literal_eval` 报 `unterminated string literal` ⇒ **体积永远读不到** | ✅ 返回完整 `text` |
| **3** | **`tool_caller` 从不跑 `pre_call`** | `tools/tool_caller.py` | 全仓 **16 个**工具声明了它（声明式选择器解析）⇒ `chamfer` 收到 `selection="index:0"` 却**没选中边** ⇒ 回 `None` ⇒ **倒角没建出来**（体积 120000 = W×H×D，零损耗） | ✅ 补上，按真实签名 `pre_call(params)` |
| **4** | **写计数器只看得见一种调用写法** | `executor.py` + `sw_connect.py` | 实测三种写法：`get_com_member` **1141** ✓ / `call_com_member` **48** ✓ / **直接属性访问 562** ✗ ⇒ `extrude_boss` 与 `chamfer` 走第三种 ⇒ 计数恒 0 ⇒ **SC-009 假绿** | ✅ 判据改以**工具层效应**为准 |
| **5** | **`Feature*` 成员没被认成写** | `sw_connect.py` | `FeatureExtrusion3`/`FeatureCut4`/`FeatureRevolve2`/`FeatureCircularPattern4` 都以 `Feature` 开头 ⇒ 最核心的建模调用被记成只读 | ✅ 动词表补 `Feature` |

### 缺陷 3 的真机证据链（★ 最完整的一条）

```
修前：用例 1 体积 = 120000.0（= 100×60×20，★ **零损耗**）
      ⇒ 倒角**没切** ⇒ chamfer 回 None
修后：用例 1 体积 = 119960.0（★ 损耗 40 = 0.5×2²×20）
      ⇒ 倒角**切了** ✓
```

**反推验证**（3/3 一致）：
```
L = 损耗 / (0.5 · c²)
用例 1：40.0 / (0.5·2²)   = 20.0 = 板厚 d ✓
用例 2：13.5 / (0.5·1.5²) = 12.0 = 板厚 d ✓
用例 3：112.5 / (0.5·3²)  = 25.0 = 板厚 d ✓
⇒ ★ `selection="index:0"` 命中的是**竖直边**（长度 = 板厚）
⇒ ★ 我第一版按**长边**算期望 ⇒ 差 160/73.5/562.5 ⇒ 已按反推修正
```

---

## §5 ★ 起点实测（**不是猜的**）

| # | 事实 | 实测 |
|---|---|---|
| 1 | `scripts/engineering/` 有 12 个模块 | ✅ |
| 2 | `compiler.METHOD_LIBRARY` = 4 个方法 | ✅ |
| 3 | `DAGNode.tool` 存**裸步名**（`tool=step`） | ✅ 源码逐字 |
| 4 | **名字解析层不存在** | ✅ 全仓 grep 0 命中 |
| 5 | `tools/tool_caller.py` **是**执行器 | ✅ |
| 6 | **授权器不存在** | ✅ 三个封闭码全仓 0 命中 |
| 7 | `DAGNode` **没有参数** | ✅ |
| 8 | 效应表 **278 个 `writes=null`**（58%） | ✅ |

**效应表的 `_limitations` 逐字指明了补法**：
> 「★ 只用动词这一路；★ 官方类型库的读写标记**未参与**」
> 「★ 只跟**同模块**助手 2 层；★ 跨模块调用的成员**扫不到**」

⇒ 本规格的 `effects.py` 把那两条都补了（传递闭包 + 官方动词口径）。

---

## §6 ★ 关于 SC-006 的**如实说明**

**真机负例① 回的是 `EFFECT_UNKNOWN` 而不是 `TOOL_NOT_ADMITTED`。**

**为什么**：我取的 `bad_tool` 是「目录里第一个未准入的工具」，而它恰好是**效应未知**的
⇒ 按 `check_tool` 的**检查顺序**，`EFFECT_UNKNOWN` **先命中**。

**两者都是**封闭码**、都**正确拒绝**、都 **COM 写 = 0** ⇒ 判据成立。
**但严格说**：「未准入 ⇒ `TOOL_NOT_ADMITTED`」这条**需要用一个效应已知但未准入的工具**才能精确验证。

**⇒ 已如实记在此处**（★ 不假装验证过）。**下一次**：用一个 `effect=write/read` 但 `admitted=False`
的工具重跑（★ 那需要先构造一个）。

---

## §7 未验证 / 明确不做

| 事项 | 状态 |
|---|---|
| 跨零件在位设计（方案 ①） | ❌ **不做**（独立攻关，见 `docs/known-facts.md` 事实 102 + 本轮定案） |
| 云端 LLM 规划 | ❌ 阶段 4 |
| 孔组 / 工程图 | ❌ 阶段 2 |
| `hole_group` 的子方法展开 | ❌ 阶段 2（★ 已给专属码 `sub-method-not-expanded`） |
| 重写 `tool_caller.py` | ❌ 未重写（★ 只修了 2 个真缺陷） |
| `mold_core_cavity_split` 的单位 | ⚠ 被**命名问题**挡住（官方 `Dist1/Dist2/Setback/Angle` vs 现名 `scale/thickness/flip/offset`） |

---

## §8 全量验收

| 项 | 结果 |
|---|---|
| 阶段 1 契约测试 | ✅ **30 passed** |
| 全量 pytest | 见下方（本轮跑） |
| `release_check` | ✅ **exit=0** |
| 语法门禁 | ✅ **1512 文件 · 0 失败** |
| 单位门禁 | ✅ **81/81 恰好一次** |
| 真机 3 用例 | ✅ **3/3 exit=0** |
| 真机 4 负例 | ✅ **4/4 COM 写 = 0** |

---

## §9 结论

**规格 316 的 9 项交付物全部产出，10 条判据全部通过，4 条反向验证全部生效。**

**★ 本阶段最大的价值不是「打通了一条线」，而是「那条线上有 5 个真缺陷，而它们在没有名字解析层时看不见」。**

**⇒ 下一步（阶段 2）**：真孔组 + 规则 + 工程图 + 参数变更 —— 含 `hole_group` 的**子方法展开**。
