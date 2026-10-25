"""E4 证据探针的共用小件：**边跑边写**的证据收集器。

## 为什么单独一个文件

两个 E4 探针（`probe_e4_build_assembly.py` / `probe_e4_mate_by_faces.py`）都要
「每步立刻落盘」——因为**进程可能被弹窗冻住或被 SolidWorks 崩溃连带杀掉**，
那时 `finally` 不会执行（第 43 轮实测：一份证据都没留下）。

★ 三次重复实现同一件事会触发统一化门禁（跨文件同函数体）⇒ 抽成一处。

## 用法

```python
ev = Evidence(Path("output/xxx.json"), {"probe": "xxx"})
ev.mark("open_part", ok=True)          # 打一行 + 立刻落盘
ev.data["conclusion"] = "..."          # 任意时刻往里加
ev.flush()
```
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身（E4 证据探针的共用小件）
# 文件:   tools/e4_probe_common.py
# 定位:   提供 `Evidence`：每 `mark()` 一次就把 JSON 落盘一次。
#          ★ 为什么需要：第 43 轮实测进程被 SolidWorks 崩溃连带杀掉时 `finally` 不执行，
#            一份证据都没留下（同时试两条路 + 只在 finally 里写 = 零证据）。
#          ★ 为什么单独一个文件：两个 E4 探针都要这件事，重复实现会触发统一化门禁的
#            「跨文件同函数体」判据。
# 官方依据: 不适用（纯本地 JSON 落盘，不调 SolidWorks API、不联网）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import time
from pathlib import Path


class Evidence:
    """★ 每 `mark()` 一次就落盘一次 —— 崩溃时也能留下读数。"""

    def __init__(self, path: Path, seed: dict) -> None:
        self.path = path
        self.data: dict = dict(seed)
        self.data.setdefault("steps", [])
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.flush()

    def flush(self) -> None:
        self.path.write_text(
            json.dumps(self.data, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def mark(self, step: str, **kw) -> None:
        self.data["steps"].append(
            dict(step=step, at=time.strftime("%H:%M:%S"), **kw)
        )
        self.flush()
        print("· %-22s %s" % (step, kw))
