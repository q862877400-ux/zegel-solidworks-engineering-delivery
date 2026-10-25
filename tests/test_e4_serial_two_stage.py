"""★ E4 采集与判定必须**串行两段**（第 57 轮实测的架构）。

## 三种摆法的真机对比（同一轮内，只差一处）

```
采集器单独跑（无别的 COM 客户端）   → components 2 · interference 0   ✓
运行器**起子进程**跑采集器          → -1（RPC_E_DISCONNECTED）
运行器**进程内**采集                → -1（同一原因）
```

⇒ **两个进程同时持有到同一个 SolidWorks 实例的 COM 连接 ⇒ 后连的被断连。**
  ★ 这是本仓事实 24「多个进程抢同一 COM 连接」的另一副面孔：
    那条记的是**死锁**，这条记的是**断连**。

⇒ 正确摆法：**串行 + 文件接缝**

```
python -B tools/collect_e4_standalone.py   # ① 采集（此时无别的客户端）
python -B tools/run_s3_acceptance.py       # ② 判定（只读 output/e4-standalone.json）
```

## 本文件钉什么

① 运行器**不许**再起子进程跑采集（那会并发持 COM）
② 运行器**不许**在进程内读组件数（`GetComponents` 不该出现）
③ 运行器必须**读文件**，且文件缺失时**如实报错**（不静默当 0 个组件）
④ 采集器必须写 `finished_at`（供判新鲜度）并**不信任** `new_document` 返回的对象
⑤ 采集器收尾把文档清到 0 并记账
"""
from __future__ import annotations

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
_RUNNER = REPO / "tools" / "run_s3_acceptance.py"
_STANDALONE = REPO / "tools" / "collect_e4_standalone.py"


def _runner() -> str:
    return _RUNNER.read_text(encoding="utf-8")


def _std() -> str:
    return _STANDALONE.read_text(encoding="utf-8")


def test_运行器不许起子进程跑采集() -> None:
    """★★ 并发持 COM ⇒ 后连的被断连（实测三种摆法）。

    ★ 只查 subprocess —— 注释里会**提到**采集器的文件名（说明用），
      那是解释不是调用（第 57 轮又踩了一次这种误报）。
    """
    src = _runner()
    assert "subprocess" not in src, (
        "★ 运行器里出现了 subprocess ⇒ 又起子进程了，会 RPC_E_DISCONNECTED"
    )


def test_运行器不许在进程内读组件数() -> None:
    src = _runner()
    assert '"GetComponents"' not in src, (
        "★ 运行器里又出现 `GetComponents` ⇒ 又回到进程内采集那条路"
    )


def test_运行器读文件且缺失时如实报错() -> None:
    src = _runner()
    assert "e4-standalone.json" in src, "★ 没读采集证据文件"
    assert "没有采集证据" in src or "请先跑" in src, (
        "★ 文件缺失时没有如实报错 ⇒ 会被当成「0 个组件」"
    )


def test_采集器写_finished_at() -> None:
    """★ 判定侧要能看出证据是不是这次的。"""
    assert "finished_at" in _std(), "★ 采集器没写 finished_at"


def test_采集器不信任_NewDocument_返回的对象() -> None:
    """★ 事实 569：`ok=True` 不等于对象还能用 ⇒ 要从 `ActiveDoc` 重取。"""
    src = _std()
    i = src.find("c_.try_call(c_.new_document")
    assert i > 0, "★ 找不到 new_document 调用处"
    seg = src[i:i + 1200]
    assert "ActiveDoc" in seg, "★ 没有从 `ActiveDoc` 重取"


def test_采集器收尾记账() -> None:
    src = _std()
    assert "docs_left" in src, "★ 没收尾记文档数"
    assert "CloseAllDocuments" in src, "★ 没有清场兜底"


def test_采集器记每步读数() -> None:
    """★ 只有 `-1` 时无从下手 —— 步骤记录是排障的唯一入口。"""
    src = _std()
    for key in ("pre_docs", "open_part", "new_assembly", "asm_title", "add_component"):
        assert key in src, "★ 采集器缺步骤读数 `%s`" % key
