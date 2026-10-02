"""
SolidWorks 友好会话 API

本模块在底层 COM helper 之上提供更顺手的门面接口，适合脚本和 AI 代理快速组合
“打开/新建/保存/导出/关闭”等常见流程。底层函数仍保留在 sw_connect.py、
sw_part.py、sw_export.py 等模块中，便于精细控制。
"""
from pathlib import Path
import os

try:
    from .sw_connect import close_owned_solidworks, connect_solidworks, get_com_member, new_document, open_document, save_document
    from .sw_export import export_to_dxf, export_to_iges, export_to_pdf, export_to_stl, export_to_step
except ImportError:
    from sw_connect import close_owned_solidworks, connect_solidworks, get_com_member, new_document, open_document, save_document
    from sw_export import export_to_dxf, export_to_iges, export_to_pdf, export_to_stl, export_to_step


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
        self.model = new_document(self.sw, doc_type=doc_type, template_path=template_path)
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
    return SolidWorksSession(version=version, wait_seconds=wait_seconds, visible=visible)

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


# ── objective② / 四家缺口 `undo`：**撤销（`IModelDoc2.EditUndo2`）** ─────────────────────
# ★★★★ 2026-10-03（轮 395）**补 `undo`** —— objective② 三层证据判它是**真缺**（事实 311），
#   而官方入口明确：`C:\swapi\types\IModelDoc2\EditUndo2.md`
#   ```
#   void EditUndo2(int Steps)   —— 「Undoes the specified number of actions in the active
#                                    SOLIDWORKS Design session」
#   · EditUndo(uint NSteps)  **Obsolete**（★ 后继是 EditUndo2）· SketchUndo() 零参（★ 撤最后一条草图画线）
#   ```
# ★★ **为什么它对自动化 agent 特别有用**：★ 我们的工具会**改模型**；★ 一旦某一步改错，
#   ★ **没有撤销就意味着只能重来**（★ 或留下脏状态）。★ 它是**我们自己的改动**的回退手段。
# ★ 规则 2 / 6：★ 对外只暴露 `steps`（★ 个数，★ 不是长度 ⇒ 无单位）；★ 它回 **`void`**
#   ⇒ ★★ 判据**不能是返回值**，只能是「**特征树退回了**」（★ 建完/撤完都要回读）。
# ★ ⚠ **边界**：★ `EditUndo2` 撤的是「**会话里的动作**」—— ★ 它**不区分**是不是我们做的
#   ⇒ ★ 所以本工具**只该在我们自己的改动之后调用**（★ 调用方负责；★ 这是**使用纪律**，不是本函数能强制的）。


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
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "stage": "read_before", "error": str(exc)[:120]}
    before = len(before_names)
    try:
        get_com_member(model, "EditUndo2", n)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "stage": "call", "steps": n,
                "error": "%s: %s" % (type(exc).__name__, str(exc)[:200])}
    try:
        after_names = feature_names(model)
    except Exception as exc:                                   # noqa: BLE001
        return {"ok": False, "stage": "read_after", "steps": n, "error": str(exc)[:120]}
    after = len(after_names)
    gone = [x for x in before_names if x not in after_names]
    return {"ok": after < before, "steps": n, "tree_before": before, "tree_after": after,
            "removed_features": gone[-4:], "undone": after < before,
            "★": "它回 void ⇒ 判据是**特征树真的退回了**（★ 规则 6）；"
                 "★ 官方 1 参 · 反射 arity 1 · `EditUndo` 已 Obsolete"}
