"""★ 建**并集分母**：UI 功能（145 项）∪ 纯 API 功能（774 族）—— ★ 业主定的口径。

★ 业主 2026-10-03 的决定逐字：★「**分母就取并集，不管是 UI 的功能还是无 UI 的纯 API 功能，
  但凡是个功能，我就想要**」。
★ ★★ 所以本脚本做三件事：
  ① ★ 抽 **UI 侧**：`docs/user-feature-coverage.md` §九 的「完整清单（145 项 × 5 列）」；
  ② ★ 抽 **API 侧**：`C:\\swapi\\types\\` 的接口族（★ 与 `tools/gen_family_coverage.py` 同源）；
  ③ ★★ **给出去重规则下的并集**，并**如实报出两个"粒度不一致"的地方**。
★ ★★★ 关键判断（★ 本脚本的核心，也是我必须说清的）：
  ★ **两个来源的"粒度"不一样** —— ★ UI 侧是**用户心智单位**（"画直线"、"拉伸"），
  ★ 而 API 侧的**族**是**接口**（`IFeatureManager` 一个族里 200+ 名成员，覆盖几十个功能）。
  ⇒ ★★ **直接取并集会严重低估"功能"数**（★ 因为 `IFeatureManager` 被当成 1 个）。
  ⇒ ★★★ 所以本脚本**同时算三个数**（★ 不挑一个好看的报）：
    · **N_ui** = 145（★ UI 心智单位）
    · **N_family** = 接口族数（★ 粗粒度：一族算一个功能）
    · **N_member_leaf** = **不重复成员名数**（★ 细粒度上界：一成员算一个"功能"）
  ★ 并集 = **N_ui ∪ N_family ∪ (member 里那些不属于任何已列功能族的新功能)** ——
  ★★ 而"哪些成员算独立功能"**需要一条判据**，★ 本脚本给出**候选判据 + 它的读数**，
    ★ **但把拍板留给 Lead/业主**（★ 这是判据设计，M3）。
★ 只读。产出 `output/union-denominator.json`。
"""
# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身
# 文件:   tools/build_union_denominator.py
# 定位:   建**并集分母**：UI 功能（145 项）∪ 纯 API 功能（774 族）—— ★ 业主定的口径。
# 官方依据: 官方源 `C:\swapi\types\**`（★ 逐条见文件内引用）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────

from __future__ import annotations

import json
import re
import sys
import time
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
REPO = Path(Path(__file__).resolve().parents[1])
SWAPI = Path(r"C:\swapi\types")
OUT = REPO / "output" / "union-denominator.json"

#: ★ 族里"不是功能"的形态（★ 纯数据 / 枚举 / 通知 —— ★ 它们不构成用户可指认的功能）
NON_FEATURE_IFACE = re.compile(
    r"^(I?)(Event|Events|Notify|Notification|Handler|Callback|Sink|"
    r"Enum|Constants?|Table|List|Array|Collection|Enumerator|Iterator|"
    r"Error|Errors|Status|Result|Info|Data\b.*$)", re.I)


def ui_items() -> list:
    """★ 抽 UI 侧 145 项：§九 的表 `| 域 | 功能 | … |`（★ 6 列）。"""
    f = REPO / "docs" / "user-feature-coverage.md"
    t = f.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"## 九 · 完整清单.*?\n(.*?)(?=\n## )", t, re.S)
    if not m:
        return []
    out = []
    for line in m.group(1).splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 3 or cells[0] in ("域", "") or set(cells[0]) <= set("-: "):
            continue
        out.append({"domain": cells[0], "feature": cells[1],
                    "ours": cells[2] if len(cells) > 2 else ""})
    return out


def families() -> dict:
    """★ 抽 API 侧：`C:\\swapi\\types\\<接口>\\*.md` ⇒ 族 → 成员名列表。"""
    out = {}
    for d in sorted(p for p in SWAPI.iterdir() if p.is_dir()):
        members = sorted(p.stem for p in d.glob("*.md"))
        if members:
            out[d.name] = members
    return out


def main() -> int:
    started = time.time()
    ui = ui_items()
    fam = families()
    n_ui, n_family = len(ui), len(fam)

    #: ★ 所有成员名（★ 不重复）
    all_members = set()
    for ms in fam.values():
        all_members |= set(ms)
    #: ★★ 剔除"明显不是功能"的族（★ 事件/枚举/容器/错误…）⇒ 得到"候选功能族"
    feature_fams = {k: v for k, v in fam.items() if not NON_FEATURE_IFACE.match(k)}
    dropped = sorted(set(fam) - set(feature_fams))
    #: ★★ 粗粒度：★ 一族算一个功能（★ 剔掉非功能族）
    n_family_feature = len(feature_fams)
    #: ★★★ 细粒度：★ 一成员算一个功能（★ 上界）
    n_member = len(all_members)

    #: ★ 并集（★ 粗粒度口径）：UI 项 ∪ 候选功能族
    #:   ★ 去重只能靠名字/词根近似 —— ★ 这里**只给出可复算的粗并集**，★ 精确去重需要判据（M3）
    ui_tokens = set()
    for it in ui:
        ui_tokens |= set(re.findall(r"[\u4e00-\u9fff]{2,}|[A-Za-z]{3,}", it["feature"]))
    overlap_guess = sorted(k for k in feature_fams
                           if any(tok.lower() in k.lower() for tok in ui_tokens))

    R = {
        "at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "口径": "并集（UI 功能 ∪ 纯 API 功能）—— 业主 2026-10-03 定",
        "N_ui": n_ui,
        "N_family_total": n_family,
        "N_family_feature_candidate": n_family_feature,
        "N_family_dropped_as_nonfeature": len(dropped),
        "N_member_unique": n_member,
        "dropped_examples": dropped[:24],
        "overlap_by_token_guess": len(overlap_guess),
        "overlap_examples": overlap_guess[:24],
        "union_coarse": n_ui + n_family_feature - len(overlap_guess),
        "★_三口径": {
            "粗（族算一个功能）": n_ui + n_family_feature - len(overlap_guess),
            "细下界（UI 145）": n_ui,
            "细上界（一成员一功能）": n_ui + n_member,
        },
        "★_粒度说明":
            "★ UI 侧是**用户心智单位**（画直线/拉伸），API 侧**族**是**接口** —— "
            "`IFeatureManager` 一族里 200+ 成员覆盖几十个功能 ⇒ 直接取并集会**严重低估**功能数。",
        "ui_items": ui,
        "feature_families": sorted(feature_fams),
    }
    OUT.write_text(json.dumps(R, ensure_ascii=False, indent=1), encoding="utf-8")

    print("★★★ 并集分母（三口径，★ 不挑一个好看的报）：")
    print("   ★ N_ui（UI 心智单位，现成的那份）            = **%d**" % n_ui)
    print("   ★ N_family（接口族总数）                     = **%d**" % n_family)
    print("   ★★ N_family_feature（剔掉非功能族后的候选）  = **%d**" % n_family_feature)
    print("   ★★ N_member_unique（不重复成员名，细粒度上界）= **%d**" % n_member)
    print()
    print("   ⇒ ★ **粗粒度并集** = %d + %d - %d（按词根粗估的重叠） = **%d**"
          % (n_ui, n_family_feature, len(overlap_guess),
             n_ui + n_family_feature - len(overlap_guess)))
    print("   ⇒ ★ **细粒度下界** = %d（UI 145）" % n_ui)
    print("   ⇒ ★ **细粒度上界** = %d + %d = **%d**" % (n_ui, n_member, n_ui + n_member))
    print()
    print("★ 被当作「非功能族」剔掉的（前 24）：")
    print("   " + ", ".join(dropped[:24]))
    print()
    print("★ 按词根粗估与 UI 重叠的族（前 24）：")
    print("   " + ", ".join(overlap_guess[:24]))
    print()
    print("★★ 产出:", OUT, "（%.1f s）" % (time.time() - started))
    print("★★★ 注意：★ 精确去重**需要一条判据**（何为「同一个功能」）—— ★ 那是判据设计（M3），★ 本脚本不拍板。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
