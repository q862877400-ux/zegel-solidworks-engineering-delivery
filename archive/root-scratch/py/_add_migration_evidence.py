import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")

# ① 能力条目：把轮 148 那句「21 份只迁移了示范」改掉
import json
Q = Path(r"C:\swprojects\sw-skill-fork\capabilities.yaml")
d = json.loads(Q.read_text(encoding="utf-8"))
OLD = "⚠ **21 份复制的迁移本轮只做了示范**（未全量替换）⇒ 其余仍带旧过滤。"
NEW = ("★ **2026-10-01（轮 149）21 份已全量迁移**：每份的 `modal_dialogs` 都改成"
       "**委托** `sw_connect.residual_dialogs`（函数内双路导入，照本仓既有模式），"
       "并**把扫到的窗口总数一并返回/打印** ⇒ ★ 端到端实测输出变成"
       "「**扫了 49 个窗口 · 无模态框**」（此前只写「无」，无法区分「没有」与「没扫到」）。"
       "⚠ 唯一豁免：`tools/probe_window_vs_graphics.py`（它的 `main_windows()` **本身**"
       "要用可见性做对照实验，且**不在收尾路径上**）。")
n = 0
for c in d["capabilities"]:
    lim = c.get("limitations") or []
    for i, s in enumerate(lim):
        if OLD in str(s):
            lim[i] = str(s).replace(OLD, NEW)
            n += 1
Q.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("  ok capabilities 更正 %d 处" % n)

# ② 已知事实 89
FACT = "| 89 | " + "".join([
    "**同一个检查被抄 21 份 ⇒ 错误口径也被抄了 21 份；全量迁移后判据不再空转** —— ",
    "2026-10-01（轮 149）：事实 88 查出 21 份 `modal_dialogs` 都带 `IsWindowVisible`（漏检 48/49）；",
    "本轮**把 21 份全部改成委托** `sw_connect.residual_dialogs`（函数内双路导入），",
    "并**把扫到的窗口总数一并返回/打印**。★ 端到端实测：收尾那行的输出从「无」变成",
    "「**扫了 49 个窗口 · 无模态框**」⇒ ★ **空列表第一次有了意义**",
    "（此前无法区分「没有模态框」与「没扫到任何窗口」）。",
    "★★ 迁移手法的两条关键（都来自本会话的教训）：① **改函数体、不改调用点**",
    "（21 个调用点原样不动 ⇒ 风险面小得多）；② **导引用函数内双路 try/except**",
    "（照本仓既有模式）—— 第一版直接写 `sw_connect.residual_dialogs(...)` 就 `NameError` 了，",
    "因为那些工具并**没有**把 `sw_connect` 当模块导入。",
    "★ 并加了结构判据 `tests/test_modal_dialogs_single_source.py`（4 条）：",
    "**每个 `modal_dialogs` 都必须委托** · **不许再用 `IsWindowVisible`** ·",
    "共享实现要返回总数 · **豁免名单要小而明确**（目前只有那一个对照实验探针）。",
    "⚠ 仍未查证：**没有**构造真模态框验证新判据能抓到它（只证「扫到的窗口数 1 → 49」）。 | ",
    "`tests/test_modal_dialogs_single_source.py`（4 条）；`tools/verify_bmp_smoke.py` 的端到端输出；",
    "事实 88 |",
])
K = Path(r"D:\AI\SW\docs\known-facts.md")
tk = K.read_text(encoding="utf-8")
if "同一个检查被抄 21 份" not in tk:
    K.write_text(tk.rstrip() + "\n\n" + FACT + "\n", encoding="utf-8")
    print("  ok known-facts 已加 89")
else:
    print("  已有 89")
