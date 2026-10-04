"""★ 门禁：核「我派出去的子代理**实际**跑在哪个模型上」—— ★ 防"派活写着 bunny、实际跑 DeepSeek"。

★ 为什么要有它（★ 业主 2026-10-04 追问触发）：
```
★ 仓里的纪律逐字要求「**子代理一律用 space-bunny，不用 DeepSeek**」（`docs/team-roles.md`）——
  ★★ 而"我在 `agent()` 里写了 provider/model"**不等于**"它真的那么跑了"（★ 事实 62 同族：
  写着 ≠ 生效；★ 支线还实测过：只写 `model` 会**整批静默失败**，返回 `returned: 0` 而**不报错**）✓
⇒ ★ 所以判据必须是**运行期记录**，不是我的调用参数 ✓
```

★ 判据（三条，全从盘上重推）：
```
① 从 DSH 的 session 缓存里，按**提示词标记串**挑出"我派的"子代理会话
   （★ 标记串由调用方给，例如我扇出时提示词里独有的文件名 / 字段名）
② 逐份读它的 `model` / `provider` / `lastModel` 字段（★ 那是**运行期写下的**）
③ ★ 任何一份不是 `space-bunny-free` / `opencode-zen` ⇒ **报出来**（退出码 1）
```
⚠ ★ 会话缓存目录由 `DSH_HOME` 决定（默认 `~/.dsh`），本机实测路径见下；★ 换机器要改 `--base`。
"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（真机核查工具，非移植）
# 文件:   `~/.dsh/storages/session_projcache/sessions/*.json`（DSH 的会话投影缓存）
# 定位:   处置"派活参数 ≠ 运行期实际模型"这一**静默**风险；★ 与 `docs/team-roles.md`
#         的「子代理一律用 space-bunny」配套 ✓
# 官方依据: 无（本仓自建工具）；★ 字段名 `model`/`provider`/`lastModel` 是**实测读出来的**
#         （2026-10-04：62 路 Bunny 的子代理会话里逐字存在这三个字段）✓
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import argparse
import collections
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
WANT_MODEL = "space-bunny-free"
WANT_PROVIDER = "opencode-zen"


def _default_base() -> str:
    home = os.environ.get("DSH_HOME") or os.path.join(os.path.expanduser("~"), ".dsh")
    return os.path.join(home, "storages", "session_projcache", "sessions")


def scan(base: str, markers: list[str], *, exclude_self: str = "") -> dict:
    out: dict = {"mine": [], "other_children": 0, "files": 0}
    for name in os.listdir(base):
        p = os.path.join(base, name)
        try:
            t = io.open(p, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        out["files"] += 1
        if '"lastUser"' not in t or '"model"' not in t:
            continue
        if not any(m and m in t for m in markers):
            out["other_children"] += 1
            continue
        if exclude_self and exclude_self in name:
            continue
        m = re.search(r'"model"\s*:\s*"([^"]+)"', t)
        pr = re.search(r'"provider"\s*:\s*"([^"]+)"', t)
        lm = re.search(r'"lastModel"\s*:\s*"([^"]+)"', t)
        out["mine"].append({"file": name, "model": m.group(1) if m else "",
                            "provider": pr.group(1) if pr else "",
                            "last_model": lm.group(1) if lm else "",
                            "deepseek_mentions": t.count("deepseek")})
    return out


def _selftest() -> int:
    """★★ 自测（事实 62）：★ 造 2 份**假会话**（一份 bunny、一份 deepseek）⇒ ★ 门禁必须**报出那一份** ✓"""
    import json as _json
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        for name, model, prov in (("a.json", WANT_MODEL, WANT_PROVIDER),
                                  ("b.json", "deepseek-flash", "deepseek-official")):
            io.open(os.path.join(d, name), "w", encoding="utf-8").write(_json.dumps({
                "lastUser": "MARKER_XYZ 你是子代理", "model": model, "provider": prov,
                "lastModel": model}))
        r = scan(d, ["MARKER_XYZ"])
        bad = [x for x in r["mine"] if x["model"] != WANT_MODEL]
        ok = (len(r["mine"]) == 2 and len(bad) == 1 and bad[0]["model"] == "deepseek-flash")
        print("%s 自测：扫到 %d 份 · 报出非 Bunny %d 份（%s）"
              % ("[OK]" if ok else "[BAD]", len(r["mine"]), len(bad),
                 bad[0]["model"] if bad else "无"))
        #: ★ 反例 2：**一份都没匹配** ⇒ 必须判"判据失效"（★ 不许当成通过）
        r2 = scan(d, ["NO_SUCH_MARKER"])
        ok2 = not r2["mine"]
        print("%s 自测2：标记串不存在时 `mine` 为空 ⇒ 上层会判「判据失效」（退出码 2）"
              % ("[OK]" if ok2 else "[BAD]"))
        print("★ 自测结论：%s" % ("门禁有效 ✓" if (ok and ok2) else "★ 门禁有洞 ✗"))
        return 0 if (ok and ok2) else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=_default_base(), help="DSH 会话缓存目录")
    ap.add_argument("--selftest", action="store_true", help="★ 自测：造 1 bunny + 1 deepseek 假会话")
    ap.add_argument("--marker", action="append", default=[],
                    help="★ 我提示词里独有的串（可多次给）；用于挑出「我派的」会话")
    ap.add_argument("--exclude-self", default="", help="排除 Lead 自己的会话文件名片段")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.marker:
        print("★ 用法：check_subagent_models.py --marker <我提示词里独有的串> [--marker …]")
        print("   ★ 例：--marker bunny-screen-rows.json --marker 三问筛")
        return 2
    if not os.path.isdir(a.base):
        print("⚠ 会话缓存目录不存在: %s ⇒ ★ 本门禁**无法执行**（★ 不许当成通过）" % a.base)
        return 2
    r = scan(a.base, a.marker, exclude_self=a.exclude_self)
    print("★ 扫过 %d 份会话记录；其中**我的**子代理 %d 个（别人的子代理 %d 个，未计入）"
          % (r["files"], len(r["mine"]), r["other_children"]))
    if not r["mine"]:
        print("⚠ ★ 一份都没匹配到 ⇒ ★ **判据可能失效**（标记串写错？或扇出没真跑）——"
              "★ **不许当成通过**")
        return 2
    print("   模型分布:", dict(collections.Counter(x["model"] for x in r["mine"])))
    print("   供应商分布:", dict(collections.Counter(x["provider"] for x in r["mine"])))
    bad = [x for x in r["mine"]
           if x["model"] != WANT_MODEL or x["provider"] != WANT_PROVIDER]
    for x in bad[:10]:
        print("   ✗ %-44s model=%-18s provider=%s" % (x["file"][:44], x["model"], x["provider"]))
    if bad:
        print("★ 结论：**有 %d 路不是 Bunny** ⇒ 违反 `docs/team-roles.md` 的纪律 ✗" % len(bad))
        return 1
    print("★ 结论：**%d 路全部是 %s / %s** ✓（★ 判据来自运行期记录，不是我的调用参数）"
          % (len(r["mine"]), WANT_MODEL, WANT_PROVIDER))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
