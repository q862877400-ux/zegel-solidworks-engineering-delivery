r"""@brief 探针：找「**文件在、却没被登记**」与「**登记了、文件却不在**」的表。

## 第三种形态的死守卫
`053`/`054` 扫的是**常量**（规则 2 的两半）· `055` 扫的是**函数**（`match_modules`）。
★ 第三种：**注册表 / 批次清单** ——
一个 `tool_specs_batchN.py` **躺在磁盘上**，却**没进 `BATCH_MODULES`**
（⇒ 它的工具**永远不会被注册**，而文件看着好好的）。
反之：`BATCH_MODULES` 里写了个**不存在的模块** ⇒ 注册时炸（那种会自己暴露）。

## 判法（**纯结构**：文件名 vs 清单项）
```
① 磁盘上 mcp-server/tool_specs_batch*.py 的集合
② register_capabilities.BATCH_MODULES 的集合
③ 两边做差 ⇒ 两个方向各自的可疑
```
★ 这与事实 74 的对照最清楚：**判结构（在不在清单里）不涉及任何语义判断。**

# ── 来源 ──
# 仓库:   本项目自身（只读探针）
# 文件:   tools/probe_registry_wiring.py
# 定位:   给 Spec Kit `056` 取证：注册表里有没有"文件在却没登记"的项。
# 官方依据: 不适用（本项目内部工具）。
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "mcp-server"))
sys.stdout.reconfigure(encoding="utf-8")


def main() -> int:
    #: ① 磁盘上的批次文件
    on_disk = {p.stem for p in (ROOT / "mcp-server").glob("tool_specs_batch*.py")}

    #: ② 清单里登记的
    src = (ROOT / "mcp-server" / "register_capabilities.py").read_text(encoding="utf-8")
    m = re.search(r"BATCH_MODULES\s*=\s*\((.*?)\)", src, re.S)
    declared = set(re.findall(r'"(tool_specs_batch\w+)"', m.group(1))) if m else set()

    print("  磁盘上的批次文件 : %d 个" % len(on_disk))
    print("  清单里登记的     : %d 个" % len(declared))
    print()
    missing = sorted(on_disk - declared)
    ghost = sorted(declared - on_disk)
    print("  ★ **文件在、却没登记**（工具永远不会被注册）: %d 个" % len(missing))
    for x in missing:
        print("      %s" % x)
    print("  ★ **登记了、文件却不在**（注册时会炸）: %d 个" % len(ghost))
    for x in ghost:
        print("      %s" % x)

    #: ③ 顺带量：每个批次文件声明的 spec 名字，与 all_specs() 是否对得上
    print()
    try:
        import register_capabilities as rc
        allnames = {s.name for s in rc.all_specs()}
        for mod in sorted(declared):
            mm = __import__(mod)
            var = next((getattr(mm, n) for n in dir(mm)
                        if n.startswith("SPECS_") and isinstance(getattr(mm, n), list)), None)
            if var is None:
                print("  ⚠ %s 里找不到 SPECS_* 列表" % mod)
                continue
            names = {s.name for s in var}
            absent = sorted(names - allnames)
            print("  %-22s 声明 %2d 条 · 不在 all_specs() 里: %d %s"
                  % (mod, len(names), len(absent), absent or ""))
    except Exception as exc:      # noqa: BLE001
        print("  ⚠ 无法导入注册器：%s" % str(exc)[:120])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
