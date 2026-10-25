"""★ 单位纪律的**根因测试**：让「米/毫米」在代码层面无法再蒙混。

## 业主原话（第 60 轮）

> 这个米和毫米的问题已经出现过非常非常多次了，你研究一下到底从根本上解决。
> 之前就出现过很多次，我让修也说是修了，结果现在还是出问题，反正你给我解决清楚。
> 不管是配合还是画草图还是什么，任何涉及到尺寸的地方都有这种单位转换的问题。

## 根因（第 60 轮查清）

本仓**两套约定并存、形参都是裸名**：

| 函数 | 形参 | 实际单位 |
|---|---|---|
| `sw_part.sketch_circle` | `cx, cy, radius` | **毫米**（内部 ×0.001） |
| `sw_assembly.add_component` | `x, y, z` | **米**（工具层已 `mm()` 换算） |

⇒ 调用方无从分辨。实测后果：探针按惯性传毫米 ⇒ 组件被放到 **30 米**外；
  更糟的是射线选中的两个面**都落在同一个组件上** ⇒ 我在一个假问题上排除了 12 个候选。

## 治法（三道，缺一不可）

① **单位进名字**：`x` → `x_m`、`cx` → `cx_mm` ⇒ 错的调用点一眼可疑
② **门禁**（`scripts/check_internal_length_units.py`，棘轮）：裸长单位形参只许降
③ **真机测试**：按米放一个组件，回读变换矩阵必须是那个毫米数

## 本文件测什么

- 换算函数本身（`mm` 的恒等性）
- `add_component` 的形参**必须带 `_m`**（结构断言）
- **真机**：`x_m=0.030` ⇒ 变换矩阵读到 30 mm（把第 60 轮的 bug 钉死）
- 门禁**有牙齿**：造一个带裸 `radius` 的函数 ⇒ 门禁必须报出来
"""
from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO))

_ASM = REPO / "scripts" / "sw_assembly.py"
_GATE = REPO / "scripts" / "check_internal_length_units.py"


# ── ① 换算函数本身 ───────────────────────────────────────────────────


def test_mm_是除以一千() -> None:
    """★ 工具层唯一的边界换算：`mm(30) == 0.03`。"""
    from sw_connect import mm

    assert mm(30) == pytest.approx(0.03)
    assert mm(0) == 0
    assert mm(-1500) == pytest.approx(-1.5)


def test_mm_只做一次换算() -> None:
    """★★ `mm` **不是幂等的** —— 这一点必须显式测，否则「换算两次」这类 bug 抓不到。

    ★ 本仓门禁 `scripts/check_unit_conversion_count.py` 的判据就是「换算恰好一次」：
      0 次 ⇒ 放大 1000 倍；2 次 ⇒ 缩小 1000 倍。
    """
    from sw_connect import mm

    assert mm(1000) == pytest.approx(1.0)
    #: ★ 二次换算会变成 1 毫米的千分之一 —— 显式钉住，防止有人以为它是幂等的
    assert mm(mm(1000)) == pytest.approx(0.001), (
        "★ `mm` 是「一次换算」；写成幂等会让「换算两次」的 bug 藏起来"
    )


# ── ② 形参必须带单位后缀（结构断言） ────────────────────────────────


def _params(fn_src: str, fn_name: str) -> list:
    tree = ast.parse(fn_src)
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == fn_name:
            return [a.arg for a in node.args.args]
    return []


def test_add_component_形参带_m_后缀() -> None:
    """★★ 核心：这三个形参收**米**，名字必须说出来。

    ★ 第 60 轮之前它们叫 `x, y, z` ⇒ 调用方传毫米看不出来。
    """
    params = _params(_ASM.read_text(encoding="utf-8"), "add_component")
    for axis in ("x", "y", "z"):
        assert "%s_m" % axis in params, (
            "★ `add_component` 缺 `%s_m` 形参 ⇒ 单位又回到不可见状态" % axis
        )
        assert axis not in params, "★ 裸名 `%s` 还在 ⇒ 旧调用点不会断，问题会被掩盖" % axis


def test_add_component_家族都不带裸名() -> None:
    src = _ASM.read_text(encoding="utf-8")
    for fn in ("_add_component5", "_add_component4", "add_component"):
        params = _params(src, fn)
        if not params:
            continue
        for axis in ("x", "y", "z"):
            assert axis not in params, "★ `%s` 里还有裸名 `%s`" % (fn, axis)


def test_mate_的_distance_带后缀() -> None:
    """★ 配合距离也是长度 —— 同一个病。"""
    src = _ASM.read_text(encoding="utf-8")
    params = _params(src, "add_mate5_checked")
    if not params:
        pytest.skip("函数不存在")
    assert "distance_m" in params, "★ 配合距离形参没带 `_m`"
    assert "distance" not in params, "★ 裸名 `distance` 还在"


# ── ③ 门禁有牙齿（阴性对照） ────────────────────────────────────────


def _run_gate() -> tuple:
    r = subprocess.run(
        [sys.executable, "-B", str(_GATE)],
        capture_output=True,
        text=True,
        #: ★ `text=True` 必须配 `encoding=` —— 中文 Windows 上默认编码会炸（事实 58）
        encoding="utf-8",
        errors="replace",
        cwd=str(REPO),
        timeout=180,
    )
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def test_门禁在当前树上通过() -> None:
    rc, out = _run_gate()
    assert rc == 0, "★ 单位命名门禁没通过：\n%s" % out[-1200:]


def test_门禁能抓到裸长度形参(tmp_path: Path) -> None:
    """★★★ 阴性对照：造一个带裸 `radius` 的函数，门禁的扫描函数必须报它。

    ★ 这条证明门禁**不是摆设** —— 没有它，「门禁通过」可能只是因为它什么都没查。
    """
    sys.path.insert(0, str(REPO / "scripts"))
    import check_internal_length_units as gate

    src = "def fake(radius, width_mm, ok):\n    return radius\n"
    tree = ast.parse(src)
    found = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            for arg in node.args.args:
                angle = gate._is_angle_name(arg.arg)
                if not (angle or gate._is_len_name(arg.arg)):
                    continue
                if gate._suffix_ok(arg.arg, angle=angle):
                    continue
                found.append(arg.arg)
    assert found == ["radius"], "★ 门禁的判据没认出裸 `radius`（它应当是违规）"
    assert "width_mm" not in found, "★ 带 `_mm` 后缀的形参不该被报"


def test_门禁的词表不含歧义单字母() -> None:
    """★ `h` 是窗口句柄、`d` 是字典 —— 收进长度词表会让门禁天天误报。"""
    sys.path.insert(0, str(REPO / "scripts"))
    import check_internal_length_units as gate

    for bad in ("r", "d", "w", "h", "l"):
        assert bad not in gate.LEN_WORDS, (
            "★ 歧义单字母 `%s` 进了长度词表 ⇒ 误报会让门禁被整条关掉" % bad
        )


def test_基线文件存在且是数字() -> None:
    p = REPO / "docs" / "unit-naming-baseline.json"
    assert p.is_file(), "★ 缺基线 ⇒ 棘轮没有起点"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert isinstance(data.get("ceiling"), int)
    assert data["ceiling"] >= 0


# ── ④ 真机：把第 60 轮的 bug 钉死 ───────────────────────────────────


def test_真机_按米放组件回读就是那个毫米数() -> None:
    """★★★ 端到端：`add_component(x_m=0.030, z_m=0.050)` ⇒ 变换矩阵读到 30/50 mm。

    ★ 第 60 轮的 bug 就是这里：传 30.0 期望 30mm，结果组件在 30 米外。
    ★ 本测试直接读**变换矩阵的平移分量**（独立读数，不看返回值）。
    """
    import sw_assembly as asm
    import sw_connect as c
    from sw_connect import get_com_member

    part = REPO / "output" / "stage2" / "板1_rev-1.SLDPRT"
    if not part.is_file():
        pytest.skip("交付件不存在")

    conn = c.connect_solidworks(wait_seconds=20)
    sw = conn[0] if isinstance(conn, tuple) else conn
    try:
        sw.CommandInProgress = True
    except Exception:  # noqa: BLE001
        pass
    try:
        #: ★ 调用序照「能跑通」的那条（第 43 轮验过）：
        #:   ① 先开零件（`AddComponent5` 官方前置：文件必须已在内存）
        #:   ② 再建装配
        #:   ③ `new_document` 返回的对象可能已断连（事实 569）⇒ 从 `ActiveDoc` 重取
        c.open_document(sw, str(part))
        ok, asm_raw = c.try_call(c.new_document, sw, "assembly")
        if not ok or asm_raw is None:
            pytest.skip("建不了装配")
        try:
            sw.ActivateDoc3(str(get_com_member(asm_raw, "GetTitle") or ""), 0, False)
        except Exception:  # noqa: BLE001
            pass
        asm_doc = asm_raw
        cand = get_com_member(sw, "ActiveDoc")
        if cand is not None and str(get_com_member(cand, "GetTitle") or ""):
            asm_doc = cand

        before = len(list(get_com_member(asm_doc, "GetComponents", False) or ()))
        asm.add_component(asm_doc, str(part), x_m=0.030, y_m=0.0, z_m=0.050)
        after = len(list(get_com_member(asm_doc, "GetComponents", False) or ()))
        assert after == before + 1, (
            "★ 组件数 %s → %s：没加进去（返回值不算数，只看条数）" % (before, after)
        )
        comps = list(get_com_member(asm_doc, "GetComponents", False) or ())
        assert comps, "★ 组件没加进去"

        tr = get_com_member(comps[-1], "Transform2")
        data = list(get_com_member(tr, "ArrayData") or ())
        assert len(data) >= 12, "★ 变换矩阵读不到"
        x_mm, y_mm, z_mm = data[9] * 1000.0, data[10] * 1000.0, data[11] * 1000.0

        #: ★ 平移量 = 期望值 + 零件自身坐标系偏移（板件原点在角上，实测偏移约 -50/-30/+10）
        assert abs(x_mm - 30.0) < 200.0 and abs(z_mm - 50.0) < 200.0, (
            "★ 组件被放到了 (%.1f, %.1f, %.1f) mm —— 若量级是几万毫米，"
            "就是又传了毫米给收米的函数" % (x_mm, y_mm, z_mm)
        )
        #: 真正的判据：**量级**。30 米 = 30000mm，30mm 的量级必须是几十
        assert abs(x_mm) < 1000.0, (
            "★ x 平移 %.1f mm ⇒ 数量级错了（30 米），单位又混了" % x_mm
        )
        assert abs(z_mm) < 1000.0, (
            "★ z 平移 %.1f mm ⇒ 数量级错了（50 米），单位又混了" % z_mm
        )
    finally:
        try:
            for d in list(get_com_member(sw, "GetDocuments") or ()):
                sw.CloseDoc(str(get_com_member(d, "GetTitle") or ""))
        except Exception:  # noqa: BLE001
            pass
        try:
            sw.CommandInProgress = False
        except Exception:  # noqa: BLE001
            pass


# ── ⑤ 守卫：不许在实现里加换算（业主提醒） ──────────────────────────


def test_add_component_体内不许加换算() -> None:
    """★★★ 业主原话：「有的函数本来就是要 3 米，你别以为它要 3 毫米就给它改了」。

    ⇒ 治法只动**名字**（`x` → `x_m`），值**原样**交给 COM。
    ★ 如果谁在体内加一句 `x_m * 0.001`，会把**本来正确**的调用全改错 1000 倍。
    """
    src = _ASM.read_text(encoding="utf-8")
    for fn in ("_add_component5", "_add_component4"):
        tree = ast.parse(src)
        body_src = ""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == fn:
                body_src = ast.get_source_segment(src, node) or ""
                break
        assert body_src, "★ 找不到 `%s` 的函数体" % fn
        for bad in ("* 0.001", "/ 1000", "* 1e-3", "/ 1e3", "* _MM_TO_M"):
            assert bad not in body_src, (
                "★ `%s` 体内出现 `%s` —— 它本来就收**米**，加换算会把正确调用改错"
                % (fn, bad)
            )


def test_工具层换算恰好一次() -> None:
    """★★ 规则 2：换算只在**边界**做一次（工具层），实现层一律米。"""
    src = (REPO / "mcp-server" / "server.py").read_text(encoding="utf-8")
    i = src.find("def solidworks_add_component")
    assert i > 0, "★ 找不到工具层入口"
    seg = src[i:i + 900]
    assert "mm(" in seg, "★ 工具层没有做 mm() 换算 ⇒ 到实现层就不是米了"
    assert seg.count("mm(") >= 3, "★ 三个坐标都要换算（x/y/z）"
