using System;
using System.Linq;
using System.Collections.Generic;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using SolidWorks.Interop.sldworks;
using SolidWorks.Interop.swconst;
using SolidworksExecution.Infrastructure;
using SolidworksExecution.Models;

namespace SolidworksExecution.Services
{
    public partial class SolidWorksService
    {
        /// <summary>★★ 2026-09-28 insert a surface-finish (roughness) symbol onto a drawing view.
        /// Official: InsertSurfaceFinishSymbol3(SymType,LeaderType,LocX,LocY,LocZ,LaySymbol,ArrowType,
        ///   MachAllowance,OtherVals,ProdMethod,SampleLen,MaxRoughness,MinRoughness,RoughnessSpacing)
        /// THREE documented traps: (1) "based on the LAST SELECTION"; (2) LocX/Y/Z ignored when
        /// LeaderType==swNO_LEADER; (3) Max/MinRoughness are STRINGS (Ra in micrometres).
        /// Entity handoff: IView.SelectEntity(Object,bool) is the ONLY entity-aware method on IView
        /// (IModelDocExtension has no SelectByPoint; IView has no Select2 - verified by reflection).
        /// enums: swSFSymType_e swSFBasic=0 | swLeaderStyle_e swSTRAIGHT=1 | swSFLaySym_e swSFNone=0
        ///        swArrowStyle_e swOPEN_ARROWHEAD=0</summary>
        public ExecutionResponse AddSurfaceFinish(ToolRequest request)
        {
            if (_guard.IsDuplicate(request.OperationId)) return _guard.GetDuplicate(request.OperationId);
            if (!_guard.IsStateVersionValid(request.StateVersion))
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "INVALID_STATE_VERSION", "Incoming state_version does not match current state.");
            var drawing = SafeActiveDoc();
            if (drawing == null)
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "NO_ACTIVE_DOCUMENT", "Open a drawing first.");
            IDrawingDoc drawingDoc = drawing as IDrawingDoc;
            if (drawingDoc == null)
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "NOT_A_DRAWING", "Active document is not a drawing. create_drawing + add_drawing_view first.");

            var p = request.Params as JObject;
            var log = new JArray();
            int symType   = p != null && p["sym_type"]   != null ? p.Value<int>("sym_type")   : 0;
            int leader    = p != null && p["leader"]      != null ? p.Value<int>("leader")      : 1;
            int lay       = p != null && p["lay"]         != null ? p.Value<int>("lay")         : 0;
            int arrow     = p != null && p["arrow"]       != null ? p.Value<int>("arrow")       : 0;
            string maxR   = Str(p, "max_roughness",  "3.2");
            string minR   = Str(p, "min_roughness",  "");
            string sLen   = Str(p, "sample_length",  "");
            string prodM  = Str(p, "prod_method",    "");
            string machA  = Str(p, "mach_allowance", "");
            string otherV = Str(p, "other_values",   "");
            string spacg  = Str(p, "roughness_spacing", "");
            double px     = p != null && p["px"]  != null ? p.Value<double>("px")  : 0.1;
            double py     = p != null && p["py"]  != null ? p.Value<double>("py")  : 0.1;
            string vNameW = Str(p, "view_name", "");
            string mPath  = Str(p, "model_path", "");
            int    faceIx = p != null && p["face_index"] != null ? p.Value<int>("face_index") : 0;

            // 1) locate the model view
            IView view = null;
            try
            {
                var v = drawingDoc.GetFirstView() as IView;
                while (v != null)
                {
                    string n = ""; try { n = v.Name ?? ""; } catch { }
                    if (vNameW.Length > 0) { if (n.IndexOf(vNameW, StringComparison.OrdinalIgnoreCase) >= 0) { view = v; break; } }
                    else if (n.IndexOf("Sheet View", StringComparison.OrdinalIgnoreCase) < 0) { view = v; break; }
                    try { v = v.GetNextView() as IView; } catch { break; }
                }
            }
            catch (Exception exV) { log.Add("view scan EX " + exV.Message); }
            if (view == null)
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "NO_VIEW", "No model view on the sheet (or view_name did not match).");
            string vName = ""; try { vName = view.Name; } catch { }
            log.Add("view='" + vName + "'");

            // 2) grab a Face2 from the part
            IModelDoc2 partDoc = null;
            try
            {
                var docs = _solidWorks.GetDocuments() as IModelDoc2[];
                if (docs != null) foreach (var d in docs) if (d is IPartDoc) { partDoc = d; break; }
            }
            catch { }
            if (partDoc == null && mPath.Length > 0)
            {
                int oe = 0, ow = 0;
                try { partDoc = _solidWorks.OpenDoc6(mPath, (int)swDocumentTypes_e.swDocPART, 1, "", ref oe, ref ow) as IModelDoc2; }
                catch (Exception exO) { log.Add("OpenDoc6 EX " + exO.Message); }
            }
            if (partDoc == null)
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "NO_PART", "No part open and model_path unusable.");

            object[] faces = null;
            try
            {
                var pd = partDoc as IPartDoc; var bodies = (pd == null ? null : pd.GetBodies2(0, true) as object[]);
                if (bodies != null && bodies.Length > 0)
                {
                    faces = (bodies[0] as IBody2).GetFaces() as object[];
                    log.Add("part faces=" + (faces == null ? 0 : faces.Length));
                }
            }
            catch (Exception exF) { log.Add("GetFaces EX " + exF.Message); }
            if (faces == null || faces.Length == 0)
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "NO_FACES", "No face from the part body.");
            if (faceIx < 0 || faceIx >= faces.Length) faceIx = 0;

            // 3) hand the face to the view, then insert
            bool selOk = false;
            try { selOk = view.SelectEntity(faces[faceIx], false); }
            catch (Exception exSel) { log.Add("SelectEntity EX " + exSel.Message); }
            log.Add("view.SelectEntity(face[" + faceIx + "]) -> " + selOk);

            int nSel = 0, selType = 0;
            try
            {
                var smgr = partDoc.SelectionManager as ISelectionMgr;
                if (smgr != null) { nSel = smgr.GetSelectedObjectCount2(-1); }
            }
            catch { }
            log.Add("selection nSel=" + nSel + " type=" + selType + " (swSelFACES=2)");

            object sym = null; string errMsg = "";
            try
            {
                sym = drawing.Extension.InsertSurfaceFinishSymbol3(
                    symType, leader, px, py, 0.0, lay, arrow, machA, otherV, prodM, sLen, maxR, minR, spacg);
            }
            catch (Exception exI) { errMsg = exI.Message; log.Add("Insert EX " + errMsg); }

            int cnt = -1;
            try { var sfs = view.GetSFSymbols() as object[]; cnt = sfs == null ? 0 : sfs.Length; }
            catch (Exception exC) { log.Add("GetSFSymbols EX " + exC.Message); }

            var ok = new JObject
            {
                ["stage"] = "add_surface_finish",
                ["log"] = log,
                ["view_name"] = vName,
                ["face_index"] = faceIx,
                ["view_select_entity"] = selOk,
                ["selected"] = nSel,
                ["selected_type"] = selType,
                ["inserted"] = (sym != null),
                ["insert_error"] = errMsg,
                ["sf_symbol_count"] = cnt,
                ["params"] = new JObject {
                    ["sym_type"] = symType, ["leader"] = leader, ["lay"] = lay,
                    ["arrow"] = arrow, ["max_roughness"] = maxR },
                ["note"] = "Max/MinRoughness are STRINGS (Ra in um). LeaderType must be != swNO_LEADER(0) "
                         + "or LocX/Y/Z are ignored. Entity handoff uses IView.SelectEntity."
            };
            return OkWrite(request, drawing, null, ok.ToString(Formatting.None));
        }

        private static string Str(JObject p, string k, string d)
        {
            if (p == null || p[k] == null || p[k].Type == JTokenType.Null) return d;
            return p.Value<string>(k) ?? d;
        }    }
}
    

namespace SolidworksExecution.Services
{
    public partial class SolidWorksService
    {
        /// <summary>
        /// ★★ 2026-09-28 — fit a drawing sheet: read the real sheet size, pick a STANDARD scale that
        /// makes the model fit the printable area, then lay the views out on a grid so nothing overlaps.
        ///
        /// Why this exists: the default template is A4 (0.210 x 0.297 m) and hard-coded view positions
        /// (0.15, 0.15) put every view in the same corner — the user reported "线条都压在一起了".
        /// Placement has to be DERIVED from the sheet, not guessed.
        ///
        /// APIs used (verified by reflection):
        ///   ISheet.GetSize(out double width, out double height) -> int
        ///   ISheet.SetSize(int size, double width, double height) -> bool
        ///   IView.ScaleDecimal { get; set; }          // 0.2 == 1:5
        ///   IView.Position    { get; }                 // object[3]
        ///   IModelDoc2.GetPartBox(bool) -> double[]    // metres
        /// </summary>
        public ExecutionResponse LayoutDrawing(ToolRequest request)
        {
            if (_guard.IsDuplicate(request.OperationId)) return _guard.GetDuplicate(request.OperationId);
            if (!_guard.IsStateVersionValid(request.StateVersion))
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "INVALID_STATE_VERSION", "Incoming state_version does not match current state.");
            var doc = SafeActiveDoc();
            var drawingDoc = doc as IDrawingDoc;
            if (drawingDoc == null)
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "NOT_A_DRAWING", "Active document is not a drawing.");

            var p = request.Params as JObject;
            var log = new JArray();
            double margin = p != null && p["margin"] != null ? p.Value<double>("margin") : 0.010;   // 10 mm
            string paper  = p != null && p["paper"] != null ? p.Value<string>("paper") : "";         // "A3"/"A4"/"A2"
            bool autoScale = p == null || p["auto_scale"] == null || p.Value<bool?>("auto_scale") != false;

            // ---- 1) sheet size -------------------------------------------------------
            // ★ IGetCurrentSheet() is the reliable accessor. IDrawingDoc.Sheet is an INDEXED
            //   property (needs the localized sheet name, e.g. the drawing title block name);
            //   there is no GetSheet()/IGetSheet() on IDrawingDoc (verified by reflection).
            ISheet sheet = null;
            try { sheet = drawingDoc.IGetCurrentSheet(); } catch (Exception exSheet) { log.Add("IGetCurrentSheet EX " + exSheet.Message); }
            double sw = 0, sh = 0;
            if (sheet != null) { try { sheet.GetSize(ref sw, ref sh); } catch { } }
            log.Add("sheet before = " + sw.ToString("0.0000") + " x " + sh.ToString("0.0000") + " m");

            if (paper.Length > 0 && sheet != null)
            {
                // SetSize(size, w, h): pass 0 for "user size" and give the wanted w/h in metres.
                double nw = 0, nh = 0;
                switch (paper.ToUpperInvariant())
                {
                    case "A3": nw = 0.420; nh = 0.297; break;
                    case "A2": nw = 0.594; nh = 0.420; break;
                    case "A1": nw = 0.841; nh = 0.594; break;
                    case "A0": nw = 1.189; nh = 0.841; break;
                    default:  nw = 0.297; nh = 0.210; break;   // A4 portrait
                }
                try
                {
                    // SetSize(size, w, h): size=0 means "user-defined"; SW wants width>=height.

                // ★ swDwgPaperSizes_e: 0=A(landscape) 1=A(portrait) 6=A4 7=A4vert 8=A3 9=A2 10=A1 11=A0
                    //   12 = user-defined. Passing 0 does NOT mean "custom" — it means A landscape, and
                    //   SolidWorks then reports Letter-ish dimensions (measured 0.2794 x 0.2159).
                    int paperEnum;
                    switch (paper.ToUpperInvariant())
                    {
                        case "A3": paperEnum = 8; break;
                        case "A2": paperEnum = 9; break;
                        case "A1": paperEnum = 10; break;
                        case "A0": paperEnum = 11; break;
                        case "A4V": paperEnum = 7; break;
                        case "A4": paperEnum = 6; break;
                        default: paperEnum = 12; break;   // user-defined
                    }
                    if (paperEnum == 12)
                    {
                        if (nw < nh) { double t = nw; nw = nh; nh = t; }
                        bool okU = sheet.SetSize(12, nw, nh);
                        log.Add("SetSize(user " + nw + "x" + nh + ") = " + okU);
                    }
                    else
                    {
                        bool ok = sheet.SetSize(paperEnum, 0, 0);
                        log.Add("SetSize(swDwgPaperSizes_e=" + paperEnum + ") = " + ok);
                    }

                }
                catch (Exception exS) { log.Add("SetSize EX " + exS.Message); }
            }
            if (sw <= 0) { sw = 0.297; sh = 0.210; log.Add("!! sheet size unreadable, assuming A4"); }

            // ---- 2) model bounding box ------------------------------------------------
            IModelDoc2 partDoc = null;
            try
            {
                var docs = _solidWorks.GetDocuments() as IModelDoc2[];
                if (docs != null) foreach (var d in docs) if (d is IPartDoc) { partDoc = d; break; }
            }
            catch { }
            double[] box = null;
            if (partDoc != null) { try { box = (partDoc as IPartDoc).GetPartBox(true) as double[]; } catch { } }
            double mW = 0.1, mH = 0.1;
            if (box != null && box.Length >= 6)
            {
                mW = Math.Abs(box[3] - box[0]); mH = Math.Abs(box[4] - box[1]);
                log.Add("model bbox = " + mW.ToString("0.0000") + " x " + mH.ToString("0.0000") + " m");
            }
            else log.Add("!! part not open / GetPartBox failed — scale left unchanged");

            // ---- 3) collect the model views -------------------------------------------
            var views = new System.Collections.Generic.List<IView>();
            try
            {
                var v = drawingDoc.GetFirstView() as IView;
                while (v != null)
                {
                    string n = ""; try { n = v.Name ?? ""; } catch { }
                    if (n.IndexOf("Sheet View", StringComparison.OrdinalIgnoreCase) < 0
                        && n.IndexOf("图纸", StringComparison.OrdinalIgnoreCase) < 0
                        && n.Trim() != "Sheet1") views.Add(v);
                    try { v = v.GetNextView() as IView; } catch { break; }
                }
            }
            catch { }
            if (views.Count == 0)
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "NO_VIEWS", "No model views on the sheet to lay out.");
            log.Add("views = " + views.Count);

            // ---- 4) pick a standard scale ---------------------------------------------
            // printable area, leaving room for the title block along the bottom edge
            double usableW = sw - 2 * margin;
            double usableH = sh - 2 * margin - 0.030;      // 30 mm title block
            int cols = (int)Math.Ceiling(Math.Sqrt(views.Count));
            int rows = (int)Math.Ceiling((double)views.Count / cols);
            double cellW = usableW / Math.Max(1, cols);
            double cellH = usableH / Math.Max(1, rows);

            double scale = 0.0;
            if (autoScale && mW > 0 && mH > 0)
            {
                double need = Math.Min(cellW / mW, cellH / mH) * 0.85;   // 15 % breathing room
                // snap DOWN to the nearest standard scale
                double[] std = { 1.0, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01, 0.005, 0.002, 0.001 };
                foreach (var s in std) { if (s <= need) { scale = s; break; } }
                if (scale == 0) scale = 0.001;
                log.Add("needed scale <= " + need.ToString("0.0000") + "  => chose 1:" +
                        (1.0 / scale > 0 ? (1.0 / scale).ToString("0.##") : "?"));
            }

            // ---- 5) apply scale + grid placement --------------------------------------
            var placed = new JArray();
            for (int i = 0; i < views.Count; i++)
            {
                int cx = i % cols, cy = i / cols;
                double x = margin + cellW * (cx + 0.5);
                double y = margin + 0.030 + cellH * (rows - 1 - cy + 0.5);
                var v = views[i];
                string vn = ""; try { vn = v.Name; } catch { }
                try { if (scale > 0) v.ScaleDecimal = scale; } catch (Exception exS) { log.Add("scale EX " + exS.Message); }
                double applied = -1; try { applied = v.ScaleDecimal; } catch { }
                // Position is object[3] (x, y, z) in sheet metres
                try
                {
                    var pos = v.Position as object[];
                    if (pos != null && pos.Length >= 2)
                    {
                        var ax = (double[])pos[0]; var ay = (double[])pos[1];
                        if (ax.Length >= 1) ax[0] = x;
                        if (ay.Length >= 1) ay[0] = y;
                        v.Position = new object[] { ax, ay, new double[] { 0.0 } };
                    }
                }
                catch (Exception exP) { log.Add("position EX " + exP.Message); }
                placed.Add(new JObject { ["name"] = vn, ["x"] = x, ["y"] = y, ["scale"] = applied });
            }

            var okOut = new JObject
            {
                ["stage"] = "layout_drawing",
                ["log"] = log,
                ["sheet_w"] = sw, ["sheet_h"] = sh,
                ["paper"] = paper,
                ["model_w"] = mW, ["model_h"] = mH,
                ["cols"] = cols, ["rows"] = rows,
                ["scale"] = scale,
                ["scale_ratio"] = (scale > 0 ? "1:" + (1.0 / scale).ToString("0.###") : "unchanged"),
                ["views"] = placed,
                ["note"] = "Layout is DERIVED from the real sheet size (ISheet.GetSize), not hard-coded. "
                         + "A4 = 0.210x0.297 m; pass paper='A3' to grow the sheet. Title block reserves 30 mm."
            };
            return OkWrite(request, doc, null, okOut.ToString(Formatting.None));
        }
    }
}
    
namespace SolidworksExecution.Services
{
    public partial class SolidWorksService
    {
        /// <summary>★★★★ 2026-09-28 probe: can we create an empty restraint/force and then feed it
        /// one entity at a time?
        /// WHY: ICWLoadsAndRestraintsManager.AddRestraint(NRestraintType, Object DispArray, RefGeom, out err)
        /// takes a SAFEARRAY(of IDispatch) which the CLR refuses to marshal ("未能将调用的参数 1 转换").
        /// BUT the resulting ICWRestraint / ICWForce expose
        ///     BeginEdit() / InsertEntity(Object DispEntity) / EndEdit() / set_RestraintType(...)
        /// — SINGLE IDispatch arguments, which the CLR marshals fine. So if an empty array is enough to
        /// CREATE the feature, the whole SAFEARRAY problem is bypassed.
        /// shapes tried, in order: empty object[] / Type.Missing / null / 1-element object[]
        /// and for each: does lrm.Count increase? does GetLoadsAndRestraints(i) return a non-null object?
        /// </summary>
        public ExecutionResponse ProbeAddRestraint(ToolRequest request)
        {
            if (_guard.IsDuplicate(request.OperationId)) return _guard.GetDuplicate(request.OperationId);
            if (!_guard.IsStateVersionValid(request.StateVersion))
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "INVALID_STATE_VERSION", "Incoming state_version does not match current state.");
            var doc = SafeActiveDoc();
            if (doc == null)
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "NO_ACTIVE_DOCUMENT", "Open a part first.");
            var p = request.Params as JObject;
            var log = new JArray();

            // ---- reach cosworks ----------------------------------------------------
            object addin = null; int loadRet = -1; int att = 0;
            while (att < 6 && addin == null)
            {
                att++;
                loadRet = SafeInt(() => _solidWorks.LoadAddIn(
                    "D:\\Program Files\\SOLIDWORKS Corp\\SOLIDWORKS\\Simulation\\cosworks.dll"));
                foreach (var id in new[] { "CosmosWorks.CosmosWorks", "SldWorks.Simulation" })
                { try { addin = _solidWorks.GetAddInObject(id); if (addin != null) break; } catch { } }
                if (addin == null) { GC.Collect(); GC.WaitForPendingFinalizers(); System.Threading.Thread.Sleep(150); }
            }
            if (addin == null)
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "ADDIN_UNREACHABLE", "Simulation add-in unreachable.");
            dynamic cwA = addin; dynamic cwm = cwA.CosmosWorks.ActiveDoc; dynamic sm = cwm.StudyManager;

            // ---- a fresh static study to experiment on --------------------------------
            int e0 = 0;
            // ★ dynamic 下 out 参数必须写 ref（comclass 双重 byref 陷阱，与 AddForce 同一个坑）
            dynamic study = sm.CreateNewStudy3("PROBE_" + DateTime.Now.ToString("HHmmss"), 0, 0, ref e0);
            log.Add("CreateNewStudy3 err=" + e0);
            if (study == null) return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(), "NO_STUDY", "create failed");
            if (study == null) return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(), "NO_STUDY", "create failed");
            // ★ GetStudy is 1-based and the freshly created study may not be counted yet — scanning is
            //   the only reliable way to get it back (same lesson as the import tool).
            int cnt0 = Convert.ToInt32(sm.StudyCount);
            try { sm.ActiveStudy = cnt0; } catch { }
            dynamic got = null;
            for (int i = 1; i <= cnt0; i++) { try { var s = sm.GetStudy(i); if (s != null) { got = s; break; } } catch { } }
            if (got == null) { try { got = sm.GetStudy(cnt0); } catch { } }
            if (got == null) return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(), "NO_STUDY", "cannot re-acquire the new study");
            study = got;
            dynamic lrm = study.LoadsAndRestraintsManager;
            if (lrm == null) return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(), "NO_LRM", "LoadsAndRestraintsManager is null");
            int baseCount = Convert.ToInt32(lrm.Count);
            log.Add("baseline lrm.Count = " + baseCount);

            // ---- a real face to insert later -------------------------------------------
            var pd = doc as IPartDoc;
            object faceObj = null;
            try
            {
                var bodies = pd.GetBodies2(0, true) as object[];
                var faces = (bodies[0] as IBody2).GetFaces() as object[];
                if (faces != null && faces.Length > 0) faceObj = faces[0];
            }
            catch { }
            log.Add("face object = " + (faceObj == null ? "NULL" : faceObj.GetType().FullName));

            var results = new JArray();

            // ---- try shapes until one makes Count grow --------------------------------
            var shapes = new List<KeyValuePair<string, object>>();
            shapes.Add(new KeyValuePair<string, object>("empty object[]", new object[0]));
            shapes.Add(new KeyValuePair<string, object>("Array.Empty", Array.Empty<object>()));
            shapes.Add(new KeyValuePair<string, object>("object[]{null}", new object[] { null }));
            shapes.Add(new KeyValuePair<string, object>("Type.Missing", Type.Missing));
            shapes.Add(new KeyValuePair<string, object>("null", null));

            object created = null; string winning = "";
            foreach (var sh in shapes)
            {
                int before = Convert.ToInt32(lrm.Count);
                int err = -999; bool ok = false; string ex = "";
                try
                {
                    dynamic m = lrm;
                    ok = (bool)m.AddRestraint(0 /*Fixed*/, sh.Value, null, ref err);
                }
                catch (Exception exR) { ex = exR.GetType().Name + ": " + exR.Message; }
                int after = Convert.ToInt32(lrm.Count);
                log.Add("AddRestraint(" + sh.Key + ") -> ok=" + ok + " err=" + err + " count " + before + "->" + after
                        + (ex.Length > 0 ? "  EX " + ex : ""));
                results.Add(new JObject { ["shape"] = sh.Key, ["ok"] = ok, ["err"] = err, ["count"] = after, ["ex"] = ex });
                if (after > before)
                {
                    created = null;
                    int idx = after - 1;
                    int gerr = -999;
                    try { dynamic m2 = lrm; created = m2.GetLoadsAndRestraints(idx, ref gerr); }
                    catch { }
                    log.Add("  ⇒ COUNT GREW. GetLoadsAndRestraints(" + idx + ") err=" + gerr
                          + " obj=" + (created == null ? "NULL" : "有"));
                    if (created != null) { winning = sh.Key; break; }
                }
            }

            // ---- if we got an object, try the single-entity path ----------------------
            bool inserted = false; string insLog = "";
            if (created != null && faceObj != null)
            {
                try
                {
                    dynamic r = created;
                    r.RestraintBeginEdit();
                    r.InsertEntity(faceObj);
                    int eEnd = Convert.ToInt32(r.RestraintEndEdit());
                    inserted = (eEnd == 0);
                    insLog = "RestraintBeginEdit -> InsertEntity(face) -> RestraintEndEdit = " + eEnd;
                }
                catch (Exception exI) { insLog = "EX " + exI.Message; }
                log.Add("  single-entity path: " + insLog);
            }

            var okOut = new JObject
            {
                ["stage"] = "probe_add_restraint",
                ["log"] = log,
                ["shapes"] = results,
                ["winning_shape"] = winning,
                ["created_object"] = (created != null),
                ["entity_inserted"] = inserted,
                ["insert_log"] = insLog,
                ["note"] = "AddRestraint needs SAFEARRAY(of IDispatch) — CLR refuses it. ICWRestraint."
                         + "InsertEntity(Object) takes a SINGLE IDispatch, which the CLR marshals. If an "
                         + "empty array creates the feature, the SAFEARRAY problem is bypassed entirely."
            };
            return OkWrite(request, doc, null, okOut.ToString(Formatting.None));
        }
    }
}
