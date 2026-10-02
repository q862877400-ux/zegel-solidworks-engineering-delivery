
# ── 24h 计划 段 5「修地基」（Spec Kit `145`）：**网格参数生效判据** ─────────────────
# ★★★★★ 为什么加它（2026-10-01 轮 248，把"跑求解必挂"的链条**掐断在网格这一步**）：
#
#   | 方式 | 报出的 element_size | CreateMesh 后的单元数 | RunAnalysis |
#   | 既有 `tools/capture_simulation_evidence.py`（**跑通**）| **4.933908705960544** | **7310** | **1 秒 · 4 张图** |
#   | 本项目其它链                                          | **4930.501659457233** | **7250** | ★ **300 秒超时 / 无结果** |
#
#   ⇒ ★★ **两次读同一条 `default_element_size_and_tolerance(study, -1)` 却差**恰好 1000 倍**
#     （★ 原因**未查清**：`probe_document_units` 里"文档单位"那一处读不到，报 `非选择性的参数`／`-1`）。
#   ⇒ ★★★ **而 4930.5 是**不合理的**：那比零件（100 mm）大 49 倍** ——
#     单元比零件还大 ⇒ ★ **网格退化** ⇒ `CreateMesh` **静默退回默认值**（7250 ≈ 默认的 7310）
#     ⇒ ★★★★ **求解因此无解 / 卡住** ⇒ **而弹框与挂起就发生在那一步**。
#   ⇒ ★★★★★ **所以：只要在**建网格之前**判出"这个 element_size 不合理"，就**不必跑求解** ⇒
#     **挂起从源头被掐断**（★ 这与 `sw_isolate` 的进程隔离**互补**：一个防外溢，一个防发生）。
#
# ★★ 判据怎么选（★ 不发明）：★ **拿 `element_size` 与**零件自身尺寸**比** ——
#   官方建议值必然是零件尺度的一个**小分数**（本机实测：100 mm 的板 ⇒ 4.93 mm，约 **1/20**）。
#   ⇒ 取一个**宽到不可能误伤**的门槛：**单元尺寸不得大于零件的最大边**。
#     ★ 这个门槛**永远不该被合法的网格参数触到**（单元等于零件最大边 ⇒ 网格只有 1 个单元）。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_simulation.py —— 本段
# 定位:   建网格前的**参数合理性判据**（24h 段 5「修地基」）。
# 官方依据: `ICWMesh.GetDefaultElementSizeAndTolerance`（本模块已记：两次实测差 1000 倍）；
#          零件尺寸取 `IBody2.GetBodyBox`（本模块/`sw_part` 已有）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   下面这个 `check_mesh_size_sane`
# ─────────────────────────────────────────────────────────────────────────────


def check_mesh_size_sane(model, element_size: float) -> dict[str, Any]:
    """★ **建网格之前**判一次：给定的单元尺寸对**这个零件**是否合理。

    ★★★ 这是把"跑求解必挂"**掐断在源头**的那道闸 —— 依据见本段顶部的对照表：
    读到的 `element_size` 若**大于零件的最大边**，那么网格必然退化、
    `CreateMesh` 会**静默退回默认值**，而随后的 `RunAnalysis` **无解 ⇒ 弹模态框 ⇒ 挂住会话**。

    :param model: 活动文档（用来量零件包围盒）。
    :param element_size: 打算传给 ``CreateMesh`` 的单元尺寸（★ 单位口径见 `create_mesh` 的 docstring）。
    :returns: ``{"ok": bool, "element_size": float, "max_dim": float | None, "reason": str}``
        ★ **`ok=False` 时调用方应当停下**（不要建网格、更不要跑求解）。
    """
    out: dict[str, Any] = {"element_size": float(element_size), "max_dim": None,
                           "ok": True, "reason": "", "★": "建网格前的合理性判据（段 5 修地基）"}
    if not (float(element_size) > 0.0):
        out.update({"ok": False, "reason": "element_size 不是正数（%r）" % element_size})
        return out
    try:
        size = None
        try:
            import sw_part

            bb = sw_part.get_bounding_box(model)
            size = (bb or {}).get("size")
        except Exception:                                      # noqa: BLE001
            size = None
        if not size:
            out.update({"reason": "量不到零件包围盒 ⇒ **只记不判**（★ 不因为没有参照就误报）"})
            return out
        max_dim = max(float(x) for x in size)
        out["max_dim"] = max_dim
        if float(element_size) > max_dim:
            out.update({
                "ok": False,
                "reason": ("单元尺寸 %.4f 大于零件最大边 %.4f ⇒ **网格必然退化**"
                           "（CreateMesh 会静默退回默认值，随后 RunAnalysis 无解 ⇒ 弹模态框 ⇒ 挂住会话）"
                           % (float(element_size), max_dim)),
            })
        return out
    except Exception as exc:                                   # noqa: BLE001
        out.update({"reason": "判据自身出错（★ 不因此阻断）：%s: %s"
                              % (type(exc).__name__, str(exc)[:120])})
        return out
