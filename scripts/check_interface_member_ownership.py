r"""@brief 接口归属检查 —— 装上**可核验的 `CONST → 接口` 映射表**，补上已知事实 36 的盲点。

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   SolidWorks 官方 API 文档（`C:\swapi\`）+ 出厂类型库反射
# 文件:   `types\IFeatureManager\CreateDefinition.md` 的 Parameters 段
#           ⇒ 常量的**官方括注**（如 `swFmSMGusset (sheet metal gusset)`）
#         `types\<接口>\_overview.md` 的 **Description** 段
#           ⇒ 接口的**官方描述**（如 "Allows access to a sheet metal gusset feature."）
#         `D:\AI\SW\_raw\**\enum_values_sldworks.txt` ⇒ 常量数值（反查用）
#         `D:\AI\SW\gen_const_iface_map.py`（第 30 轮的生成器，**本工具内联同一判据**）
# 定位:   三件事叠在一起才做对，前两轮各错一次：
#
#   **① 第 29 轮：判据错。** 当时用「成员交集为空」—— **抓不到「整体用错接口」那一类**
#      （已知事实 42 的**否定结果**：种负例后仍报 PASS，因为那套名字**互相自洽**）。
#      **⇒ 唯一能抓的办法是知道**期望的接口**是哪个 ⇒ 需要 `CONST → 接口` 映射表。**
#
#   **② 第 29 轮：两处形状不匹配。**
#      · `CreateDefinition` 实际是 `get_com_member(m, "CreateDefinition", 35)`
#        （**字符串+逗号**），我的正则只认括号形式 ⇒ 一个都没匹配到；
#      · 成员设在**嵌套函数** `def _apply(data):` 里（**有缩进**），我的 `^def` 只认顶格。
#
#   **③ 第 29 轮：假绿。** `检查过 0 个` 却报 PASS。本工具**保留**这条守卫
#      （检查量为 0 时返回非 0）—— 与 `audit_byref_args.py` 的「≥300」同源。
#
# ## 判据（**期望接口**，不是交集启发式）
# ```
# data = CreateDefinition(<CONST>)          ⇒ 由映射表查 CONST 的**期望接口**
# data.X = ... / data.X(...)                ⇒ X **必须在该接口的成员集里**
# ```
#
# ## ⚠ 本工具的定位（**诊断**，不是门禁）
# 映射表来自**官方文本匹配**，**有歧义与未映射的洞**
# （第 30 轮：20 唯一 / 4 歧义 / 11 未映射 ⇒ **第 39 轮消歧到 24/0/11**
#   ⇒ **第 41 轮加 `MANUAL_MAP` 到 31 唯一（自动 24 + 人工确证 7）/ 0 歧义 / 4 未映射**）。
# **⇒ 它报 `[HIT]` 时值得看；但没有命中**不等于**归属一定正确。**
# **⇒ 一个覆盖不全的门禁会让人以为防住了** —— 所以它不冒充门禁。
#
# ## ⚠ 与 `check_member_names.py` 的分工（**不重造**）
# * 门禁那个：判「名字在**某个**接口里存在」—— 快、全仓、无外部依赖。
# * **本工具**：判「名字在**这个**接口里存在」—— 需官方文档树，覆盖窄但更深。
# **⇒ 互补，不互相替代。**
#
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 纯静态（读官方 markdown + 源码），**不连 SolidWorks**，**不写任何文件**。
# 覆盖:   全文件
# ────────────────────────────────────────────────────────────────────
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

#: 2026-10-03（接手轮）强制 stdout 为 UTF-8 —— 本门禁会 print 中文与箭头/勾这类符号，
#:   而 stdout 是管道时（测试正是用管道抓输出）默认按 locale（本机 GBK）编码
#:   ⇒ UnicodeEncodeError: 'gbk' codec can't encode character … ⇒ 门禁自己崩掉。
#:   known-facts 58 那一族（中文 Windows 上两侧默认编码不一致 —— 病灶在输出侧）；
#:   而测试那侧的 subprocess.run 已经带了 encoding='utf-8'。
sys.stdout.reconfigure(encoding="utf-8")

REPO = Path(__file__).resolve().parent.parent
SWAPI = Path(r"C:\swapi")
TYPES = SWAPI / "types"
CD_DOC = TYPES / "IFeatureManager" / "CreateDefinition.md"
RAW = Path(Path(__file__).resolve().parents[1] / "_raw")

#: ★★ **官方 `CreateDefinition` 宿主页清单**（spec 238）—— 官方**不止一个** `CreateDefinition`
#: 方法：`IFeatureManager::CreateDefinition` 与 `IMotionStudy::CreateDefinition`，
#: 两者各有**自己的** `Type` 常量域。旧实现只认第一个 ⇒ 把宿主没表达出来
#: （`sw_motion.py` 的站点宿主是 `IMotionStudy`，却被拿去查 `IFeatureManager` 的表）。
CD_HOSTS = ("IFeatureManager", "IMotionStudy")
#: `{宿主: CreateDefinition.md}`（`TYPES` 变动后由 `_cimo()` 之类的调用方重算）。
CD_DOCS: dict = {_h: TYPES / _h / "CreateDefinition.md" for _h in CD_HOSTS}

IGNORE = {"AccessSelections", "ReleaseSelectionAccess", "GetType", "GetTypeName2"}
CD_PAREN = re.compile(r"\bCreateDefinition\s*\(")
CD_STR = re.compile(r"[\"']CreateDefinition[\"']")
ASSIGN = re.compile(r"^\s*(\w+)\s*=\s*(.*)$")

#: ⚠⚠ **不要用行窗口** —— 第 29 轮与第 38 轮**各踩一次**：
#: `data` 这个变量名在**多个 `_apply(data)` 嵌套函数**里复用
#: ⇒ 一个 `WINDOW = 400` 的行窗口把**别的特征**的成员也算了进来
#:   （实测：base flange 那个站点把 edge flange / draft / **gusset** 的成员全吞了，
#    报出 6 个假阳性）。**⇒ 范围必须贴合代码的**组织单元**：所在函数。**


#: 靠**人工确证表**（`MANUAL_MAP`）补上的常量 —— **不是推断**，输出时与自动结果**分开报**
MANUAL_USED: set = set()

#: ── **人工确证的补充映射**（**不是推断**）─────────────────────────────
#: 自动映射（`build_map` 的官方文本匹配）覆盖不到、但**已逐条读官方描述确认**的常量。
#: **⚠ 每条都写明依据；没有依据的不许进来。**
#: **⚠⚠ 本表与自动结果在输出里**分开统计**** —— 免得有人把人工条当成推断产物
#: （第 40 轮正是这么错的：用启发式硬凑，连续改 6 版都不对，最后回退）。
#: 证据与「待核」清单见 `docs/T-040-unmapped-constants-evidence.md`。
MANUAL_MAP: dict = {
    # 描述 `Allows access to a sweep feature.`
    "swFmSweep": "ISweepFeatureData",
    # 同 `swFmSweep` —— **扫掠切除与扫掠共用同一个 FeatureData**（名字里的 `Cut` 不改变类型）
    "swFmSweepCut": "ISweepFeatureData",
    # ⚠ **领域判断**：`sweep thread` 是**螺纹**（用扫掠方式生成），不是扫掠特征。
    #   描述 `Allows access to a thread feature.` ⇒ 不是纯文本匹配能得到的。
    "swFmSweepThread": "IThreadFeatureData",
    # `…a derived pattern feature.`（对照候选 `IDerivedPartFeatureData` 是 `…a derived part feature.`）
    "swFmDerivedLPattern": "IDerivedPatternFeatureData",
    # 名字唯一命中；描述 `Allows access to a table pattern feature.`
    "swFmTablePattern": "ITablePatternFeatureData",
    # 名字唯一命中；与 `swFmLibraryFeature` 的消歧结论互相印证。
    # ⚠ 2026-10-01 轮 44：**已"升级"** —— `ILibraryFormToolFeatureData` 的 `_overview.md`
    #   里**官方直接点名** `swFmFormToolInstance` ⇒ 现在由 `officially_named()` 给出
    #   （**官方断言 > 人工确证**），故从本表移出。**留下的这条注释是记录这次升级。**
    # `IDimPatternFeatureData` desc: "Allows access to a **variable pattern** feature,
    #   which uses a **table to store the dimensions** and values…"
    #   ⇒ 括注 "variable/dimension pattern" 的**两个词都对上**（variable + dimension）
    "swFmDimPattern": "IDimPatternFeatureData",
    # `…a mirror component feature.`；对照：Part / Pattern / Solid 三个同族接口
    "swFmMirrorComponent": "IMirrorComponentFeatureData",
    # ★★ 2026-10-01（轮 48）：`swFmRefSurface` —— **官方 Returns 段逐字列出**，不是文本推断：
    #   `ISweepFeatureData/SweepType.md` 的 ## Returns 写着
    #     「Sweep type as defined in [[swFeatureNameID_e]]:
    #        - swFmSweep (swept boss)
    #        - swFmSweepCut (swept cut)
    #        - **swRefSurface (swept surface)**」
    #   ⇒ **同一个接口，前端靠 `SweepType` 分 boss/cut/surface** ⇒ `swFmRefSurface` ⇒ `ISweepFeatureData`。
    #   ★ 三条**独立佐证**：① 该接口 `_overview.md` 的官方示例就叫
    #     **"Insert **Swept-surface** Feature (VBA)"**；② 官方括注是 `(surface sweep)`；
    #     ③ 全 swapi 里**没有**任何 `ISurfaceSweep*` 接口（候选里只有 `ISweepFeatureData`）。
    #   ★ **同一条证据顺带官方确认了本表已有的 `swFmSweep` / `swFmSweepCut`** ——
    #     它们从「人工确证」升到**有官方 Returns 段背书**（依据变硬，结论不变）。
    "swFmRefSurface": "ISweepFeatureData",
}


def _norm(s: str) -> str:
    """规范化：小写、去标点、去冠词、压缩空白 —— 只用于**比对**。"""
    s = s.lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    s = re.sub(r"\b(a|an|the|of|to|for|and|or)\b", " ", s)
    return re.sub(r"\s+", " ", s).strip()


#: 靠**官方概览直接点名**定下来的常量（**最强证据** —— 官方断言，不是推断）
OFFICIAL_NAMED: set = set()


def officially_named() -> dict:
    """@brief 取**官方接口概览里直接点名**的 `CONST → 接口` 映射（**最强证据**）。

    # ── 来源 ─────────────────────────────────────────────────────────
    # 仓库:   SolidWorks 官方 API 文档（`C:\\swapi\\types\\<接口>\\_overview.md`）
    # 定位:   ★★ **三条映射来源里**最硬**的一条**（2026-10-01，轮 44 发现）：
    #         官方有时在接口自己的 `_overview.md` 里**逐字写出**它就是哪个
    #         `CreateDefinition` 的类型。实例（`ISimpleFilletFeatureData2`）：
    #           「To create a simple fillet feature: 1. Call [[IFeatureManager::CreateDefinition]],
    #             passing Type = [[swFeatureNameID_e]].**swFmFillet**, to create an instance of
    #             **ISimpleFilletFeatureData2**.」
    #         **⇒ 这比「拿括注去匹配描述」硬得多 —— 它是官方**断言**，不是**推断**。**
    #
    #   **三条来源的优先级（本函数排第一）**：
    #     ① **官方点名**（本函数）—— 官方断言
    #     ② 官方文本匹配（`build_map` 的主体）—— 对官方 prose 的推断
    #     ③ `MANUAL_MAP`（人工确证）—— 兜底
    #
    #   ⚠ **覆盖窄**：35 个常量里只有 **5 条**用了这种写法
    #     （`swFmFillet` / `swFmFormToolInstance` / `swFmNormalCut` / `swFmRefCurve` /
    #      `swFmSolidToSheetMetal`）。**⇒ 可靠但稀疏。**
    #   ★ **可信度已交叉验证**：其中 3 条与**别的来源独立得出同一答案**
    #     （`swFmRefCurve` / `swFmFormToolInstance` / `swFmNormalCut`）⇒ **3/3 一致**。
    #   ⚠ **多命中不取**（与别处同一条纪律：唯一才用）。
    # ────────────────────────────────────────────────────────────────
    """
    out: dict = {}
    if not TYPES.is_dir() or not CD_DOC.is_file():
        return out
    consts = set(re.findall(r"^\s*-\s*(swFm\w+)\s*\(", CD_DOC.read_text(encoding="utf-8"), re.M))
    for d in sorted(TYPES.iterdir()):
        if not d.is_dir() or not d.name.startswith("I"):
            continue
        f = d / "_overview.md"
        if not f.is_file():
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        for c in consts:
            if re.search(r"\b%s\b" % c, text):
                out.setdefault(c, set()).add(d.name)
    return {c: sorted(v)[0] for c, v in out.items() if len(v) == 1}


def host_pages() -> dict:
    """⇒ ``{常量: {宿主: 官方点名的返回接口}}`` —— 只收**逐条点名**的条目（spec 238）。

    # ── 来源 ─────────────────────────────────────────────────────────
    # 仓库:   SolidWorks 官方 API 文档（`C:\\swapi\\types\\<宿主>\\CreateDefinition.md`）
    # 定位:   ★★ 官方**两个** `CreateDefinition` 宿主页的 `## Parameters` 段格式**不同**：
    #           · `IFeatureManager`：`- swFmBaseFlange (sheet metal base flange)` —— **散文标签**
    #           · `IMotionStudy`  ：`- swFmAEMGravity ([[ISimulationGravityFeatureData]])` —— **点名接口**
    #         ⇒ 本函数只认**后者**（`swFmX ([[IIface]])`），因为那是**官方断言**（最强证据）。
    #         ★ 散文标签那一侧继续走 `build_map()` 的文本匹配（那是**推断**）。
    #   ⚠ **多宿主点名不一致**时不在这里裁决（留给 `check_cd_host_scope.py` 判红）。
    # ────────────────────────────────────────────────────────────────
    """
    out: dict = {}
    for host, doc in CD_DOCS.items():
        if not doc.is_file():
            continue
        text = doc.read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r"^\s*-\s*(swFm\w+)\s*\(\[\[(\w+)\]\]\)\s*$", text, re.M):
            out.setdefault(m.group(1), {})[host] = m.group(2)
    return out


def host_consts() -> dict:
    """⇒ ``{常量: [收录它的官方宿主页]}``（**所有** `CreateDefinition` 页的 `Type` 清单）。

    ★★ 用途：回答「这个常量**属于哪个**宿主」—— 与「它映射到哪个接口」是**两件事**。
    旧实现把两件事合成一件 ⇒ `sw_motion.py` 的站点被拿去查**别的宿主**的表。
    """
    out: dict = {}
    for host, doc in CD_DOCS.items():
        if not doc.is_file():
            continue
        text = doc.read_text(encoding="utf-8", errors="replace")
        for c in re.findall(r"^\s*-\s*(swFm\w+)\s*\(", text, re.M):
            out.setdefault(c, [])
            if host not in out[c]:
                out[c].append(host)
    return out


def build_map() -> tuple:
    """从**官方文本**造 `CONST → 接口` ⇒ ``(mapped, ambiguous, unmapped)``。

    **⚠ 多命中记歧义（不猜）、零命中记未映射（不编）。**
    """
    mapped: dict = {}
    ambiguous: dict = {}
    unmapped: list = []
    #: 靠**名字回退**定下来的常量（**弱信号**）—— 单独标出来
    name_based: set = set()
    #: 靠**人工确证表**（`MANUAL_MAP`）补上的常量 —— **不是推断**，单独统计
    manual_used: set = set()
    if not CD_DOC.is_file() or not TYPES.is_dir():
        return mapped, ambiguous, unmapped
    consts = {m.group(1): m.group(2).strip()
              for m in re.finditer(r"^\s*-\s*(swFm\w+)\s*\(([^)]*)\)\s*$",
                                   CD_DOC.read_text(encoding="utf-8"), re.M)}
    if not consts:
        return mapped, ambiguous, unmapped
    ifaces: dict = {}
    for d in TYPES.iterdir():
        if not d.is_dir() or not d.name.startswith("I"):
            continue
        f = d / "_overview.md"
        if not f.is_file():
            continue
        t = f.read_text(encoding="utf-8", errors="replace")
        m = re.search(r"##\s*Description\s*\n+(.+?)(?=\n##|\Z)", t, re.S)
        if m:
            ifaces[d.name] = " ".join(m.group(1).split())
    # ★★ **① 官方点名（最强证据）—— 在文本匹配**之前**应用，其余来源不得覆盖它**
    #    （位置必须在这里：`ifaces` 刚建好。第一版把它放在 `ifaces` 之前 ⇒ 名字都不存在。）
    for _c, _i in officially_named().items():
        if _i in ifaces:
            mapped[_c] = _i
            OFFICIAL_NAMED.add(_c)
    # ★★ **①′ 官方宿主页逐条点名**（spec 238）—— 与 ① 同为**官方断言**，优先级相同。
    #    `IMotionStudy/CreateDefinition.md` 的 `Type` 清单**每条都带 `[[返回接口]]`** ⇒
    #    直接采用，**不做文本匹配**（那是推断）。★ 多宿主点名不一致 ⇒ 不取，留给
    #    `check_cd_host_scope.py` 报 `ambiguous-host`（门禁**不自动挑选约定**）。
    for _c, _hosts in host_pages().items():
        _vals = sorted(set(_hosts.values()))
        if len(_vals) == 1 and _vals[0] in ifaces:
            mapped[_c] = _vals[0]
            OFFICIAL_NAMED.add(_c)
    for cname, cdesc in consts.items():
        # ⚠ **官方点名的条目不得被文本匹配覆盖**（官方断言 > 推断）
        if cname in OFFICIAL_NAMED:
            continue
        key = _norm(cdesc)
        if not key:
            if cname not in mapped:
                unmapped.append(cname)
            continue
        hits = [i for i, d in ifaces.items() if key in _norm(d)]
        if len(hits) > 1:
            # ── **消歧**：两条规则，都从**官方描述**读出（不是挑一个看起来对的）
            #   ① **含 "group" 的是子项** ⇒ 排除。官方证据：
            #      `ISMNormalCutGroupData` = "…a normal cut **feature's cut-extrude face group**"
            #      `ITabAndSlotGroupData`  = "…a tab and slot **feature group**"
            #      ⇒ 它们是**别的接口**的子对象，**不是 `CreateDefinition` 返回的那个**。
            #   ② 剩下的里**含 "feature" 者优先**。官方证据：
            #      `ICornerReliefFeatureData` = "…corner relief **feature data**"
            #      `ISMCornerReliefData`      = "…corner relief **data**"（**少了 feature**）
            noword = [i for i in hits if "group" not in _norm(ifaces[i]).split()]
            if len(noword) == 1:
                hits = noword
            else:
                withf = [i for i in noword if "feature" in _norm(ifaces[i]).split()]
                if len(withf) == 1:
                    hits = withf
                elif len(withf) > 1:
                    # ③ **兜底**（**证据较弱**，故排在最后）：
                    #    取描述**比常量括注多出的词最少**者 ——
                    #    `CreateDefinition` 的括注是那个类型的**短官方标签**，
                    #    描述离它最近的那个更可能是它。
                    #    实例：`swFmLibraryFeature (library)` ⇒
                    #      `ILibraryFeatureData`           = "library feature data"（+2 词）
                    #      `ILibraryFormToolFeatureData`   = "library forming tool feature data"（+4 词）
                    #    ⇒ 选前者。
                    #    ⚠ **本规则是启发式**，不如 ①② 硬 —— 因此**排在最后**，
                    #      且仅在 ①② 之后仍多命中时才用。
                    base = set(_norm(cdesc).split())
                    ranked = sorted(withf, key=lambda i: len(set(_norm(ifaces[i]).split()) - base))
                    if len(ranked) >= 2 and (
                            len(set(_norm(ifaces[ranked[0]]).split()) - base)
                            < len(set(_norm(ifaces[ranked[1]]).split()) - base)):
                        hits = [ranked[0]]
        if len(hits) == 1:
            mapped[cname] = hits[0]
        elif len(hits) > 1:
            ambiguous[cname] = hits
        else:
            unmapped.append(cname)
    # ── **人工确证的补充映射**：只在自动匹配**没给出结论**时补上。
    #    ⚠ **绝不覆盖**自动结果（自动有官方文本依据，优先级更高）。
    for _c, _i in MANUAL_MAP.items():
        if _c not in mapped and _c not in ambiguous and _i in ifaces:
            mapped[_c] = _i
            MANUAL_USED.add(_c)
            if _c in unmapped:
                unmapped.remove(_c)
    return mapped, ambiguous, unmapped


def enum_values() -> dict:
    """`{swFm*: 数值}`（反射转储）—— 用于把模块常量反查回 `swFm*` 名。"""
    for r in RAW.rglob("enum_values_sldworks.txt"):
        try:
            return dict(re.findall(r"(swFm\w+)\s*[=:,]\s*(-?\d+)",
                                   r.read_text(encoding="utf-8", errors="replace")))
        except OSError:
            pass
    return {}


def module_consts(path: Path) -> dict:
    """同文件里的 `SW_FM_X = <int>` ⇒ ``{常量名: 数值}``。

    ★★★ **2026-10-09（spec 237）：正则宽化到容忍行尾注释** —— 旧正则要求常量行
    **以数字结尾**（`\\s*$`）⇒ `SW_FM_MATE_PROFILE_CENTER = 101  # swFmMateProfileCenter`
    **一律读不到** ⇒ 整文件常量表成了 `{}` ⇒ `scripts/sw_weldment.py` 唯一的
    `CreateDefinition` 站点被**静默判成「常量解析不出」**（读数 `no-const 1`）。
    ★ 这是「**窄读取器读出 0 也会骗人**」的第七次（spec 233/234/230 同族）。
    ⇒ 现在允许 `[ \t]*(#.*)?$`。★ 能红的判据：
    `tests/test_cd_site_disposition.py::test_module_consts_reads_trailing_comment`。
    """
    try:
        return {m.group(1): m.group(2)
                for m in re.finditer(r"^[ \t]*([A-Z][A-Z0-9_]*)[ \t]*=[ \t]*(\d+)[ \t]*(?:#.*)?$",
                                     path.read_text(encoding="utf-8"), re.M)}
    except OSError:
        return {}


def cd_calls(path: Path) -> list:
    """``var = ...CreateDefinition(<实参>)...`` ⇒ ``[(var, 行号, 实参文本)]``（**两种写法**）。"""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    out = []
    for i, line in enumerate(lines):
        m = ASSIGN.match(line)
        if not m:
            continue
        var, rhs = m.group(1), m.group(2)
        if not (CD_PAREN.search(rhs) or CD_STR.search(rhs)):
            continue
        arg = ""
        mm = re.search(r"[\"']CreateDefinition[\"']\s*,\s*([^)\s]+)", rhs)
        if mm:
            arg = mm.group(1)
        else:
            mm = re.search(r"CreateDefinition\s*\(([^)]*)\)", rhs)
            if mm:
                arg = mm.group(1).strip()
        out.append((var, i + 1, arg))
    return out


def to_const(arg: str, consts: dict, byval: dict) -> str:
    """把实参文本解析成 `swFm*` 名（支持 `35` / `SW_FM_X` / `swFeatureNameID_e.swFmX`）。"""
    a = (arg or "").strip()
    for name in re.findall(r"\b(swFm\w+)\b", a):
        return name
    val = consts.get(a) or (a if re.fullmatch(r"-?\d+", a) else None)
    if val is None:
        return ""
    for k, v in byval.items():
        if str(v) == str(val):
            return k
    return ""


def enclosing_range(lines: list, start: int) -> tuple:
    """返回 ``(起, 止)`` —— `start` 行**所在函数**的行范围（0-based，含首不含尾）。

    ⚠ **第 29 轮与第 38 轮各踩一次**：用「行窗口」会把**同名的 `data` 变量**
    在别的函数里的用法也算进来 ⇒ **假阳性**。
    **⇒ 判据：从 `start` 往回找最近的顶格 `def`；再往后找下一个缩进 <= 它的 `def`。**
    """
    def_line = None
    for i in range(start, -1, -1):
        if re.match(r"^def\s", lines[i]):
            def_line = i
            break
        if lines[i] and not lines[i][0].isspace() and not lines[i].startswith(("#", ")", "]", "}")):
            break
    if def_line is None:
        return max(0, start - 40), min(len(lines), start + 40)
    end = len(lines)
    for j in range(def_line + 1, len(lines)):
        m = re.match(r"^(\s*)def\s", lines[j])
        if m and len(m.group(1)) == 0:
            end = j
            break
        if lines[j] and not lines[j][0].isspace() and not lines[j].startswith(("#", ")", "]", "}")):
            end = j
            break
    return def_line, end


def enclosing_func_name(lines: list, start: int) -> str:
    """`start` 行**所在函数**的名字（找不到返回空串）。"""
    for i in range(start, -1, -1):
        m = re.match(r"^def\s+(\w+)", lines[i])
        if m:
            return m.group(1)
        if lines[i] and not lines[i][0].isspace() and not lines[i].startswith(("#", ")", "]", "}")):
            break
    return ""


def calls_of(lines: list, fname: str) -> list:
    """找 `fname(` 的**调用点** ⇒ ``[(行号(1-based), 实参文本列表)]``。

    ⚠ **为什么必须跟着调用走**：本项目把常量当**形参**传 ——
    `_create_from_definition(model, SW_FM_SM_GUSSET, _apply)`
    ⇒ `CreateDefinition(int(fm_type))` 里的 `fm_type` **在函数体内定不下来**，
    **只有调用点的实参才给出常量**。第 38 轮第一版没做这步 ⇒
    `swFmSMGusset`/`swFmEdgeFlange`/`swFmSketchBend` 三个站点**全被跳过**。
    """
    out = []
    pat = re.compile(r"\b%s\s*\(" % re.escape(fname))
    for i, line in enumerate(lines):
        if not pat.search(line) or re.match(r"^\s*def\s", line):
            continue
        inner = line[line.find("(") + 1:]
        depth, buf, args = 1, "", []
        for ch in inner:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth == 0:
                    break
            if ch == "," and depth == 1:
                args.append(buf.strip())
                buf = ""
            else:
                buf += ch
        if buf.strip():
            args.append(buf.strip())
        out.append((i + 1, args))
    return out


def param_index(lines: list, fname: str, pname: str) -> int:
    """`fname` 的形参 `pname` 是第几个（0-based）；找不到返回 -1。"""
    for line in lines:
        m = re.match(r"^def\s+%s\s*\(([^)]*)\)" % re.escape(fname), line)
        if m:
            plist = [x.strip().split(":")[0].split("=")[0].strip()
                     for x in m.group(1).split(",")]
            return plist.index(pname) if pname in plist else -1
    return -1


def members_of(iface: str) -> set:
    d = TYPES / iface
    if not d.is_dir():
        return set()
    return {f.stem for f in d.glob("*.md") if f.stem != "_overview"}


#: ★★ **站点处置码（封闭词表）** —— spec 237 抽出。
#: 旧实现把四种语义**完全不同**的处置**合成一个 `跳过 N`**（静默降级）：
#: `no-const`（可能只是读取器太窄）/ `unmapped`（该审却漏审）/ `empty-members`（数据源缺）/
#: `no-members-used`（确实无事可查）。合成之后，**一次把 `checked` 退化成 `unmapped` 的回归
#: 完全不可见**（读数仍是「跳过 5→6」）。⇒ 分开报，并由
#: `scripts/check_create_definition_site_disposition.py` 逐站点要求表态。
SITE_CODES = ("checked", "unmapped", "empty-members", "no-members-used", "dynamic")


def scan_sites(paths) -> list:
    """⇒ **逐站点处置记录**（spec 237 从 `main()` 抽出；口径**不重写**，只搬家）。

    每条 = `{"path", "line", "var", "arg", "const", "code", "used", "bad", "why", "arg_texts"}`：
    · `line`  = `CreateDefinition(...)` **调用行**（同一行可产生多条计划）；
    · `code`  ∈ `SITE_CODES`；`const` 为 `None` 表示 `dynamic`；
    · `arg_texts` = 解析常量时**实际看过的实参文本**（`dynamic` 的自证要用它 ——
      ★ 它必须包含**调用点**的实参文本，否则「读取器太窄」这条守卫会失效）。
    """
    byval = enum_values()
    mapped, _ambiguous, _unmapped = build_map()
    #: ★ spec 238：站点**属于哪个官方宿主页**（与「映射到哪个接口」是两件事）。
    hconsts = host_consts()
    out: list = []
    for t in paths:
        t = Path(t)
        if not t.is_file():
            continue
        consts = module_consts(t)
        calls = cd_calls(t)
        if not calls:
            continue
        try:
            lines = t.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for var, line_no, arg in calls:
            # ⚠⚠ **形参驱动的站点必须展开成 N 个检查**（每个调用点一次）。
            const0 = to_const(arg, consts, byval)
            plans = []          # [(常量, [要收集的范围], 说明)]
            arg_texts = [arg or ""]
            if const0:
                plans.append((const0, [enclosing_range(lines, line_no - 1)], "块内"))
            else:
                fn = enclosing_func_name(lines, line_no - 1)
                ids = re.findall(r"\b([A-Za-z_]\w*)\b", (arg or ""))
                pname = next((x for x in ids if x not in ("int", "float", "str")), "")
                pi = param_index(lines, fn, pname) if (fn and pname) else -1
                if fn and pi >= 0:
                    base = enclosing_range(lines, line_no - 1)
                    for cl, args in calls_of(lines, fn):
                        if pi >= 0 and pi < len(args):
                            arg_texts.append(args[pi])
                            c2 = to_const(args[pi], consts, byval)
                            if c2:
                                plans.append((c2, [base, enclosing_range(lines, cl - 1)],
                                              "调用点 L%d" % cl))
            if not plans:
                out.append({"path": t, "line": line_no, "var": var, "arg": arg,
                            "const": None, "code": "dynamic", "used": 0, "bad": 0,
                            "why": "块内", "arg_texts": arg_texts, "hosts": []})
                continue
            pat = re.compile(r"\b%s\s*\.\s*(\w+)\s*(?:=[^=]|\()" % re.escape(var))
            for const, ranges, why in plans:
                rec = {"path": t, "line": line_no, "var": var, "arg": arg, "const": const,
                       "code": "checked", "used": 0, "bad": 0, "why": why,
                       "arg_texts": arg_texts, "hosts": hconsts.get(const, [])}
                iface = mapped.get(const)
                if not iface:
                    rec["code"] = "unmapped"
                    out.append(rec)
                    continue
                members = members_of(iface)
                if not members:
                    rec["code"] = "empty-members"
                    out.append(rec)
                    continue
                used = {}
                for rlo, rhi in ranges:
                    for j in range(rlo, min(rhi, len(lines))):
                        for m in pat.finditer(lines[j]):
                            if m.group(1) not in IGNORE:
                                used.setdefault(m.group(1), j + 1)
                rec["used"] = len(used)
                rec["bad_members"] = sorted(mm for mm in used if mm not in members)
                rec["bad"] = len(rec["bad_members"])
                rec["members"] = sorted(used)
                rec["iface"] = iface
                if not used:
                    rec["code"] = "no-members-used"
                out.append(rec)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="接口归属检查（期望接口判据）")
    ap.add_argument("--glob", default="scripts/*.py")
    ap.add_argument("--all", action="store_true", help="连 tools/ 一起扫")
    a = ap.parse_args(argv)

    mapped, ambiguous, unmapped = build_map()
    if not mapped:
        print("[SKIP] 官方文档树不在（`%s`）—— **缺数据源不算违规**" % TYPES)
        return 0
    _auto = len(mapped) - len(MANUAL_USED)
    _named = len(OFFICIAL_NAMED)
    _manual = len(MANUAL_USED)
    _auto = len(mapped) - _manual - _named
    print("`CONST → 接口` 映射表：唯一命中 **%d**"
          "（**官方点名** %d + **文本匹配** %d + **人工确证** %d）/ 歧义 %d / 未映射 %d"
          % (len(mapped), _named, _auto, _manual, len(ambiguous), len(unmapped)))
    print("  ⚠ **三类证据强度递减**：官方点名（官方**断言**）> 文本匹配（对官方 prose 的**推断**）"
          "> 人工确证（我逐条读过官方描述）")
    if OFFICIAL_NAMED:
        print("     ★ 官方点名 %d 条：%s" % (_named, " ".join(sorted(OFFICIAL_NAMED))))
    if MANUAL_USED:
        print("     · 人工确证 %d 条：%s" % (_manual, " ".join(sorted(MANUAL_USED))))
    targets = sorted(REPO.glob(a.glob))
    if a.all:
        targets += sorted(REPO.glob("tools/*.py"))

    #: ★ spec 237：取点循环搬进 `scan_sites()`（口径不变），此处只做**分码汇总**。
    sites = scan_sites(targets)
    codes: dict = {}
    for s in sites:
        codes[s["code"]] = codes.get(s["code"], 0) + 1
    checked = codes.get("checked", 0)
    skipped = len(sites) - checked
    problems = [(s["path"].name, s["why"], s["const"], s["iface"],
                 [(m, 0) for m in s["bad_members"]])
                for s in sites if s["code"] == "checked" and s["bad"]]

    print("扫描 %d 个文件；**检查过 %d 个 `CreateDefinition` 站点**；跳过 %d"
          "（映射表没有 / 成员集空 / 没收集到成员）" % (len(targets), checked, skipped))
    #: ★★ **分码明细** —— 旧实现把四种处置合成一个数（静默降级，spec 237）。
    print("  ★ 分码：%s" % " · ".join("%s %d" % (c, codes.get(c, 0)) for c in SITE_CODES))
    for s in sites:
        if s["code"] != "checked":
            print("     [%s] %s:%d  const=%s  官方宿主页=%s" % (
                s["code"], s["path"].name, s["line"], s["const"] or "（解析不出）",
                " / ".join(s.get("hosts") or []) or "**无**（没有任何官方 `CreateDefinition` 页收录）"))
    print()

    # ⚠ **假绿守卫**（第 29 轮的教训，保留）
    if checked == 0:
        print("[FAIL] **检查量为 0 ⇒ 这个结论不可信（假绿）**。")
        print("  可能原因：① 调用形状又变了；② 官方文档树不在；③ 收集成员的窗口不对。")
        print("  ⇒ **在修好之前，本工具的任何「通过」都没有意义。**")
        return 1

    if problems:
        print("[HIT] **%d 处的成员不在**期望的**接口上**：" % len(problems))
        for fname, line_no, const, iface, bad in problems:
            print()
            print("  %s（%s）  `%s` ⇒ 期望 `%s`" % (fname, line_no, const, iface))
            for mm, ln in sorted(bad, key=lambda x: x[1])[:8]:
                print("      L%-5d %-26s **不在 `%s` 上**" % (ln, mm, iface))
    else:
        print("[OK] 没有「成员不在期望接口上」的站点")
    print()
    print("  ⚠ **本工具按「诊断」定位**：映射表来自**文本匹配**，有歧义/未映射的洞")
    print("     （实测：**%d 唯一**（官方点名 %d + 文本匹配 %d + 人工确证 %d）/ 歧义 %d / 未映射 %d）"
          % (len(mapped), _named, _auto, _manual, len(ambiguous), len(unmapped)))
    print("     ⇒ 报 `[HIT]` 时值得看；**没有命中不等于归属一定正确**。")
    print("  ⚠ ★ 官方 `CreateDefinition` **宿主页不止一个**（%s）⇒ 「常量属于哪个宿主」由"
          % " / ".join(sorted(CD_DOCS)))
    print("     `scripts/check_cd_host_scope.py` 判（本工具只按宿主域查成员）。")
    print("  ⚠ 与 `check_member_names.py`（**门禁**）互补不替代：")
    print("     那个判「名字在**某个**接口里存在」（快、全仓）；本工具判「在**这个**接口里存在」。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
