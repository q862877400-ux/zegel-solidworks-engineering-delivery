"""★ 状态指纹：一组廉价读数，用来判「这次调用到底有没有改东西」。"""
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力实现，铁律 3 的 `scripts/`）
# 文件:   scripts/sw_fingerprint.py
# 定位:   ★ 规格 `specs/210-declarative-effects` 的 **B2**。★★ 它是 **B3（存活普查）的量具** ——
#   ★ B3 要「每次调用前后抓指纹差分」，★ 那**先得有一个可靠的指纹** ✓
#   ★ 外部评审的原话：★「整套方案的**量具是指纹**，所以要**校准它**，与你们『**回读的量具要校准**』是同一个思路」✓
# 判据:   ★★ **九类状态**（评审给的清单）：选区 · 编辑态 · 文档修改标志 · 特征数 · 体数 · 面数 ·
#     显示状态 · 活动配置 · 重建状态 ✓
#   ★ 每一类的读数都**标明官方成员**（★ 铁律 4：不许凭印象）；★ **拿不到 ⇒ 记 `None` + 原因**，
#     ★★ **绝不假装读到了**（★ 那会让 B3 的差分把「读不到」当成「没变」）✓
#   ⚠ **读数必须只读**：★ 本模块只调**读**类成员；★ 且 B2 的灵敏度测试里有一格专门验这件事
#     （★ 「连读两次、中间不做任何事 ⇒ 两次必须相等」）✓
# 官方依据（逐个已读页面）：`ISelectionMgr.GetSelectedObjectCount2` · `IModelDoc2.GetActiveSketch2` ·
#   `IModelDoc2.GetSaveFlag`（「dirty and needs to be saved」）· `IModelDoc2.FirstFeature` +
#   `IFeature.GetNextFeature` · `IPartDoc.GetBodies2` · `IBody2.GetFaceCount` ·
#   `IModelDocExtension.GetDisplayStateSetting` · `IModelDoc2.GetActiveConfiguration` ·
#   `IModelDoc2.GetBendState`? —— ★ 见 `needs_rebuild` 一格（★ 由 `sw_session.needs_rebuild_status` 提供）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   全文件
# ─────────────────────────────────────────────────────────────────────────────
from __future__ import annotations

try:
    from .sw_connect import get_com_member
except ImportError:                                                     # pragma: no cover
    from sw_connect import get_com_member

#: ★★ 九类状态（★ 评审给的清单，★ 顺序固定便于比对与显示）✓
STATE_CLASSES = ("selection", "edit_mode", "dirty", "features", "bodies", "faces",
                 "display", "config", "rebuild")

#: ★ 每类的**官方成员**（★ 铁律 4：读数要能指认出处）✓
OFFICIAL = {
    "selection": "ISelectionMgr.GetSelectedObjectCount2(-1)",
    "edit_mode": "IModelDoc2.GetActiveSketch2",
    "dirty": "IModelDoc2.GetSaveFlag",
    "features": "IModelDoc2.FirstFeature + IFeature.GetNextFeature",
    "bodies": "IPartDoc.GetBodies2",
    "faces": "IBody2.GetFaceCount",
    "display": "IModelDocExtension.GetDisplayStateSetting",
    "config": "IModelDoc2.GetActiveConfiguration",
    "rebuild": "IModelDoc2.GetBendState / 重建状态（见 sw_session.needs_rebuild_status）",
}

#: ★ 特征遍历的**上限**（★ 防病态文档把探针拖死；★ 到顶就记 `None` + 原因，★ 不假装数完）✓
FEATURE_CAP = 5000


#: ★ `swBodyType_e.swAllBodies`（官方 `C:\\swapi\\enums\\swBodyType_e.md`：`-1 = All solid and sheet bodies`）✓
SW_ALL_BODIES = -1
#: ★ `swDisplayStateOpts_e.swAllDisplayState`（官方同页：`2 = All display states`）✓
SW_ALL_DISPLAY_STATE = 2


def jsonable(value):
    """★ 把读数**归一成 JSON 安全标量**（`None` / `bool` / `int` / `float` / `str`）✓

    ★★★ 2026-10-06 真机踩过（★ 它让第 0 格**虚警**了一整轮）：
      ★ 指纹里某些读数是 **COM 对象** ⇒ ★ `dict.__eq__` 对它们的比较**不成立** ⇒
      ★★ 于是"两次读数相等"被判成**不相等** ⇒ ★ 我一度以为**读数有副作用** ✗
      ★ 而逐字段 `%r` 打印**看起来一模一样** ⇒ ★ 靠肉眼看是发现不了的 ✓
    ⇒ ★ 所以**在 read() 里就归一**：★ COM 对象 ⇒ `str()`；★ 其余标量原样 ✓
      ★★ 好处：★ 第 0 格与 B3 的差分都建立在**可比、可序列化**的值上 ✓
    """
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    try:
        return str(value)
    except Exception:                                                   # noqa: BLE001
        return "<unprintable>"


def _read(member, obj, *args, default=None):
    """★ 读一个成员并**吞掉异常** ⇒ 回 `(值, 错误说明)` —— ★ 拿不到**不等于**没变 ✓

    ★★★ 2026-10-06 **真机踩过的坑（必须记住）**：本仓的 `get_com_member(obj, attr, *args)`
      **没有 `default=` 这个关键字** —— ★★ 传 `default=None` 会被当成**位置实参** ⇒
      ⇒ ★ **变成「用 None 去调那个成员」** ⇒ ★ 绝大多数成员当场抛异常 ⇒
      ★★ 结果：**九类读数全部为 None，而第 0 格「两次读数相等」照样通过** ✗
      ⇒ ★ 所以**一次都没读到**这件事，靠"两次相等"是**发现不了**的 ✓
    """
    try:
        return get_com_member(obj, member, *args), ""
    except Exception as exc:                                            # noqa: BLE001
        return default, "%s: %s" % (type(exc).__name__, str(exc)[:80])


def _count_features(model):
    """★ 特征计数：从 `FirstFeature` 顺着 `GetNextFeature` 数（★ 到 `FEATURE_CAP` 就停并说明）✓"""
    try:
        feat = get_com_member(model, "FirstFeature")
    except Exception as exc:                                            # noqa: BLE001
        return None, "FirstFeature 取不到：%s" % type(exc).__name__
    n = 0
    while feat is not None:
        n += 1
        if n >= FEATURE_CAP:
            return None, "★ 特征数超过上限 %d ⇒ 不敢把「数到一半」当数完" % FEATURE_CAP
        try:
            feat = get_com_member(feat, "GetNextFeature")
        except Exception:                                               # noqa: BLE001
            return None, "GetNextFeature 在遍历中抛异常"
    return n, ""


def read(model, sw=None) -> dict:
    """★★ 抓一次**状态指纹** —— ★ 每个读数都带**官方出处**与**拿不到时的原因** ✓

    :returns: `{"readings": {类: 值}, "missing": {类: 原因}, "official": {类: 成员}}`
    ★★ `missing` 非空是有信息的：★ 它说明**这一类当前读不到** ⇒ ★ B3 的差分对它是**盲的**，
      ★★ 必须在 B2 的灵敏度报告里**明写「不可见」**，★ 而不是当成「没变」 ✗
    """
    readings, missing, notes = {}, {}, {}

    def notes_add(cls, text):
        notes.setdefault(cls, []).append(text)

    def put(cls, value, why=""):
        #: ★★ **在出口归一**（★ 见 `jsonable` 的说明：COM 对象会让比较虚警）✓
        value = jsonable(value)
        readings[cls] = value
        if value is None:
            missing[cls] = why or "★ 读不到（值就是 None）"

    # ① 选区数（★ 事实 8：`SelectByID2` 的 bool 不可信 ⇒ 一律用计数回读）✓
    sel_mgr, why = _read("SelectionManager", model)
    if sel_mgr is None:
        put("selection", None, "SelectionManager 取不到：%s" % (why or "返回 None"))
    else:
        #: ★★★ 真机踩过：★ `GetSelectedObjectCount2` **是方法、要吃 `-1` 实参**
        #:   （★ 事实 8 就是用 `-1` 表示"全部标记"）—— ★ 我**无参**调它 ⇒
        #:   ★ `get_com_member` 的"无实参 ⇒ 先无参调一次、失败则**返回成员本身**"语义生效 ⇒
        #:   ★★ 读出的是 **`<bound method ...>`**（★ 再被 `jsonable` 变成字符串）✗
        #:   ⇒ ★ 于是 `selection` 那一格**从来不是数字**，★ 差分自然"没动" ✓
        v, why2 = _read("GetSelectedObjectCount2", sel_mgr, -1)
        put("selection", v, why2 or "★ GetSelectedObjectCount2(-1) 返回 None")

    # ② 编辑态（★ 正在编辑草图 ⇒ `GetActiveSketch2` 非空）✓
    sk, why = _read("GetActiveSketch2", model)
    if sk is None and why:
        put("edit_mode", None, why)
    else:
        name, why2 = _read("Name", sk) if sk is not None else ("", "")
        put("edit_mode", ("sketch:" + str(name)) if sk is not None else "none", why2)

    # ③ 文档修改标志（★ 官方原文：dirty and needs to be saved）✓
    v, why = _read("GetSaveFlag", model)
    put("dirty", v, why or "★ GetSaveFlag 返回 None")

    # ④ 特征数 / ⑤ 体数 / ⑥ 面数
    n, why = _count_features(model)
    put("features", n, why)
    #: ★ 官方签名（已读页面）：`IPartDoc.GetBodies2(BodyType, BVisibleOnly)` —— **要两个实参** ⇒
    #:   ★ 我第一版无参调它 ⇒ 抛异常 ⇒ ★ `bodies`/`faces` 两格一直是「读不到」✗
    #:   ★ `swAllBodies = -1`（官方 `swBodyType_e` 页给的数值本页就有）；`False` = 含不可见的 ✓
    bodies, why = _read("GetBodies2", model, SW_ALL_BODIES, False)
    if bodies is None:
        #: ★★★ 2026-10-06 **真机查明（这条很值）**：★ 在**空零件**上 `GetBodies2(-1, False)`
        #:   返回 **`None`** —— ★★ 那**不是"读不到"，是"本来就没有实体"** ✓
        #:   （★ 真机对照：★ 建出一个实体之后同一调用 ⇒ **`tuple(len=1)`** ✓）
        #:   ★★ 而我把两者混成了「读不到」⇒ `bodies`/`faces` 两格**一直 unreadable** ✗
        #:   ⇒ ★ 处置：★ **按 0 计**，★ 但把这条不确定**写进 `notes`**（★ 不假装分得清）✓
        #:   ★ 同族教训（本仓老话）：★「**选不上**」与「**选了也没用**」是两件事 ——
        #:     ★ 这里就是「**没有**」与「**读不到**」被混成了一件 ✓
        notes_add("bodies", "★ GetBodies2 返回 None ⇒ 按「**没有实体**」计 0；"
                            "★ 与「读不到」在此调用形状下**无法区分**（★ 已记此注，不假装）")
        put("bodies", 0)
        put("faces", 0)
        notes_add("faces", "★ 由 bodies=0 推出 0（同上，无法与「读不到」区分）")
    else:
        seq = bodies if isinstance(bodies, (list, tuple)) else [bodies]
        seq = [b for b in seq if b is not None]
        put("bodies", len(seq))
        total, bad = 0, 0
        for b in seq:
            c, _ = _read("GetFaceCount", b)
            if c is None:
                bad += 1
            else:
                total += int(c)
        put("faces", total if not bad else None,
            "" if not bad else "★ %d 个体读不到面数 ⇒ 不敢报总数" % bad)

    # ⑦ 显示状态（★ 官方 `IModelDocExtension.GetDisplayStateSetting`）✓
    ext, why = _read("Extension", model)
    if ext is None:
        put("display", None, "Extension 取不到：%s" % (why or "返回 None"))
    else:
        #: ★★★ 真机踩过（与 `selection` **同一个坑**）：★ `GetDisplayStateSetting` 是**方法、
        #:   要吃一个 `swDisplayStateOpts_e` 实参** ⇒ ★ 我无参调它 ⇒ 拿到的是
        #:   ★★ **`<bound method ...>`**（★ 再被 `jsonable` 变成字符串）✗
        #:   ★ 官方签名（已读）：`DisplayStateSetting GetDisplayStateSetting(int Option)`；
        #:     ★ `swAllDisplayState = 2`（官方 `swDisplayStateOpts_e` 页给了数值）✓
        #:   ★ 而且要读的是它里面的**标量** —— ★ 返回的是 `IDisplayStateSetting` **对象**，
        #:     ★ 直接存对象又会落回"不可比的字符串" ✗ ⇒ ★ 取它的 `Names` ✓
        setting, why2 = _read("GetDisplayStateSetting", ext, SW_ALL_DISPLAY_STATE)
        if setting is None:
            put("display", None, why2 or "★ GetDisplayStateSetting(2) 返回 None")
        else:
            names, why3 = _read("Names", setting)
            if names is None:
                put("display", None, why3 or "★ IDisplayStateSetting.Names 返回 None")
            else:
                #: ★ 归成一个**可比、稳定**的表示：排序后的名字元组 ✓
                seq = names if isinstance(names, (list, tuple)) else [names]
                put("display", tuple(sorted(str(n) for n in seq if n is not None)))

    # ⑧ 活动配置（★ 官方 `IModelDoc2.GetActiveConfiguration` ⇒ 取名字）✓
    cfg, why = _read("GetActiveConfiguration", model)
    if cfg is None:
        put("config", None, why or "★ GetActiveConfiguration 返回 None")
    else:
        name, why2 = _read("Name", cfg)
        put("config", name, why2 or "★ 配置名为 None")

    # ⑨ 重建状态（★ 复用现有能力 `sw_session.needs_rebuild_status` —— ★ 一处实现）
    #: ★ 走一个模块级钩子 ⇒ ★ 测试可以替换它，★ 而不必把 `sw_session` 整个伪造出来 ✓
    put("rebuild", *(_REBUILD_READER(model)))

    #: ★★★ **指纹失效判据**（★ 这是本轮真机踩坑换来的）：★ **九类一个都读不到** ⇒
    #:   ★ 那不是"状态没变"，★ 而是**量具本身坏了** ⇒ ★ 必须显式标出来 ✓
    #:   ★★ 为什么非要加这条：★ 全 None 的指纹**照样能让"两次读数相等"通过** ⇒
    #:     ★ 光靠第 0 格**发现不了**它 ✗（★ 我就是在真机上这么栽的）
    usable = any(v is not None for v in readings.values())
    return {"readings": readings, "missing": missing, "notes": notes,
            "official": dict(OFFICIAL),
            "usable": usable,
            "unusable_why": "" if usable else
            "★★ 九类读数**全部为 None** ⇒ 指纹**失效**（★ 别把它当成「什么都没变」）"}


def _default_rebuild_reader(model):
    """★ 默认的重建读数：★ 复用 `sw_session.needs_rebuild_status`（★ 一处实现，不另写一份）✓"""
    try:
        try:
            from .sw_session import needs_rebuild_status
        except ImportError:
            from sw_session import needs_rebuild_status
        st = needs_rebuild_status(model)
        if isinstance(st, dict):
            #: ★★★ 真机踩过：★ 我读的是 `needs_rebuild` —— ★ **那个键不存在** ✗
            #:   ★ `needs_rebuild_status` 回的是 `{raw, state, fully_rebuilt}` ⇒
            #:   ★★ 于是 `rebuild` 一直被记成「读不到」，★ 而**真因是我读错了键** ✓
            return (not st.get("fully_rebuilt")), ""
        return str(st), ""
    except Exception as exc:                                            # noqa: BLE001
        return None, "needs_rebuild_status 不可用：%s" % type(exc).__name__


#: ★ 可替换的重建读数（★ 默认走 `sw_session`；★ 测试用它换成假件）✓
_REBUILD_READER = _default_rebuild_reader


def compare(before, after) -> list:
    """★ 两个指纹的差分 —— ★ 只回**真的变了**的那些类 ✓

    :returns: `[{"class", "before", "after"}]`
    ★★ **`None` 的处置是这里的关键**：★ 若一侧是 `None`（读不到）⇒ ★ **我们不知道它变没变** ⇒
      ★ 记进 `unknown` 而不是当成「没变」 ✗ —— ★ 见 `compare_detailed` ✓
    """
    return compare_detailed(before, after)["changed"]


def compare_detailed(before, after) -> dict:
    """★ 差分**分三桶**：`changed`（确实变了）· `unknown`（有一侧读不到 ⇒ 不知道）· `same` ✓

    ★★ 为什么必须分桶：★ 把「读不到」混进 `same` ⇒ ★ **B3 会把盲区报成「声明一致」** ✗
      ★★ 而那正是本规格要防的那类假结论（同族：把「选不上」当成「能力不行」）✓
    """
    changed, unknown, same = [], [], []
    rb, ra = (before or {}).get("readings", {}), (after or {}).get("readings", {})
    for cls in STATE_CLASSES:
        #: ★ 双保险：★ 即便上游没归一，这里也按归一后的值比 ✓
        b, a = jsonable(rb.get(cls)), jsonable(ra.get(cls))
        if b is None or a is None:
            unknown.append({"class": cls, "before": b, "after": a})
        elif b != a:
            changed.append({"class": cls, "before": b, "after": a})
        else:
            same.append(cls)
    return {"changed": changed, "unknown": unknown, "same": same}
