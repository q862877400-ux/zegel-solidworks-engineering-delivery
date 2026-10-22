"""★ 规格 207 · V7-1：核验 349 条记录的覆盖与合法性（SC-1 / SC-5）。"""

# ── 来源 ─────────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/verify_union_349.py
# 定位:   ★ 规格 207 的 SC-1（349/349 且 op 集合与 `union-gap-v3.json` 完全一致）与SC-
#           5（每条记录是**合法 JSON**；★ 上一轮返回体 1.8 MB 被截断且 JSON 非法 ⇒ 这条
#           是硬门禁）✓
#         ★★ **必须带负例**（仓里事实 62：「一个门禁写了不等于有效 —— 负例测试是唯一的证明」）
#           ⇒ `--selftest` 会造三种坏输入（**缺一条** / **多一条** / **一条非法 JSON**）
#             并断言核验器**会红** ✓
# 官方依据: 不适用（本仓工序）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────
from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(Path(__file__).resolve().parents[1])
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
WORKLOAD = ROOT / "output" / "union-workload-349.json"
RECORDS = ROOT / "output" / "bunny-records-verify"

#: ★ 返回体大小上限（SC-5）：单条记录不许超过它（散文该进 notes 字段而不该爆量）
MAX_BYTES = 256 * 1024


def check(records_dir: Path, workload: Path, *, only_task: str | None = None) -> dict:
    """★ 判据本体。返回 dict：ok / 计数 / 问题清单。★ 纯读，不改任何东西。

    ★★ `only_task` 是**必需的**：本轮实际产出落在**两个**目录 ——
      `bunny-records-verify/`（①档 273 条）与 `bunny-records-deep/`（②③档 76 条）⇒
      ★ 若仍按"一个目录凑 349"判，会**误报"缺 76 条"**（★ 本条是我先写错、后改对的）✓
    """
    wl = json.loads(workload.read_text(encoding="utf-8"))
    items = wl["items"]
    if only_task is not None:
        items = [x for x in items if x.get("task") == only_task]
    want = {int(x["index"]): str(x["op"]) for x in items}

    problems: list[str] = []
    seen: dict[int, str] = {}
    bad_json: list[str] = []
    oversized: list[str] = []

    files = sorted(records_dir.glob("*.json")) if records_dir.is_dir() else []
    for f in files:
        try:
            raw = f.read_text(encoding="utf-8", errors="replace")
            rec = json.loads(raw)
        except Exception as exc:  # noqa: BLE001
            bad_json.append("%s（%s）" % (f.name, type(exc).__name__))
            continue
        if len(raw.encode("utf-8")) > MAX_BYTES:
            oversized.append(f.name)
        try:
            i = int(rec.get("index"))
        except Exception:  # noqa: BLE001
            problems.append("%s：index 不是整数" % f.name)
            continue
        seen[i] = str(rec.get("op"))

    missing = sorted(set(want) - set(seen))
    extra = sorted(set(seen) - set(want))
    mismatch = sorted(i for i in set(want) & set(seen) if want[i] != seen[i])

    if len(seen) != len(want):
        problems.append("记录数 %d != 期望 %d" % (len(seen), len(want)))
    if missing:
        problems.append("缺 %d 条：%s" % (len(missing), missing[:20]))
    if extra:
        problems.append("多 %d 条（索引不在 1..349）：%s" % (len(extra), extra[:20]))
    if mismatch:
        problems.append(
            "op 对不上 %d 条（索引 → 期望/实际）：%s"
            % (len(mismatch), [(i, want[i], seen[i]) for i in mismatch[:10]])
        )
    if bad_json:
        problems.append("非法 JSON %d 条：%s" % (len(bad_json), bad_json[:10]))
    if oversized:
        problems.append(
            "超大记录 %d 条（>%d B）：%s" % (len(oversized), MAX_BYTES, oversized[:5])
        )

    return {
        "ok": not problems,
        "records": len(seen),
        "expected": len(want),
        "missing": missing,
        "extra": extra,
        "mismatch": mismatch,
        "bad_json": bad_json,
        "oversized": oversized,
        "problems": problems,
    }


def selftest() -> int:
    """★★ 负例自检：三种坏输入**必须**让核验器变红（事实 62）。"""
    wl = json.loads(WORKLOAD.read_text(encoding="utf-8"))
    cases = []
    with tempfile.TemporaryDirectory() as td:
        base = Path(td)

        def write_all(
            d: Path, skip: int | None = None, extra: bool = False, broken: bool = False
        ):
            d.mkdir(parents=True, exist_ok=True)
            for x in wl["items"]:
                if skip is not None and int(x["index"]) == skip:
                    continue
                body = json.dumps(
                    {"index": x["index"], "op": x["op"], "verdict": "已有等价物"},
                    ensure_ascii=False,
                )
                if broken and int(x["index"]) == 7:
                    body = '{"index": 7, "op": "x", "verdict": "a\nb"}'  # 裸换行 ⇒ 非法 JSON
                (d / ("%d.json" % x["index"])).write_text(body, encoding="utf-8")
            if extra:
                (d / "999.json").write_text(
                    '{"index": 999, "op": "ghost"}', encoding="utf-8"
                )

        for name, kw in (
            ("负例①：缺一条", {"skip": 5}),
            ("负例②：多一条", {"extra": True}),
            ("负例③：一条非法 JSON", {"broken": True}),
        ):
            # negproof-exempt: 这一句**不是造负例输入** —— 它只是把负例**目录名**里的全
            # 角「：」
            #   换成「_」（`负例①：缺一条` ⇒ `负例①_缺一条`）。★ 真正的坏输入由**下一行**
            #   `write_all(d, **kw)` 的实参造出来（`skip` 少一条 / `extra` 多一条 /
            #   `broken` 那条非法 JSON）⇒ ★ 这里是**路径消毒**，没有"变换生效与否"可自证。
            d = base / name.replace("：", "_")
            write_all(d, **kw)
            r = check(d, WORKLOAD)
            cases.append((name, r["ok"] is False, r["problems"][:1]))

        #: ★ 正例：全 349 条合法 ⇒ 必须绿
        d = base / "正例"
        write_all(d)
        r = check(d, WORKLOAD)
        cases.append(("正例：349 条齐全 ⇒ 应绿", r["ok"] is True, r["problems"][:1]))

    print("★ 负例自检（判据 = 「坏输入必须红、好输入必须绿」）：")
    allok = True
    for name, passed, why in cases:
        print(
            "   %-26s %s  %s"
            % (name, "PASS" if passed else "**FAIL**", "" if passed else why)
        )
        allok = allok and passed
    print("★ 自检结论：%s" % ("全部通过" if allok else "★ 有失败 ⇒ 门禁不可信"))
    return 0 if allok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--records-dir", default=str(RECORDS))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()

    #: ★★ tier-aware：本轮产出落在**两个**目录（见 `check` 的 docstring）⇒
    #:   按"一个目录凑 349"判会**误报"缺 76 条"**（★ 我先写错、后改对）✓
    pairs = [
        (
            Path(a.records_dir)
            if a.records_dir
            else ROOT / "output" / "bunny-records-verify",
            "verify",
            273,
        ),
        (ROOT / "output" / "bunny-records-deep", "deep", 76),
    ]
    allok = True
    for d, task, expect in pairs:
        r = check(d, WORKLOAD, only_task=task)
        print("★ [%s 档] %s" % (task, d))
        print(
            "   记录数 %d / 期望 %d（workload 里该档条数）"
            % (r["records"], r["expected"])
        )
        if r["ok"]:
            print(
                "   ★★ **通过**：%d/%d、op 集合与 union-gap-v3 一致、全部合法 JSON"
                % (r["records"], expect)
            )
        else:
            allok = False
            print("   ★★ **不通过**：")
            for pr in r["problems"]:
                print("     · %s" % pr)
        print()
    return 0 if allok else 1


if __name__ == "__main__":
    raise SystemExit(main())
