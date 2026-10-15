

# ── 来源 ─────────────────────────────────────────────────────────────
# 仓库:   本项目自身既有模式（`sw_part._get_sketch_name_candidates` 的中英文变体 + 本模块的按名取）
# 文件:   scripts/sw_sketch.py（**本组为追加**，2026-10-01 轮 222 / 砌墙 W1）
# 定位:   ★ **真机验证抓出来的 bug 的修法**：`sw_part.current_sketch_name` 在
#         **草图已关闭**时回**英文 fallback `"Sketch1"`**，而中文 UI 下真名是「草图1」
#         ⇒ 第一次真机调用就报「找不到名为 'Sketch1' 的草图特征」。
#         ★ 这个错**只有真机能暴露** —— 静态门禁、62 个工具全部挂载成功，全绿。
# 官方依据: `IModelDoc2.FeatureByName` / `IFeature.GetSpecificFeature2` / `IModelDoc2.FeatureByPositionReverse`
# 许可:   本仓库 MIT。无第三方代码引入。
# ⚠ 名字随 UI 语言变是本仓库的既有事实（见 `docs/known-facts.md` 第 9 条：
#   基准面名 `Front Plane` / `前视基准面` 同理）⇒ **一律走候选名，不写死一种**。
# 覆盖:   本组 1 个函数
# ────────────────────────────────────────────────────────────────────
def resolve_sketch(model, name: str = ""):
    """★ **稳健地**取到一个 `ISketch`，中英文名都能用，留空则取"最后一个草图"。

    解决三件事（★ 都由真机暴露，不是设想出来的）：
    ```
    ① 草图**已关闭**时，`SketchManager.ActiveSketch` 与 `model.GetActiveSketch2` 都是 None
       （真机探针 `tools/probe_sketch_object_routes.py`）
    ② 中文 UI 下草图真名是「草图1」，而 `sw_part.current_sketch_name` 在取不到时
       回**英文 fallback** `"Sketch1"` ⇒ 直接按那个名字找**必然找不到**
    ③ 调用方常常**根本不知道该填什么名字**（"我就要刚才建的那个草图"）
    ```

    查找顺序（每一步都**真的去取**，取到才返回）：
    ```
    1. 给了 name            ⇒ 按 候选名（中英文变体）逐个 FeatureByName
    2. 没给 name            ⇒ current_sketch_name 的结果 + 候选名
    3. 都不行               ⇒ ★ 从特征树里找**最后一个草图特征**（语言无关）
    4. 还找不到             ⇒ **抛错**（选不中要报错，不静默）
    ```

    :param model: `IModelDoc2`
    :param name: 草图特征名（中英文皆可）；留空 ⇒ 自动找
    :raises RuntimeError: 四种路径都取不到
    """
    if model is None:
        raise ValueError("model 为 None")

    tried: list[str] = []

    def _try(candidate: str):
        if not candidate:
            return None
        tried.append(candidate)
        try:
            return sketch_by_name(model, candidate)
        except RuntimeError:
            return None

    #: 1+2 · 显式名，或"当前草图名"（★ 两者都试中英文变体）
    from scripts.sw_part import _get_sketch_name_candidates, current_sketch_name

    base = str(name or "").strip() or current_sketch_name(model)
    for cand in _get_sketch_name_candidates(base):
        sk = _try(cand)
        if sk is not None:
            return sk

    #: 3 · 从特征树里找**最后一个草图特征**（★ 语言无关的兜底）
    try:
        total = int(get_com_member(model, "GetFeatureCount"))
    except Exception:                                          # noqa: BLE001
        total = 0
    for i in range(1, total + 1):
        feature = get_com_member(model, "FeatureByPositionReverse", i)
        fname = str(get_com_member(feature, "Name") or "") if feature is not None else ""
        if fname.startswith(("Sketch", "草图")):
            sk = _try(fname)
            if sk is not None:
                return sk

    raise RuntimeError(
        "取不到草图：试过 %r；特征树里也没找到以 Sketch/草图 开头的特征"
        % (tried or [base])
    )
