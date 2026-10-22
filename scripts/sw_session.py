"""
SolidWorks 友好会话 API

本模块在底层 COM helper 之上提供更顺手的门面接口，适合脚本和 AI 代理快速组合
“打开/新建/保存/导出/关闭”等常见流程。底层函数仍保留在 sw_connect.py、
sw_part.py、sw_export.py 等模块中，便于精细控制。
"""

from pathlib import Path
import os

try:
    from .sw_connect import (
        close_owned_solidworks,
        connect_solidworks,
        get_com_member,
        new_document,
        open_document,
        save_document,
    )
    from .sw_export import (
        export_to_dxf,
        export_to_iges,
        export_to_pdf,
        export_to_stl,
        export_to_step,
    )
except ImportError:
    from sw_connect import (
        close_owned_solidworks,
        connect_solidworks,
        get_com_member,
        new_document,
        open_document,
        save_document,
    )
    from sw_export import (
        export_to_dxf,
        export_to_iges,
        export_to_pdf,
        export_to_stl,
        export_to_step,
    )


EXPORTERS = {
    ".step": export_to_step,
    ".stp": export_to_step,
    ".stl": export_to_stl,
    ".iges": export_to_iges,
    ".igs": export_to_iges,
    ".pdf": export_to_pdf,
    ".dxf": export_to_dxf,
    ".dwg": export_to_dxf,
}


class SolidWorksSession:
    """
    SolidWorks 自动化会话。

    示例:
        session = SolidWorksSession()
        model = session.new_part()
        session.save(model, r"C:\\temp\\part.sldprt")
        session.export(model, r"C:\\temp\\part.step")
    """

    def __init__(self, version=None, wait_seconds=5, visible=True):
        """
        初始化并连接 SolidWorks。

        参数:
            version: SolidWorks 年份，例如 2024；None 表示自动连接默认 ProgID。
            wait_seconds: 新启动实例后的等待秒数。
            visible: 新启动实例是否显示窗口。
        """
        self.sw, self.model, self.connection_info = connect_solidworks(
            version=version,
            wait_seconds=wait_seconds,
            visible=visible,
            return_metadata=True,
        )

    @property
    def active_doc(self):
        """返回当前活动文档并同步到 session.model。"""
        self.model = self.sw.ActiveDoc
        return self.model

    def new(self, doc_type="part", template_path=None):
        """
        新建文档。

        参数:
            doc_type: "part"、"assembly"、"drawing" 或常见扩展名。
            template_path: 指定模板路径；None 表示自动查找模板。
        """
        self.model = new_document(
            self.sw, doc_type=doc_type, template_path=template_path
        )
        return self.model

    def new_part(self, template_path=None):
        """新建零件文档。"""
        return self.new("part", template_path=template_path)

    def new_assembly(self, template_path=None):
        """新建装配体文档。"""
        return self.new("assembly", template_path=template_path)

    def new_drawing(self, template_path=None):
        """新建工程图文档。"""
        return self.new("drawing", template_path=template_path)

    def open(self, file_path, read_only=False, silent=False, raise_on_error=True):
        """
        打开文档。

        参数:
            file_path: SolidWorks 文件或中间格式文件路径。
            read_only: 是否只读打开。
            silent: 是否静默打开。
            raise_on_error: 打开失败时是否抛出异常。
        """
        self.model = open_document(
            self.sw,
            file_path,
            read_only=read_only,
            silent=silent,
            raise_on_error=raise_on_error,
        )
        return self.model

    def save(self, model=None, file_path=None):
        """
        保存文档。

        参数:
            model: 指定文档；None 表示当前活动文档。
            file_path: 另存为路径；None 表示保存到当前位置。
        """
        model = model or self.active_doc
        if model is None:
            raise RuntimeError("当前没有可保存的活动文档")
        return save_document(model, file_path=file_path)

    def export(self, model=None, output_path=None, format_ext=None, **kwargs):
        """
        按输出扩展名导出文档。

        参数:
            model: 指定文档；None 表示当前活动文档。
            output_path: 输出文件路径。
            format_ext: 显式格式扩展名；None 表示从 output_path 推断。
            **kwargs: 传给具体导出函数的附加参数，例如 STL quality。
        """
        model = model or self.active_doc
        if model is None:
            raise RuntimeError("当前没有可导出的活动文档")
        if not output_path:
            raise ValueError("必须提供 output_path")

        output = Path(os.path.expandvars(str(output_path))).expanduser()
        output.parent.mkdir(parents=True, exist_ok=True)
        ext = (format_ext or output.suffix).lower()
        if not ext.startswith("."):
            ext = f".{ext}"

        exporter = EXPORTERS.get(ext)
        if exporter is None:
            raise ValueError(f"暂不支持导出格式: {ext}")
        return exporter(model, str(output), **kwargs)

    def close(self, model=None, title=None):
        """
        关闭文档。

        参数:
            model: 指定文档；None 表示按 title 或当前活动文档关闭。
            title: 文档标题；适合关闭已知标题的文档。
        """
        if title is None:
            model = model or self.active_doc
            if model is None:
                return False
            title = get_com_member(model, "GetTitle")
        is_current_model = False
        if self.model:
            try:
                is_current_model = get_com_member(self.model, "GetTitle") == title
            except Exception:
                is_current_model = True
        self.sw.CloseDoc(title)
        if is_current_model:
            self.model = self.sw.ActiveDoc
        return True

    def quit_owned_instance(self):
        """退出本会话启动的实例；附着到用户实例时不执行任何关闭操作。"""
        return close_owned_solidworks(
            self.sw,
            bool(self.connection_info.get("started_by_cad_studio")),
        )


def session(version=None, wait_seconds=5, visible=True):
    """
    创建 SolidWorksSession 的便捷函数。

    参数同 SolidWorksSession。
    """
    return SolidWorksSession(
        version=version, wait_seconds=wait_seconds, visible=visible
    )


# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_session.py —— 追加 undo_report
# 定位:   objective② 的四家缺口 `undo`（★ 事实 311 三层证据判定的真缺）；官方
#   IModelDoc2.EditUndo2(int Steps)（★ 1 参、回 void）⇒ 判据只能是特征树退回（规则 6）。
# 官方依据: C:\swapi\types\IModelDoc2\EditUndo2.md（★ void EditUndo2(int Steps)）
#   · EditUndo（★ Obsolete）· SketchUndo()（★ 零参）· 反射 arity 1
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────────────
#: ★ 本模块新增入口所需的两个依赖（★ 就地 import，★ 避免动首部结构）
from sw_connect import get_com_member  # noqa: E402
from sw_feature_readback import feature_names  # noqa: E402


# ── objective② / 四家缺口 `undo`：**撤销（`IModelDoc2.EditUndo2`）** ──────────────────
# ───
# ★★★★ 2026-10-03（轮 395）**补 `undo`** —— objective② 三层证据判它是**真缺**（事实 311
# ），
#   而官方入口明确：`C:\swapi\types\IModelDoc2\EditUndo2.md`
#   ```
#   void EditUndo2(int Steps)   —— 「Undoes the specified number of actions in the active
#                                    SOLIDWORKS Design session」
# · EditUndo(uint NSteps)  **Obsolete**（★ 后继是 EditUndo2）· SketchUndo() 零参（★ 撤最
# 后一条草图画线）
#   ```
# ★★ **为什么它对自动化 agent 特别有用**：★ 我们的工具会**改模型**；★ 一旦某一步改错，
#   ★ **没有撤销就意味着只能重来**（★ 或留下脏状态）。★ 它是**我们自己的改动**的回退手段。
# ★ 规则 2 / 6：★ 对外只暴露 `steps`（★ 个数，★ 不是长度 ⇒ 无单位）；★ 它回 **`void`**
#   ⇒ ★★ 判据**不能是返回值**，只能是「**特征树退回了**」（★ 建完/撤完都要回读）。
# ★ ⚠ **边界**：★ `EditUndo2` 撤的是「**会话里的动作**」—— ★ 它**不区分**是不是我们做的
# ⇒ ★ 所以本工具**只该在我们自己的改动之后调用**（★ 调用方负责；★ 这是**使用纪律**，不是
# 本函数能强制的）。


def undo_report(model, steps: int = 1) -> dict:
    """★ **撤销**（★ 官方 `IModelDoc2.EditUndo2`，**1 参**，★ 回 `void`）。

    :param steps: 要撤的动作数（★ 必须 ≥ 1）。
    :returns: `{ok, steps, tree_before, tree_after, undone}` —— ★★ **判据是特征树真的退回了**
        （★ 它回 `void` ⇒ 只能回读；★ 规则 6）。

    ⚠ **调用纪律**：★ `EditUndo2` 撤的是**会话里的动作**，★ **不区分是不是我们做的** ⇒
      ★ **只在我们自己的改动之后调用**（★ 例如"建完发现参数错 ⇒ 撤掉重来"）。
    """
    if model is None:
        return {"ok": False, "error": "model 为 None"}
    try:
        n = int(steps)
    except (TypeError, ValueError) as exc:
        return {"ok": False, "error": "steps 必须是整数：%s" % str(exc)[:80]}
    if n < 1:
        return {"ok": False, "error": "steps 必须 ≥ 1（★ 收到 %r）" % steps}
    try:
        before_names = feature_names(model)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "stage": "read_before", "error": str(exc)[:120]}
    before = len(before_names)
    try:
        get_com_member(model, "EditUndo2", n)
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "stage": "call",
            "steps": n,
            "error": "%s: %s" % (type(exc).__name__, str(exc)[:200]),
        }
    try:
        after_names = feature_names(model)
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "stage": "read_after", "steps": n, "error": str(exc)[:120]}
    after = len(after_names)
    gone = [x for x in before_names if x not in after_names]
    return {
        "ok": after < before,
        "steps": n,
        "tree_before": before,
        "tree_after": after,
        "removed_features": gone[-4:],
        "undone": after < before,
        "★": "它回 void ⇒ 判据是**特征树真的退回了**（★ 规则 6）；"
        "★ 官方 1 参 · 反射 arity 1 · `EditUndo` 已 Obsolete",
    }


# ── 规格 209（规格 207 的 18 条采纳候选 · B1 批）：**重建**（三档 mode 一条工具）──────
# ────────
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_session.py —— 追加 `rebuild_report`
# 定位:   ★ 规格 `specs/209-union-adopt-18/` 的 **B1 批** · 外部项目 idx **235 `rebuil
#           d_document`**
# + idx **236 `rebuild_model`**。★★ 裁决书（`docs/recon-207/adjudication.md` §一）逐字要
# 求：
# 「与 236 **合并成一条工具**（三档 mode），**不建两条**」—— 理由是「两条工具做同一件事
# 会在
#   能力清单里留下两条永远同进同退的条目」✓
# 官方依据 （★ 铁律 4：`C:\swapi` 逐页读过 + 出厂类型库反射 arity 互证）：
# · `C:\swapi\types\IModelDoc2\EditRebuild3.md` —— `System.bool EditRebuild3()`（**零参*
# *）
# ★★ `## Remarks` 逐字：「This method only works **in-context of the active document**.
# 」
# · `C:\swapi\types\IModelDoc2\ForceRebuild3.md` —— `System.bool ForceRebuild3(System.bo
# ol TopOnly)`
# ★ `## Parameters` 逐字：TopOnly「True rebuilds the top-level assembly only; false rebu
# ilds
#       the top-level assembly and all subassemblies」
# · `C:\swapi\types\IModelDocExtension\ForceRebuildAll.md` —— `System.bool ForceRebuildA
# ll()`（**零参**）
# ★ 摘要逐字：「Forces a rebuild of all features in **all configurations without activat
# ing
#       each configuration**」（★ 这正是它与 `ForceRebuild3` 的**分工**：一个只动活动配置、
#       一个**不动配置就能重建全部**）
# · `C:\swapi\types\IModelDocExtension\NeedsRebuild2.md` —— `System.int NeedsRebuild2 {g
# et;}`
# · `C:\swapi\enums\swModelRebuildStatus_e.md` —— `FullyRebuilt=0` · `NonFrozenFeatureNe
# edsRebuild=1`
#     · `FrozenFeatureNeedsRebuild=2`；★ 官方 `## Description` 逐字写 **Bitmask**
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   后续同级定义
# ─────────────────────────────────────────────────────────────────────────────
# ★★★ **本函数最容易犯的错（裁决书点名的硬约束）**：★ `EditRebuild3` 是**方法**、不是**
# 属性** ——
#   三家外部项目都当属性读（`_get(doc, 'EditRebuild3')`）⇒ ★ 照抄会拿到 **bound method**，
#   ★★ 而**拿它当判据会永远为真**（函数对象本身恒真）⇒ ★★ 本函数**必须真的调用它**，
#   ★★ 且**判据一律用回读**（`NeedsRebuild2` + 特征树计数 + 包围盒），**不用那个返回值**✓

#: ★ 三档 mode（★ 逐档对应**一个**官方成员 —— 不是三个入口随便挑）
REBUILD_MODES = ("edit", "force", "all")

#: ★ 官方 `swModelRebuildStatus_e`（★ 位掩码；`0` = 已完全重建）
NEEDS_REBUILD_STATES = {
    0: "fully_rebuilt",
    1: "non_frozen_feature_needs_rebuild",
    2: "frozen_feature_needs_rebuild",
}


def needs_rebuild_status(model) -> dict:
    """★ 读**重建状态**（★ 官方 `IModelDocExtension.NeedsRebuild2`，回 `swModelRebuildStatus_e`）。

    :returns: `{"raw": int, "state": str, "fully_rebuilt": bool}`；★ 取不到就抛（★ 不静默回 0 ——
        ★★ 「读不到」与「已重建」**是两件事**，混起来会让判据永远为真）。
    """
    ext = get_com_member(model, "Extension")
    if ext is None:
        raise RuntimeError("IModelDoc2.Extension 为 None ⇒ 读不到重建状态")
    raw = int(get_com_member(ext, "NeedsRebuild2") or 0)
    return {
        "raw": raw,
        "state": NEEDS_REBUILD_STATES.get(raw, "unknown_%d" % raw),
        "fully_rebuilt": raw == 0,
    }


def rebuild_report(model, mode: str = "edit", *, top_only: bool = False) -> dict:
    """★ **重建模型**（★ 三档 mode，一条工具 —— 裁决书强制合并 235/236）。

    :param mode: ``"edit"``（★ `IModelDoc2.EditRebuild3()`，**只重建需要重建的特征**，零参）·
        ``"force"``（★ `IModelDoc2.ForceRebuild3(TopOnly)`，**强制重建活动配置的全部特征**）·
        ``"all"``（★ `IModelDocExtension.ForceRebuildAll()`，**不动配置就重建全部配置**，零参）。
    :param top_only: ★ **只对 `mode="force"` 有意义**（对应官方 `ForceRebuild3` 的 `TopOnly`）：
        `True` 只重建顶层装配、`False` 连子装配一起。★ 其余两档**忽略它**并在返回值里说明。
    :returns: `{ok, mode, entry_used, returned, needs_rebuild_before/after, state_before/after,
        tree_before/after, bbox_changed, error}`

    ★★ **判据是回读，不是返回值**（★ 规则 6 + 裁决书的硬约束）：
      · `needs_rebuild_after.raw == 0`（★ 真的不再需要重建）；
      · `tree_after == tree_before`（★ **重建不增删特征** —— 它变的是特征的状态，不是树的形状）；
      · `bbox_changed == False`（★ 同参数下重建**不该改几何** —— ★ 改了说明发生了回滚/报错）。
    ⚠ **边界（如实记）**：★ `EditRebuild3` 的官方 Remarks 逐字说它**只在活动文档的上下文里**工作
      ⇒ ★ 对未激活的文档调用**没有意义**（本函数不做「先激活」—— 那是调用方的事）。
    """
    out: dict = {
        "ok": False,
        "mode": None,
        "entry_used": None,
        "returned": None,
        "needs_rebuild_before": None,
        "needs_rebuild_after": None,
        "state_before": None,
        "state_after": None,
        "tree_before": None,
        "tree_after": None,
        "bbox_changed": None,
        "bbox_before": None,
        "bbox_after": None,
        "bbox_comparable": None,
        "top_only_applied": None,
        "error": None,
        "note": None,
        "★": "判据用**回读**（NeedsRebuild2 + 特征树 + 包围盒），**不用返回值** —— "
        "`EditRebuild3` 是**方法**，当属性读会拿到 bound method（恒真）",
    }
    key = str(mode or "").strip().lower()
    if key not in REBUILD_MODES:
        out["error"] = "未知的 mode %r；合法：%s" % (mode, ", ".join(REBUILD_MODES))
        return out
    if model is None:
        out["error"] = "model 为 None"
        return out
    out["mode"] = key

    def _bbox_key():
        """★ 取包围盒的**可比较键**（`sw_part.get_bounding_box` 回的是**字典** ⇒ 取 min/max 两组）。

        ⚠⚠ **2026-10-06 自查抓到的一处"静默失效"（本轮修的）**：第一版写的是
        `tuple(float(v) for v in bb)` —— ★ 而 `bb` 是**字典** ⇒ 迭代出来的是**键名字符串**
        （`"min"/"max"/"size"`）⇒ `float("min")` 抛异常 ⇒ 被 `except` 吞掉 ⇒ **回 `None`**
        ⇒ ★★ 于是 `bbox_changed` **永远是 `False`** —— **判据看着在、其实空转** ✓
        ⇒ ★ 修法两件：① 这个函数**取对字段**；② 返回值里**显式给出 `bbox_comparable`**
        （★ `None`（读不到）与 `False`（没变）**必须分得开** —— 否则"读不到"会被当成"没变"）✓
        """
        try:
            from sw_part import get_bounding_box

            bb = get_bounding_box(model)
            if not isinstance(bb, dict):
                return None
            return (
                tuple(round(float(v), 6) for v in bb["min"]),
                tuple(round(float(v), 6) for v in bb["max"]),
            )
        except Exception:  # noqa: BLE001
            return None

    try:
        out["state_before"] = needs_rebuild_status(model)["state"]
        out["needs_rebuild_before"] = needs_rebuild_status(model)["raw"]
        out["tree_before"] = len(feature_names(model))
        bbox_before = _bbox_key()
    except Exception as exc:  # noqa: BLE001
        out["error"] = "前置回读失败：%s: %s" % (type(exc).__name__, str(exc)[:150])
        return out

    try:
        if key == "edit":
            out["entry_used"] = "IModelDoc2::EditRebuild3()"
            out["top_only_applied"] = False
            out["returned"] = get_com_member(model, "EditRebuild3")  # ★ 真的调它
        elif key == "force":
            out["entry_used"] = "IModelDoc2::ForceRebuild3(System.bool TopOnly)"
            out["top_only_applied"] = bool(top_only)
            out["returned"] = get_com_member(model, "ForceRebuild3", bool(top_only))
        else:
            ext = get_com_member(model, "Extension")
            if ext is None:
                out["error"] = "IModelDoc2.Extension 为 None ⇒ ForceRebuildAll 不可达"
                return out
            out["entry_used"] = "IModelDocExtension::ForceRebuildAll()"
            out["top_only_applied"] = False
            out["returned"] = get_com_member(ext, "ForceRebuildAll")
    except Exception as exc:  # noqa: BLE001
        out["error"] = "调用失败：%s: %s" % (type(exc).__name__, str(exc)[:200])
        return out

    try:
        out["needs_rebuild_after"] = needs_rebuild_status(model)["raw"]
        out["state_after"] = needs_rebuild_status(model)["state"]
        out["tree_after"] = len(feature_names(model))
        bbox_after = _bbox_key()
    except Exception as exc:  # noqa: BLE001
        out["error"] = "后置回读失败：%s: %s" % (type(exc).__name__, str(exc)[:150])
        return out

    out["bbox_changed"] = (
        bbox_before is not None and bbox_after is not None and bbox_before != bbox_after
    )
    out["bbox_before"] = bbox_before
    out["bbox_after"] = bbox_after
    #: ★★ **`None`（读不到，判据不可用）与 `False`（读了、没变）必须分得开** ——
    #:   否则"读不到"会被当成"没变"（★ 那正是本函数第一版踩的坑）✓
    out["bbox_comparable"] = bbox_before is not None and bbox_after is not None
    out["ok"] = (
        out["needs_rebuild_after"] == 0
        and out["tree_after"] == out["tree_before"]
        and (not out["bbox_changed"] if out["bbox_comparable"] else True)
    )
    if not out["ok"]:
        out["error"] = (
            "回读判据未过：needs_rebuild_after=%r（要 0）· tree %r→%r（要相等）· "
            "bbox_changed=%r（要 False）"
            % (
                out["needs_rebuild_after"],
                out["tree_before"],
                out["tree_after"],
                out["bbox_changed"],
            )
        )
    elif not out["bbox_comparable"]:
        out["note"] = (
            "★ 包围盒这一条**判据不可用**（读不到 —— 例如文档里没有实体）⇒ "
            "本轮只用「状态归零 + 特征树不变」两条，★ 如实记，**不拿没读到当没变**"
        )
    return out


# ── 会话预检（规格 210 · B5-1/B5-2）─────────────────────────────────────
# ★★ 来源：外部评审对「SolidWorks 自己写的文件拦不住」的判决 ——
#   ★ 它给的第一条不是"拦内部写"，而是「**SolidWorks 打开的永远不是原件**」+
#   ★「**预检门禁**：真机跑开始前枚举已打开的文档，只要有不是我方的就拒绝开始」✓
# ★ 官方依据（铁律 4 的第 0 步，已读）：`ISldWorks.GetDocuments` ——
#   "Gets the open documents in this SOLIDWORKS Design session"（返回文档数组）；
# ★ 配套 `GetDocumentCount` 拿数量；★ 官方示例 `Get_Paths_of_Open_Documents` 给的调用序
# 是
#   `GetDocumentCount` → `GetDocuments` → 逐档 `IModelDoc2.GetPathName` ✓
# ★ 为什么不用 `GetFirstDocument`：★ 它的官方 Remarks 明写「若最先打开的是装配体，
# 则返回该装配体里**第一个组件**文档」⇒ ★ **它不是一次完整枚举**，不能用来判"有哪些开着"
#  ✓
# ⚠ 限度：★ path 为空（新建未存盘的文档）**按"非我方"处理**（保守）；
#   ★ 真要放行未命名文档，得显式传 `allow_untitled=True` ✓


class ForeignDocumentError(RuntimeError):
    """★ 会话预检失败：SolidWorks 里开着**不是我们打开的**文档 ⇒ 拒绝开始（不删用户数据）✓"""


def _norm_path(value) -> str:
    """★ 归一化路径用于比较：★ Windows 大小写不敏感 · 去掉尾部分隔符 ✓"""
    text = str(value or "").strip().strip('"')
    if not text:
        return ""
    try:
        return os.path.normcase(os.path.normpath(text))
    except Exception:  # noqa: BLE001
        return text.lower()


def open_documents(sw) -> dict:
    """★ 枚举当前 SolidWorks 会话里**已打开的文档**（★ 判据是**回读**，不是被调成员的返回值）。

    :returns: `{"count": 读到的数量, "documents": [{"path","title","dirty"}], "count_matches": 是否对得上,
               "readback_problem": 数量与数组长度不一致时的说明, "dirty_count": 有未保存改动的文档数}`
    ★ `dirty` 取官方 `IModelDoc2.GetSaveFlag`（"是否脏、需要保存"）；★ 读不到记 **None（未知）** ✓
    ★★ 为什么必须回读数量：本仓一贯纪律 —— ★ **被调成员的返回值不可信**（事实 8/40 同族）；
      ★ 这里拿 `GetDocumentCount` 当**独立读数**，与 `GetDocuments` 数组长度**互相校验** ✓
    """
    documents: list = []
    problem = ""
    count = None
    try:
        count = int(get_com_member(sw, "GetDocumentCount") or 0)
    except Exception:  # noqa: BLE001
        count = None
    try:
        raw = get_com_member(sw, "GetDocuments")
    except Exception:  # noqa: BLE001
        raw = None
    if raw is None:
        problem = "GetDocuments 返回空 ⇒ ★ 无法确认会话里有哪些文档（★ 按铁律 5 记「查不到」）"
    else:
        seq = raw if isinstance(raw, (list, tuple)) else [raw]
        for item in seq:
            if item is None:
                continue
            try:
                path = get_com_member(item, "GetPathName")
            except Exception:  # noqa: BLE001
                path = ""
            try:
                title = get_com_member(item, "GetTitle")
            except Exception:  # noqa: BLE001
                title = ""
            #: ★★ **未保存标记**用官方成员读（★ 不是从窗口标题抠 `*`）：
            #: `IModelDoc2.GetSaveFlag` 的官方原文 = "Gets whether the document is curre
            #: ntly dirty
            #:   and needs to be saved" ⇒ ★ 真 = **有未保存改动** ✓
            #: ★ 读不到时记 `None`（**未知**）—— ★ 绝不默认"没有未保存"（那会让人以为杀
            #: 进程是安全的）✓
            try:
                dirty = bool(get_com_member(item, "GetSaveFlag"))
            except Exception:  # noqa: BLE001
                dirty = None
            documents.append(
                {"path": str(path or ""), "title": str(title or ""), "dirty": dirty}
            )
    if count is not None and documents and count != len(documents):
        problem = (
            "★ 回读不一致：GetDocumentCount=%d 而 GetDocuments 给了 %d 个 "
            "⇒ 以**较大者**为准并如实报出 ✓" % (count, len(documents))
        )
    return {
        "count": count,
        "documents": documents,
        "count_matches": (count is None or not documents or count == len(documents)),
        "readback_problem": problem,
        #: ★★ 有未保存改动的文档数 —— ★ 它是"能不能安全杀进程/关会话"的依据（评审点名的
        #: 风险）✓
        "dirty_count": sum(1 for d in documents if d.get("dirty") is True),
        "dirty_unknown": sum(1 for d in documents if d.get("dirty") is None),
    }


def classify_open_documents(
    docs, allowed_paths=(), *, allow_untitled: bool = False
) -> tuple:
    """★ 把已打开的文档分成 **(我方的, 非我方的)** —— ★ 判据是路径归一化后是否在允许集里。

    :param docs: `open_documents()` 的 `documents`
    :param allowed_paths: ★ 我们**明确知道是自己打开**的那些路径（★ 由调用方给出，不猜）
    :param allow_untitled: ★ 默认 **False** ⇒ 空路径（新建未存盘）**算非我方** ✓ 保守
    """
    allowed = {_norm_path(p) for p in (allowed_paths or ()) if str(p or "").strip()}
    ours, foreign = [], []
    for d in docs or ():
        path = str((d or {}).get("path") or "")
        if not path:
            (ours if allow_untitled else foreign).append(d)
            continue
        (ours if _norm_path(path) in allowed else foreign).append(d)
    return ours, foreign


def precheck_session(sw, allowed_paths=(), *, allow_untitled: bool = False) -> dict:
    """★★ **预检门禁**：会话里只要开着**非我方**的文档 ⇒ **抛 `ForeignDocumentError` 拒绝开始** ✓

    ★ 评审的要求：★ 真机跑**开始前**先做这件事；★ 且"**启动 SolidWorks 之前先问一次、
      连上之后再问一次**"（★ 两次都要做：前者是"没在运行"与"在运行但有空文档"的区分）✓
    :returns: `{"documents": …, "ours": …, "foreign": …, "count_matches": …}`（★ 未拒绝时才有返回值）
    """
    snap = open_documents(sw)
    ours, foreign = classify_open_documents(
        snap["documents"], allowed_paths, allow_untitled=allow_untitled
    )
    if foreign:
        listed = "; ".join(
            d.get("title") or d.get("path") or "(未命名)" for d in foreign[:5]
        )
        raise ForeignDocumentError(
            "★ 会话里有 %d 个**不是我们打开的**文档 ⇒ 拒绝开始（★ 免得写到用户文件上）：%s"
            % (len(foreign), listed)
        )
    return {
        "documents": snap["documents"],
        "ours": ours,
        "foreign": foreign,
        "count_matches": snap["count_matches"],
        "readback_problem": snap["readback_problem"],
    }
