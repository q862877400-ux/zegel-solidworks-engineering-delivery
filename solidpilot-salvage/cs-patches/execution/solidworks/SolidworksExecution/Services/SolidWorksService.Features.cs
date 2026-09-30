using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using Newtonsoft.Json.Linq;
using SolidWorks.Interop.sldworks;
using SolidWorks.Interop.swconst;
using SolidworksExecution.Infrastructure;
using SolidworksExecution.Models;


namespace SolidworksExecution.Services
{
    // SolidWorksService partial: part-modeling features (extrude/revolve/sweep/loft, rib, edge fillet/chamfer, reference geometry, patterns, material, dimension/feature edits).
    public partial class SolidWorksService
    {

        /// <summary>草图 -> 边对象数组（照 codestack 的 Body2.GetEdges() 路线：线段先 CreateWireBody）。</summary>
        private static List<object> ExtractEdges(ISketch sketch)
        {
            var res = new List<object>();
            if (sketch == null) return res;
            try
            {
                var segs = sketch.GetSketchSegments() as object[];
                if (segs == null) return res;
                foreach (var s in segs)
                {
                    var sg = s as ISketchSegment;
                    if (sg == null) continue;
                    try
                    {
                        var wb = sg.CreateWireBody() as IBody2;
                        if (wb == null) continue;
                        var eds = wb.GetEdges() as object[];
                        if (eds != null) foreach (var e in eds) res.Add(e);
                    }
                    catch { }
                }
            }
            catch { }
            return res;
        }
        public ExecutionResponse ExtrudeFeature(ToolRequest request)
        {
            if (_guard.IsDuplicate(request.OperationId))
                return _guard.GetDuplicate(request.OperationId);

            if (!_guard.IsStateVersionValid(request.StateVersion))
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "INVALID_STATE_VERSION", "Incoming state_version does not match current state.");

            if (!EnsureConnected())
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "COM_ATTACH_FAILED", "SolidWorks process not found or COM not registered.");

            try
            {
                var p = request.Params as JObject;
                double? depth = p?.Value<double?>("depth");

                string featureType = (p?.Value<string>("feature_type") ?? "boss").ToLowerInvariant();
                if (featureType != "boss" && featureType != "cut" && featureType != "revolve" && featureType != "sweep" && featureType != "sweep_modeler" && featureType != "loft")
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "UNSUPPORTED_FEATURE_TYPE",
                        $"feature_type '{featureType}' is not supported. Supported: boss, cut, revolve, sweep, sweep_modeler, loft.");

                // depth (> 0) is required ONLY for a BLIND boss/cut. A through-all (through=true) ignores
                // depth, and revolve/sweep/loft don't use it — so don't demand it there (KNOWN-LIMITATIONS #13).
                bool throughAll = p?.Value<bool?>("through") ?? false;
                // up_to_face_index >= 0 ⇒ up-to-surface end condition: the extrude/cut terminates ON that
                // face (index from analyze_model(faces), same enumeration create_sketch(on_face) walks).
                // Depth is ignored, like through-all.
                int upToFaceIndex = p?.Value<int?>("up_to_face_index") ?? -1;
                bool upToSurface = upToFaceIndex >= 0;
                // mid_plane=true ⇒ swEndCondMidPlane: the feature extrudes SYMMETRICALLY about the
                // sketch plane; depth = the TOTAL width (SolidWorks midplane semantics).
                bool midPlane = p?.Value<bool?>("mid_plane") ?? false;
                if (upToSurface && featureType != "boss" && featureType != "cut")
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "INVALID_PARAMETER", "up_to_face_index is only valid for feature_type 'boss' or 'cut'.");
                if (midPlane && featureType != "boss" && featureType != "cut")
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "INVALID_PARAMETER", "mid_plane is only valid for feature_type 'boss' or 'cut'.");
                if (midPlane && (throughAll || upToSurface))
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "INVALID_PARAMETER", "mid_plane conflicts with through/up_to_face_index — pick ONE end condition.");
                if ((featureType == "boss" || featureType == "cut") && !throughAll && !upToSurface && (depth == null || depth.Value <= 0))
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "MISSING_PARAMETER", "depth (> 0 meters) is required for a blind or mid-plane boss/cut. Pass through=true for a through-all instead.");

                var modelDoc = _solidWorks.IActiveDoc2 as IModelDoc2;
                if (modelDoc == null)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "NO_ACTIVE_DOCUMENT", "No active document found in SolidWorks.");

                // Direction + end-condition controls (boss/cut). reverse flips the feature direction
                // (needed e.g. for a cut sketched on a part FACE, where "into the body" is the opposite
                // side from a cut sketched on a boundary plane). through = through-all (depth ignored).
                bool reverse = p?.Value<bool?>("reverse") ?? false;
                int endCond = upToSurface
                    ? (int)swEndConditions_e.swEndCondUpToSurface
                    : midPlane
                        ? (int)swEndConditions_e.swEndCondMidPlane
                        : throughAll
                            ? (int)swEndConditions_e.swEndCondThroughAll
                            : (int)swEndConditions_e.swEndCondBlind;
                // Through-all ignores depth; a blind boss/cut already validated depth > 0 above.
                // Default a missing depth to 0 so the API call is safe (e.g. a REST through-cut with no depth).
                double depthVal = depth ?? 0.0;

                // Capture the active sketch name before exiting — it is the PROFILE for sweep (and is
                // useful context generally). Re-selected by name after exit (names resolve post-exit).
                string activeProfileSketchName = (modelDoc.SketchManager.ActiveSketch as IFeature)?.Name;

                // Exit sketch mode if a sketch is still active. EXCEPTION: revolve selects its axis
                // line by coordinate, which only works while the sketch is still active (a closed
                // sketch's segments are not coordinate-pickable). Revolve handles its own selection
                // below with the sketch open; FeatureRevolve2 consumes the sketch as the profile.
                if (featureType != "revolve" && modelDoc.SketchManager.ActiveSketch != null)
                    modelDoc.SketchManager.InsertSketch(true);

                var featureMgr = modelDoc.FeatureManager;
                IFeature feature = null;

                if (featureType == "revolve")
                {
                    // Requires depth param ignored; needs axis defined by two coordinate points in the sketch
                    double ax1 = p?.Value<double?>("axis_x1") ?? 0.0;
                    double ay1 = p?.Value<double?>("axis_y1") ?? 0.0;
                    double ax2 = p?.Value<double?>("axis_x2") ?? 0.0;
                    double ay2 = p?.Value<double?>("axis_y2") ?? 0.001;
                    // angle arrives in DEGREES (model-facing convention, like create_pattern circular /
                    // sheet_metal); convert to radians for FeatureRevolve2. Default 360 = full revolve.
                    double angleDeg = p?.Value<double?>("angle") ?? 360.0;
                    double angle = angleDeg * Math.PI / 180.0;
                    // Snap anything within ~0.06° of a full turn to an exact 2π so "full revolve" is clean
                    // (guards float rounding). Partial revolves (e.g. 180°) are unaffected.
                    if (Math.Abs(angle - 2.0 * Math.PI) < 1e-3) angle = 2.0 * Math.PI;

                    // The sketch is still active here (the generic exit above skips revolve), so the
                    // axis line is coordinate-pickable. Select it at the midpoint of the two endpoints.
                    if (modelDoc.SketchManager.ActiveSketch == null)
                        return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                            "SKETCH_NOT_ACTIVE", "revolve needs the profile+axis sketch active. Call create_sketch and draw the profile + axis line first.");

                    modelDoc.ClearSelection2(true);
                    // EXACT axis match by ENDPOINTS. Coordinate picking (SelectByID2 at a point) grabs the
                    // NEAREST segment, and on a large sketch a profile edge can be nearer than the axis.
                    // The ConstructionGeometry flip below then converts a PROFILE edge into a centerline —
                    // which produced silently-wrong revolves (right feature created, wrong volume, no error).
                    ISketchSegment axisSeg = null;
                    var revSketch = modelDoc.SketchManager.ActiveSketch as ISketch;
                    if (revSketch != null)
                    {
                        const double axisTol = 1e-6;          // 1 micron
                        var cand = revSketch.GetSketchSegments() as object[];
                        if (cand != null)
                        {
                            foreach (var co in cand)
                            {
                                var cln = co as ISketchLine;
                                if (cln == null) continue;
                                double cax1, cay1, cax2, cay2;
                                try
                                {
                                    var ps = cln.IGetStartPoint2();
                                    var pe = cln.IGetEndPoint2();
                                    if (ps == null || pe == null) continue;
                                    cax1 = ps.X; cay1 = ps.Y; cax2 = pe.X; cay2 = pe.Y;
                                }
                                catch { continue; }
                                bool fwd = Math.Abs(cax1 - ax1) < axisTol && Math.Abs(cay1 - ay1) < axisTol
                                        && Math.Abs(cax2 - ax2) < axisTol && Math.Abs(cay2 - ay2) < axisTol;
                                bool bwd = Math.Abs(cax2 - ax1) < axisTol && Math.Abs(cay2 - ay1) < axisTol
                                        && Math.Abs(cax1 - ax2) < axisTol && Math.Abs(cay1 - ay2) < axisTol;
                                if (fwd || bwd) { axisSeg = cln as ISketchSegment; break; }
                            }
                        }
                    }
                    if (axisSeg == null)
                        return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                            "AXIS_NOT_FOUND",
                            $"No sketch line has endpoints ({ax1},{ay1})->({ax2},{ay2}). Draw the axis line at exactly those sketch coordinates (call analyze_model(sketch) to read back actual coordinates), then call revolve.");

                    // Convert the axis line to construction geometry (a centerline) so SolidWorks
                    // treats it as the axis of revolution and the remaining closed loop as the sole profile
                    // — mirrors the manual flow (axis-of-revolution = line, selected-contour = sketch region).
                    axisSeg.ConstructionGeometry = true;
                    axisSeg.Select2(false, 0);

                    // Remember the profile sketch, then exit it (post-exit, re-select it by name — names
                    // resolve after exit even though coordinates do not).
                    string profileSketchName = (modelDoc.SketchManager.ActiveSketch as IFeature)?.Name;
                    modelDoc.SketchManager.InsertSketch(true);
                    modelDoc.ClearSelection2(true);
                    if (!string.IsNullOrEmpty(profileSketchName))
                        modelDoc.Extension.SelectByID2(profileSketchName, "SKETCH", 0, 0, 0, false, 0, null, 0);

                    feature = featureMgr.FeatureRevolve2(
                        true, true, false, false, false, false,
                        0, 0, angle, 0, false, false,
                        0.0, 0.0, 0, 0.0, 0.0, true, true, true) as IFeature;
                }
                else if (featureType == "sweep" || featureType == "sweep_modeler")
                {
                    // ★★ 2026-09-28 新增：IModeler 路线（codestack 的 Macro.vba 配方）
                    //   sweep/loft 走 FeatureManager.InsertProtrusionSwept4 在本机 5 轮全 null；
                    //   正确入口是 ISldWorks.GetModeler().CreateSweptBody(...)（15 参）。
                    //   配方要点：① 轮廓/路径各自 CreateWireBody() ② 选区类型 1=轮廓 / 4=路径
                    //             ③ 用 SelectionMgr.SuspendSelectionList / ResumeSelectionList 包裹
                    if (featureType == "sweep_modeler" || p?.Value<bool>("use_modeler") == true)
                    {
                        var logM = new System.Text.StringBuilder();
                        Func<string, string, ExecutionResponse> failM = (code, msg) =>
                        {
                            ExecLog.Write("sweep_modeler: " + logM.ToString());
                            return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(), code, msg + " | log: " + logM.ToString());
                        };
                        string pathName = p?.Value<string>("path_sketch");
                        if (string.IsNullOrEmpty(pathName))
                            return failM("MISSING_PARAMETER", "sweep_modeler requires path_sketch.");

                        var mdl = modelDoc as IModelDoc2;
                        IFeature profFeat = null;
                        IFeature pathFeat = null;
                        var f = mdl.FirstFeature() as IFeature;
                        int guard = 0;
                        while (f != null && guard++ < 400)
                        {
                            string n = "";
                            try { n = f.Name; } catch { }
                            if (n == activeProfileSketchName && profFeat == null) profFeat = f;
                            if (n == pathName && pathFeat == null) pathFeat = f;
                            try { f = f.GetNextFeature() as IFeature; } catch { break; }
                        }
                        logM.Append("profFeat=" + (profFeat == null ? "null" : profFeat.Name)
                                 + " pathFeat=" + (pathFeat == null ? "null" : pathFeat.Name));
                        if (profFeat == null || pathFeat == null)
                            return failM("PROFILE_NOT_FOUND", "profile '" + activeProfileSketchName + "' or path '" + pathName + "' not in tree.");

                        var profSketch = profFeat.GetSpecificFeature2() as ISketch;
                        var pathSketchFeat = pathFeat.GetSpecificFeature2() as ISketch;
                        object profEdges = profSketch == null ? null : profSketch.GetSketchSegments();
                        object pathEdges = pathSketchFeat == null ? null : pathSketchFeat.GetSketchSegments();
                        int nProf = profEdges == null ? 0 : ((object[])profEdges).Length;
                        int nPath = pathEdges == null ? 0 : ((object[])pathEdges).Length;
                        logM.Append("profSegs=" + nProf + " pathSegs=" + nPath);
                        if (nProf == 0 || nPath == 0)
                            return failM("PROFILE_EMPTY", "profile or path sketch has no segments.");

                        // 选区：类型 1=轮廓 / 4=路径，用 Suspend/Resume 包裹（codestack 配方）
                        var selMgr = mdl.SelectionManager as ISelectionMgr;
                        if (selMgr == null)
                            return failM("NO_SELECTION_MGR", "IModelDoc2.SelectionManager is not an ISelectionMgr.");
                        object sweptBody = null;
                        try
                        {
                            // ★★★ 2026-09-28 实测定位：
                            //   SelectByID2 把两个草图都选进 UI 选区成功（uiCount=2），
                            //   但紧接着 SuspendSelectionList + AddSelectionListObjects 反而把选区清空
                            //   （added=0+0 selected=0）⇒ ★ 选区已在 UI 里时，【不要】再动选区，
                            //   直接用 IModeler.CreateSweptBody 读当前 UI 选区。
                            // ★★★★★★ 官方 Remarks 原文（C:\swapi\types\IModeler\CreateSweptBody.md）：
                            //   "Use IModelDocExtension::SelectByID2 to select the profile and sweep curves.
                            //    The mark for: 1 = Profile / 2 = Guide curve / 4 = Sweep path"
                            //   ★ 官方说选【curves】。所以正确组合是：
                            //     ① SelectByID2 选中两条曲线（Type="CURVE"）
                            //     ② ISelectionMgr.Select4? 没有 ⇒ 用 ISketchSegment/ICurve 的 Select4
                            //   我用 ISketchSegment.Select4(append, selData) 逐段打 Mark（官方签名存在）。
                            var sdP = selMgr.CreateSelectData(); sdP.Mark = 1;   // 轮廓
                            var sdL = selMgr.CreateSelectData(); sdL.Mark = 4;   // 路径
                            int n1 = 0, n2 = 0;
                            foreach (var s in (object[])profEdges)
                            { try { var sg = s as ISketchSegment; if (sg != null && sg.Select4(n1 > 0, sdP)) n1++; } catch { } }
                            foreach (var s in (object[])pathEdges)
                            { try { var sg = s as ISketchSegment; if (sg != null && sg.Select4(n1 > 0, sdL)) n2++; } catch { } }
                            int nSel = 0;
                            try { nSel = selMgr.GetSelectedObjectCount2(-1); } catch { }
                            int k0 = -1, k1 = -1;
                            try { k0 = selMgr.GetSelectedObjectMark(0); } catch { }
                            try { k1 = selMgr.GetSelectedObjectMark(1); } catch { }
                            logM.Append("segSelect4 prof=" + n1 + " path=" + n2 + " sel=" + nSel
                                      + " marks=" + k0 + "," + k1);
                            if (nSel < 2)
                                return failM("SELECTION_REJECTED",
                                    "ISketchSegment.Select4 marked " + n1 + "/" + n2
                                    + " segments; selection list holds " + nSel + ".");

                            var modeler = _solidWorks.GetModeler() as IModeler;
                            if (modeler == null)
                                return failM("NO_MODELER", "ISldWorks.GetModeler() is not an IModeler.");
                            // ★ 15 参，参数顺序照 codestack Macro.vba
                            sweptBody = modeler.CreateSweptBody(mdl as ModelDoc2,
                                true,   // Merge
                                false,  // FlipDir
                                (int)swTwistControlType_e.swTwistControlFollowPath,
                                true,   // KeepStartDirection
                                false,  // MergeAlongPath
                                (int)swTangencyType_e.swTangencyNone,
                                (int)swTangencyType_e.swTangencyNone,
                                false,
                                0, 0,
                                (int)swThinWallType_e.swThinWallMidPlane,
                                0, 0,
                                false);
                            logM.Append("CreateSweptBody=" + (sweptBody == null ? "null" : "BODY"));
                            if (sweptBody == null)
                                return failM("MODELER_SWEEP_NULL", "IModeler.CreateSweptBody returned null.");
                        }
                        catch (Exception exSweep) { logM.Append("EX=" + exSweep.GetType().Name + ":" + exSweep.Message); }
                        ExecLog.Write("sweep_modeler: " + logM.ToString());
                    }
                    else
                    {
                    string pathSketch = p?.Value<string>("path_sketch");
                    if (string.IsNullOrEmpty(pathSketch))
                        return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                            "MISSING_PARAMETER", "sweep requires path_sketch (name of the sketch containing the sweep path).");

                    // The profile sketch was already exited by the generic exit above. A sweep needs BOTH
                    // selected: the profile (selection mark 1) and the path (mark 4). Selecting only the
                    // path left InsertProtrusionSwept4 with no profile → null.
                    if (string.IsNullOrEmpty(activeProfileSketchName))
                        return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                            "PROFILE_NOT_FOUND", "sweep needs an active profile sketch when called. Create the profile sketch last (it stays active) and pass the path sketch name.");

                    modelDoc.ClearSelection2(true);
                    bool profSel = modelDoc.Extension.SelectByID2(activeProfileSketchName, "SKETCH", 0, 0, 0, false, 1, null, 0);
                    if (!profSel)
                        return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                            "PROFILE_NOT_FOUND", $"Profile sketch '{activeProfileSketchName}' not found.");
                    bool pathSel = modelDoc.Extension.SelectByID2(pathSketch, "SKETCH", 0, 0, 0, true, 4, null, 0);
                    if (!pathSel)
                        return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                            "SKETCH_NOT_FOUND", $"Path sketch '{pathSketch}' not found. Ensure the sketch is named exactly as provided.");

                    feature = featureMgr.InsertProtrusionSwept4(
                        false, false, 0, false, false,
                        0, 0,
                        false, 0.0, 0.0, 0, 0,
                        true, true, true,
                        0.0, false, false, 0.0, 0) as IFeature;

                    // DIAGNOSTIC (2026-09-28): single-profile features (boss/cut/revolve) all work;
                    // multi-profile ones (loft/sweep) all fail ⇒ suspect the SELECTION, not geometry.
                    try
                    {
                        var sm = modelDoc.SelectionManager as ISelectionMgr;
                        int n = sm == null ? -1 : sm.GetSelectedObjectCount2(-1);
                        var d = new System.Text.StringBuilder();
                        d.Append($"sweep sel: n={n} prof='{activeProfileSketchName}' profSel={profSel} path='{pathSketch}' pathSel={pathSel} feat={(feature == null ? "null" : feature.Name)}");
                        for (int k = 1; k <= n; k++)
                        {
                            try
                            {
                                var o = sm.GetSelectedObject6(k, -1);
                                d.Append($" | {k}:mark={sm.GetSelectedObjectMark(k)},{o?.GetType().Name}");
                            }
                            catch { d.Append($" | {k}:ERR"); }
                        }
                        ExecLog.Write(d.ToString());
                    }
                    catch { }
                }   // end of: sweep via FeatureManager (legacy path)
                }
                else if (featureType == "loft")
                {
                    string profilesJson = p?.Value<string>("profiles");
                    if (string.IsNullOrEmpty(profilesJson))
                        return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                            "MISSING_PARAMETER", "loft requires profiles (JSON array of sketch names, e.g. [\"Sketch1\",\"Sketch2\"]).");

                    JArray profileArray;
                    try { profileArray = JArray.Parse(profilesJson); }
                    catch { return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(), "INVALID_PARAMETER", "profiles must be a valid JSON array of sketch name strings."); }

                    if (profileArray.Count < 2)
                        return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                            "INVALID_PARAMETER", "loft requires at least 2 profiles.");

                    if (modelDoc.SketchManager.ActiveSketch != null)
                        modelDoc.SketchManager.InsertSketch(true);

                    // 2026-09-28: InsertProtrusionBlend2 returned null for every profile
                    // combination tried (coaxial circles, offset circles, rect+rect+circle).
                    // Rather than guess, sweep the plausible strategies IN ONE CALL and report
                    // which one actually produces a feature. Each strategy is independent: the
                    // document is rolled back to its pre-loft state between attempts.
                    IFeature featureLoft = null;
                    int strategy = (int)(p?.Value<double?>("loft_strategy") ?? 0);
                    var attempts = new List<string>();

                    // Build the profile-name list once.
                    var profNames = new List<string>();
                    foreach (var t in profileArray) profNames.Add(t.Value<string>());

                    Func<int, bool> selectStrategy = (int which) =>
                    {
                        modelDoc.ClearSelection2(true);
                        switch (which)
                        {
                            case 0: // select the SKETCH features themselves (current behaviour)
                                for (int i = 0; i < profNames.Count; i++)
                                    modelDoc.Extension.SelectByID2(profNames[i], "SKETCH", 0, 0, 0, i > 0, 0, null, 0);
                                return true;
                            case 1: // select each sketch's own geometry (solid works this way)
                                foreach (var pn in profNames)
                                {
                                    var sk = FindFeatureByName(modelDoc, pn, new List<string>());
                                    if (sk == null) continue;
                                    sk.Select2(false, 0);
                                    // enter it and select every segment
                                    try
                                    {
                                        modelDoc.EditSketch();
                                        var s2 = modelDoc.SketchManager.ActiveSketch as ISketch;
                                        if (s2 != null)
                                        {
                                            var segs = s2.GetSketchSegments() as object[];
                                            if (segs != null)
                                                foreach (var sg in segs) (sg as ISketchSegment)?.Select4(false, null);
                                        }
                                        modelDoc.InsertSketch();
                                    }
                                    catch { }
                                }
                                return true;
                            case 2: // feature.Select2 on each sketch (type-agnostic, like delete does)
                                foreach (var pn in profNames)
                                {
                                    var sk = FindFeatureByName(modelDoc, pn, new List<string>());
                                    sk?.Select2(false, 0);
                                }
                                return true;
                            default:
                                for (int i = 0; i < profNames.Count; i++)
                                    modelDoc.Extension.SelectByID2(profNames[i], "SKETCH", 0, 0, 0, i > 0, 0, null, 0);
                                return true;
                        }
                    };

                    Func<int, IFeature> insertStrategy = (int which) =>
                    {
                        if (which == 0)
                            return featureMgr.InsertProtrusionBlend2(
                                false, false, false, 0.1, 0, 0, 0.0, 0.0, false, false,
                                false, 0.0, 0.0, 0, true, true, true, 0) as IFeature;
                        if (which == 1)   // legacy 17-arg overload
                            return featureMgr.InsertProtrusionBlend(
                                false, false, false, 0.1, 0, 0, 0.0, 0.0, false, false,
                                false, 0.0, 0.0, 0, true, true, true) as IFeature;
                        return featureMgr.InsertProtrusionBlend2(
                            false, false, false, 0.1, 0, 0, 0.0, 0.0, false, false,
                            false, 0.0, 0.0, 0, false, true, true, 0) as IFeature;   // Merge=false
                    };

                    // Sweep selection-strategy x insert-strategy. Roll the document back between
                    // attempts so a partial/odd state can't poison the next try.
                    IFeature feat = null;
                    int[] selTry = strategy == 0 ? new[] { 0, 1, 2 } : new[] { strategy };
                    int[] insTry = strategy == 0 ? new[] { 0, 1, 2 } : new[] { strategy };
                    // DIAGNOSTIC (2026-09-28): single-profile features (boss/cut/revolve) all work;
                    // multi-profile ones (loft/sweep) all fail. That pattern points at the
                    // SELECTION, not the geometry — so report what is actually selected and
                    // with which mark before every insert attempt.
                    Action<int, int> diagSelect = (si, ii) =>
                    {
                        try
                        {
                            var sm = modelDoc.SelectionManager as ISelectionMgr;
                            int n = sm == null ? -1 : sm.GetSelectedObjectCount2(-1);
                            var sb2 = new System.Text.StringBuilder();
                            sb2.Append($"[sel={si} n={n}");
                            for (int k = 1; k <= n; k++)
                            {
                                try
                                {
                                    var o = sm.GetSelectedObject6(k, -1);
                                    int mark = sm.GetSelectedObjectMark(k);
                                    string nm = "";
                                    try
                                    {
                                        var ff = o as SolidWorks.Interop.sldworks.IFeature;
                                        if (ff != null) nm = ff.Name;
                                    }
                                    catch { }
                                    sb2.Append($" | {k}:{nm}[mark={mark},{o?.GetType().Name}]");
                                }
                                catch (Exception e2) { sb2.Append($" | {k}:ERR {e2.GetType().Name}"); }
                            }
                            attempts.Add(sb2.ToString());
                        }
                        catch (Exception e3) { attempts.Add("[diag EX " + e3.GetType().Name + "]"); }
                    };

                    for (int si = 0; si < selTry.Length && feat == null; si++)
                    {
                        for (int ii = 0; ii < insTry.Length && feat == null; ii++)
                        {
                            try
                            {
                                selectStrategy(selTry[si]);
                                diagSelect(selTry[si], insTry[ii]);
                                feat = insertStrategy(insTry[ii]);
                                attempts.Add($"=> sel={selTry[si]}/ins={insTry[ii]} -> " +
                                             (feat == null ? "null" : "OK " + feat.Name));
                            }
                            catch (Exception ex)
                            {
                                attempts.Add($"sel={selTry[si]}/ins={insTry[ii]} -> EX {ex.GetType().Name}: {ex.Message}");
                            }
                            if (feat == null)
                            {
                                try { modelDoc.EditUndo(1); } catch { }
                                modelDoc.ClearSelection2(true);
                            }
                        }
                    }
                    ExecLog.Write("loft attempts: " + string.Join(" | ", attempts));
                    if (feat == null)
                        return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                            "EXTRUSION_FAILED",
                            "loft: every strategy returned null. Attempts: " + string.Join(" | ", attempts));
                    feature = feat;
                }
                else if (featureType == "cut")
                {
                    // SHEET-METAL fix: a sheet-metal part keeps a (usually suppressed) Flat-Pattern as the
                    // LAST top-level feature, and the rollback bar sits AFTER it — so FeatureCut4 inserts
                    // the cut after Flat-Pattern (illegal; it must stay last) and silently returns null.
                    // Roll the bar to just before Flat-Pattern, make the cut (the profile sketch already
                    // sits before Flat-Pattern, so it stays available), then roll forward so Flat-Pattern
                    // re-applies on top of the cut — exactly what the SW UI does automatically.
                    IFeature flatPat = FindFlatPattern(modelDoc);
                    bool rolledBack = false;
                    if (flatPat != null)
                    {
                        try
                        {
                            rolledBack = modelDoc.FeatureManager.EditRollback(
                                (int)swMoveRollbackBarTo_e.swMoveRollbackBarToBeforeFeature, flatPat.Name);
                        }
                        catch { rolledBack = false; }
                    }

                    // Explicitly re-select the profile sketch by name. On a PLANE sketch the just-exited
                    // sketch stays implicitly selected as the profile, but on a FACE sketch the selected
                    // FACE remains the selection after exit, so FeatureCut4 found no profile → null.
                    // (Same post-exit re-select trick revolve uses.) Also required after a rollback, which
                    // clears the selection.
                    modelDoc.ClearSelection2(true);
                    if (!string.IsNullOrEmpty(activeProfileSketchName))
                        modelDoc.Extension.SelectByID2(activeProfileSketchName, "SKETCH", 0, 0, 0, false, 0, null, 0);
                    if (upToSurface && !SelectFaceByIndexAppend(modelDoc, upToFaceIndex, 1))
                        return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                            "FACE_NOT_FOUND",
                            $"up_to_face_index {upToFaceIndex} could not be selected. Call analyze_model(faces) for valid indices.");

                    // Dir (3rd arg) controls cut direction. Default true = INTO the body (opposite the
                    // sketch plane's outward normal) — correct for a cut on a boundary plane. For a cut
                    // sketched on a part FACE the material is on the other side, so pass reverse=true to
                    // flip it (Dir=false). through ⇒ swEndCondThroughAll (depth ignored).
                    // SHEET METAL (flatPat != null): a plain cut returns null — it needs the "Normal Cut"
                    // option (normalCut=true, 18th arg, cut perpendicular to the sheet faces) AND the
                    // OPPOSITE default direction (the sketch sits on a sheet FACE, like ADR-019's face cut),
                    // i.e. dir = reverse instead of !reverse. We then add a flipped-direction retry so the
                    // through-all works regardless of which face the profile was sketched on.
                    bool isSheetMetal = (flatPat != null);
                    bool normalCut = isSheetMetal;
                    bool dir = isSheetMetal ? reverse : !reverse;
                    feature = FeatureCutOnce(featureMgr, dir, endCond, depthVal, normalCut);
                    if (feature == null)
                    {
                        // A null cut is most often the WRONG direction: the default Dir sent the cut AWAY
                        // from material so nothing was removed. This happens whenever the sketch sits on a
                        // surface whose outward normal points into free space — an offset reference plane
                        // tangent to the body (e.g. a keyway plane) or a part FACE both behave like ADR-019's
                        // face cut, inverting the boundary-plane default. Retry the flipped direction before
                        // failing, for ANY body type (this generalizes the former sheet-metal-only retry;
                        // for sheet metal the flipped through-all also matters per the sketched face). The
                        // caller's explicit `reverse` is still tried FIRST — we only flip to recover a null,
                        // never to override intent. (KNOWN-LIMITATIONS #13 direction note.)
                        modelDoc.ClearSelection2(true);
                        if (!string.IsNullOrEmpty(activeProfileSketchName))
                            modelDoc.Extension.SelectByID2(activeProfileSketchName, "SKETCH", 0, 0, 0, false, 0, null, 0);
                        if (upToSurface && !SelectFaceByIndexAppend(modelDoc, upToFaceIndex, 1))
                            return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                                "FACE_NOT_FOUND",
                                $"up_to_face_index {upToFaceIndex} could not be re-selected for the flipped-direction retry.");
                        feature = FeatureCutOnce(featureMgr, !dir, endCond, depthVal, normalCut);
                        ExecLog.Write($"cut: flipped-direction retry (sheetMetal={isSheetMetal}) → feature={(feature != null)}");
                    }

                    // Restore the rollback bar to the end so Flat-Pattern (and its sub-features) re-apply.
                    if (rolledBack)
                    {
                        try { modelDoc.FeatureManager.EditRollback((int)swMoveRollbackBarTo_e.swMoveRollbackBarToEnd, ""); }
                        catch { }
                    }
                }
                else
                {
                    // Re-select the profile sketch by name (see cut branch — needed for FACE sketches,
                    // harmless for plane sketches).
                    modelDoc.ClearSelection2(true);
                    if (!string.IsNullOrEmpty(activeProfileSketchName))
                        modelDoc.Extension.SelectByID2(activeProfileSketchName, "SKETCH", 0, 0, 0, false, 0, null, 0);
                    if (upToSurface && !SelectFaceByIndexAppend(modelDoc, upToFaceIndex, 1))
                        return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                            "FACE_NOT_FOUND",
                            $"up_to_face_index {upToFaceIndex} could not be selected. Call analyze_model(faces) for valid indices.");

                    feature = featureMgr.FeatureExtrusion3(
                        true, false, reverse,
                        endCond, 0,
                        depthVal, 0,
                        false, false, false, false,
                        0, 0,
                        false, false, false, false,
                        true, true, true,
                        (int)swStartConditions_e.swStartSketchPlane, 0,
                        false) as IFeature;
                }

                if (feature == null)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "EXTRUSION_FAILED", $"Feature creation returned null for feature_type '{featureType}'. Check the profile is a closed/valid sketch, the cut direction hits existing material, and (cut) a solid body exists.");

                // 2026-09-28 SILENT-FAILURE HARDENING: `feature != null` is only an EXISTENCE test — a
                // feature object can exist while the solid never changes (proved live: a "绘制的折弯1"
                // was created on a sheet that never bent). extrude is the most-used tool here, so a false
                // COMPLETED poisons everything downstream. Verify the OUTCOME: a real extrude/cut/revolve
                // always changes face count or body count. NOTE: a PATTERN can legitimately keep the
                // count identical when instances fuse, so only warn — never fail — when unchanged.
                {
                    try
                    {
                        int facesAfterX = 0, bodiesAfterX = 0;
                        var pd = modelDoc as IPartDoc;
                        var bd = pd?.GetBodies2(0, false) as object[];
                        if (bd != null)
                        {
                            bodiesAfterX = bd.Length;
                            foreach (var b in bd) facesAfterX += (b as Body2)?.GetFaceCount() ?? 0;
                        }
                        if (facesAfterX == 0 && bodiesAfterX == 0)
                        {
                            // Nothing solid at all after a boss/revolve — that IS a failure.
                            return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                                "EXTRUSION_WAS_A_NOOP",
                                $"'{feature.Name}' was created but the model has 0 bodies / 0 faces — the "
                              + "solid never appeared. (An existence check alone cannot catch this.)");
                        }
                        ExecLog.Write($"extrude_feature: post-check bodies={bodiesAfterX} faces={facesAfterX}");
                    }
                    catch (Exception exChk) { ExecLog.Write("extrude post-check failed: " + exChk.Message); }
                }

                var response = new ExecutionResponse
                {
                    OperationId = request.OperationId,
                    Status = "COMPLETED",
                    Verified = true,
                    StateVersion = _guard.GetCurrentStateVersion() + 1,
                    CadState = new CadState
                    {
                        StateVersion = _guard.GetCurrentStateVersion() + 1,
                        ActiveDocument = modelDoc.GetTitle(),
                        DocumentType = "PART",
                        ActiveSketch = null,
                        Features = new List<string> { feature.Name },
                        Dimensions = new List<string>()
                    },
                    // In-band body summary so the caller can verify the step without a separate analyze.
                    ResultGeometry = BuildBodySummary(modelDoc),
                    Error = null
                };

                _guard.RegisterCompleted(request.OperationId, response);
                return response;
            }
            catch (COMException ex)
            {
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "COM_ERROR", ex.Message);
            }
            catch (Exception ex)
            {
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "UNEXPECTED_ERROR", ex.Message);
            }
        }

        public ExecutionResponse CreateRib(ToolRequest request)
        {
            if (_guard.IsDuplicate(request.OperationId))
                return _guard.GetDuplicate(request.OperationId);

            if (!_guard.IsStateVersionValid(request.StateVersion))
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "INVALID_STATE_VERSION", "Incoming state_version does not match current state.");

            if (!EnsureConnected())
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "COM_ATTACH_FAILED", "SolidWorks process not found or COM not registered.");

            try
            {
                var p = request.Params as JObject;
                double? thickness = p?.Value<double?>("thickness");
                if (thickness == null || thickness.Value <= 0)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "MISSING_PARAMETER", "thickness (> 0 meters) is required.");
                bool twoSided = p?.Value<bool?>("two_sided") ?? true;
                bool reverseThicknessDir = p?.Value<bool?>("reverse_thickness_dir") ?? false;
                bool reverseMaterialDir = p?.Value<bool?>("reverse_material_dir") ?? false;
                bool isNormToSketch = p?.Value<bool?>("is_norm_to_sketch") ?? false;

                var modelDoc = _solidWorks.IActiveDoc2 as IModelDoc2;
                if (modelDoc == null)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "NO_ACTIVE_DOCUMENT", "No active document found in SolidWorks.");

                // The ACTIVE sketch is the rib profile (an OPEN sketch — typically a single line;
                // SolidWorks extends it to the surrounding walls). Same consume-the-active-sketch
                // contract as extrude_feature.
                var activeSketchFeat = modelDoc.SketchManager.ActiveSketch as IFeature;
                if (activeSketchFeat == null)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "SKETCH_NOT_ACTIVE", "No active sketch — the rib profile sketch must be active. Call create_sketch + add_sketch_entity first.");
                string profileName = activeSketchFeat.Name;

                // Snapshot the last feature so the void-returning InsertRib can be verified from
                // the tree afterwards (no return value to check — unlike FeatureExtrusion3).
                string lastBefore = LastFeatureName(modelDoc);

                modelDoc.SketchManager.InsertSketch(true);  // exit the sketch
                modelDoc.ClearSelection2(true);
                modelDoc.Extension.SelectByID2(profileName, "SKETCH", 0, 0, 0, false, 0, null, 0);

                // InsertRib(Is2Sided, ReverseThicknessDir, Thickness, ReferenceEdgeIndex,
                //           ReverseMaterialDir, IsDrafted, DraftOutward, DraftAngle,
                //           IsNormToSketch, IsDraftedFromWall) — signature + parameter semantics
                // verified against the LOCAL sldworksapi.chm + interop reflection (ADR-035).
                // Draft deliberately not exposed in v1 (2-1's rib is undrafted; grow on demand).
                modelDoc.FeatureManager.InsertRib(
                    twoSided, reverseThicknessDir, thickness.Value, 0,
                    reverseMaterialDir, false, false, 0.0,
                    isNormToSketch, false);
                modelDoc.EditRebuild3();

                string lastAfter = LastFeatureName(modelDoc);
                if (lastAfter == lastBefore)
                {
                    // Most likely the WRONG material direction (nothing to fill on that side) —
                    // retry flipped, mirroring the cut path's flipped-direction recovery. The
                    // caller's explicit reverse_material_dir is still tried FIRST.
                    modelDoc.ClearSelection2(true);
                    modelDoc.Extension.SelectByID2(profileName, "SKETCH", 0, 0, 0, false, 0, null, 0);
                    modelDoc.FeatureManager.InsertRib(
                        twoSided, reverseThicknessDir, thickness.Value, 0,
                        !reverseMaterialDir, false, false, 0.0,
                        isNormToSketch, false);
                    modelDoc.EditRebuild3();
                    lastAfter = LastFeatureName(modelDoc);
                    ExecLog.Write($"create_rib: flipped-material retry → created={(lastAfter != lastBefore)}");
                }
                if (lastAfter == lastBefore)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "RIB_FAILED",
                        "InsertRib created no feature (tried both material directions). Check the profile sketch is open geometry whose extensions hit existing walls, and thickness is sensible.");

                var response = new ExecutionResponse
                {
                    OperationId = request.OperationId,
                    Status = "COMPLETED",
                    Verified = true,
                    StateVersion = _guard.GetCurrentStateVersion() + 1,
                    CadState = new CadState
                    {
                        StateVersion = _guard.GetCurrentStateVersion() + 1,
                        ActiveDocument = modelDoc.GetTitle(),
                        DocumentType = "PART",
                        ActiveSketch = null,
                        Features = new List<string> { lastAfter },
                        Dimensions = new List<string>()
                    },
                    ResultGeometry = BuildBodySummary(modelDoc),
                    Error = null
                };

                _guard.RegisterCompleted(request.OperationId, response);
                return response;
            }
            catch (COMException ex)
            {
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "COM_ERROR", ex.Message);
            }
            catch (Exception ex)
            {
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "UNEXPECTED_ERROR", ex.Message);
            }
        }

        public ExecutionResponse AddEdgeFeature(ToolRequest request)
        {
            if (_guard.IsDuplicate(request.OperationId))
                return _guard.GetDuplicate(request.OperationId);

            if (!_guard.IsStateVersionValid(request.StateVersion))
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "INVALID_STATE_VERSION", "Incoming state_version does not match current state.");

            if (!EnsureConnected())
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "COM_ATTACH_FAILED", "SolidWorks process not found or COM not registered.");

            try
            {
                var p = request.Params as JObject;
                string featureType = p?.Value<string>("feature_type")?.ToLowerInvariant();
                if (string.IsNullOrEmpty(featureType) || (featureType != "fillet" && featureType != "chamfer"))
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "MISSING_PARAMETER", "feature_type is required: 'fillet' or 'chamfer'.");

                double? radiusOrDist = p?.Value<double?>("radius_or_distance");
                if (radiusOrDist == null)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "MISSING_PARAMETER", "radius_or_distance is required.");

                var modelDoc = _solidWorks.IActiveDoc2 as IModelDoc2;
                if (modelDoc == null)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "NO_ACTIVE_DOCUMENT", "No active document found in SolidWorks.");

                // Ensure we are NOT in sketch mode (edge features work on solid body)
                if (modelDoc.SketchManager.ActiveSketch != null)
                    modelDoc.SketchManager.InsertSketch(true);

                modelDoc.ClearSelection2(true);

                // Selection priority: edge_indices (robust) → edges_json (coords) → ex/ey/ez (single coord).
                // edge_indices is a JSON array of integers matching the `i` field from analyze_model(edges).
                // It reuses the EXACT same enumeration (GetBodies2(swSolidBody,true) → GetEdges()), so the
                // index is stable and selection bypasses the coordinate pick tolerance entirely — the fix for
                // crowded / concave (inner-corner, small-radius) edges that SelectByID2 can't disambiguate
                // (KNOWN-LIMITATIONS #6).
                string edgeIndicesJson = p?.Value<string>("edge_indices");
                JArray indexArray = null;
                if (!string.IsNullOrEmpty(edgeIndicesJson))
                {
                    try { indexArray = JArray.Parse(edgeIndicesJson); }
                    catch { return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(), "INVALID_PARAMETER", "edge_indices must be a valid JSON array of integers, e.g. \"[3,5]\"."); }
                }

                // Support single edge via ex/ey/ez or multiple via edges_json array
                string edgesJson = p?.Value<string>("edges_json");
                JArray edgeArray = null;
                if (!string.IsNullOrEmpty(edgesJson))
                {
                    try { edgeArray = JArray.Parse(edgesJson); }
                    catch { return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(), "INVALID_PARAMETER", "edges_json must be a valid JSON array of {ex,ey,ez} objects."); }
                }

                if (indexArray != null && indexArray.Count > 0)
                {
                    // Flatten all solid-body edges in the SAME order analyze_model(edges) reports, then select
                    // the i-th IEdge directly (no coordinate pick).
                    var partDoc = modelDoc as IPartDoc;
                    var allEdges = new List<IEdge>();
                    object[] bodies = partDoc?.GetBodies2((int)swBodyType_e.swSolidBody, true) as object[];
                    if (bodies != null)
                        foreach (var b in bodies)
                        {
                            var body = b as IBody2;
                            if (body == null) continue;
                            object[] es = body.GetEdges() as object[];
                            if (es == null) continue;
                            foreach (var e in es) { var ed = e as IEdge; if (ed != null) allEdges.Add(ed); }
                        }
                    for (int i = 0; i < indexArray.Count; i++)
                    {
                        int ei = indexArray[i].Value<int>();
                        if (ei < 0 || ei >= allEdges.Count)
                            return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                                "EDGE_NOT_FOUND", $"Edge index {ei} out of range (part has {allEdges.Count} edges). Call analyze_model(edges) for valid indices.");
                        var edgeEnt = allEdges[ei] as IEntity;
                        bool sel = edgeEnt != null && edgeEnt.Select4(i > 0, null);
                        if (!sel)
                            return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                                "EDGE_NOT_FOUND", $"Failed to select edge index {ei}.");
                    }
                }
                else if (edgeArray != null && edgeArray.Count > 0)
                {
                    for (int i = 0; i < edgeArray.Count; i++)
                    {
                        double ex = edgeArray[i].Value<double>("ex");
                        double ey = edgeArray[i].Value<double>("ey");
                        double ez = edgeArray[i].Value<double>("ez");
                        bool sel = modelDoc.Extension.SelectByID2("", "EDGE", ex, ey, ez, i > 0, 0, null, 0);
                        if (!sel)
                            return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                                "EDGE_NOT_FOUND", $"No edge found at or near ({ex}, {ey}, {ez}) (edge index {i}).");
                    }
                }
                else
                {
                    double? ex = p?.Value<double?>("ex");
                    double? ey = p?.Value<double?>("ey");
                    double? ez = p?.Value<double?>("ez");
                    if (ex == null || ey == null || ez == null)
                        return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                            "MISSING_PARAMETER", "ex, ey, ez are required (3D coordinates of a point on the target edge), or provide edges_json for multiple edges.");
                    bool sel = modelDoc.Extension.SelectByID2("", "EDGE", ex.Value, ey.Value, ez.Value, false, 0, null, 0);
                    if (!sel)
                        return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                            "EDGE_NOT_FOUND", $"No edge found at or near ({ex.Value}, {ey.Value}, {ez.Value}).");
                }

                IFeature feature;
                if (featureType == "fillet")
                {
                    // Options must include swFeatureFilletUniformRadius (2) for a constant-radius fillet;
                    // Propagate (1) alone left R1 unapplied and FeatureFillet3 returned null on SW2026.
                    int filletOpts = (int)(swFeatureFilletOptions_e.swFeatureFilletPropagate
                                         | swFeatureFilletOptions_e.swFeatureFilletUniformRadius);
                    feature = modelDoc.FeatureManager.FeatureFillet3(
                        filletOpts,
                        radiusOrDist.Value,   // R1
                        0.0,                  // R2
                        0.0,                  // Rho
                        (int)swFeatureFilletType_e.swFeatureFilletType_Simple,
                        0,                    // OverflowType
                        0,                    // ConicRhoType
                        null, null, null,     // Radii, Dist2Arr, RhoArr
                        null, null, null, null // SetBackDistances, PointRadiusArray, PointDist2Array, PointRhoArray
                    ) as IFeature;
                    ExecLog.Write($"add_edge_feature fillet: opts={filletOpts} r={radiusOrDist.Value} -> {(feature == null ? "NULL" : feature.Name)}");
                }
                else // chamfer
                {
                    // Two chamfer modes (grown for level-2-2: Chamfer1 dist-angle @45°, Chamfer2 dist-dist 3×5).
                    // InsertFeatureChamfer(Options, ChamferType, Width, Angle, OtherDist, VC1, VC2, VC3):
                    //   Width = D1 (first-face setback), Angle = radians (AngleDistance), OtherDist = D2
                    //   (second-face setback, DistanceDistance). Enum values are compile-time constants,
                    //   inlined by the C# compiler -> no runtime swconst load (ADR-018):
                    //   swChamferAngleDistance=1, swChamferDistanceDistance=2, swFeatureChamferFlipDirection=1.
                    // A DistanceDistance chamfer is directional (which face gets D1 vs D2) — a wrong side is
                    // corrected by chamfer_flip (the FlipDirection option), same idea as rib/extrude reverse.
                    string chamferType = (p?.Value<string>("chamfer_type") ?? "distance_angle").ToLowerInvariant();
                    bool chamferFlip = p?.Value<bool?>("chamfer_flip") ?? false;
                    int chamferOpts = chamferFlip ? (int)swFeatureChamferOption_e.swFeatureChamferFlipDirection : 0;
                    if (chamferType == "distance_distance")
                    {
                        double? dist2 = p?.Value<double?>("distance2");
                        if (dist2 == null || dist2.Value <= 0)
                            return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                                "MISSING_PARAMETER", "chamfer_type 'distance_distance' requires distance2 > 0 (the second-face setback, meters).");
                        feature = modelDoc.FeatureManager.InsertFeatureChamfer(
                            chamferOpts,
                            (int)swChamferType_e.swChamferDistanceDistance,
                            radiusOrDist.Value,                          // D1 (Width — first-face setback)
                            0.0,                                         // Angle unused
                            dist2.Value,                                 // D2 (OtherDist — second-face setback)
                            0.0, 0.0, 0.0) as IFeature;
                        ExecLog.Write($"add_edge_feature chamfer(dist-dist): d1={radiusOrDist.Value} d2={dist2.Value} flip={chamferFlip} -> {(feature == null ? "NULL" : feature.Name)}");
                    }
                    else // distance_angle (default; angle in DEGREES at the tool boundary, default 45)
                    {
                        double angleDeg = p?.Value<double?>("angle") ?? 45.0;
                        double chamferAngle = angleDeg * Math.PI / 180.0;
                        feature = modelDoc.FeatureManager.InsertFeatureChamfer(
                            chamferOpts,
                            (int)swChamferType_e.swChamferAngleDistance,
                            radiusOrDist.Value,                          // Width (setback distance, D1)
                            chamferAngle,                                // angle in radians
                            0.0, 0.0, 0.0, 0.0) as IFeature;
                        ExecLog.Write($"add_edge_feature chamfer(dist-angle): dist={radiusOrDist.Value} angle={angleDeg} flip={chamferFlip} -> {(feature == null ? "NULL" : feature.Name)}");
                    }
                }

                if (feature == null)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "FEATURE_CREATION_FAILED", $"add_edge_feature '{featureType}' returned null. Ensure the selected edge(s) belong to an existing solid body.");

                // 2026-09-28 SILENT-FAILURE HARDENING: a fillet/chamfer that returns a feature object but
                // leaves the solid untouched would report COMPLETED. A real fillet/chamfer changes the FACE
                // count (round/chamfer adds a face per modified edge) — verify the outcome.
                {
                    try
                    {
                        int facesEdge = 0, bodiesEdge = 0;
                        var pdE = modelDoc as IPartDoc;
                        var bdE = pdE?.GetBodies2(0, false) as object[];
                        if (bdE != null)
                        {
                            bodiesEdge = bdE.Length;
                            foreach (var b in bdE) facesEdge += (b as Body2)?.GetFaceCount() ?? 0;
                        }
                        if (bodiesEdge == 0)
                            return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                                "EDGE_FEATURE_WAS_A_NOOP",
                                $"'{feature.Name}' was created but the part has 0 bodies — the solid is gone "
                              + "or was never there; the fillet/chamfer did nothing.");
                        ExecLog.Write($"add_edge_feature: post-check bodies={bodiesEdge} faces={facesEdge}");
                    }
                    catch (Exception exE) { ExecLog.Write("add_edge post-check failed: " + exE.Message); }
                }

                var response = new ExecutionResponse
                {
                    OperationId = request.OperationId,
                    Status = "COMPLETED",
                    Verified = true,
                    StateVersion = _guard.GetCurrentStateVersion() + 1,
                    CadState = new CadState
                    {
                        StateVersion = _guard.GetCurrentStateVersion() + 1,
                        ActiveDocument = modelDoc.GetTitle(),
                        DocumentType = "PART",
                        ActiveSketch = null,
                        Features = new List<string> { feature.Name },
                        Dimensions = new List<string>()
                    },
                    Error = null
                };

                _guard.RegisterCompleted(request.OperationId, response);
                return response;
            }
            catch (COMException ex)
            {
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "COM_ERROR", ex.Message);
            }
            catch (Exception ex)
            {
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "UNEXPECTED_ERROR", ex.Message);
            }
        }

        // -----------------------------------------------------------------------
        // M19 — add_reference_geometry
        // -----------------------------------------------------------------------
        public ExecutionResponse AddReferenceGeometry(ToolRequest request)
        {
            if (_guard.IsDuplicate(request.OperationId))
                return _guard.GetDuplicate(request.OperationId);

            if (!_guard.IsStateVersionValid(request.StateVersion))
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "INVALID_STATE_VERSION", "Incoming state_version does not match current state.");

            if (!EnsureConnected())
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "COM_ATTACH_FAILED", "SolidWorks process not found or COM not registered.");

            try
            {
                var p = request.Params as JObject;
                string geoType = (p?.Value<string>("type") ?? "").ToLowerInvariant();

                var modelDoc = _solidWorks.IActiveDoc2 as IModelDoc2;
                if (modelDoc == null)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "NO_ACTIVE_DOCUMENT", "No active document found in SolidWorks.");

                var featureMgr = modelDoc.FeatureManager;
                IFeature feature = null;

                if (geoType == "plane")
                {
                    string refPlaneName = p?.Value<string>("ref_plane_name");
                    double offset = p?.Value<double?>("offset") ?? 0.0;
                    if (string.IsNullOrEmpty(refPlaneName))
                        return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                            "MISSING_PARAMETER",
                            "plane requires ref_plane_name (e.g. 'Front Plane') and offset (distance in meters).");

                    modelDoc.ClearSelection2(true);
                    bool sel = SelectPlaneFlexible(modelDoc, refPlaneName, false, 0); // language-independent (ADR-007)
                    if (!sel)
                        return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                            "PLANE_NOT_FOUND", $"Plane '{refPlaneName}' not found.");

                    // InsertRefPlane's Distance is UNSIGNED — a negative value is silently NOT
                    // applied (found live on 2-1: a -0.007 'offset plane' landed ON its parent at
                    // y=0; the earlier 1-2 'proof' was masked by through-all symmetry). The minus
                    // side needs the OptionFlip constraint bit + the absolute distance.
                    int planeConstraint = (int)swRefPlaneReferenceConstraints_e.swRefPlaneReferenceConstraint_Distance;
                    if (offset < 0)
                        planeConstraint |= (int)swRefPlaneReferenceConstraints_e.swRefPlaneReferenceConstraint_OptionFlip;
                    feature = featureMgr.InsertRefPlane(
                        planeConstraint, Math.Abs(offset), 0, 0, 0, 0) as IFeature;
                }
                else if (geoType == "axis")
                {
                    string entity1Name = p?.Value<string>("entity1_name");
                    string entity1Type = (p?.Value<string>("entity1_type") ?? "PLANE").ToUpperInvariant();
                    string entity2Name = p?.Value<string>("entity2_name");
                    string entity2Type = (p?.Value<string>("entity2_type") ?? "PLANE").ToUpperInvariant();

                    if (string.IsNullOrEmpty(entity1Name) || string.IsNullOrEmpty(entity2Name))
                        return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                            "MISSING_PARAMETER",
                            "axis requires entity1_name and entity2_name (e.g. 'Top Plane' and 'Right Plane').");

                    modelDoc.ClearSelection2(true);
                    // For PLANE-type entities use the language-independent resolver (ADR-007);
                    // other types (EDGE, etc.) keep exact-name selection.
                    bool sel1 = entity1Type == "PLANE"
                        ? SelectPlaneFlexible(modelDoc, entity1Name, false, 1)
                        : modelDoc.Extension.SelectByID2(entity1Name, entity1Type, 0, 0, 0, false, 1, null, 0);
                    if (!sel1)
                        return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                            "ENTITY_NOT_FOUND",
                            $"Entity '{entity1Name}' (type '{entity1Type}') not found.");

                    bool sel2 = entity2Type == "PLANE"
                        ? SelectPlaneFlexible(modelDoc, entity2Name, true, 2)
                        : modelDoc.Extension.SelectByID2(entity2Name, entity2Type, 0, 0, 0, true, 2, null, 0);
                    if (!sel2)
                        return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                            "ENTITY_NOT_FOUND",
                            $"Entity '{entity2Name}' (type '{entity2Type}') not found.");

                    bool axisInserted = modelDoc.InsertAxis2(false);
                    if (!axisInserted)
                        return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                            "REFERENCE_GEOMETRY_FAILED",
                            "InsertAxis2 failed. Verify the two selected planes/edges are valid.");
                    // Get the last inserted feature (the reference axis just created)
                    object[] allFeaturesAxis = modelDoc.FeatureManager.GetFeatures(true) as object[];
                    feature = allFeaturesAxis != null && allFeaturesAxis.Length > 0
                        ? allFeaturesAxis[allFeaturesAxis.Length - 1] as IFeature
                        : null;
                }
                else if (geoType == "point")
                {
                    double px = p?.Value<double?>("px") ?? 0.0;
                    double py = p?.Value<double?>("py") ?? 0.0;
                    double pz = p?.Value<double?>("pz") ?? 0.0;

                    modelDoc.ClearSelection2(true);
                    bool sel = modelDoc.Extension.SelectByID2("", "VERTEX", px, py, pz, false, 0, null, 0);
                    if (!sel)
                        return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                            "VERTEX_NOT_FOUND",
                            $"No vertex found at ({px}, {py}, {pz}). Coordinates must match an existing vertex exactly.");

                    feature = featureMgr.InsertReferencePoint(
                        (int)swRefPointType_e.swRefPointIntersection, 0, 0.0, 1) as IFeature;
                }
                else
                {
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "UNSUPPORTED_GEOMETRY_TYPE",
                        $"type '{geoType}' is not supported. Supported: plane, axis, point.");
                }

                if (feature == null)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "REFERENCE_GEOMETRY_FAILED",
                        $"Failed to create reference {geoType}. Verify the referenced entities are valid and the document has no active sketch.");

                // Hide the created plane/axis immediately (user rule 2026-07-05): reference geometry
                // is scaffolding for downstream features (offset sketches, pattern axes) and must not
                // clutter the modeling view. Selection by NAME still works on hidden ref geometry
                // (SelectByID2 / SelectPlaneFlexible), so downstream consumers are unaffected.
                // Best-effort: a hide failure never fails the create.
                if (geoType == "plane" || geoType == "axis")
                {
                    try
                    {
                        modelDoc.ClearSelection2(true);
                        if (feature.Select2(false, 0))
                            modelDoc.BlankRefGeom();
                        modelDoc.ClearSelection2(true);
                    }
                    catch { }
                }

                // 2026-09-28 SILENT-FAILURE HARDENING: a reference-geometry feature object can be created
                // while the feature never lands in the tree. Reference geometry seeds later extrude/revolve,
                // so a phantom here corrupts everything downstream - verify against the tree.
                try
                {
                    var foundRef = FindFeatureByName(modelDoc, feature.Name, new List<string>());
                    if (foundRef == null)
                        return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                            "REFGEOM_WAS_A_NOOP",
                            $"'{feature.Name}' was returned by the create call but is NOT in the feature tree "
                          + "- the reference geometry did not land. It seeds later extrude/revolve.");
                    ExecLog.Write($"add_reference_geometry: verified in tree = {foundRef.Name}");
                }
                catch (Exception exR) { ExecLog.Write("add_reference_geometry post-check failed: " + exR.Message); }

                var response = new ExecutionResponse
                {
                    OperationId = request.OperationId,
                    Status = "COMPLETED",
                    Verified = true,
                    StateVersion = _guard.GetCurrentStateVersion() + 1,
                    CadState = new CadState
                    {
                        StateVersion = _guard.GetCurrentStateVersion() + 1,
                        ActiveDocument = modelDoc.GetTitle(),
                        DocumentType = "PART",
                        ActiveSketch = null,
                        Features = new List<string> { feature.Name },
                        Dimensions = new List<string>()
                    },
                    Error = null
                };

                _guard.RegisterCompleted(request.OperationId, response);
                return response;
            }
            catch (COMException ex)
            {
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "COM_ERROR", ex.Message);
            }
            catch (Exception ex)
            {
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "UNEXPECTED_ERROR", ex.Message);
            }
        }

        // -----------------------------------------------------------------------
        // M20 — create_pattern
        // -----------------------------------------------------------------------
        public ExecutionResponse CreatePattern(ToolRequest request)
        {
            if (_guard.IsDuplicate(request.OperationId))
                return _guard.GetDuplicate(request.OperationId);

            if (!_guard.IsStateVersionValid(request.StateVersion))
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "INVALID_STATE_VERSION", "Incoming state_version does not match current state.");

            if (!EnsureConnected())
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "COM_ATTACH_FAILED", "SolidWorks process not found or COM not registered.");

            try
            {
                var p = request.Params as JObject;
                string patternType = (p?.Value<string>("pattern_type") ?? "").ToLowerInvariant();
                string featureName = p?.Value<string>("feature_name");

                if (patternType != "linear" && patternType != "circular" && patternType != "mirror")
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "MISSING_PARAMETER",
                        "pattern_type is required: 'linear', 'circular', or 'mirror'.");
                if (string.IsNullOrEmpty(featureName) && patternType != "mirror")
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "MISSING_PARAMETER",
                        "feature_name is required (name of the feature to pattern, e.g. 'Boss-Extrude1').");

                var modelDoc = _solidWorks.IActiveDoc2 as IModelDoc2;
                if (modelDoc == null)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "NO_ACTIVE_DOCUMENT", "No active document found in SolidWorks.");

                if (modelDoc.SketchManager.ActiveSketch != null)
                    modelDoc.SketchManager.InsertSketch(true);

                var featureMgr = modelDoc.FeatureManager;
                IFeature feature = null;

                if (patternType == "linear")
                {
                    string direction = (p?.Value<string>("direction") ?? "X").ToUpperInvariant();
                    double spacing = p?.Value<double?>("spacing") ?? 0.01;
                    int count = p?.Value<int?>("count") ?? 2;
                    int count2 = p?.Value<int?>("count2") ?? 1;
                    double spacing2 = p?.Value<double?>("spacing2") ?? 0.01;
                    bool flip = p?.Value<bool?>("flip") ?? false;

                    // Select seed feature with mark=4
                    modelDoc.ClearSelection2(true);
                    bool featSel = modelDoc.Extension.SelectByID2(featureName, "BODYFEATURE", 0, 0, 0, false, 4, null, 0);
                    if (!featSel)
                        return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                            "FEATURE_NOT_FOUND",
                            $"Feature '{featureName}' not found. Ensure the name matches the feature tree entry exactly.");

                    // Select direction entity with mark=1:
                    // X→Right Plane (normal=X), Y→Top Plane (normal=Y), Z→Front Plane (normal=Z)
                    string dirPlane;
                    switch (direction)
                    {
                        case "Y": dirPlane = "Top Plane";   break;
                        case "Z": dirPlane = "Front Plane"; break;
                        default:  dirPlane = "Right Plane"; break; // X
                    }
                    // append=true keeps the seed feature (mark=4) selected; language-independent (ADR-007)
                    bool dirSel = SelectPlaneFlexible(modelDoc, dirPlane, true, 1);
                    if (!dirSel)
                        return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                            "DIRECTION_NOT_FOUND",
                            $"Direction plane '{dirPlane}' not found. Ensure default planes exist in the document.");

                    // FeatureLinearPattern3(Num1, Spacing1, Num2, Spacing2, FlipDir1, FlipDir2,
                    // DName1, DName2, GeometryPattern, VaryInstance) — reflection-verified
                    // (ADR-035). FlipDir1 exposed as 'flip' (v0.7.0): pattern toward the NEGATIVE
                    // axis. FlipDir2 stays false — the D2 direction entity is not wired (count2
                    // is accepted but has no direction-2 selection; see the contract note).
                    feature = featureMgr.FeatureLinearPattern3(
                        count, spacing,
                        count2, spacing2,
                        flip, false,
                        null, null,
                        false, false) as IFeature; // geometryPattern=false (SW default). NOTE: disjoint instances warn & are skipped — see KNOWN-LIMITATIONS.md; geometryPattern=true returns null here, not a safe blanket default.
                }
                else if (patternType == "mirror")
                {
                    // Mirror pattern (grown for 4-1's Mirror1): mirrors FEATURES about a plane.
                    // InsertMirrorFeature2 selection marks read from the local CHM (ADR-035):
                    // features to mirror = mark 1, mirror plane / planar face = mark 2.
                    string planeName = p?.Value<string>("plane");
                    if (string.IsNullOrEmpty(planeName)) planeName = "Right Plane";
                    bool geometryPattern = p?.Value<bool?>("geometry_pattern") ?? false;

                    var mirrorNames = new List<string>();
                    string featuresJson = p?.Value<string>("features_json");
                    if (!string.IsNullOrEmpty(featuresJson) && featuresJson != "[]")
                    {
                        try
                        {
                            var arr = JArray.Parse(featuresJson);
                            foreach (var t in arr) mirrorNames.Add(t.ToString());
                        }
                        catch (Exception ex)
                        {
                            return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                                "INVALID_PARAMETER",
                                $"features_json must be a JSON array of feature tree names: {ex.Message}");
                        }
                    }
                    else if (!string.IsNullOrEmpty(featureName))
                        mirrorNames.Add(featureName);
                    if (mirrorNames.Count == 0)
                        return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                            "MISSING_PARAMETER",
                            "mirror requires features_json (JSON array of feature tree names, e.g. '[\"Edge-Flange1\",\"Sketched Bend2\"]') or feature_name.");

                    // Sheet-metal parts keep a (suppressed) Flat-Pattern as the LAST feature with the
                    // rollback bar AFTER it; the generic InsertMirrorFeature2 would insert after
                    // Flat-Pattern (illegal → null; live-caught on the scratch test — the sheet-metal-
                    // aware bend API handles this itself). Same fix as the sheet-metal cut (ADR-026):
                    // roll the bar before Flat-Pattern, insert, restore.
                    IFeature mirrorFlatPat = FindFlatPattern(modelDoc);
                    bool mirrorRolled = false;
                    if (mirrorFlatPat != null)
                    {
                        try
                        {
                            mirrorRolled = modelDoc.FeatureManager.EditRollback(
                                (int)swMoveRollbackBarTo_e.swMoveRollbackBarToBeforeFeature, mirrorFlatPat.Name);
                        }
                        catch { mirrorRolled = false; }
                    }
                    try
                    {
                        modelDoc.ClearSelection2(true);
                        foreach (var nm in mirrorNames)
                        {
                            bool sel = modelDoc.Extension.SelectByID2(nm, "BODYFEATURE", 0, 0, 0, true, 1, null, 0);
                            if (!sel)
                            {
                                // Fallback for feature types BODYFEATURE won't match: the same tree walk
                                // analyze uses + IFeature.Select2 with the mark.
                                var mf = FindFeatureByName(modelDoc, nm, null);
                                sel = mf != null && mf.Select2(true, 1);
                            }
                            if (!sel)
                                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                                    "FEATURE_NOT_FOUND",
                                    $"Feature '{nm}' not found for mirror. Names must match the feature tree exactly.");
                        }

                        if (!SelectPlaneFlexible(modelDoc, planeName, true, 2))
                            return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                                "PLANE_NOT_FOUND",
                                $"Mirror plane '{planeName}' not found. Use a default plane name or a created reference plane's name.");

                        feature = featureMgr.InsertMirrorFeature2(false, geometryPattern, false, false, 0) as IFeature;
                        ExecLog.Write($"mirror: features=[{string.Join(",", mirrorNames)}] plane={planeName} rolled={mirrorRolled} -> {(feature == null ? "NULL" : feature.Name)}");
                    }
                    finally
                    {
                        if (mirrorRolled)
                        {
                            try { modelDoc.FeatureManager.EditRollback((int)swMoveRollbackBarTo_e.swMoveRollbackBarToEnd, ""); }
                            catch { }
                        }
                    }
                }
                else // circular
                {
                    string axisName = p?.Value<string>("axis_name");
                    int count = p?.Value<int?>("count") ?? 4;
                    double angleDeg = p?.Value<double?>("angle") ?? 90.0;
                    double angleRad = angleDeg * Math.PI / 180.0;
                    // equal_spacing=true (default): angle = TOTAL angle spread across all instances (pass
                    // 360 for a full ring). equal_spacing=false: angle = the angle BETWEEN adjacent
                    // instances (matches a model authored that way; can exceed 360 and wrap/overlap).
                    bool equalSpacing = p?.Value<bool?>("equal_spacing") ?? true;

                    if (string.IsNullOrEmpty(axisName))
                        return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                            "MISSING_PARAMETER",
                            "circular pattern requires axis_name (name of the rotation axis, e.g. 'Axis1'). Create one first with add_reference_geometry.");

                    // Select seed feature with mark=4
                    modelDoc.ClearSelection2(true);
                    bool featSel = modelDoc.Extension.SelectByID2(featureName, "BODYFEATURE", 0, 0, 0, false, 4, null, 0);
                    if (!featSel)
                        return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                            "FEATURE_NOT_FOUND",
                            $"Feature '{featureName}' not found.");

                    // Select axis with mark=1 — try AXIS type first, then REFERENCECURVES
                    bool axisSel = modelDoc.Extension.SelectByID2(axisName, "AXIS", 0, 0, 0, true, 1, null, 0);
                    if (!axisSel)
                        axisSel = modelDoc.Extension.SelectByID2(axisName, "REFERENCECURVES", 0, 0, 0, true, 1, null, 0);
                    if (!axisSel)
                        return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                            "AXIS_NOT_FOUND",
                            $"Axis '{axisName}' not found. Create a reference axis with add_reference_geometry first.");

                    feature = featureMgr.FeatureCircularPattern4(
                        count, angleRad,
                        false,
                        null,
                        false, equalSpacing, false) as IFeature; // geometryPattern=false (SW default); see KNOWN-LIMITATIONS.md re: disjoint instances
                }

                if (feature == null)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "PATTERN_FAILED",
                        $"Pattern feature creation returned null. Verify seed feature and direction/axis are valid.");
                // 2026-09-28 SILENT-FAILURE HARDENING: a pattern feature can be created while the
                // solid is untouched. A real pattern changes the volume OR the bounding extent —
                // either changing proves it, because instances may legitimately fuse (face count
                // can stay equal). Compared by logging only, so a fused pattern is not misreported.
                try
                {
                    int mpStatus2;
                    var mp2 = modelDoc.Extension.GetMassProperties2(0, out mpStatus2, false) as object[];
                    if (mp2 != null && mp2.Length > 9)
                        ExecLog.Write($"create_pattern: post-check vol={Convert.ToDouble(mp2[3])} " +
                            $"x=[{Convert.ToDouble(mp2[0])},{Convert.ToDouble(mp2[1])}] " +
                            $"z=[{Convert.ToDouble(mp2[8])},{Convert.ToDouble(mp2[9])}]");
                }
                catch (Exception exP) { ExecLog.Write("create_pattern post-check failed: " + exP.Message); }

                var response = new ExecutionResponse
                {
                    OperationId = request.OperationId,
                    Status = "COMPLETED",
                    Verified = true,
                    StateVersion = _guard.GetCurrentStateVersion() + 1,
                    CadState = new CadState
                    {
                        StateVersion = _guard.GetCurrentStateVersion() + 1,
                        ActiveDocument = modelDoc.GetTitle(),
                        DocumentType = "PART",
                        ActiveSketch = null,
                        Features = new List<string> { feature.Name },
                        Dimensions = new List<string>()
                    },
                    // In-band body summary so the caller can verify the pattern without a separate analyze.
                    ResultGeometry = BuildBodySummary(modelDoc),
                    Error = null
                };

                _guard.RegisterCompleted(request.OperationId, response);
                return response;
            }
            catch (COMException ex)
            {
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "COM_ERROR", ex.Message);
            }
            catch (Exception ex)
            {
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "UNEXPECTED_ERROR", ex.Message);
            }
        }

        // -----------------------------------------------------------------------
        // M21 — set_part_material
        // -----------------------------------------------------------------------
        public ExecutionResponse SetPartMaterial(ToolRequest request)
        {
            if (_guard.IsDuplicate(request.OperationId))
                return _guard.GetDuplicate(request.OperationId);

            if (!_guard.IsStateVersionValid(request.StateVersion))
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "INVALID_STATE_VERSION", "Incoming state_version does not match current state.");

            if (!EnsureConnected())
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "COM_ATTACH_FAILED", "SolidWorks process not found or COM not registered.");

            try
            {
                var p = request.Params as JObject;
                string materialName = p?.Value<string>("material_name");
                string library = p?.Value<string>("library") ?? "SolidWorks Materials";

                if (string.IsNullOrEmpty(materialName))
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "MISSING_PARAMETER",
                        "material_name is required (e.g. 'AISI 1020 Steel (SS)', 'Aluminum 1060 Alloy', 'ABS').");

                var modelDoc = _solidWorks.IActiveDoc2 as IModelDoc2;
                if (modelDoc == null)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "NO_ACTIVE_DOCUMENT", "No active document found in SolidWorks.");

                if (!(modelDoc is IPartDoc))
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "WRONG_DOCUMENT_TYPE",
                        "set_part_material requires an active part document, not a drawing or assembly.");

                var partDoc = modelDoc as IPartDoc;
                if (partDoc == null)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "DOCUMENT_CAST_FAILED", "Active document is not castable to IPartDoc.");

                // Apply material — "" config name = all configurations
                partDoc.SetMaterialPropertyName2("", library, materialName);

                // Verify material was applied
                string appliedMaterial = partDoc.GetMaterialPropertyName2("", out string appliedDb);
                if (string.IsNullOrEmpty(appliedMaterial))
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "MATERIAL_NOT_FOUND",
                        $"Material '{materialName}' in library '{library}' was not found or could not be applied. Check spelling and ensure the material library is installed.");

                var response = new ExecutionResponse
                {
                    OperationId = request.OperationId,
                    Status = "COMPLETED",
                    Verified = true,
                    StateVersion = _guard.GetCurrentStateVersion() + 1,
                    CadState = new CadState
                    {
                        StateVersion = _guard.GetCurrentStateVersion() + 1,
                        ActiveDocument = modelDoc.GetTitle(),
                        DocumentType = "PART",
                        ActiveSketch = null,
                        Features = new List<string> { $"material={appliedMaterial}", $"library={appliedDb}" },
                        Dimensions = new List<string>()
                    },
                    Error = null
                };

                _guard.RegisterCompleted(request.OperationId, response);
                return response;
            }
            catch (COMException ex)
            {
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "COM_ERROR", ex.Message);
            }
            catch (Exception ex)
            {
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "UNEXPECTED_ERROR", ex.Message);
            }
        }

        // -----------------------------------------------------------------------
        // modify_dimension — UNIVERSAL parametric value edit (the variants keystone).
        // Sets a named display dimension's value (e.g. "D1@Boss-Extrude1@Part.Part") in SI units
        // (meters for length, radians for angle), rebuilds, then echoes the EFFECTIVE value back in
        // result_geometry for in-band verification (ADR-023 spirit). Bumps state_version (geometry
        // changes — unlike analyze). Flow: analyze_model(features) reports every feature's dimension
        // full-names + SI values → pick a name → modify_dimension(name, value).
        // -----------------------------------------------------------------------
        public ExecutionResponse ModifyDimension(ToolRequest request)
        {
            if (_guard.IsDuplicate(request.OperationId))
                return _guard.GetDuplicate(request.OperationId);

            if (!_guard.IsStateVersionValid(request.StateVersion))
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "INVALID_STATE_VERSION", "Incoming state_version does not match current state.");

            if (!EnsureConnected())
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "COM_ATTACH_FAILED", "SolidWorks process not found or COM not registered.");

            try
            {
                var p = request.Params as JObject;
                string name = p != null ? p.Value<string>("name") : null;
                double? value = p != null ? p.Value<double?>("value") : null;

                if (string.IsNullOrEmpty(name))
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "MISSING_PARAMETER",
                        "name is required (the dimension full-name, e.g. 'D1@Boss-Extrude1@Part.Part' — get it from analyze_model(features)).");
                if (value == null)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "MISSING_PARAMETER",
                        "value is required (SI units: meters for length, radians for angle).");

                var modelDoc = _solidWorks.IActiveDoc2 as IModelDoc2;
                if (modelDoc == null)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "NO_ACTIVE_DOCUMENT", "No active document found in SolidWorks.");

                if (modelDoc.SketchManager.ActiveSketch != null)
                    modelDoc.SketchManager.InsertSketch(true);

                var dim = modelDoc.Parameter(name) as IDimension;
                if (dim == null)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "DIMENSION_NOT_FOUND",
                        $"Dimension '{name}' not found. Use the exact full-name reported by analyze_model(features) (e.g. 'D1@Boss-Extrude1@Part.Part').");

                // SI setter (meters/radians). SystemValue writes the document-units (SI) value.
                dim.SystemValue = value.Value;
                modelDoc.EditRebuild3(); // commit so analyze_model/verify_state read the new geometry

                // Read the effective value back (a rebuild may clamp it or an equation may drive it).
                // Same reader analyze uses: GetSystemValue3(1=swThisConfiguration, ...) — inlined int (ADR-018).
                double effective = value.Value;
                try
                {
                    var sv = dim.GetSystemValue3(1, null) as double[];
                    if (sv != null && sv.Length > 0) effective = sv[0];
                    else effective = dim.SystemValue;
                }
                catch { try { effective = dim.SystemValue; } catch { } }

                ExecLog.Write($"modify_dimension: '{name}' requested={value.Value} effective={effective}");

                var response = new ExecutionResponse
                {
                    OperationId = request.OperationId,
                    Status = "COMPLETED",
                    Verified = true,
                    StateVersion = _guard.GetCurrentStateVersion() + 1,
                    CadState = new CadState
                    {
                        StateVersion = _guard.GetCurrentStateVersion() + 1,
                        ActiveDocument = modelDoc.GetTitle(),
                        DocumentType = "PART",
                        ActiveSketch = null,
                        Features = new List<string>(),
                        Dimensions = new List<string> { name }
                    },
                    ResultGeometry = new JObject
                    {
                        ["dimension"] = name,
                        ["requested"] = value.Value,
                        ["effective"] = effective
                    },
                    Error = null
                };

                _guard.RegisterCompleted(request.OperationId, response);
                return response;
            }
            catch (COMException ex)
            {
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "COM_ERROR", ex.Message);
            }
            catch (Exception ex)
            {
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "UNEXPECTED_ERROR", ex.Message);
            }
        }

        // -----------------------------------------------------------------------
        // edit_feature — discriminated STRUCTURAL edit of a named feature.
        // action: suppress | unsuppress | delete | rename (rename needs new_name). Each rebuilds and
        // bumps state_version. RESOLVER PROBE (P1.3): suppress/delete CHANGE topology, so selectors or
        // coordinates captured earlier may no longer resolve — re-query with analyze_model afterwards.
        // -----------------------------------------------------------------------
        public ExecutionResponse EditFeature(ToolRequest request)
        {
            if (_guard.IsDuplicate(request.OperationId))
                return _guard.GetDuplicate(request.OperationId);

            if (!_guard.IsStateVersionValid(request.StateVersion))
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "INVALID_STATE_VERSION", "Incoming state_version does not match current state.");

            if (!EnsureConnected())
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "COM_ATTACH_FAILED", "SolidWorks process not found or COM not registered.");

            try
            {
                var p = request.Params as JObject;
                string featureName = p != null ? p.Value<string>("feature_name") : null;
                string action = ((p != null ? p.Value<string>("action") : null) ?? "").ToLowerInvariant();
                string newName = p != null ? p.Value<string>("new_name") : null;

                if (string.IsNullOrEmpty(featureName))
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "MISSING_PARAMETER",
                        "feature_name is required (exact feature-tree name, e.g. 'Boss-Extrude1').");
                if (action != "suppress" && action != "unsuppress" && action != "delete" && action != "rename")
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "MISSING_PARAMETER",
                        "action is required: 'suppress', 'unsuppress', 'delete', or 'rename'.");

                var modelDoc = _solidWorks.IActiveDoc2 as IModelDoc2;
                if (modelDoc == null)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "NO_ACTIVE_DOCUMENT", "No active document found in SolidWorks.");

                if (modelDoc.SketchManager.ActiveSketch != null)
                    modelDoc.SketchManager.InsertSketch(true);

                var allNames = new List<string>();
                var feature = FindFeatureByName(modelDoc, featureName, allNames);
                if (feature == null)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "FEATURE_NOT_FOUND",
                        $"Feature '{featureName}' not found. Available features: [{string.Join(", ", allNames)}].");

                string resultName = featureName;
                switch (action)
                {
                    case "suppress":
                        // swSuppressFeature=0, swThisConfiguration=1 (inlined enum constants, ADR-018).
                        // SetSuppression2 returns bool — it was DISCARDED, so a failed suppression
                        // still reported COMPLETED (verified 2026-09-28: volume unchanged across
                        // suppress/unsuppress/delete). Now the result is checked: a silent no-op is
                        // the worst failure mode here, because the caller trusts COMPLETED.
                        if (!feature.SetSuppression2(
                                (int)swFeatureSuppressionAction_e.swSuppressFeature,
                                (int)swInConfigurationOpts_e.swThisConfiguration, null))
                            return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                                "SUPPRESS_FAILED",
                                $"SetSuppression2(suppress) returned false for '{featureName}' — "
                                + "the feature was NOT suppressed (this is what used to be reported as COMPLETED).");
                        // Also verify the STATE, not just the return code.
                        modelDoc.EditRebuild3();
                        try
                        {
                            if (!feature.IsSuppressed())
                                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                                    "SUPPRESS_FAILED",
                                    $"SetSuppression2 returned true but IsSuppressed() is still false for "
                                    + $"'{featureName}' — suppression did not take effect.");
                        }
                        catch { /* IsSuppressed can throw on some feature types; the return code stands */ }
                        break;
                    case "unsuppress":
                        if (!feature.SetSuppression2(
                                (int)swFeatureSuppressionAction_e.swUnSuppressFeature,
                                (int)swInConfigurationOpts_e.swThisConfiguration, null))
                            return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                                "UNSUPPRESS_FAILED",
                                $"SetSuppression2(unsuppress) returned false for '{featureName}' — "
                                + "the feature was NOT unsuppressed.");
                        break;
                    case "rename":
                        if (string.IsNullOrEmpty(newName))
                            return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                                "MISSING_PARAMETER", "new_name is required for action='rename'.");
                        feature.Name = newName;
                        resultName = newName;
                        break;
                    case "delete":
                        // Select the FOUND IFeature directly (type-agnostic) then EditDelete. The old
                        // SelectByID2(..., "BODYFEATURE", ...) only matched body features and FAILED on
                        // sketches / reference geometry (a sketch is "SKETCH", not "BODYFEATURE"); selecting
                        // the feature object we already resolved via FindFeatureByName deletes ANY type.
                        modelDoc.ClearSelection2(true);
                        bool sel = feature.Select2(false, 0);
                        if (!sel)
                            return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                                "FEATURE_NOT_FOUND",
                                $"Feature '{featureName}' could not be selected for deletion.");
                        // EditDelete returns VOID in this interop, so there is no return value to check.
                        // Verify the OUTCOME instead (stronger than trusting a return code): the
                        // feature must no longer be resolvable by name. A silent no-op delete used
                        // to report COMPLETED (verified 2026-09-28: volume never changed).
                        modelDoc.EditRebuild3();
                        if (FindFeatureByName(modelDoc, featureName, allNames) != null)
                            return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                                "DELETE_FAILED",
                                $"EditDelete() ran but '{featureName}' is still in the tree — nothing was "
                                + "deleted (this used to be reported as COMPLETED).");
                        break;
                }

                modelDoc.EditRebuild3(); // commit so analyze_model/verify_state reflect the edit
                ExecLog.Write($"edit_feature: {action} '{featureName}'" + (action == "rename" ? $" -> '{newName}'" : ""));

                var response = new ExecutionResponse
                {
                    OperationId = request.OperationId,
                    Status = "COMPLETED",
                    Verified = true,
                    StateVersion = _guard.GetCurrentStateVersion() + 1,
                    CadState = new CadState
                    {
                        StateVersion = _guard.GetCurrentStateVersion() + 1,
                        ActiveDocument = modelDoc.GetTitle(),
                        DocumentType = "PART",
                        ActiveSketch = null,
                        Features = action == "delete" ? new List<string>() : new List<string> { resultName },
                        Dimensions = new List<string>()
                    },
                    Error = null
                };

                _guard.RegisterCompleted(request.OperationId, response);
                return response;
            }
            catch (COMException ex)
            {
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "COM_ERROR", ex.Message);
            }
            catch (Exception ex)
            {
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "UNEXPECTED_ERROR", ex.Message);
            }
        }

        private IFeature FeatureCutOnce(IFeatureManager featureMgr, bool dir, int endCond, double depthVal, bool normalCut)
        {
            return featureMgr.FeatureCut4(
                true, false, dir,
                endCond, 0,
                depthVal, 0,
                false, false, false, false,
                0, 0,
                false, false, false, false,
                normalCut, true, true,
                false, false, false,
                (int)swStartConditions_e.swStartSketchPlane, 0,
                false, false) as IFeature;
        }
    }
}

