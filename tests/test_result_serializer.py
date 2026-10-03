"""★ 事实 508 的负例：`_result` **不许**因为返回值不可 JSON 序列化而把成功变成 error。

★ 为什么要这条测试（★ 事实 62：负例是门禁/判据有效的唯一证明）：
  真机实测（证据 `output/result-serializer-evidence.json`）—— `sw_part.fillet` 建成 `圆角1`，
  ★ 而它回的是 `CDispatch` ⇒ 旧 `_result` 的 `json.dumps(payload)` **抛 TypeError**
  ⇒ 被 `_run_locked` 吞掉 ⇒ ★★ **调用方收到一条 error**（"建成了却报错"）。
★ 本测试**离线**跑（不连 SolidWorks、不 import 整个 server）：
  只从 `mcp-server/server.py` 里**取 `_jsonable` 与 `_result` 两段**执行，
  ★ 这样既验了真源码、又不拉 COM 依赖。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SERVER = REPO / "mcp-server" / "server.py"


def _load_result():
    """★ 从真源码里抽出 `_jsonable` + `_result` 两段并执行（★ 不 import server）。"""
    src = SERVER.read_text(encoding="utf-8", errors="replace")
    a = src.index("def _jsonable")
    b = src.index("def _tool_error")
    seg = src[a:b]
    assert "_result" in seg and "_jsonable" in seg, "★ 没抽到 _result / _jsonable —— 源码结构变了？"

    class _RF:
        JSON = "json"

    ns = {"Any": object, "Dict": dict, "json": json, "ResponseFormat": _RF}
    exec(seg, ns)                                                        # noqa: S102
    return ns["_result"]


class _FakeCOM:
    """★ 冒充原始 COM 对象：**不可 JSON 序列化**，且带 `Name`（★ 真对象常能读到名字）。"""

    Name = "圆角1"

    def __repr__(self) -> str:                                           # pragma: no cover
        return "<COMObject <unknown>>"


def test_com_object_is_wrapped_not_raised():
    """★★ 负例：原始 COM 对象 ⇒ **必须包成可序列化**的返回，★ 而**不是**抛出去。"""
    result = _load_result()
    out = result(_FakeCOM(), "json")                                     # ★ 旧版在这里抛 TypeError
    payload = json.loads(out)                                            # ★ 能解析 = 没抛
    assert payload["status"] == "ok", "★ COM 返回不该被当成错误"
    assert "圆角1" in json.dumps(payload, ensure_ascii=False), \
        "★ 降级包装应当**保住对象的名字**（否则调用方看不出建成了什么）"
    assert payload.get("result_type") == "_FakeCOM", "★ 应当标明原始类型名"


def test_non_dict_scalar_is_wrapped():
    """★ 非 dict 标量（如 `int`）也要包，而不是让 markdown 分支的 `.get` 炸。"""
    result = _load_result()
    for value in (42, True, "done", 3.5):
        payload = json.loads(result(value, "json"))
        assert payload["status"] == "ok"
        assert payload["result"] == value


def test_normal_dict_is_unchanged():
    """★★ **正对照**：本来就规范的 dict **一个字节都不许变**（★ 否则就是改了语义）。"""
    result = _load_result()
    src = {"status": "ok", "n": 1, "nested": {"a": [1, 2]}}
    out = result(src, "json")
    assert json.loads(out) == src, "★ 正常 dict 的返回被改了 —— 这是回归"


def test_markdown_branch_survives_non_dict():
    """★ markdown 分支原先会 `payload.get(...)` ⇒ 非 dict 必 `AttributeError`。"""
    result = _load_result()
    out = result(_FakeCOM(), "markdown")
    assert out.startswith("# ok"), "★ markdown 也必须活下来"
    assert "_FakeCOM" in out or "result_type" in out


@pytest.mark.parametrize("bad", ["CDispatch", "COMObject"])
def test_source_no_longer_serializes_bare(bad: str):
    """★ 源码级判据：`_result` 不许再出现**不带 `default=`** 的 `json.dumps`。

    ★★ 2026-10-03 修：第一版**直接对源码文本跑正则** ⇒ ★ 命中了 `_result` docstring 里
      **引用的旧代码**（「`_result` 原先只有一句 `json.dumps(payload, ensure_ascii=False, indent=2)`」）
      ⇒ 测试**误报失败**。
      ★ 这正是**事实 60** 的教训：「**写了一个好用的工具函数，就要在所有同类场合用它**」
      ⇒ ★ 本测试改用仓内既有的 **`scripts/check_env_pitfalls.py::strip_comments_and_strings`**
        （★ 与门禁同一个实现，★ 不另造一个）。
    """
    sys.path.insert(0, str(REPO / "scripts"))
    from check_env_pitfalls import strip_comments_and_strings      # noqa: PLC0415

    src = SERVER.read_text(encoding="utf-8", errors="replace")
    a, b = src.index("def _jsonable"), src.index("def _tool_error")
    seg = strip_comments_and_strings(src[a:b])                     #: ★ 先剥注释与字符串
    for m in re.finditer(r"json\.dumps\(([^)]*)\)", seg, re.S):
        assert "default=" in m.group(1), \
            "★ `_result` 里出现了不带 default= 的 json.dumps ⇒ 不可序列化的返回会再变 error"
