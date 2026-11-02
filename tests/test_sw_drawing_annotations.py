"""sw_drawing_annotations 的离线契约测试（假 COM，不连接 SolidWorks）。

被测对象：`scripts/sw_drawing_annotations.py`
定位：补 `capabilities.yaml` 的 `drawing_dimension_insertion` 工具层缺口的回归保护。
判据来源：`C:\\swapi\\types\\IDrawingDoc\\InsertModelAnnotations4.md`（8 参 / 返回
    IAnnotation 数组 / AllViews 语义）· `InsertModelDimensions.md`（void，1 参）·
    `examples/Insert_Model_Annotations_Example_CSharp.md`（调用序）。
"""

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（本任务新增的测试）
# 文件:   tests/test_sw_drawing_annotations.py —— 本文件自身
# 定位:   ① 钉死 8 参/6 参/1 参三个成员的**实参布局与顺序**；
#         ② 钉死「返回空 + 回读无增量 ⇒ ok=False」（不许把 None 当成功）；
#         ③ 钉死「回读读不到 ⇒ delta=None 且 ok=False」（不许把未知当 0）。
# 官方依据: 上述三份 C:\swapi 文档
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   scripts/sw_drawing_annotations.py 全文件
# ⚠ 假 COM，未在本机实测（见 AGENTS.md 铁律 2）
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import importlib.util
import sys
import types
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = REPO_ROOT / "scripts" / "sw_drawing_annotations.py"


class FakeCall:
    """记录每次 call_com_member 的 (成员名, 实参)，并返回预设值。"""

    def __init__(self) -> None:
        self.seen: list[tuple[str, tuple]] = []
        self.returns: dict[str, object] = {}
        self.raises: dict[str, Exception] = {}

    def _dispatch(self, obj, name, *args):
        self.seen.append((name, args))
        if name in self.raises:
            raise self.raises[name]
        #: ★ 视图标注计数直接按对象属性回答（不靠重装 self._dispatch ——
        #:   模块在 load 时捕获的是**当时的绑定方法**，事后再赋值改不到它）
        if name == "GetAnnotationCount":
            return getattr(obj, "annotations")
        if name in self.returns:
            value = self.returns[name]
            return value(*args) if callable(value) else value
        return None

    def names(self) -> list[str]:
        return [name for name, _ in self.seen]


def _load(fake: FakeCall):
    """装载被测模块，并把 sw_connect 的取/调两个入口换成假件。"""
    connect = types.ModuleType("sw_connect")
    connect.get_com_member = fake._dispatch
    connect.call_com_member = fake._dispatch
    connect.set_com_member = lambda obj, name, value, *a, **k: setattr(obj, name, value)
    sys.modules["sw_connect"] = connect
    spec = importlib.util.spec_from_file_location("sw_drawing_annotations", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules["sw_drawing_annotations"] = module
    spec.loader.exec_module(module)
    return module


class FakeView:
    """一个视图替身，只带标注计数。"""

    def __init__(self, annotations: int) -> None:
        self.annotations = annotations


class FakeDrawing:
    """图纸替身：GetCurrentSheet → GetViews → 各视图。"""

    def __init__(self, views: list[FakeView]) -> None:
        self.views = views


def _wire_views(fake: FakeCall, views: list[FakeView]) -> None:
    """让 GetCurrentSheet / GetViews / GetAnnotationCount 走假件。"""
    sheet = object()
    fake.returns["GetCurrentSheet"] = sheet
    fake.returns["GetViews"] = lambda: views

    return sheet


def test_signature_is_official_eight_args():
    """① 8 参布局与顺序必须与官方一致：Option / Types / AllViews / 其余五个 False。"""
    fake = FakeCall()
    module = _load(fake)
    _wire_views(fake, [FakeView(0)])
    fake.returns["InsertModelAnnotations4"] = [object(), object()]

    report = module.insert_model_annotations_report(FakeDrawing([FakeView(0)]), all_views=True)

    assert report["member_used"] == "InsertModelAnnotations4"
    assert report["args"] == [0, 32768, True, False, False, False, False, False], report["args"]
    assert report["inserted_returned"] == 2
    assert report["ok"] is True


def test_all_views_false_is_passed_through():
    """①b AllViews=False 必须真的传下去（只插选中视图）。"""
    fake = FakeCall()
    module = _load(fake)
    _wire_views(fake, [FakeView(0)])
    fake.returns["InsertModelAnnotations4"] = [object()]
    report = module.insert_model_annotations_report(FakeDrawing([FakeView(0)]), all_views=False)
    assert report["args"][2] is False


def test_empty_return_and_no_delta_is_failure():
    """② 返回空 + 回读无增量 ⇒ ok=False（这正是本轮真机遇到的情形，不许美化）。"""
    fake = FakeCall()
    module = _load(fake)
    _wire_views(fake, [FakeView(3)])
    fake.returns["InsertModelAnnotations4"] = []
    report = module.insert_model_annotations_report(FakeDrawing([FakeView(3)]))
    assert report["ok"] is False
    assert report["delta"] == 0
    assert "没有产出非空插入" in " ".join(report["notes"])


def test_unreadable_readback_is_unknown_not_zero():
    """③ 回读读不到 ⇒ delta=None 且 ok=False（不许把未知当 0，也不许当成功）。"""
    fake = FakeCall()
    module = _load(fake)
    fake.raises["GetCurrentSheet"] = RuntimeError("no sheet")
    fake.returns["InsertModelAnnotations4"] = []
    report = module.insert_model_annotations_report(FakeDrawing([]))
    assert report["annotations_before"] is None
    assert report["delta"] is None
    assert report["ok"] is False


def test_fallback_chain_order():
    """④ 4 缺 → 3 缺 → 退回 void 的 InsertModelDimensions(0)。"""
    fake = FakeCall()
    module = _load(fake)
    _wire_views(fake, [FakeView(0)])
    fake.raises["InsertModelAnnotations4"] = AttributeError("no 4")
    fake.raises["InsertModelAnnotations3"] = AttributeError("no 3")
    fake.returns["InsertModelDimensions"] = None
    report = module.insert_model_annotations_report(FakeDrawing([FakeView(0)]))
    assert report["member_used"] == "InsertModelDimensions"
    assert report["args"] == [0]
    assert any("InsertModelAnnotations4" in e for e in report.get("call_errors", []))


def test_all_members_fail_reports_no_member():
    """⑤ 三个成员都调不通 ⇒ stage=no_member，不许降级成「大概插上了」。"""
    fake = FakeCall()
    module = _load(fake)
    _wire_views(fake, [FakeView(0)])
    for name in ("InsertModelAnnotations4", "InsertModelAnnotations3", "InsertModelDimensions"):
        fake.raises[name] = AttributeError(f"no {name}")
    report = module.insert_model_annotations_report(FakeDrawing([FakeView(0)]))
    assert report["stage"] == "no_member"
    assert report["ok"] is False


def test_view_activation_follows_official_order():
    """⑥ 传了 view_name ⇒ 先 SelectByID2 再 ActivateView 再 ClearSelection2（官方示例序）。"""
    fake = FakeCall()
    module = _load(fake)
    _wire_views(fake, [FakeView(0)])
    fake.returns["Extension"] = object()
    fake.returns["SelectByID2"] = True
    fake.returns["ActivateView"] = True
    fake.returns["InsertModelAnnotations4"] = [object()]
    report = module.insert_model_annotations_report(
        FakeDrawing([FakeView(0)]), view_name="Drawing View1"
    )
    names = fake.names()
    assert "SelectByID2" in names and "ActivateView" in names and "ClearSelection2" in names
    assert names.index("SelectByID2") < names.index("ActivateView")
    assert report["member_used"] == "InsertModelAnnotations4"
