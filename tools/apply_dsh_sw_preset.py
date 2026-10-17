"""★ 把生成好的 preset 块**安全地**追加进 DSH 活配置（★ 校验不过就自动回滚）。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（DSH 侧配置应用器）
# 文件:   tools/apply_dsh_sw_preset.py
# 定位:   ★ 用户 2026-10-07 指令：「★ 建一个新 preset…就叫 Lean模式（SW工程师）」✓
#   ★★ **为什么要有这个应用器、而不是直接追加**（★ 本会话的**真事故**）：
#     ★ 我第一版用 `Add-Content -Value (Get-Content <块> -Raw)` ✗ ——
#     ★★ 而**验证那次我调错了 node 的参数位**（`process.argv[1]` 是**脚本路径** ✗、
#       参数在 `process.argv[2]` ✓）⇒ ★ 解析器**把 `.cjs` 自己当 YAML** ✗ ⇒
#       报「顶层 968 条」✗ ⇒ ★★★ **我据此误判配置被写坏、当场回滚** ✗
#     ⇒ ★★★★ **真因是我的校验器，★ 不是配置** ✓（★ 回滚本身无害：回到的是好状态 ✓）
#   ⇒ ★ **本应用器把三件事钉在一起**：★ ① 用 Python 写文件（★ 避开 PS 编码坑 ✓）·
#     ★ ② **写前**先校验"原配置 + 块" ✓ · ★ ③ **写后**再校验落盘文件 ✓、
#     ★★ **任一步不过就自动回滚** ✓✓
# 判据:   ★★ 全程机器判（★ 事实 62）：
#     ★ ① 阳性对照：**原配置**必须能解析（★ 且把它的 insert id 记下来 ✓）
#     ★ ② 合并体能解析 · ★ 新 id（`lean-mode-sw` / `preset-sw-engineer` / `mcp-solidworks`）齐 ✓
#     ★ ③ **原有 id 一个不丢** ✓（★ 用户明令不许动别的 preset ✗）
#     ★ ④ 落盘后再验一遍（★ 防"写进去的和验过的不一样" ✗）
# 许可:   本仓库 MIT。★ 只写 `~/.dsh` 下的**一个**文件，★ 且**先备份** ✓。覆盖: 全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

HOME = Path(os.path.expanduser("~"))
LIVE_CFG = HOME / ".dsh/profiles/web/cordis.patch.yml"
BLOCK = Path(Path(__file__).resolve().parents[1] / "output" / "_dsh_sw_preset_block.yml")
DSH_ROOT = Path(r"D:\AI\DSH\deepseek-harness")
OUT_JSON = Path(Path(__file__).resolve().parents[1] / "output" / "dsh-sw-preset-apply.json")

#: ★ 复核脚本 —— ★★ **写成文件再调**（★ 这样参数位**无歧义** ✓）：
#:   ★ `node -e "<代码>" <arg>` ⇒ 参数在 **`argv[1]`** ✗
#:   ★★ `node <脚本文件> <arg>` ⇒ 参数在 **`argv[2]`** ✓
#:   ★★★ 本会话在这上面**栽了两次**（★ 一次误判配置被写坏、一次阳性对照假失败 ✗）
#:     ⇒ ★ **定则：★ 别用 `-e` 传带参数的校验脚本，★ 写文件** ✓
JS_CHECK = r"""
const fs = require('fs');
const yaml = require('D:/AI/DSH/deepseek-harness/node_modules/js-yaml');
const p = process.argv[2];
if (!p) { console.log(JSON.stringify({ ok: false, err: 'NO_PATH' })); process.exit(2); }
let src = fs.readFileSync(p, 'utf8').replace(/!!js/g, '');
try {
  const doc = yaml.load(src);
  const ids = [], presets = {};
  for (const blk of (doc || [])) for (const it of ((blk && blk.insert) || [])) {
    if (!it) continue;
    if (it.id) ids.push(it.id);
    const cfg = it.config || {};
    if (cfg.id && Array.isArray(cfg.plugins)) presets[cfg.id] = cfg.plugins.filter(Boolean).map(x => x.id).filter(Boolean);
  }
  console.log(JSON.stringify({ ok: true, top: doc.length, ids, presets }));
} catch (e) { console.log(JSON.stringify({ ok: false, err: String(e.message).slice(0, 300) })); process.exit(1); }
"""
CHECKER = Path(Path(__file__).resolve().parents[1] / "output" / "_dsh_yaml_checker.cjs")


def _check(path: Path) -> dict:
    CHECKER.write_text(JS_CHECK, encoding="utf-8")
    r = subprocess.run(["node", str(CHECKER), str(path)],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=180)
    try:
        return json.loads((r.stdout or "").strip().splitlines()[-1])
    except Exception:                                                   # noqa: BLE001
        return {"ok": False, "err": "校验器输出不可解析：%r" % ((r.stdout or r.stderr) or "")[:200]}


def _all_ids(chk: dict) -> list:
    """★ 两层求并（★ 第一版只取顶层 ⇒ 把 `mcp-solidworks` 误判成缺失 ✗）：
    ★ ① 顶层 `- insert:` 的条目 id ✓ · ★★ ② **preset 的 `config.plugins[]` 里的插件 id** ✓
    """
    ids = list(chk.get("ids") or [])
    for v in (chk.get("presets") or {}).values():
        ids.extend(v or [])
    return ids


WANT = ["lean-mode-sw", "preset-sw-engineer", "mcp-solidworks"]


def main() -> int:
    out: dict = {"live_cfg": str(LIVE_CFG), "block": str(BLOCK)}
    if not LIVE_CFG.is_file() or not BLOCK.is_file():
        print("✗ 缺文件")
        return 2

    #: ★ 判据①：阳性对照 —— ★ 原配置必须能解析 ✓
    base = _check(LIVE_CFG)
    out["before"] = base
    print("★ ① 阳性对照 ⇒ ok=%r · 顶层 %r 条 · insert id %r"
          % (base.get("ok"), base.get("top"), base.get("ids")))
    if not base.get("ok"):
        print("✗ 原配置就解析不了 ⇒ **不动它** ✓")
        return 3
    base_ids = list(base.get("ids") or [])  # ★ 顶层 id（★ 原配置里没有 preset ✓）

    #: ★ 判据②③：★ 先在**临时合并体**上验（★ 不碰活配置 ✓）
    tmp = LIVE_CFG.with_suffix(".patch.yml.__merged_preview__")
    try:
        tmp.write_text(LIVE_CFG.read_text(encoding="utf-8").rstrip("\n") + "\n\n"
                       + BLOCK.read_text(encoding="utf-8").rstrip("\n") + "\n",
                       encoding="utf-8")
        merged = _check(tmp)
        out["merged"] = merged
        if not merged.get("ok"):
            print("✗ 合并体解析失败：%r ⇒ **不动活配置** ✓" % merged.get("err"))
            return 4
        mid = _all_ids(merged)
        missing = [w for w in WANT if w not in mid]
        lost = [x for x in base_ids if x not in mid]
        out["missing"] = missing
        out["lost"] = lost
        print("★ ② 合并体 ⇒ ok · 顶层 %r · id %d 个" % (merged.get("top"), len(mid)))
        print("     新 id 缺失 %r · **原有 id 丢失** %r（★ 必须两个都空）" % (missing, lost))
        if missing or lost:
            print("✗ 判据②/③ 没过 ⇒ **不动活配置** ✓")
            return 5
        presets = merged.get("presets") or {}
        print("     ★★ 声明出来的 preset ⇒ %r" % list(presets.keys()))
        for k, v in presets.items():
            if k == "sw-engineer":
                print("        preset %r 共 %d 个插件 · **含 mcp-solidworks=%r**"
                      % (k, len(v), "mcp-solidworks" in v))
    finally:
        try:
            tmp.unlink()
        except Exception:                                               # noqa: BLE001
            pass

    #: ── 写：★ 先备份，★ 用 Python（★ 避开 PS 编码坑 ✓）──────────────────
    stamp = time.strftime("%Y%m%d-%H%M%S")
    bak = LIVE_CFG.with_name(LIVE_CFG.name + ".bak-%s-before-apply-sw-preset" % stamp)
    shutil.copy2(LIVE_CFG, bak)
    out["backup"] = str(bak)
    print("★ 备份 ⇒ %s" % bak.name)

    LIVE_CFG.write_text(merged_src := (LIVE_CFG.read_text(encoding="utf-8").rstrip("\n") + "\n\n"
                                       + BLOCK.read_text(encoding="utf-8").rstrip("\n") + "\n"),
                        encoding="utf-8")

    #: ★ 判据④：★ 落盘后再验（★ 防"写进去的和验过的不一样" ✗）
    after = _check(LIVE_CFG)
    out["after"] = after
    print("★ ④ 落盘后校验 ⇒ ok=%r · 顶层 %r 条" % (after.get("ok"), after.get("top")))
    if not after.get("ok"):
        shutil.copy2(bak, LIVE_CFG)
        print("✗✗ 落盘后校验失败 ⇒ **已自动回滚** ✓（★ 从 %s 恢复）" % bak.name)
        return 6
    aid = _all_ids(after)
    if [w for w in WANT if w not in aid] or [x for x in base_ids if x not in aid]:
        shutil.copy2(bak, LIVE_CFG)
        print("✗✗ 落盘后 id 对不上 ⇒ **已自动回滚** ✓")
        return 7
    out["applied"] = True
    out["presets_after"] = list((after.get("presets") or {}).keys())
    print("✓✓✓ **应用成功** —— ★ preset 声明 ⇒ %r" % out["presets_after"])
    print("   ★★ 用户下一步：★ **新建会话 → 选 preset「Lean 模式（SW工程师）」** ✓")
    OUT_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print("★ 证据：%s" % OUT_JSON)
    return 0


if __name__ == "__main__":
    import traceback
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except BaseException:                                              # noqa: BLE001
        tb = traceback.format_exc()
        Path(Path(__file__).resolve().parents[1] / "output" / "dsh-sw-preset-apply-traceback.txt").write_text(tb, encoding="utf-8")
        print("★★ 异常已落盘：\n%s" % tb[-1500:])
        raise SystemExit(3)
