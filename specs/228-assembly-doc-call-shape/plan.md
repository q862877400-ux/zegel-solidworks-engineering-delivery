# plan 228 —— `call_assembly_doc` 调用形状门禁

## 一、三源与冲突裁决顺序（本仓纪律）

| 序 | 源 | 用途 | 本切片用到的部分 |
|---|---|---|---|
| ① | `C:/swapi`（官方类型表 md） | 签名与 Remarks 的**语义真源** | **未直接引用**（本切片只比**个数**与 `&`，不比语义） |
| ② | CHM 解包 | 例子/See Also | 未用 |
| ③ | `_raw/**/iface_*.txt`（出厂反射转储） | **形参个数与类型**的机器可读源 | ★ 主源：`## <Iface>` + `Ret Name(params)` 两行式；`&` 即 by-ref |
| ④ | 本仓 `sw_connect.out_i4()` / `out_dispatch()` 来源块的**真机结论** | 判定「by-ref 该不该由调用方传」 | ★ 契约依据（§三） |

**冲突裁决顺序**（铁律 4 家族）：**真机实测 > 出厂反射 > `C:/swapi` md > CHM > 类推**。
本切片的关键冲突（「by-ref 要不要传」）**由真机实测裁决**（`out_i4`），不靠类推。

## 二、实现

| 件 | 动作 |
|---|---|
| `scripts/check_assembly_doc_call_shape.py` | **新增**。AST 扫 `ROOT/scripts/**/*.py`：① 找 `ASSEMBLY_DOC_ARITY` 表（连同其正上方声明）；② 找 `call_assembly_doc` 的字面量调用点；③ arity 比对；④ by-ref 位置要求包装器（口径 `import audit_byref_args`）；⑤ 检查量 0 判失败；⑥ 输出「与 PURE_OUT 口径不符」一节（不判罪） |
| `tests/test_assembly_doc_call_shape.py` | **新增**。13 例：真树绿 + 非空；合成树端到端负例（arity / 未知成员 / 裸 by-ref / 未表态 / 契约冲突 / 0 检查量）；**承重性**（同一调用点末位换 `out_i4()` ⇒ 绿）；缺数据源两条；包装器**边界冻结**（接受 6 种写法、拒绝 8 种裸值） |
| `scripts/release_check.py` | 新增 `_run_assembly_doc_call_shape_gate()` + 调用点 + `raise` 判据 + `_gate_results["assembly_doc_call_shape"]` |
| `docs/gate-classification.json` | 新增 1 条（`kind: hard`），39 → **40** |
| `scripts/sw_assembly_doc.py` | `call_assembly_doc` 的 **docstring 补 by-ref 契约**（§三 证据链）。★ **逻辑零改动** |
| `output/_add_228_classification.py` | 一次性登记脚本（幂等；放 `output/` 不进仓库代码） |

## 三、关键设计（为什么这么定）

1. **不新造声明机制**：复用 227 的 `#: arity-reflect: byref=included` —— 一个事实一个家。
   门禁只是**第二个消费者**（第一个是 `check_arity_tables_vs_reflection.py`）。
2. **口径同源**：by-ref 包装器判定 `import audit_byref_args.BYREF_OK`，
   by-ref 变量收集 `import audit_byref_args.byref_variables` —— 不重写一份。
3. **关联方式确定性**：表 ↔ 声明用「向上跳过空行取第一行非空行」（227 同款），
   **不用行窗口启发式**（225 已证窗口对「插入注释」敏感）。
4. **负例在合成树**：`DSH_ASSEMBLY_CALL_ROOT`（扫描根）+ `DSH_ARITY_DUMPS`（反射路径，与 227 共用）。
   合成夹具**只含被测对象**（不含别的表、不含别的包装器）⇒ 不会「因错误的原因」通过。
5. **不判罪的那一节**：跨工具口径不一致**必须可见但不能拦发布** —— 拦了就是
   「门禁自己挑约定」（227 明令禁止），不报就是**静默**。⇒ 只报。

## 四、风险与边界

| 风险 | 处置 |
|---|---|
| 合成夹具若把 `DSH_ARITY_DUMPS` 留空，门禁会回退 glob 合成树的 `_raw/` ⇒ 「缺数据源」路径走不到 | ★ 测试里把该变量指向一个**不存在**的路径（已在 `run_gate` 注释里写明） |
| `_run_*` 只加函数不加 `_gate_results` ⇒ 元门禁报「跳过与没跑等价」 | 已加（元门禁已三次抓到同类疏漏） |
| 加函数时误删相邻函数的来源块注释 | 本轮**踩到过一次**（`_run_interface_ownership_probe` 的 `# ── 来源 ──` 头被吞），已即刻补回并 `sed` 复核 |
| 真机未验 | 本切片纯静态；契约依据是**他人已做的真机结论**（`out_i4`/`out_dispatch` 来源块），本轮未新增真机证据 |

## 五、验收

见 `acceptance.md`（全部是可复制执行的命令 + 读数）。
