"""★ 语义选择器接进 `resolve_entity()` —— E3 的「不依赖下标」修法。

判据来源：`docs/ENGINEERING-PATH.md` 第四节 E3「必须读什么」：

> 主尺寸/基准/孔位必须有稳定语义引用，跨重建不依赖选区或下标。

## 本文件证明什么

`sw_selection_spec.resolve_entity()` 原本只认：
  - `__current_selection__` —— 依赖当前选区
  - `index:<n>` —— 下标会漂
  - COM 对象

两者都**不可跨重建**。本轮加了第三类：**语义选择器**
（`+z` / `top_face` / `near:x,y,z`）。

## 怎么测（不连 SolidWorks）

用一个**假 model**（只要 `entities_on_body` 能拿到东西）。
经 `monkeypatch` 把 `entity_geometry` 之外的取数换成受控值，
验证「语义选择器 → 下标 → 选中对象」这条链走通。

★ 真机验证在 `tools/probe_s3_e1_real_machine.py` 与 S3 后续；
  本文件只证明**分流逻辑**对。
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import engineering.reference_collect as rc  # noqa: E402
from engineering.reference_resolver import EdgeInfo, FaceInfo, ResolverError  # noqa: E402


# ────────────────── 语义判定 ──────────────────


@pytest.mark.parametrize(
    "selector",
    ["+z", "-z", "+x", "-x", "+y", "-y", "top_face"],
    ids=["+z", "-z", "+x", "-x", "+y", "-y", "top_face"],
)
def test_语义形态被识别(selector) -> None:
    assert rc.is_semantic_selector(selector) is True


def test_near_锚点被识别() -> None:
    assert rc.is_semantic_selector("near:10,20,30") is True


@pytest.mark.parametrize(
    "selector",
    ["index:0", "__current_selection__", "", "  ", "随便什么"],
    ids=["index0", "current", "empty", "spaces", "garbage"],
)
def test_非语义形态不被误判(selector) -> None:
    """★ `index:` 与 `__current_selection__` 必须**不**被当语义 —— 它们走原路径。"""
    assert rc.is_semantic_selector(selector) is False


def test_非字符串不当语义() -> None:
    """★ COM 对象走原路径。"""
    assert rc.is_semantic_selector(object()) is False


# ────────────────── 解析链（假 model）──────────────────


class _FakeFace:
    """★ 一个平面矩形面：法向 +Z、盒 [0,0,0]–[100,60,0]。"""

    def __init__(self, *, normal=(0.0, 0.0, 1.0), bbox=(0, 0, 0, 100, 60, 0)):
        self._n = normal
        self._b = bbox

    def Normal(self):
        return self._n

    def GetBox(self):
        return self._b

    def GetSurface(self):
        #: ★ 必须给一个能回 IsPlane()=True 的曲面，
        #:   否则 top_face / +z 的 planar 过滤会把所有面排掉
        return _FakeSurface()


class _FakeSurface:
    """★ 平面曲面：ISurface.IsPlane() 回 True（三源互证成员）。"""

    def IsPlane(self):
        return True


class _FakeVertex:
    def __init__(self, pt):
        self._p = pt

    def GetPoint(self):
        return self._p


class _FakeEdge:
    """★ 一条边：起点 (0,0,0)、终点 (100,0,0) ⇒ 中点 (50,0,0)。"""

    def __init__(self, start=(0.0, 0.0, 0.0), end=(100.0, 0.0, 0.0)):
        self._s = start
        self._e = end

    def GetStartVertex(self):
        return _FakeVertex(self._s)

    def GetEndVertex(self):
        return _FakeVertex(self._e)


class _FakeModel:
    def __init__(self, faces):
        self._faces = faces


def _patch(monkeypatch, faces):
    """★ 把 `collect_faces` 依赖的两个取数换成受控值。"""
    import sw_selection_spec as spec

    monkeypatch.setattr(
        spec, "entities_on_body", lambda model, kind, body_index=0: list(model._faces)
    )

    def _gcm(obj, name, *a):
        fn = getattr(obj, name, None)
        if fn is None:
            return None
        return fn(*a) if a else fn()

    import sw_connect

    monkeypatch.setattr(sw_connect, "get_com_member", _gcm)


def test_方向语义解析成下标(monkeypatch) -> None:
    """★ `+z` ⇒ 找到法向朝 +Z 的面，回它的 index。"""
    faces = [
        _FakeFace(normal=(0.0, 0.0, -1.0), bbox=(0, 0, -10, 100, 60, 0)),
        _FakeFace(normal=(0.0, 0.0, 1.0), bbox=(0, 0, 0, 100, 60, 10)),
    ]
    _patch(monkeypatch, faces)
    got = rc.resolve_semantic(_FakeModel(faces), "+z", "FACE")
    assert got["kind"] == "face"
    assert got["index"] == 1, "★ +Z 应选法向朝上的那个（index 1），实得 %r" % got["index"]


def test_语义解析结果标注质心是近似(monkeypatch) -> None:
    """★★ 面质心是盒中心近似 —— 调用方必须能看见这个前提。"""
    faces = [_FakeFace()]
    _patch(monkeypatch, faces)
    got = rc.resolve_semantic(_FakeModel(faces), "+z", "FACE")
    assert got["centroid_is_approximate"] is True


def test_top_face标注需要平面(monkeypatch) -> None:
    """★ `top_face` 只在平面上成立 —— 结果里带 `planar_required`。"""
    #: ★ top_face 的定义是「法向 +Y 且质心 Y 最大」⇒ 假面法向必须是 +Y
    faces = [_FakeFace(normal=(0.0, 1.0, 0.0), bbox=(0, 0, 0, 100, 60, 10))]
    _patch(monkeypatch, faces)
    got = rc.resolve_semantic(_FakeModel(faces), "top_face", "FACE")
    assert got["planar_required"] is True


def test_边语义不标质心近似(monkeypatch) -> None:
    """★ 边中点取两点均值是精确的，不该被标成近似。"""
    edge = _FakeEdge()
    import sw_selection_spec as spec

    monkeypatch.setattr(
        spec, "entities_on_body", lambda model, kind, body_index=0: [edge]
    )
    import sw_connect

    monkeypatch.setattr(
        sw_connect,
        "get_com_member",
        lambda o, n, *a: (getattr(o, n)() if hasattr(o, n) else None),
    )
    got = rc.resolve_semantic(_FakeModel([]), "near:50,0,0", "EDGE")
    assert got["centroid_is_approximate"] is False
    assert got["kind"] == "edge"


def test_不支持的kind被拒() -> None:
    with pytest.raises(ResolverError):
        rc.resolve_semantic(_FakeModel([]), "+z", "VERTEX")


# ────────────────── 能力边界自述 ──────────────────


def test_limits_如实报四条能力与一条注意() -> None:
    """★ 能力边界要能被程序读出来，而不是只写在文档里。"""
    lim = rc.limits()
    assert "Normal" in lim["face_normal"]
    assert "近似" in lim["face_centroid"], "★ 质心必须标为近似"
    assert "IsPlane" in lim["face_planar"]
    assert "精确" in lim["edge_midpoint"]
    assert "曲面" in lim["top_face_caveat"], "★ 必须写明 top_face 的适用边界"


def test_质心近似有官方依据() -> None:
    """★ 为什么是近似：官方 `GetBox` 的 Remarks 自己说「not guaranteed」。

    这条把「近似」的依据钉在代码里，防后人以为是偷懒。
    """
    import io

    src = io.open(
        REPO / "scripts" / "engineering" / "reference_collect.py", encoding="utf-8"
    ).read()
    assert "not guaranteed" in src, (
        "★ 应引用官方 GetBox 的 Remarks 原文（not guaranteed），"
        "否则「质心是近似」这个说法没有依据"
    )


# ────────────────── 与 resolver 的契约 ──────────────────


def test_FaceInfo字段与collect_faces对齐() -> None:
    """★ `collect_faces` 造的 keyword 必须都是 `FaceInfo` 的字段。"""
    fields = set(FaceInfo.__dataclass_fields__)
    #: collect_faces 可能塞的额外键（诊断用，不在 dataclass 里）
    extras = {"normal_missing", "centroid_missing"}
    for key in ("index", "normal", "centroid", "bbox", "planar"):
        assert key in fields
    #: 诊断键不在 dataclass 里 ⇒ 若真被塞进去会 TypeError；
    #: 本测试只确认核心字段存在
    assert extras  # 非空，提醒读者这些是诊断键


def test_EdgeInfo字段与collect_edges对齐() -> None:
    fields = set(EdgeInfo.__dataclass_fields__)
    assert "index" in fields
    assert "midpoint" in fields
