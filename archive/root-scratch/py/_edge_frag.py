

# ── 24h 计划 段 4 续（Spec Kit `163`）：**让"找不到入口圆边"的失败可见** ──────────────
# ★★★★★ 2026-10-01（轮 297）真凶：`_find_hole_entry_edge` 用 `except Exception: continue`
#   **把"断在哪一环"吞掉了** —— ★ 于是真机上只看到一句
#   「无法按圆心和半径找到沉头孔入口圆边」，★ **而看不出**是
#   ① `GetBodies2` 空 · ② `GetFaces` 空 · ③ `GetEdges` 空 · ④ `GetCurve` 空 ·
#   ⑤ `IsCircle` 假 · ⑥ `CircleParams` 不足 7 个 · ⑦ 半径不匹配 —— **七种可能之一**。
#   ⇒ ★★ 这正是本项目一贯要防的"静默吞错"（事实 185/187/198 一族）。
#
# ★ 判据：★ **不改判定逻辑**（★ 仍然找同一条边、仍然用同样的容差），
#   ★★ **只把每一环的计数与第一个异常记下来**，★ 并在失败时**回一个带诊断的 `RuntimeError`**。
#   ⇒ ★ **于是"下一次"能一眼看出断在哪**（★ 而不是再猜一轮）。
#
# ── 来源 ─────────────────────────────────────────────────────────────────────
# 仓库:   本项目自身（能力层）
# 文件:   scripts/sw_hole_features.py —— 本段
# 定位:   段 4 续：把 `_find_hole_entry_edge` 的静默吞错改成**带诊断的失败**。
# 官方依据: `IBody2.GetFaces` · `IFace2.GetEdges` · `IEdge.GetCurve` ·
#          `ICurve.IsCircle` / `ICurve.CircleParams`（★ 见 `scripts/sw_hole_features.py` 既有来源块）
# 许可:   本仓库 MIT。无第三方代码引入。
# 覆盖:   下面 1 个函数（替换版）
# ─────────────────────────────────────────────────────────────────────────────


def _find_hole_entry_edge(model, plane_name: str, center: tuple[float, float], radius: float,
                          tolerance: float = 1e-6):
    """★ **按圆心和半径寻找通孔在草图基准面一侧的圆边**（★ 带**逐环诊断**的版本）。

    ★★ 与旧版的差别**只在失败路径**：★ 旧版 `except Exception: continue` 把原因吞了，
    于是失败时只有一句"找不到"；本版**记下每环的计数与第一个异常**，
    并在失败时把它们放进 `RuntimeError`（★ **判定逻辑一字未改**）。
    """
    target = _entry_point_3d(plane_name, center)
    diag = {"bodies": 0, "faces": 0, "edges": 0, "curves": 0, "circles": 0,
            "params_ok": 0, "first_error": None}
    candidates = []

    def _note(stage, exc):
        if diag["first_error"] is None:
            diag["first_error"] = "%s: %s: %s" % (stage, type(exc).__name__, str(exc)[:160])

    try:
        bodies = list(get_com_member(model, "GetBodies2", 0, False) or [])
    except Exception as exc:                                   # noqa: BLE001
        _note("GetBodies2", exc)
        bodies = []
    diag["bodies"] = len(bodies)
    for body in bodies:
        try:
            faces = list(get_com_member(body, "GetFaces") or [])
        except Exception as exc:                               # noqa: BLE001
            _note("GetFaces", exc)
            continue
        diag["faces"] += len(faces)
        for face in faces:
            try:
                edges = list(get_com_member(face, "GetEdges") or [])
            except Exception as exc:                           # noqa: BLE001
                _note("GetEdges", exc)
                continue
            diag["edges"] += len(edges)
            for edge in edges:
                try:
                    curve = get_com_member(edge, "GetCurve")
                except Exception as exc:                       # noqa: BLE001
                    _note("GetCurve", exc)
                    continue
                if curve is None:
                    continue
                diag["curves"] += 1
                try:
                    if not bool(get_com_member(curve, "IsCircle")):
                        continue
                except Exception as exc:                       # noqa: BLE001
                    _note("IsCircle", exc)
                    continue
                diag["circles"] += 1
                try:
                    params = list(get_com_member(curve, "CircleParams") or [])
                except Exception as exc:                       # noqa: BLE001
                    _note("CircleParams", exc)
                    continue
                if len(params) < 7:
                    continue
                try:
                    if abs(float(params[6]) - radius) > tolerance:
                        continue
                except Exception as exc:                       # noqa: BLE001
                    _note("params[6]", exc)
                    continue
                diag["params_ok"] += 1
                try:
                    distance = math.dist([float(value) for value in params[:3]], target)
                except Exception as exc:                       # noqa: BLE001
                    _note("math.dist", exc)
                    continue
                candidates.append((distance, edge))
    if not candidates:
        raise RuntimeError(
            "无法按圆心和半径找到沉头孔入口圆边 —— ★ 逐环诊断（★ 判定逻辑未改，只加诊断）："
            "bodies=%d · faces=%d · edges=%d · curves=%d · circles=%d · params_ok=%d · "
            "target=%s · radius=%r · first_error=%s"
            % (diag["bodies"], diag["faces"], diag["edges"], diag["curves"],
               diag["circles"], diag["params_ok"], target, radius, diag["first_error"]))
    candidates.sort(key=lambda item: item[0])
    if candidates[0][0] > max(tolerance * 10.0, 1e-5):
        raise RuntimeError(f"找到的圆边偏离沉头入口位置: {candidates[0][0] * 1000.0:.3f} mm")
    return candidates[0][1]
