

#: ⚑ **官方分类字段的正则**（2026-10-01 轮 210 / Spec Kit `129`）。
#: ⚠⚠ **它只有一个来源**：`C:\swapi\types\<接口>\*.md` 的 `category` 字段
#:   —— 那是 **help 站点的文档镜像**（来源仓 `offline-solidworks-api-docs`，**无许可**）。
#:   实测：**两份出厂反射转储都没有该字段**（`iface_sldworks.txt` 只有接口名；
#:   `iface_cosworks.txt` 只有 `<接口> :: <返回类型> <方法名>(…)`）
#:   ⇒ ★ **无法按铁律 4 做三源互证** ⇒ 本字段**只能标成"单一来源"**，不能声称"经官方核过"。
CATEGORY_RX = re.compile(r"(?im)^\s*\*{0,2}category\*{0,2}\s*[:：]\s*(.+)$")


def official_categories() -> dict:
    """⇒ ``{接口名: 官方 category}`` —— 从 ``C:\\swapi\\types\\<接口>\\*.md`` 读。

    :returns: 形如 ``{"ISldWorks": "Application Interfaces", …}``。
        读不到就是空 dict（**不报错、不编造**）。

    ⚑ **这个字段是"接口级"的**：一个接口只有一个 category（它的成员文件各自
      也都带同一行，本函数取该接口目录下**任意一命中**即可）。
    ⚠ 实测覆盖：``C:\\swapi\\types`` 下 **481 个接口**有该字段 —— 而 `family-coverage`
      的 881 个族里能对上 **477（54.1%）**；对不上的主要是
      **`C:\\swapi` 不收录的那些程序集**（swdimxpert / RoutingLib / sldcostingapi …）
      ＋ 路由/Composer/PDM 与仿真那两域。
    """
    out: dict = {}
    if not SWAPI.is_dir():
        return out
    for d in sorted(SWAPI.iterdir()):
        if not d.is_dir():
            continue
        for p in sorted(d.glob("*.md")):
            m = CATEGORY_RX.search(p.read_text(encoding="utf-8", errors="replace"))
            if m:
                out[d.name] = m.group(1).strip()
                break          #: 一个接口一条即可（成员文件各自都带同一行）
    return out


def official_category_section(rows: list, cats: dict) -> list:
    """⇒ md 的 ``## 四`` 那一节（**生成物**，数字全部现算，不写死）。

    :param rows: `main()` 建好的行（每行含 `domain` / `family`）。
    :param cats: `official_categories()` 的返回。
    :returns: 该节的 markdown 行列表。

    ★ **为什么加这一节**（2026-10-01 轮 210）：一份外部只读审计（`D:\\AI\\SW-transfer\\official-category-unused.md`）
      指出「官方每个接口都带 `category`（96.5%、39 类），而本仓库没用它」。
      ★ 复核结论：**它的数全对**（12,123 md / 11,703 有 category / 39 类），
      但它把 `全量索引/<程序集>` 读成"兜底桶"是**误读** ——
      那是 `_dedupe_domains()` 的「**一族只算一次**」产物（见该函数 docstring）。
      ⇒ 本节把它**量清楚**：未认领的族有多少、其中有多少能被官方分类归位。
      ⚠ 而**不替换**业务域：报告自己也说两者维度不同（厂商视角 vs 业务视角），★ 那是对的。
    """
    from collections import Counter
    total = len(rows)
    unclaimed = [r for r in rows if str(r.get("domain", "")).startswith("全量索引/")]
    joined = [r for r in unclaimed if r.get("official_category")]
    c = Counter(r["official_category"].split("/")[0] for r in joined)
    L: list = []
    L += ["", "---", "", "## 四、官方分类（`category`）与「未认领」族的归位", ""]
    L += ["> ⚠⚠ **本节的字段只有一个来源**：`C:\\swapi\\types\\<接口>\\*.md` 的 `category`",
          "> —— 那是 **help 站点的文档镜像**（来源仓 `offline-solidworks-api-docs`，**无许可**）。",
          "> ★ 实测**两份出厂反射转储都没有该字段** ⇒ **无法按铁律 4 做三源互证**。",
          "> ⇒ 本字段只能当 **\"单一来源的分类\"** 用（分类与校验），**不能声称\"经官方核过\"**。", ""]
    L += ["### 4.1 官方分类的覆盖（实测）", "",
          "| 项 | 数 |", "|---|---|",
          "| `C:\\swapi\\types` 下有 `category` 的接口 | **%d** |" % len(cats),
          "| 本表 881 族里**能对上**官方分类的 | **%d**（%.1f%%）|"
          % (sum(1 for r in rows if r.get("official_category")),
             100.0 * sum(1 for r in rows if r.get("official_category")) / max(total, 1)),
          "| 对不上的原因（主体）| ★ **`C:\\swapi` 不收录的程序集**（swdimxpert / RoutingLib / "
          "sldcostingapi …）＋ 路由/Composer/PDM 与仿真两域 |", ""]
    L += ["### 4.2 ★ 「未认领」族到底有多少（**按域全加起来**）", "",
          "> ⚠ 外部审计只数了 `全量索引/sldworks` 一个桶（385 / 881 = 43.7%）⇒ **低估了**。",
          "> 实测：`domain` 以 `全量索引/` 开头的**共有 %d 族 = %.1f%%**。" % (len(unclaimed),
          100.0 * len(unclaimed) / max(total, 1)), "",
          "| `domain` | 族数 |", "|---|---|"]
    for k, v in sorted(Counter(r["domain"] for r in unclaimed).items(), key=lambda x: -x[1]):
        L.append("| `%s` | %d |" % (k, v))
    L += ["| **合计** | **%d / %d = %.1f%%** |" % (len(unclaimed), total,
          100.0 * len(unclaimed) / max(total, 1)), ""]
    L += ["### 4.3 ★ 官方分类能救回多少", "",
          "| 项 | 数 |", "|---|---|",
          "| 未认领族中有官方分类的 | **%d / %d（%.1f%%）** |"
          % (len(joined), len(unclaimed), 100.0 * len(joined) / max(len(unclaimed), 1)), "",
          "| 一级分类 | 能归位的族数 |", "|---|---|"]
    for k, v in c.most_common():
        L.append("| %s | %d |" % (k, v))
    L += ["", "⇒ ★ **收益是具体的**：上面这张表就是「按官方分类，未认领的族能立刻有归属」的清单。",
          "",
          "### 4.4 ⚠ 怎么用 / 怎么**不**用", "",
          "```",
          "✅ **用**：① 分类与校验（发现「手写域 vs 官方类」的错位）",
          "        ② ★ 给「未认领」族兜底归属（4.3 那张表）",
          "        ③ 辅助发现空白（某个官方一级分类下我们一族都没有 ⇒ 值得看一眼）",
          "❌ **不用**：把一级分类**当作「该不该做成工具」的判据** ——",
          "         标签说的是「接口**是什么**」（厂商视角），",
          "         不是「我们**需不需要**工具」（项目视角）。★ 那正是本项目禁止的"
          "「看着像就当成」。",
          "⚠ **不替换**业务域：两者维度不同（厂商视角 vs 业务视角）——",
          "   `ISelectionMgr` 官方归 `Utility Interfaces`，而本项目归「应用与会话」"
          "（\"选中是所有操作的地基\"是业务判断，不是错）。",
          "```", ""]
    return L
