"""SolidWorks 文档打开兼容路径测试。"""
from pathlib import Path

from scripts import sw_connect


class FakeModel:
    """@brief 最小文档对象。"""


def test_open_document_reuses_existing_model(tmp_path):
    """@brief 装配体已加载组件时不重复调用 OpenDoc6。"""
    source = tmp_path / "part.sldprt"
    source.write_bytes(b"part")
    expected = FakeModel()

    class FakeSolidWorks:
        def GetOpenDocumentByName(self, path):
            assert Path(path) == source.resolve()
            return expected

        def OpenDoc6(self, *_args):
            raise AssertionError("不应重复打开已加载文档")

    assert sw_connect.open_document(FakeSolidWorks(), source) is expected


def test_open_document_falls_back_to_dynamic_proxy(tmp_path, monkeypatch):
    """@brief makepy 拒绝 by-ref VARIANT 时使用动态代理。"""
    source = tmp_path / "part.sldprt"
    source.write_bytes(b"part")
    expected = FakeModel()

    class GeneratedSolidWorks:
        _oleobj_ = object()

        def GetOpenDocumentByName(self, _path):
            return None

        def OpenDoc6(self, *_args):
            raise TypeError("int() argument must not be VARIANT")

    class DynamicSolidWorks:
        def OpenDoc6(self, _path, _doc_type, _options, _configuration, errors, warnings):
            errors.value = 0
            warnings.value = 0
            return expected

    monkeypatch.setattr(
        sw_connect.win32com_client.dynamic,
        "DumbDispatch",
        lambda ole_object, _name: DynamicSolidWorks() if ole_object is GeneratedSolidWorks._oleobj_ else None,
    )

    assert sw_connect.open_document(GeneratedSolidWorks(), source, silent=True) is expected


def test_step_import_falls_back_to_dynamic_loadfile4(tmp_path, monkeypatch):
    """@brief SW2026 LoadFile4 的 by-ref VARIANT 失败时也必须切换动态代理。"""
    source = tmp_path / "complex.step"
    source.write_bytes(b"ISO-10303-21")
    expected = FakeModel()
    import_data = object()

    class GeneratedSolidWorks:
        _oleobj_ = object()

        def GetOpenDocumentByName(self, _path):
            return None

        def GetImportFileData(self, _path):
            return import_data

        def LoadFile4(self, *_args):
            raise TypeError("int() argument must not be VARIANT")

    class DynamicSolidWorks:
        def LoadFile4(self, path, argument, data, errors):
            assert Path(path) == source.resolve()
            assert argument == "r"
            assert data is import_data
            errors.value = 0
            return expected

    #: ★★ 2026-10-07（接手轮 · 规格 214 T-214-09）**桩要跟着真契约走** ——
    #:   ★ 原桩写的是 `lambda _sw: True`，★ 而 `ensure_default_templates` 的真契约是
    #:     **回一个 dict**：`{"templates": {...}, "restore": [...]}`（`scripts/sw_connect.py:884`）✓
    #:   ★★ 后果：`open_document` 拿到它之后会转交给 `restore_default_templates(sw, info)`（L1083），
    #:     而那句是 `info.get("restore")` ⇒ ★ 传 `True` 就 `AttributeError: 'bool' object has no attribute 'get'` ✗
    #:   ⇒ ★ **本测试报的错**（"LoadFile4 回退失败"）**与它要验的东西无关** —— ★ 它是在桩上炸的 ✓
    #:   ⚠ 为什么以前是绿的：`restore_default_templates` 是**后来**才接进 `open_document` 的
    #:     （事实 525：写全局用户偏好必须还原）⇒ ★ 那一步一加，这个**说谎的桩**就变成致命 ✗
    #:   ★ 修法：★ 让桩**按真契约**回 dict —— ★ **不**给 `restore_default_templates` 加容错
    #:     （★ 契约违约就该**响亮报错**；★ 本仓既有纪律：假对象要按真实接口分布暴露缺项）✓
    monkeypatch.setattr(sw_connect, "ensure_default_templates",
                        lambda _sw: {"templates": {}, "restore": []})
    monkeypatch.setattr(
        sw_connect.win32com_client.dynamic,
        "DumbDispatch",
        lambda ole_object, _name: DynamicSolidWorks()
        if ole_object is GeneratedSolidWorks._oleobj_
        else None,
    )

    assert sw_connect.open_document(GeneratedSolidWorks(), source) is expected
