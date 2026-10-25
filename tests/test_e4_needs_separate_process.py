"""★ E4 采集必须单独进程跑（第 56 轮 4 次尝试后停手的结论）。

## 现场

运行器 E4 段读数 `组件 -1 · 干涉 -1`。诊断（已固化进证据 `E4.steps`）：

```
new_assembly   : true
asm_title      : ""                                   ← ★ 空标题：对象已废
components_err : com_error (-2147417848, '被调用的对象已与其客户端断开连接。')
                 ^ 0x80010108 = RPC_E_DISCONNECTED
```

而**独立探针 `tools/probe_e4_assembly.py` 在干净会话里组件 0 → 2 是通的**。

⇒ 差别在**会话状态**：运行器里 E4 排在 E2 之后，而 E2 反复开关文档（含保存 + 重开），
  之后 `new_document` 的对象就断连了。

## 第 56 轮试过的 4 个方向（都没救回来，只改一个变量）

① 加 `ActivateDoc3` ② 改从 `ActiveDoc` 重取 ③ 记录步骤 ④ 段前清空文档
⇒ 最后一次错误变成 `RPC 服务器不可用`（`0x800706BA`）= 会话在退化 ⇒ 停手。

## 本文件钉什么

① 诊断字段必须留着（`E4.steps` / `components_err`）—— 否则下次又是一句 `-1` 无从下手
② 事实里记了「单独进程」这条结论与它推翻了什么
③ `-1` 不许被当成分数报出去（它表示「没读到」，不是「0 个组件」）
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
_RUNNER = REPO / "tools" / "run_s3_acceptance.py"
_FACTS = REPO / "docs" / "known-facts.md"


def _src() -> str:
    return _RUNNER.read_text(encoding="utf-8")


def test_诊断字段留着() -> None:
    """★ `-1` 没有上下文时无从下手 —— 步骤记录是这轮唯一净产出。"""
    src = _src()
    assert '"steps"' in src, "★ E4 证据里没有 steps ⇒ 下次又只有一句 -1"
    assert "components_err" in src, "★ 没有记录 GetComponents 的异常文本"


def test_记录打开与新建的返回值() -> None:
    src = _src()
    for key in ("open_part", "new_assembly", "asm_is_none", "asm_title"):
        assert key in src, "★ 步骤记录缺 `%s`" % key


def test_事实记了单独进程这条() -> None:
    t = _FACTS.read_text(encoding="utf-8")
    assert "RPC_E_DISCONNECTED" in t or "已与其客户端断开连接" in t, (
        "★ 事实里没记断连这个错误"
    )
    assert "单独一个进程" in t or "单独进程" in t, (
        "★ 事实里没写「E4 采集要单独一个进程跑」这条结论"
    )


def test_事实记了停手与试过的方向() -> None:
    """★ 没有这段，下一个人会把同样的 4 个方向再试一遍。"""
    t = _FACTS.read_text(encoding="utf-8")
    assert "4 次" in t or "4 次都没救回来" in t, "★ 没记「试了 4 次」"
    assert "0x800706BA" in t or "RPC 服务器不可用" in t, "★ 没记最后的退化症状"


def test_负数不当读数() -> None:
    """★ `-1` 表示「没读到」，不是「0 个组件」—— 证据里必须原样保留 -1 而不是改成 0。"""
    src = _src()
    i = src.find("n_comp = -1")
    assert i > 0, "★ 读失败时应记 -1（不是 0）—— 0 会被误读成「装配里没有组件」"
