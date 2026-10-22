"""★ 批次②–⑥的**通用挖掘器**：扫指定目录，抽「可吸收的建模知识」，逐条判定。"""

# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库 / 文件 / 定位 / 官方依据 / 许可 / 覆盖
# 仓库:   本项目自身
# 文件:   tools/harvest_scan.py
# 定位:   规格 `specs/332-known-facts-triage` 的**批次②–⑥通用器**。★★ 业主 2026-10-14
#           授权全自动挖掘；★ 收口判据要求  「各批有明确的『已扫 / 已判断』结论」。★★ 判
#           据：**同一套分类规则**服务所有批次 ⇒ ★ 换批次不改代码。
# 官方依据: 本仓文件系统 + `tools/triage_known_facts.py` 的分类规则
# 许可:   本仓库 MIT。★ 无第三方代码引入。
# 覆盖:   全文件
# -----------------------------------------------------------------------------
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8")
ROOT = pathlib.Path(__file__).resolve().parents[1]

#: ★★ **五个批次**（★ 目录 + 后缀 + 说明）
BATCHES = {
    "② examples": (("examples",), (".py", ".json", ".md")),
    "③ apps": (("apps",), (".py", ".ts", ".tsx", ".rs", ".md")),
    "④ archive": (("archive",), (".py", ".md", ".txt")),
    "⑤ official-docs": (("AI Solidworks/官方文档/SWhelp/sldworksapi",), (".htm",)),
    "⑥ docs": (("docs",), (".md",)),
}

#: ★★ **"可吸收"的强判据** —— ★ 与 `triage_known_facts.py` 同一套词表
MODEL_ACTION = re.compile(
    r"(草图|几何关系|完全定义|约束|倒角|圆角|拉伸|旋转|切除|阵列|镜像|"
    r"孔|螺纹|槽|键槽|基准面|中心线|轮廓|拔模|抽壳|特征树|父子|"
    r"尺寸|标注|工程图|配合|装配)"
)

#: ★★ **"这是知识"的判据** —— ★ 有「不要/必须/优先/推荐」这类**规范语气**
NORMATIVE = re.compile(r"(不要|必须|应当|优先|推荐|避免|禁止|正确做法|惯例|最佳实践)")

#: ★ **"这是判据"的判据**
CRITERION = re.compile(r"(判据|回读|证据|验证|以.*为准|不能只看|才算)")

#: ★ **"这是过程记录"** ⇒ ★ 放过
PROCESS = re.compile(
    r"(轮 \d+|提交|commit|git |门禁|台账|规格 \d+|spec \d+|进度|盘点|"
    r"收口|验收|清单|统计|基线|ROADMAP|handoff)"
)


#: ★★ **已由批次①覆盖的文件**（★ 排除，免得重复计数）
#:   ⚠ 实测（2026-10-14）：`docs/known-facts.md` 就在 `docs/` 下 ⇒
#:     ★ 批次⑥把它又扫了一遍 ⇒ **重复计数** ✗
ALREADY_COVERED = {
    "docs/known-facts.md",
    "docs/dead-ends.md",
    "docs/harvest-digest.md",
    "docs/metrics.md",
    "docs/union-coverage-matrix.md",
    "docs/gate-inventory.md",
    "docs/union-level-audit.md",
}


def scan(batch: str) -> dict:
    dirs, exts = BATCHES[batch]
    files = []
    for d in dirs:
        for f in (ROOT / d).rglob("*"):
            if f.is_file() and f.suffix.lower() in exts:
                #: ★ 跳过**生成的**文件（★ 它们不是"既有知识"，是产物）
                rel = str(f.relative_to(ROOT)).replace("\\", "/")
                if rel in ALREADY_COVERED:
                    continue
                files.append(f)
    absorb, pass_, skip = [], [], 0
    for f in files:
        try:
            t = f.read_text(encoding="utf-8", errors="replace")
        except OSError:
            skip += 1
            continue
        for ln, line in enumerate(t.splitlines(), 1):
            s = line.strip()
            if not (12 < len(s) < 240):
                continue
            #: ★ 剥掉常见注释前缀
            s2 = re.sub(r"^(#|//|/\*|\*|<!--|>)\s*", "", s).strip()
            if not s2 or len(s2) < 12:
                continue
            has_model = bool(MODEL_ACTION.search(s2))
            has_norm = bool(NORMATIVE.search(s2))
            has_crit = bool(CRITERION.search(s2))
            if has_model and (has_norm or has_crit) and not PROCESS.search(s2):
                absorb.append((str(f.relative_to(ROOT)), ln, s2))
            elif PROCESS.search(s2):
                pass_.append((str(f.relative_to(ROOT)), ln, s2))
            else:
                pass_.append((str(f.relative_to(ROOT)), ln, s2))
    return {"files": len(files), "skip": skip, "absorb": absorb, "pass": pass_}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", default="all")
    ap.add_argument("--show", type=int, default=0)
    args = ap.parse_args()
    which = list(BATCHES) if args.batch == "all" else [args.batch]
    summary = {}
    for b in which:
        r = scan(b)
        #: ★★ 去重（★ 同一条文字可能在多份文件里）
        seen, uniq = set(), []
        for f, ln, s in r["absorb"]:
            k = re.sub(r"[\s*`「」]", "", s)[:60]
            if k in seen:
                continue
            seen.add(k)
            uniq.append((f, ln, s))
        summary[b] = {
            "files": r["files"],
            "skip": r["skip"],
            "absorb": len(r["absorb"]),
            "absorb_uniq": len(uniq),
            "pass": len(r["pass"]),
        }
        print(
            "★ %-18s 文件 %5d · 该吸收 %4d（去重 %4d）· 放过 %6d"
            % (b, r["files"], len(r["absorb"]), len(uniq), len(r["pass"]))
        )
        if args.show:
            print()
            for f, ln, s in uniq[: args.show]:
                print("   %s:%d" % (f, ln))
                print("      %s" % s[:150])
            print()
    out = ROOT / "output" / "harvest-scan.json"
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
    print()
    print("★ ⇒ %s" % out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
