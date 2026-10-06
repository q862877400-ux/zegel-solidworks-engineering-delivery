"""★ 给 ToolSpec 的 `doc=` **插一行短首句**（★ 只做加法、★ 不动原有内容）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（`mcp-server/tool_specs_batch*.py` 的 lean 可读性修整）
# 文件:   tools/lean_first_sentence.py
# 定位:   ★ 用户 2026-10-07 质问：「★ **你工具描述我看看你写的咋样，干了 41k，太多了**，
#   ★ 你肯定说了一堆废话，★ **lean 模式的要求是要写的精而准**」✓
#   ★★ 实测（`tools/measure_lean_catalog.py`）：★ **504 个工具的 lean 目录 = 66802 字 ≈ 16700 tokens**，
#     首句**平均 93.4 字**、★ **223 条顶到 120 字上限（近一半被截断）** ✗；
#     ★★★ 而**我自己写的 13 个更差：首句平均 121 字、13/13 全被截断** ✗✗
#   ★★★ **病根**：我把 `doc=` 当成了**变更日志 + 证据链**（★「★ 本能力是……的实证：★ 我原先走……」
#     ✗）—— ★ 那是写给人看的考古记录，★ 而 `firstLine()` **只取第一句** ⇒
#     ★★ **模型每轮看到的是被切断的半句话** ✓
# 判据:   ★★ 修法**只做加法**（★ 本仓事实 61：★ 批量改动必须先证明只做加法 ✓）：
#     ★ 在目标 `doc=` **之后插一行**短首句字符串字面量 ✓（★ Python 相邻字面量自动拼接 ✓），
#     ★★ **原有任何一个字节都不动** ✓
#   ★★★ 三道校验（★ 全机器可判 ✓）：
#     ★ ① `ast.parse` 每个改过的文件 ✓
#     ★ ② `git diff --stat` —— ★ **insertions 有、deletions 必须为 0** ✓（★ 只做加法 ✓）
#     ★ ③ **重量一次** `tools/measure_lean_catalog.py` ⇒ ★ 首句均长必须下降 ✓
# 用法:   `python tools/lean_first_sentence.py --map <映射.json> [--apply]`
#   ★ 映射形如 `{"solidworks_sweep_surface": "扫描曲面：按轮廓 + 路径生成一张曲面。"}` ✓
#   ★ **不给 `--apply` 就是只演算**（★ 只打印将要插什么 ✓、★ 不写文件 ✓）
# 许可:   本仓库 MIT。★ 只读 + 只插行。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path

ROOT = Path(r"D:\AI\SW")
BATCH_DIR = ROOT / "mcp-server"
#: ★ 首句目标上限（★ lean 的硬上限是 120 字 ✓，★ 而我们要**远低于**它 ⇒ 取 44 ✓）
TARGET_MAX = 44


def _blocks(text: str, name: str):
    """★ 找出 `name="<name>"` 那个 ToolSpec 块里的 `doc=` 起始位置（★ 行首 + 缩进 ✓）。"""
    m = re.search(r'name="%s"' % re.escape(name), text)
    if not m:
        return None
    d = re.search(r"^(\s*)doc=", text[m.end():], re.M)
    if not d:
        return None
    start = m.end() + d.start()
    indent = d.group(1)
    at = m.end() + d.end()          #: ★ `doc=` 之后的位置 ✓
    return {"indent": indent, "line_start": start, "after_doc": at}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--map", required=True, help="★ JSON：{工具名: 新首句}")
    ap.add_argument("--apply", action="store_true", help="★ 不给就是只演算")
    a = ap.parse_args()

    mapping = json.loads(Path(a.map).read_text(encoding="utf-8"))
    #: ★ 先自查**首句本身**是否够短（★ 否则就白改了 ✓）
    too_long = {k: len(v) for k, v in mapping.items() if len(v) > TARGET_MAX}
    print("★ 映射 %d 条 · ★ 超过 %d 字目标的 %d 条 %r"
          % (len(mapping), TARGET_MAX, len(too_long), too_long or ""))
    if too_long:
        print("  ⚠ 建议先压短它们（★ lean 要的是**精而准** ✓）")

    files = sorted(BATCH_DIR.glob("tool_specs_batch*.py"))
    touched: dict = {}
    for f in files:
        text = f.read_text(encoding="utf-8")
        orig = text
        for name, first in mapping.items():
            b = _blocks(text, name)
            if b is None:
                continue
            #: ★ 幂等：★ 已经以这句开头就不再插（★ 防跑两次插两遍 ✓）
            seg = text[b["after_doc"]:b["after_doc"] + 200]
            if seg.lstrip().startswith('"%s"' % first):
                continue
            ins = '\n%s    "%s"' % (b["indent"], first.replace('"', '\\"'))
            text = text[:b["after_doc"]] + ins + text[b["after_doc"]:]
            touched.setdefault(f.name, []).append(name)
        if text != orig:
            #: ★ 判据①：★ 改完必须还能解析 ✓
            try:
                ast.parse(text)
            except SyntaxError as e:
                print("✗ %s 改后语法错（L%s）：**回退这个文件** ✓" % (f.name, e.lineno))
                continue
            if a.apply:
                f.write_text(text, encoding="utf-8")
            print("★ %s ⇒ 插了 %d 条 %r%s"
                  % (f.name, len(touched.get(f.name, [])), touched.get(f.name, [])[:4],
                     "" if a.apply else "（★ 只演算、★ 未写）"))
    if not touched:
        print("★ 没有可插的（★ 要么全改过了、★ 要么名字对不上 ⇒ ★ 查映射 ✓）")
    print("★ 总插入 %d 条 · ★ 模式 = %s"
          % (sum(len(v) for v in touched.values()), "apply" if a.apply else "dry-run"))
    if a.apply:
        print("★★ 下一步必做：★ ① `git diff --stat` 看 **deletions 必须为 0** ✓ "
              "② 重跑 `python tools/measure_lean_catalog.py` 看首句均长下降 ✓")
    return 0


if __name__ == "__main__":
    import traceback
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException:                                              # noqa: BLE001
        tb = traceback.format_exc()
        (ROOT / "output" / "lean-first-sentence-traceback.txt").write_text(tb, encoding="utf-8")
        print("★★ 异常：\n%s" % tb[-1200:])
        raise SystemExit(3)
