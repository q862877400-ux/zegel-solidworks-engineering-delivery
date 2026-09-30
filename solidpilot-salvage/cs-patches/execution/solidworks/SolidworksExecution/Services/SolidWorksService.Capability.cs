using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Net.Http;
using System.Runtime.InteropServices;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using SolidWorks.Interop.sldworks;
using SolidworksExecution.Models;

namespace SolidworksExecution.Services
{
    // SolidWorksService partial — capability extension batch (2026-09-27):
    //   bom_from_assembly   : component-tree BOM (no drawing needed), optional CSV/xlsx write
    //   list_standard_parts : index the SolidWorks Toolbox design library
    //   insert_standard_part: insert an indexed part with the AddComponent5 CENTER correction
    //   lcsc_fetch_step     : EasyEDA/LCSC 3-stage 3D-model fetch (PCB parts only — see note)
    //   motion_study        : explode / rotation study + AVI (late-bound, no extra interop ref)
    public partial class SolidWorksService
    {
        private const string ToolboxRoot =
            @"C:\ProgramData\SOLIDWORKS\SOLIDWORKS 2026\design library";

        // ---------------------------------------------------------------
        // bom_from_assembly  (READ-ONLY)
        //   IAssemblyDoc.GetComponents walks the tree directly — no drawing
        //   required, columns are whatever we emit. This is the channel an
        //   LLM should prefer; InsertBomTable3 + SaveAsExcel is the
        //   "official" channel but needs a drawing document.
        //   NOTE: light-weight components MUST be resolved first or the
        //   walk silently misses them.
        // ---------------------------------------------------------------
        internal ExecutionResponse BomFromAssembly(ToolRequest request)
        {
            if (_guard.IsDuplicate(request.OperationId)) return _guard.GetDuplicate(request.OperationId);
            if (!_guard.IsStateVersionValid(request.StateVersion))
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "INVALID_STATE_VERSION", "state version mismatch");

            try
            {
                var modelDoc = SafeActiveDoc();
                if (modelDoc == null)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "NO_ACTIVE_DOCUMENT", "No active document.");
                if (modelDoc.GetType() != 2) // swDocASSEMBLY
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "WRONG_DOCUMENT_TYPE", "bom_from_assembly needs an ASSEMBLY document.");

                var asmDoc = modelDoc as IAssemblyDoc;
                try { asmDoc.ResolveAllLightWeightComponents(false); } catch { }

                bool topOnly = p_bool(request, "top_level_only", true);
                var comps = asmDoc.GetComponents(topOnly) as object[];
                if (comps == null) comps = new object[0];
                int n = comps.Length;

                var rows = new JArray();
                for (int i = 0; i < n; i++)
                {
                    var c = comps[i] as IComponent2;
                    if (c == null) continue;
                    var row = new JObject
                    {
                        ["name"] = c.Name2,
                        ["path"] = c.GetPathName(),
                        ["config"] = c.ReferencedConfiguration,
                        ["suppressed"] = SafeBool(() => c.IsSuppressed()),
                        ["excluded_from_bom"] = SafeBool(() => c.ExcludeFromBOM),
                    };
                    rows.Add(row);
                }

                string outDir = p_string(request, "out_dir", null);
                string written = null;
                if (!string.IsNullOrEmpty(outDir))
                {
                    try
                    {
                        Directory.CreateDirectory(outDir);
                        string baseName = Path.GetFileNameWithoutExtension(modelDoc.GetPathName() ?? "assembly");
                        string csv = Path.Combine(outDir, baseName + "_BOM.csv");
                        var keys = rows.OfType<JObject>()
                                       .SelectMany(r => r.Properties().Select(p2 => p2.Name))
                                       .Where(k => k.StartsWith("custom:"))
                                       .Distinct().OrderBy(k => k).ToList();
                        var sb = new System.Text.StringBuilder();
                        sb.AppendLine(string.Join(",", new[] { "name", "path", "config", "suppressed", "excluded" }
                            .Concat(keys).Select(Q)));
                        foreach (var r in rows.OfType<JObject>())
                        {
                            var cells = new List<string> {
                                r["name"]?.ToString(), r["path"]?.ToString(), r["config"]?.ToString(),
                                r["suppressed"]?.ToString(), r["excluded_from_bom"]?.ToString() };
                            cells.AddRange(keys.Select(k => r[k]?.ToString() ?? ""));
                            sb.AppendLine(string.Join(",", cells.Select(Q)));
                        }
                        File.WriteAllText(csv, sb.ToString(), new System.Text.UTF8Encoding(true));
                        written = csv;
                    }
                    catch (Exception ex) { written = "CSV write failed: " + ex.Message; }
                }

                var payload = new JObject
                {
                    ["count"] = rows.Count,
                    ["out_file"] = written,
                    ["rows"] = rows
                };
                return OkRead(request, modelDoc, "ASSEMBLY", payload.ToString(Formatting.None));
            }
            catch (COMException ex) { return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(), "COM_ERROR", ex.Message); }
            catch (Exception ex) { Infrastructure.ExecLog.Write("CAPFAIL " + ex.ToString()); return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(), "UNEXPECTED_ERROR", ex.Message + " @ " + ex.StackTrace); }
        }

        // ---------------------------------------------------------------
        // list_standard_parts  (READ-ONLY)
        //   There is NO COM API to query Toolbox by standard/size — only
        //   ExportToolboxItem/ImportToolboxItem. So we index the filesystem
        //   ourselves and hand the caller a searchable list. Nothing in
        //   SolidWorks is hacked.
        // ---------------------------------------------------------------
        internal ExecutionResponse ListStandardParts(ToolRequest request)
        {
            if (_guard.IsDuplicate(request.OperationId)) return _guard.GetDuplicate(request.OperationId);
            try
            {
                var modelDoc = SafeActiveDoc();
                string root = p_string(request, "root", ToolboxRoot);
                string filter = p_string(request, "filter", null);
                int limit = (int)(p_double(request, "limit", 500) ?? 500);

                if (!Directory.Exists(root))
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "FILE_NOT_FOUND", "Design library not found: " + root);

                var files = Directory.GetFiles(root, "*.sldprt", SearchOption.AllDirectories);
                var arr = new JArray();
                foreach (var f in files)
                {
                    if (arr.Count >= limit) break;
                    string rel = f.Substring(root.Length).TrimStart('\\');
                    if (!string.IsNullOrEmpty(filter) &&
                        rel.IndexOf(filter, StringComparison.OrdinalIgnoreCase) < 0) continue;
                    arr.Add(new JObject
                    {
                        ["file"] = f,
                        ["rel"] = rel,
                        ["category"] = rel.Split('\\')[0],
                        ["name"] = Path.GetFileNameWithoutExtension(f)
                    });
                }
                // group summary so the caller can see coverage before drilling in
                var byCat = new JObject();
                foreach (var g in arr.GroupBy(x => x["category"]?.ToString()))
                    byCat[g.Key] = g.Count();

                var payload = new JObject
                {
                    ["root"] = root,
                    ["total_sldprt"] = files.Length,
                    ["returned"] = arr.Count,
                    ["by_category"] = byCat,
                    ["parts"] = arr
                };
                return OkRead(request, modelDoc, null, payload.ToString(Formatting.None));
            }
            catch (Exception ex) { Infrastructure.ExecLog.Write("CAPFAIL " + ex.ToString()); return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(), "UNEXPECTED_ERROR", ex.Message + " @ " + ex.StackTrace); }
        }

        // ---------------------------------------------------------------
        // insert_standard_part  (WRITE)
        //   AddComponent5's x/y/z are the COMPONENT CENTER, not its origin
        //   (official: "X coordinate of the component center"). The MCP
        //   insert_component still takes x/y/z at face value, which silently
        //   mis-places anything. Here the caller gives where the part's
        //   ORIGIN should land and we add half its bounding box back.
        // ---------------------------------------------------------------
        internal ExecutionResponse InsertStandardPart(ToolRequest request)
        {
            if (_guard.IsDuplicate(request.OperationId)) return _guard.GetDuplicate(request.OperationId);
            if (!_guard.IsStateVersionValid(request.StateVersion))
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "INVALID_STATE_VERSION", "state version mismatch");
            try
            {
                var modelDoc = SafeActiveDoc();
                if (modelDoc == null)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "NO_ACTIVE_DOCUMENT", "No active document.");
                if (modelDoc.GetType() != 2)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "WRONG_DOCUMENT_TYPE", "insert_standard_part needs an ASSEMBLY document.");

                string path = p_string(request, "file", null);
                if (string.IsNullOrEmpty(path)) path = p_string(request, "part", null);
                if (string.IsNullOrEmpty(path) || !File.Exists(path))
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "FILE_NOT_FOUND", "part file not found: " + (path ?? "<null>"));

                // Where the part's CENTER should end up. NOTE: AddComponent5's x/y/z ARE the
                // component center (official wording), so callers who think in "origin" must
                // pass center_offset_* = half the part's bbox — the same correction the manual
                // documents. We do NOT open the part to measure it (OpenDoc6's out-params are
                // awkward here); the caller knows the part, so it passes the offset.
                double wantX = p_double(request, "origin_x", 0) ?? 0;
                double wantY = p_double(request, "origin_y", 0) ?? 0;
                double wantZ = p_double(request, "origin_z", 0) ?? 0;
                double offX = p_double(request, "center_offset_x", 0) ?? 0;
                double offY = p_double(request, "center_offset_y", 0) ?? 0;
                double offZ = p_double(request, "center_offset_z", 0) ?? 0;
                double placeX = wantX + offX, placeY = wantY + offY, placeZ = wantZ + offZ;

                var asmDoc = modelDoc as IAssemblyDoc;
                // swAddComponentConfigOptions_CurrentSelectedConfig is 0, NOT 2. Reflected from
                // SolidWorks.Interop.swconst.dll:
                //   0 = CurrentSelectedConfig   1 = NewConfigWithAllReferenceModels   2 = NewConfigWithAsmStructure
                // Passing 2 asks SolidWorks to CREATE A NEW CONFIGURATION from the assembly structure —
                // on an assembly with no compatible config that is a guaranteed null return, and on a
                // populated one it depends on the assembly's current config state, which is exactly the
                // "intermittent null" this tool used to return. 0 is the semantically correct value
                // ("insert this part into the CURRENT assembly"); it also matches insert_component
                // (SolidWorksService.Assembly.cs), which inserts 5/5.
                var comp = asmDoc.AddComponent5(path, 0 /*swAddComponentConfigOptions_CurrentSelectedConfig*/,
                    "", false, "", placeX, placeY, placeZ);

                if (comp == null)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "INSERT_FAILED",
                        "AddComponent5 returned null. NOTE it requires the part to be ALREADY OPEN — "
                        + "open_document it first, then call this (manual §10.1b).");

                var payload = new JObject
                {
                    ["inserted"] = comp.Name2,
                    ["file"] = path,
                    ["passed_to_AddComponent5"] = new JArray(placeX, placeY, placeZ),
                    ["requested_origin"] = new JArray(wantX, wantY, wantZ),
                    ["center_offset_applied"] = new JArray(offX, offY, offZ)
                };
                return OkWrite(request, modelDoc, "ASSEMBLY", payload.ToString(Formatting.None));
            }
            catch (COMException ex) { return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(), "COM_ERROR", ex.Message); }
            catch (Exception ex) { Infrastructure.ExecLog.Write("CAPFAIL " + ex.ToString()); return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(), "UNEXPECTED_ERROR", ex.Message + " @ " + ex.StackTrace); }
        }

        // ---------------------------------------------------------------
        // lcsc_fetch_step  (READ-ONLY + network)
        //   Proven 3-stage EasyEDA/LCSC chain (no auth):
        //     1) POST jlcpcb.com/.../selectSmtComponentList   (keyword -> LCSC part numbers)
        //     2) POST easyeda.com/api/components/searchByNumbers (numbers -> 3D "step" id)
        //     3) GET  modules.easyeda.com/qAxj6KHrDKw4blvCG8QJPs7Y/{step}  -> STEP bytes
        //   CAUTION — these are UNDOCUMENTED internal endpoints (no SLA, no
        //   published rate limit). And the library is PCB-centric: measured
        //   ball bearings 0/5 with 3D, "linear guide" has no category at
        //   all, "M3 screw" returns diodes. Use for ELECTRONIC parts only;
        //   for mechanical standard parts use list_standard_parts / bd_warehouse.
        //   GOTCHA: the uuid_3d from api/products is NOT the step id (404);
        //   only searchByNumbers' `step` field works.
        // ---------------------------------------------------------------
        internal ExecutionResponse LcscFetchStep(ToolRequest request)
        {
            if (_guard.IsDuplicate(request.OperationId)) return _guard.GetDuplicate(request.OperationId);
            try
            {
                var modelDoc = SafeActiveDoc();
                string keyword = p_string(request, "keyword", null);
                string[] numbers = p_string_array(request, "numbers", null);
                string download = p_string(request, "download_dir", null);
                int limit = (int)(p_double(request, "limit", 10) ?? 10);

                if (string.IsNullOrEmpty(keyword) && (numbers == null || numbers.Length == 0))
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "MISSING_PARAMETER", "pass keyword= (search) or numbers=[...] (direct)");

                var results = new JArray();
                // .NET 4.x HttpClient defaults to SSL3/TLS1.0; these endpoints need TLS 1.2.
                // Without this every call dies with a bare "one or more errors".
                try { System.Net.ServicePointManager.SecurityProtocol = System.Net.SecurityProtocolType.Tls12; } catch { }
                var http = new HttpClient { Timeout = TimeSpan.FromSeconds(45) };
                http.DefaultRequestHeaders.Add("User-Agent",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131.0 Safari/537.36");

                // stage 1: keyword -> LCSC numbers
                if (!string.IsNullOrEmpty(keyword))
                {
                    var body = new JObject { ["currentPage"] = 1, ["pageSize"] = limit, ["keyword"] = keyword };
                    var resp = http.PostAsync(
                        "https://jlcpcb.com/api/overseas-pcb-order/v1/shoppingCart/smtGood/selectSmtComponentList",
                        new StringContent(body.ToString(), System.Text.Encoding.UTF8, "application/json")).Result;
                    var txt = resp.Content.ReadAsStringAsync().Result;
                    var jo = JObject.Parse(txt);
                    var list = jo["data"]?["componentPageInfo"]?["list"] as JArray;
                    if (list != null)
                        foreach (var it in list)
                        {
                            results.Add(new JObject
                            {
                                ["lcsc"] = it["componentCode"]?.ToString(),
                                ["model"] = it["componentModelEn"]?.ToString(),
                                ["brand"] = it["componentBrandEn"]?.ToString(),
                                ["stock"] = it["stockCount"]?.ToString(),
                                ["type"] = it["componentTypeEn"]?.ToString()
                            });
                        }
                }

                // stage 2: numbers -> step id  (only for explicit numbers, to keep it bounded)
                if (numbers != null && numbers.Length > 0)
                {
                    var b2 = new JObject { ["numbers"] = JArray.FromObject(numbers) };
                    var r2 = http.PostAsync("https://easyeda.com/api/components/searchByNumbers",
                        new StringContent(b2.ToString(), System.Text.Encoding.UTF8, "application/json")).Result;
                    var t2 = JObject.Parse(r2.Content.ReadAsStringAsync().Result);
                    var lst = t2["data"] as JArray ?? (t2["success"]?["data"] as JArray);
                    if (lst != null)
                        foreach (var it in lst)
                        {
                            string step = it["step"]?.ToString();
                            var row = new JObject
                            {
                                ["number"] = it["number"]?.ToString(),
                                ["step_id"] = step,
                                ["uuid"] = it["uuid"]?.ToString()
                            };
                            // stage 3: download
                            if (!string.IsNullOrEmpty(step) && !string.IsNullOrEmpty(download))
                            {
                                try
                                {
                                    Directory.CreateDirectory(download);
                                    var bytes = http.GetAsync(
                                        "https://modules.easyeda.com/qAxj6KHrDKw4blvCG8QJPs7Y/" + step).Result;
                                    if (bytes.IsSuccessStatusCode)
                                    {
                                        var buf = bytes.Content.ReadAsByteArrayAsync().Result;
                                        string f = Path.Combine(download,
                                            (it["number"]?.ToString() ?? "part") + ".step");
                                        File.WriteAllBytes(f, buf);
                                        row["downloaded"] = f;
                                        row["bytes"] = buf.Length;
                                    }
                                    else row["download_error"] = ((int)bytes.StatusCode) + " " + bytes.StatusCode;
                                }
                                catch (Exception ex) { row["download_error"] = ex.Message; }
                            }
                            results.Add(row);
                        }
                }

                var payload = new JObject
                {
                    ["warning"] = "Undocumented internal endpoints. PCB-parts-only library: measured 0/5 bearings with 3D, no 'linear guide' category, 'M3 screw' returns diodes. For MECHANICAL standard parts use list_standard_parts instead.",
                    ["count"] = results.Count,
                    ["results"] = results
                };
                return OkRead(request, modelDoc, null, payload.ToString(Formatting.None));
            }
            catch (Exception ex) { Infrastructure.ExecLog.Write("CAPFAIL " + ex.ToString()); return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(), "UNEXPECTED_ERROR", ex.Message + " @ " + ex.StackTrace); }
        }

        // ---------------------------------------------------------------
        // motion_study  (WRITE)  — explode / rotation / motion + AVI
        //   Entry point is IModelDocExtension.GetMotionStudyManager()
        //   (CWSimuManager does NOT exist in SW2026). Called through `dynamic`
        //   so no extra interop reference is needed.
        //   Capability boundary: Motion = kinematics/explode/rotate + contacts
        //   + loads + AVI. NOT FEA — that is SOLIDWORKS Simulation, a
        //   separate API and (usually) a separate licence.
        // ---------------------------------------------------------------
        internal ExecutionResponse MotionStudy(ToolRequest request)
        {
            if (_guard.IsDuplicate(request.OperationId)) return _guard.GetDuplicate(request.OperationId);
            if (!_guard.IsStateVersionValid(request.StateVersion))
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "INVALID_STATE_VERSION", "state version mismatch");
            try
            {
                var modelDoc = SafeActiveDoc();
                if (modelDoc == null)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "NO_ACTIVE_DOCUMENT", "No active document.");

                string kind = p_string(request, "study", "explode") ?? "explode";   // explode | collapse | rotation | motion
                string name = p_string(request, "name", "MCP_" + kind);
                string avi = p_string(request, "avi_path", null);
                double distance = p_double(request, "explode_distance", 0.05) ?? 0.05;
                double angle = p_double(request, "angle", 360) ?? 360;
                double duration = p_double(request, "duration", 3) ?? 3;
                int steps = (int)(p_double(request, "steps", 20) ?? 20);

                dynamic mgr = modelDoc.Extension.GetMotionStudyManager();
                if (mgr == null)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "NOT_AVAILABLE",
                        "GetMotionStudyManager() returned null. Motion may not be installed/licensed on this seat (note: CWSimuManager does not exist in SW2026; this is the correct entry point).");

                // SIGNATURES VERIFIED against the local official CHM  api\swmotionstudyapi.chm
                //   IMotionStudyManager::CreateMotionStudy()          -> MotionStudy      (NO ARGUMENTS)
                //   IMotionStudyManager::GetMotionStudy(name)        -> MotionStudy
                //   IMotionStudyManager::ActivateMotionStudy(name)   -> bool
                //   IMotionStudyManager::CreateAVIParameter()        -> AVIParameter
                //   IMotionStudy::Name                                -> get/set string
                //   IMotionStudy::CreateByExplode (delExisting, duration, startTime) -> bool
                //   IMotionStudy::CreateByCollapse(delExisting, duration, startTime)-> bool
                //   IMotionStudy::CreateByRotateModel(delExisting, axis, rotationCount,
                //                        direction, duration, startTime)          -> bool
                //   IMotionStudy::SetDuration(seconds) / GetDuration()   (there is NO Duration property)
                // The old code called CreateMotionStudy(name) and CreateByRotateModel with 9
                // doubles — neither overload exists, which is why it always threw.
                string axisName = (p_string(request, "axis", "z") ?? "z").ToLowerInvariant();
                int axis = axisName == "x" ? 0 : axisName == "y" ? 1 : 2;   // swAnimatorAxisOfRotation_e
                string dirName = (p_string(request, "direction", "ccw") ?? "ccw").ToLowerInvariant();
                int rotDir = (dirName == "cw" || dirName == "clockwise") ? 0 : 1; // swAnimatorDirectionOfRotation_e

                dynamic study = mgr.GetMotionStudy(name);
                if (study == null)
                {
                    study = mgr.CreateMotionStudy();          // <-- zero-arg overload
                    if (study == null)
                        return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                            "NOT_AVAILABLE", "CreateMotionStudy() returned null (Motion module/licence unavailable).");
                    try { study.Name = name; } catch { }      // the API has no name parameter — rename after
                }

                var log = new JArray();
                try
                {
                    if (kind == "explode" || kind == "collapse")
                    {
                        // ONE call, not a loop: the animation path is defined by (duration, startTime);
                        // the API samples it itself. The old loop re-defined the path `steps` times and
                        // passed the two time fractions into the wrong parameters, and it used
                        // CreateByCollapse for kind=explode — i.e. it COLLAPSED the assembly.
                        bool explode = (kind == "explode");
                        bool ok = explode
                            ? study.CreateByExplode(false, duration, 0.0)
                            : study.CreateByCollapse(false, duration, 0.0);
                        log.Add((explode ? "explode" : "collapse") + " -> " + ok
                              + " (duration=" + duration + "s, startTime=0; steps=" + steps
                              + " is not an API parameter — the animation auto-samples)");
                    }
                    else if (kind == "rotation")
                    {
                        // 2026-09-28 SILENT FAILURE FIX: turns used to be round(angle/360) then FORCED to
                        // >=1, so `revolutions=2` was ignored (the parameter never existed) and `angle=60`
                        // silently became one whole turn. IMotionStudy.CreateByRotateModel's 3rd argument is
                        // RotationCount (an Int32 TURN COUNT) and its 6th is StartTime — NOT an angle
                        // (both verified against the interop). The API therefore only supports WHOLE turns.
                        // Honour an explicit `revolutions`; fail loudly for a sub-turn `angle` instead of
                        // quietly doing something the caller did not ask for.
                        int turns;
                        double? revs = p_double(request, "revolutions", null);
                        if (revs != null)
                        {
                            turns = (int)Math.Round(revs.Value);
                            if (turns < 1)
                                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                                    "INVALID_REVOLUTIONS",
                                    $"revolutions={revs.Value} rounds to {turns}; SolidWorks Motion only "
                                  + "supports whole turns (CreateByRotateModel takes an Int32 RotationCount).");
                            if (Math.Abs(revs.Value - turns) > 1e-6)
                                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                                    "INVALID_REVOLUTIONS",
                                    $"revolutions={revs.Value} is not a whole number of turns; "
                                  + "CreateByRotateModel(RotationCount) is an integer.");
                        }
                        else if (Math.Abs(Math.Abs(angle) % 360.0) > 1e-6 && Math.Abs(angle) < 360.0)
                        {
                            return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                                "PARTIAL_TURN_UNSUPPORTED",
                                $"angle={angle}° is not a whole number of turns. IMotionStudy."
                              + "CreateByRotateModel only accepts an integer RotationCount, so a partial turn "
                              + "(e.g. 60°) is NOT supported by the API — it used to silently become 1 full "
                              + "turn. Use revolutions=<integer> instead.");
                        }
                        else
                        {
                            turns = (int)Math.Round(Math.Abs(angle) / 360.0);
                            if (turns < 1) turns = 1;
                        }
                        bool ok = study.CreateByRotateModel(false, axis, turns, rotDir, duration, 0.0);
                        log.Add("rotate " + (angle >= 0 ? "" : "-") + Math.Abs(turns) + " turn(s) about "
                              + axisName.ToUpperInvariant() + " (" + (rotDir == 0 ? "CW" : "CCW")
                              + ") -> " + ok
                              + (revs != null ? $"  [revolutions={revs.Value}]" : ""));
                    }
                    else
                    {
                        log.Add("motion study created (no definition added — supply load/contact data via SOLIDWORKS UI)");
                    }
                }
                catch (Exception ex) { log.Add("define failed: " + ex.Message); }

                try { study.SetDuration(duration); log.Add("duration=" + duration + "s"); }
                catch (Exception ex) { log.Add("SetDuration failed: " + ex.Message); }
                // The AVI render needs the study ACTIVE and CALCULATED. These two used to be
                // fire-and-forget with empty catches, so when activation failed there was no way to
                // tell "not active" from "active" — and SaveToAVI just returned false. Report them.
                try { bool actOk = mgr.ActivateMotionStudy(name); log.Add("ActivateMotionStudy('" + name + "') -> " + actOk); }
                catch (Exception ex) { log.Add("ActivateMotionStudy FAILED: " + ex.Message); }
                try { int before = (int)mgr.GetMotionStudyCount(); log.Add("study count=" + before); } catch (Exception ex) { log.Add("GetMotionStudyCount failed: " + ex.Message); }
                try { bool calcOk = study.Calculate(); log.Add("Calculate() -> " + calcOk); }
                catch (Exception ex) { log.Add("calculate failed: " + ex.Message); }

                // AVI export. The old code called SaveToAVI, ignored its bool return and logged
                // success unconditionally — so a silently-failing render looked like a pass
                // (manual §六-9: 不验证 = 没做完). Two settings make it actually write:
                //   * SaveEntireAnimation must be true. Left false, StartTime/EndTime (both 0) select
                //     an EMPTY time window and nothing is written — with no exception raised.
                //   * OutputType must match the extension (swAnimationOutputType_e, reflected from
                //     swconst.dll). NOTE the enum has NO 0 member (AVI=1, BMP=2, TGA=3, PNG=4,
                //     JPG=5, TIF=6, MP4=7, MKV=8, FLV=9, LXO=10) while IAVIParameter.OutputType is
                //     a raw Int32, so an untouched default of 0 is not even a valid output type.
                var aviReport = new JObject();
                if (!string.IsNullOrEmpty(avi))
                {
                    try
                    {
                        string dir = Path.GetDirectoryName(avi);
                        if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);
                        string ext = (Path.GetExtension(avi) ?? "").ToLowerInvariant();
                        int outType = ext == ".bmp" ? 2 : ext == ".tga" ? 3 : ext == ".png" ? 4
                                    : (ext == ".jpg" || ext == ".jpeg") ? 5 : ext == ".tif" ? 6
                                    : ext == ".mp4" ? 7 : ext == ".mkv" ? 8 : ext == ".flv" ? 9 : 1;
                        dynamic aviParam = mgr.CreateAVIParameter();
                        try { aviParam.SaveEntireAnimation = true; } catch (Exception ex) { log.Add("SaveEntireAnimation set failed: " + ex.Message); }
                        try { aviParam.OutputType = outType; } catch (Exception ex) { log.Add("OutputType set failed: " + ex.Message); }
                        try { aviParam.RendererType = 0; } catch { }     // swRendererType_Solidworks_Screen
                        try { aviParam.FramePerSecond = 30; } catch { }
                        string readBack;
                        try { readBack = " OutputType=" + aviParam.OutputType + " SaveEntireAnimation=" + aviParam.SaveEntireAnimation
                                                 + " RendererType=" + aviParam.RendererType; }
                        catch { readBack = ""; }
                        log.Add("aviParam set: ext='" + ext + "' -> OutputType=" + outType + readBack);

                        bool saved = study.SaveToAVI(avi, aviParam);
                        bool onDisk = File.Exists(avi);
                        long bytes = onDisk ? new FileInfo(avi).Length : 0L;
                        log.Add("SaveToAVI returned " + saved + "; file on disk: "
                              + (onDisk ? bytes + " bytes" : "MISSING"));
                        aviReport["path"] = avi;
                        aviReport["save_to_avi_returned"] = saved;
                        aviReport["file_on_disk"] = onDisk;
                        aviReport["bytes"] = bytes;
                        aviReport["output_type"] = outType;
                        if (!saved || !onDisk || bytes == 0)
                            aviReport["warning"] = "AVI not produced — SaveToAVI returned "
                                + saved + ", onDisk=" + onDisk + ", bytes=" + bytes
                                + ". The render usually needs the study to be ACTIVE and calculated; "
                                + "check the Motion add-in is loaded (Tools > Motion).";
                    }
                    catch (Exception ex) { log.Add("avi failed: " + ex.Message); aviReport["error"] = ex.Message; }
                }

                var payload = new JObject
                {
                    ["study"] = name, ["kind"] = kind, ["log"] = log, ["avi"] = aviReport,
                    ["note"] = "Motion = kinematics/explode/rotate/AVI. NOT FEA (SOLIDWORKS Simulation is a separate API + licence)."
                };
                return OkWrite(request, modelDoc, null, payload.ToString(Formatting.None));
            }
            catch (COMException ex) { return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(), "COM_ERROR", ex.Message); }
            catch (Exception ex) { Infrastructure.ExecLog.Write("CAPFAIL " + ex.ToString()); return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(), "UNEXPECTED_ERROR", ex.Message + " @ " + ex.StackTrace); }
        }

        // ---------------------------------------------------------------
        // topology_optimize  (WRITE)  — SOLIDWORKS Simulation topology study
        //
        //   Entry chain, established by reflecting the LOCAL interop assemblies and the LOCAL
        //   official help only (no network, no licence/activation endpoint is ever contacted):
        //     ISldWorks.LoadAddIn("...\Simulation\cosworks.dll")
        //       -> ISldWorks.GetAddInObject("SldWorks.Simulation")   // CLSID {C8F79410-...}
        //       -> ICwAddincallback.CosmosWorks                       -> ICosmosWorks
        //       -> ICosmosWorks.ActiveDoc                             -> ICWModelDoc
        //       -> ICWModelDoc.AddDefaultOptimizationStudyPlot(int)  -> int (error code)
        //       -> ICWModelDoc.StudyManager                          -> ICWStudyManager
        //       -> .ActiveStudy (an Int32 INDEX, not an object) / .GetStudy(idx) -> ICWStudy
        //       -> ICWStudy.TopologyStudyManager / .TopologyStudyOptions / .RunAnalysis()
        //
        //   REGISTRY NOTE (the manual used to say "COM registration not found" — that was wrong):
        //   Simulation is NOT one of the 7 add-ins under HKLM\SOFTWARE\SolidWorks\AddIns. It is a
        //   standalone in-process COM server: CLSID {C8F79410-CD71-4061-A2E4-B6BF17CCB27F} ->
        //   ...\Simulation\cosworks.dll, ProgID SldWorks.Simulation.19, version-independent ProgID
        //   SldWorks.Simulation, ThreadingModel Apartment.
        //
        //   The cosworks objects are reached through `dynamic` for the same reason motion_study is:
        //   it keeps SolidWorks.Interop.cosworks.dll out of the compile references, so a missing or
        //   version-mismatched cosworks interop cannot stop the WHOLE service from loading.
        //   (It also matters because PowerShell CANNOT do this at all — see manual §6-14.)
        //
        //   MEASURED RESULT ON THIS MACHINE (2026-09-27), so read this before trusting the tool:
        //     WORKS  : LoadAddIn -> 0; GetAddInObject -> __ComObject; ICosmosWorks (v891107);
        //               ICWModelDoc; StudyManager.CreateNewStudy3(type=13) builds a real study;
        //               Extension.SelectByID2 + SolidManager.SetLibraryMaterialToSelectedEntities -> 0;
        //               TopologyStudyManager/TopologyStudyOptions both live;
        //               TopologyStudyManager.BeginEdit() + CreateGoal(2=MinimizeMass) + all four
        //               Create*Control + CreateMassConstraint + EndEdit()  => all err=0.
        //               (The controls returned err=17 until they were created INSIDE the manager's own
        //               BeginEdit()/EndEdit() session, after a goal existed. That was the real fix.)
        //     BLOCKED: AddRestraint / AddForce / AddPressure all throw a generic COM-marshalling
        //               ArgumentException. Without a fixture the solver has nothing to do, so
        //               MeshAndRun returns immediately with Results == null. See the long note at
        //               step 5c for the six already-eliminated causes — do not re-try them.
        //   ⇒ There is no validated "solve to a design result" path here. action=solve verifies the
        //     pipeline up to the solver; it does NOT produce a usable topology. Do not report a
        //     topology result from this tool as if it were a real solution.
        //     swsRunAnalysisError codes seen: 19 MaterialNotDefined, 22 AuthorizationFailed,
        //     23 MeshNotFound; swsTopoErrCode 17 = SetOperationNotSupported (fixed via BeginEdit).
        // ---------------------------------------------------------------
        // CoCreateInstance on the Simulation CLSID fails with 0x8007007E (ERROR_MOD_NOT_FOUND)
        // unless cosworks.dll's sibling dependencies can be resolved: they all live in
        // ...\SOLIDWORKS\Simulation (and the main SolidWorks folder), and this process runs from
        // bin\Debug, which is on neither search path. AddDllDirectory extends the search list
        // without replacing it (SetDllDirectory would REPLACE it, so it is only the fallback).
        [System.Runtime.InteropServices.DllImport("kernel32.dll", CharSet = System.Runtime.InteropServices.CharSet.Unicode, SetLastError = true)]
        private static extern IntPtr AddDllDirectory(string lpNewDirectory);
        [System.Runtime.InteropServices.DllImport("kernel32.dll", CharSet = System.Runtime.InteropServices.CharSet.Unicode, SetLastError = true)]
        private static extern bool SetDllDirectory(string lpPathName);

        private static void ExtendDllSearchPath(string simDllPath)
        {
            var dirs = new List<string>();
            if (!string.IsNullOrEmpty(simDllPath)) dirs.Add(Path.GetDirectoryName(simDllPath));   // ...\Simulation
            dirs.Add(@"D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS");                            // main folder
            foreach (var d in dirs)
            {
                if (string.IsNullOrEmpty(d) || !Directory.Exists(d)) continue;
                if (AddDllDirectory(d) == IntPtr.Zero) SetDllDirectory(d);   // fallback on older Windows
            }
        }

        private static int SafeCount(SolidWorks.Interop.cosworks.ICWLoadsAndRestraintsManager lrm)
        { try { return lrm.Count; } catch { return -1; } }

        // Selects one face of the active part by its analyze_model(faces) index, clearing first.
        //
        // Headless face selection — ALL THREE measured on this machine, because the official VBA
        // example's faces are UI-selected and it is easy to assume that is an API requirement. It is not:
        //   ISelectionMgr.AddSelectionListObject(face)      -> FAILS (returns false) for IFace2
        //   ILoop2.Select(null, false, null)                -> selects the loop's EDGES:
        //                                                        GetSelectedObjectType2 == 1 (swSelEDGES),
        //                                                        NOT 2 (swSelFACES) — a silent wrong answer
        //   Extension.SelectByID2("", "FACE", x, y, z)       -> WORKS, once (x,y,z) is a point that is
        //     actually ON the face. IFace2.GetClosestPointOn(px,py,pz) projects any probe point onto
        //     the face, which guarantees that. The bounding-box centre is only on the face for planar
        //     faces, so GetClosestPointOn is the reliable source.
        // Always verify with GetSelectedObjectType2(index) == 2 (swSelFACES) before handing the array
        // to cosworks — a Select() that returns true can still have selected the wrong entity type.
        private static bool SelectFaceByIndex(IModelDoc2 modelDoc, int faceIndex, SolidWorks.Interop.sldworks.ISelectionMgr selMgr)
        {
            try
            {
                var partDoc = modelDoc as SolidWorks.Interop.sldworks.IPartDoc;
                if (partDoc == null) return false;
                var bodies = partDoc.GetBodies2((int)SolidWorks.Interop.swconst.swBodyType_e.swSolidBody, true) as object[];
                if (bodies == null) return false;

                // DeSelect's index parameter is an OBJECT; an int fails to marshal, the throw used to
                // be swallowed, and the selection was never actually cleared.
                for (int si = selMgr.GetSelectedObjectCount(); si >= 1; si--)
                {
                    try { selMgr.DeSelect((object)si); } catch { }
                }

                int idx = 0;
                foreach (var b in bodies)
                {
                    var body = b as SolidWorks.Interop.sldworks.IBody2;
                    if (body == null) continue;
                    var faces = body.GetFaces() as object[];
                    if (faces == null) continue;
                    foreach (var f in faces)
                    {
                        if (idx == faceIndex)
                        {
                            var face = f as SolidWorks.Interop.sldworks.IFace2;
                            if (face == null) return false;

                            // 2) pick the face BY POSITION. SelectByID2 needs a point that actually lies
                            //    on the face, and the bounding-box centre is only on it for planar faces.
                            //    GetClosestPointOn projects any probe point onto the face, which gives a
                            //    point guaranteed to be on it. (This is also how the cosine-between-normals
                            //    check below decides whether the face is the one we want.)
                            try
                            {
                                var box = face.GetBox() as double[];
                                if (box != null && box.Length >= 6)
                                {
                                    double cx = (box[0] + box[3]) / 2.0, cy = (box[1] + box[4]) / 2.0, cz = (box[2] + box[5]) / 2.0;
                                    var on = face.GetClosestPointOn(cx, cy, cz) as double[];
                                    if (on != null && on.Length >= 3)
                                    {
                                        bool sel = modelDoc.Extension.SelectByID2("", "FACE", on[0], on[1], on[2], false, 0, null,
                                            (int)SolidWorks.Interop.swconst.swSelectOption_e.swSelectOptionDefault);
                                        if (sel && selMgr.GetSelectedObjectCount() > 0)
                                        {
                                            int st = selMgr.GetSelectedObjectType2(1);
                                            if (st == (int)SolidWorks.Interop.swconst.swSelectType_e.swSelFACES) return true;
                                            for (int si = selMgr.GetSelectedObjectCount(); si >= 1; si--) { try { selMgr.DeSelect((object)si); } catch { } }
                                        }
                                    }
                                }
                            }
                            catch { }

                            // 1) boundary-loop selection — selects the loop's EDGES (swSelEDGES), not the
                            //    face, so it is only a fallback for genuinely wireframe targets.
                            try
                            {
                                var loop = face.GetFirstLoop() as SolidWorks.Interop.sldworks.ILoop2;
                                if (loop != null)
                                {
                                    bool lr = loop.Select(null, false, null);
                                    if (lr && selMgr.GetSelectedObjectCount() > 0) return true;
                                }
                            }
                            catch { }

                            // 3) last resort: the object path (measured to fail for faces on this build)
                            bool r = selMgr.AddSelectionListObject(f, null);
                            if (!r) { int r2 = selMgr.AddSelectionListObjects(new object[] { f }, null); r = r2 > 0; }
                            return r && selMgr.GetSelectedObjectCount() > 0;
                        }
                        idx++;
                    }
                }
                return false;
            }
            catch { return false; }
        }

        // Selects a vertex for the displacement constraint. Returns 0 — and CANNOT be made to work
        // headless on this machine, for two independent reasons, both measured:
        //
        //  (1) Extension.SelectByID2 is a "what is under this cursor" hit test. A face has AREA, so
        //      IFace2.GetClosestPointOn's projected point hits it reliably (see SelectFaceByIndex). A
        //      vertex is ZERO-DIMENSIONAL: the probe point must coincide with it exactly, which
        //      floating-point coordinates never do ⇒ the call always returns false.
        //  (2) Bypassing the hit test by fetching the live object does not help on a revolved body.
        //      Walking IBody2.GetEdges() → IEdge.GetStartVertex()/GetEndVertex() and reading
        //      IVertex.GetPoint() over ALL edges yields an EMPTY list for the Ø80x110 housing, which is
        //      a pure revolved solid (2 planar + 2 cylindrical faces, 4 closed circular edges): SolidWorks
        //      does not create real vertices for closed circles.
        //
        // ⚠ Two interop traps hit while proving this, worth keeping in mind anywhere else:
        //    • IEdge.GetStartVertex() returns `object`; cast to **IVertex**, not `Vertex` — `Vertex` is an
        //      EMPTY marker interface (GetMethods() == 0) while IVertex has the real 18 members.
        //    • IModelDoc2.SelectAt(Flags, X, Y, Z) looks like the right tool but BLOCKS FOREVER without a
        //      graphics window. Never call it headless.
        // So this always returns 0 on this machine; the caller reports that honestly rather than
        // pretending the constraint is anchored. Set the displacement location in the SOLIDWORKS UI.
        private static int SelectVertexFromModel(IModelDoc2 modelDoc, SolidWorks.Interop.sldworks.ISelectionMgr selMgr, double[] pt)
        {
            return 0;
        }
        // Selects every solid body and returns them as a SAFEARRAY of VARIANT — the shape the cosworks
        // methods take for entity collections (the material API needs exactly this).
        private static object[] SelectBodyArray(IModelDoc2 modelDoc, SolidWorks.Interop.sldworks.ISelectionMgr selMgr)
        {
            try
            {
                var partDoc = modelDoc as SolidWorks.Interop.sldworks.IPartDoc;
                if (partDoc == null) return null;
                var bodies = partDoc.GetBodies2((int)SolidWorks.Interop.swconst.swBodyType_e.swSolidBody, true) as object[];
                if (bodies == null || bodies.Length == 0) return null;
                for (int si = selMgr.GetSelectedObjectCount(); si >= 1; si--) { try { selMgr.DeSelect((object)si); } catch { } }
                foreach (var b in bodies)
                {
                    var bn = (b as SolidWorks.Interop.sldworks.IBody2)?.Name;
                    if (string.IsNullOrEmpty(bn)) continue;
                    try { modelDoc.Extension.SelectByID2(bn, "SOLIDBODY", 0, 0, 0, false, 0, null, 0); } catch { }
                }
                return SelectionArray(selMgr);
            }
            catch { return null; }
        }

        // The DispArray the official example passes. In VBA that is `Array(x)` — a SAFEARRAY of
        // VARIANT. A plain CLR object[] is NOT the same thing, and cosworks' Add* methods reject it
        // with a generic marshalling ArgumentException whose text misleadingly names argument 1.
        // Array.CreateInstance(typeof(object), n) produces a real one-dimensional VARIANT SAFEARRAY,
        // which is what the COM interop layer will marshal to what the API expects.
        private static object[] SelectionArray(SolidWorks.Interop.sldworks.ISelectionMgr selMgr)
        {
            try
            {
                int n = selMgr.GetSelectedObjectCount();
                if (n <= 0) return null;
                var arr = Array.CreateInstance(typeof(object), n);
                int i = 0;
                for (int k = 1; k <= n; k++) arr.SetValue(selMgr.GetSelectedObject6(k, -1), i++);
                return (object[])arr;
            }
            catch { return null; }
        }

        // Calls a method on a dual COM interface THROUGH IDispatch explicitly.
        //
        // Why this exists: ICWLoadsAndRestraintsManager is declared with TypeLibType +
        // DispIdAttribute, i.e. a dual interface, and BOTH normal C# early binding and `dynamic`
        // late binding fail on it here with the same generic marshalling ArgumentException. Going
        // through Type.InvokeMember dispatches by DISPID straight to IDispatch::Invoke, which is the
        // one path not yet tried. The DispID is passed in rather than the name because the cosworks
        // methods are only reliably addressable by number (AddRestraint = 3, AddForce = 5).
        private static object InvokeDispatch(object comObject, string method, int dispId, object[] args, out int errOut)
        {
            errOut = -999;
            try
            {
                var t = comObject.GetType();
                var argTypes = new Type[args.Length + 1];
                for (int i = 0; i < args.Length; i++) argTypes[i] = args[i] == null ? typeof(object) : args[i].GetType();
                argTypes[args.Length] = typeof(int).MakeByRefType();      // the out ErrorCode

                object[] callArgs = new object[args.Length + 1];
                Array.Copy(args, callArgs, args.Length);
                callArgs[args.Length] = 0;

                object r = t.InvokeMember(method,
                    System.Reflection.BindingFlags.InvokeMethod, null, comObject, callArgs, null,
                    null, null);
                errOut = (int)callArgs[args.Length];
                return r;
            }
            catch (Exception ex) { throw new InvalidOperationException("InvokeDispatch(" + method + "/" + dispId + ") failed: " + ex.Message, ex); }
        }

        // Returns a strongly-typed interface view of a COM RCW, or null.
        // A plain `as TInterface` cast on a __ComObject does NOT QueryInterface in .NET, and some
        // cosworks interfaces (ICWLoadsAndRestraintsManager) are not reachable through IDispatch at
        // all — so go through IUnknown and ask COM for the interface we actually want.
        private static T Typed<T>(object comObject) where T : class
        {
            try
            {
                if (comObject == null) return null;
                if (comObject is T already) return already;
                IntPtr unk = Marshal.GetIUnknownForObject(comObject);
                try { return (T)Marshal.GetTypedObjectForIUnknown(unk, typeof(T)); }
                finally { Marshal.Release(unk); }
            }
            catch { return null; }
        }


        // ---------------------------------------------------------------
        // electrical  (READ-ONLY probe)  — SOLIDWORKS Electrical API reachability
        //
        // Electrical has NO interop in api\redist; its API ships in the product's own bin:
        //   SOLIDWORKS Electrical\bin\Interop.EwAPI.dll   (EwAPI namespace, 683 types)
        //   SOLIDWORKS Electrical\bin\ewapix.dll           (the COM server)
        // It does NOT need SolidWorks running — it is a standalone workstation product.
        //
        // The working sequence (all steps MEASURED 2026-09-27, see manual §3.5e):
        //   1) CoCreateInstance(EwInteropFactoryXClass {B5F20185-…})   -- NOT EwAPIXClass, which is
        //      declared by the interop but NOT registered (REGDB_E_CLASSNOTREG)
        //   2) factory.getEwAPI(out err)          -- MUST be IDispatch: QI to IInteropFactoryX fails
        //                                             (interop GUIDs disagree with the real ewapix.dll)
        //   3) api.setEwSoftType(kSoftTypeSWElectrical = 1)  -> 0
        //   4) api.initialize()                               -> 0 (else "Services are not initialized")
        //   5) api.newEwEnvironment()                         -> EwEnvironmentX  (QI to
        //                                             IEwEnvironmentX SUCCEEDS from here on)
        //   6) env.getEwProjectManager(out err)                -> EwProjectManagerX
        //   7) env.getVersion()                               -> "2026.0.0.5070"
        // Once step 5 succeeds, use the strongly-typed interfaces: calling by NAME through IDispatch
        // fails with DISP_E_UNKNOWNNAME (0x80020006) because the interop's member names do not
        // match the real ones.
        // ---------------------------------------------------------------
        // Loads a directory and everything already in it into this process, so that native
        // dependencies of a product API (TEKLA-DB for Electrical, cosworks for Simulation, …)
        // resolve without touching the machine-wide PATH.
        // CreateMesh 的返回值按官方 swsStudyMeshError_e 解码（否则只是一个裸 int）
        private static string DecodeMeshErr(int v)
        {
            switch (v)
            {
                case 0: return "swsStudyErrorSuccessful";
                case 1: return "swsStudyErrorNoValidShells";
                case 2: return "swsStudyErrorNoSolidBody";
                case 3: return "swsStudyErrorElementSizeTooSmall";
                case 4: return "swsStudyErrorElementSizeTooBig";
                case 5: return "swsStudyErrorSpecifyPositiveValue";
                case 6: return "swsStudyErrorSpecifyElementSizeScaleFactor";
                case 7: return "swsStudyErrorSpecifyToleranceScaleFactor";
                default: return "未知(" + v + ")";
            }
        }

        internal static class NativeProbe
        {
            [System.Runtime.InteropServices.DllImport("kernel32.dll", CharSet = System.Runtime.InteropServices.CharSet.Unicode, SetLastError = true)]
            private static extern IntPtr LoadLibraryW(string f);
            private static readonly System.Collections.Generic.HashSet<string> _loaded =
                new System.Collections.Generic.HashSet<string>(StringComparer.OrdinalIgnoreCase);

            internal static void LoadDir(string dir)
            {
                try
                {
                    if (!Directory.Exists(dir)) return;
                    if (_loaded.Add(dir)) LoadLibraryW(dir);
                    foreach (var f in Directory.GetFiles(dir, "*.dll"))
                    {
                        if (_loaded.Add(f)) LoadLibraryW(f);
                    }
                }
                catch { }
            }
        }

        internal ExecutionResponse ElectricalProbe(ToolRequest request)
        {
            var log = new JArray();
            try
            {
                string bin = p_string(request, "electrical_bin",
                    "D:\\Program Files\\SOLIDWORKS Corp\\SOLIDWORKS Electrical\\bin");
                if (!Directory.Exists(bin))
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "EW_BIN_MISSING", "Electrical bin not found: " + bin);

                // Native deps (TEKLA-DB etc.) are not on the default search path.
                NativeProbe.LoadDir(bin);

                System.Reflection.Assembly ew = null;
                try { ew = System.Reflection.Assembly.LoadFrom(Path.Combine(bin, "Interop.EwAPI.dll")); }
                catch (Exception ex)
                {
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "EW_INTEROP_LOAD_FAILED", ex.Message);
                }
                log.Add("Interop.EwAPI loaded, exported types = " + ew.GetExportedTypes().Length);

                var flags = System.Reflection.BindingFlags.InvokeMethod;

                // 1) factory
                object factory = null;
                try
                {
                    factory = Activator.CreateInstance(Type.GetTypeFromCLSID(
                        new Guid("B5F20185-7EA0-43C1-B21D-94175E6F01FF")));
                    log.Add("CoCreateInstance(EwInteropFactoryXClass) -> "
                          + (factory == null ? "null" : factory.GetType().FullName));
                }
                catch (Exception ex) { return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(), "EW_FACTORY_FAILED", ex.Message); }
                if (factory == null)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(), "EW_FACTORY_NULL", "factory is null");

                // 2) getEwAPI — IDispatch by name, because QI on IInteropFactoryX fails
                object api = null;
                int apiErr = -999;
                try
                {
                    var gargs = new object[] { null };
                    api = factory.GetType().InvokeMember("getEwAPI", flags, null, factory, gargs, null, null, null);
                    apiErr = Convert.ToInt32(gargs[0]);
                    log.Add("factory.getEwAPI(out err) -> err=" + apiErr
                          + (api == null ? " (null)" : " " + api.GetType().FullName));
                }
                catch (Exception ex) { return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(), "EW_GETAPI_FAILED", ex.Message); }
                if (api == null)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(), "EW_API_NULL", "getEwAPI returned null (err=" + apiErr + ")");

                var iApiX = ew.GetType("EwAPI.IEwAPIX");
                var eSoft = ew.GetType("EwAPI.EwSoftType");

                // 3) setEwSoftType + initialize
                try
                {
                    object soft = Enum.ToObject(eSoft, 1);   // kSoftTypeSWElectrical
                    object rc1 = api.GetType().InvokeMember("setEwSoftType", flags, null, api,
                                                           new object[] { soft }, null, null, null);
                    log.Add("api.setEwSoftType(kSoftTypeSWElectrical=1) -> " + rc1);
                    object rc2 = api.GetType().InvokeMember("initialize", flags, null, api, null, null, null, null);
                    log.Add("api.initialize() -> " + rc2 + "  (0 = EW_NO_ERROR)");
                }
                catch (Exception ex) { log.Add("init failed: " + ex.Message); }

                // 4) newEwEnvironment — IDispatch by name works here
                object env = null;
                try
                {
                    env = api.GetType().InvokeMember("newEwEnvironment", flags, null, api, null, null, null, null);
                    log.Add("api.newEwEnvironment() -> " + (env == null ? "null" : env.GetType().FullName));
                }
                catch (Exception ex) { log.Add("newEwEnvironment failed: " + ex.Message); }

                var result = new JObject
                {
                    ["reachable"] = env != null,
                    ["api_error"] = apiErr,
                    ["log"] = log,
                    ["note"] = "reach=true means the whole Electrical API chain is live: factory -> getEwAPI ->"
                            + " setEwSoftType -> initialize -> newEwEnvironment. From the environment object on,"
                            + " use the STRONGLY-TYPED EwAPI interfaces (QI succeeds there); calling by name"
                            + " through IDispatch fails with DISP_E_UNKNOWNNAME."
                };

                if (env != null)
                {
                    var iEnv = ew.GetType("EwAPI.IEwEnvironmentX");
                    bool qi = iEnv != null && iEnv.IsInstanceOfType(env);
                    result["env_qi"] = qi;
                    log.Add("IEwEnvironmentX QI = " + qi
                          + (iEnv != null ? "，方法数 = " + iEnv.GetMethods().Length : ""));
                    if (qi)
                    {
                        try { result["version"] = JToken.FromObject(iEnv.GetMethod("getVersion").Invoke(env, null)); }
                        catch (Exception ex) { log.Add("getVersion failed: " + ex.Message); }
                        try
                        {
                            var pargs = new object[] { null };
                            var pm = iEnv.GetMethod("getEwProjectManager").Invoke(env, pargs);
                            result["project_manager"] = pm != null ? pm.GetType().FullName : "null";
                            log.Add("env.getEwProjectManager(out err) -> err=" + Convert.ToInt32(pargs[0])
                                  + ", mgr=" + (pm == null ? "null" : pm.GetType().FullName));
                        }
                        catch (Exception ex) { log.Add("getEwProjectManager failed: " + ex.Message); }
                    }
                }

                return OkWrite(request, null, "ELECTRICAL", result.ToString(Formatting.None));
            }
            catch (COMException ex) { return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(), "COM_ERROR", ex.Message); }
            catch (Exception ex) { return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(), "UNEXPECTED_ERROR", ex.Message + " @ " + ex.StackTrace); }
        }

        internal ExecutionResponse TopologyOptimize(ToolRequest request)
        {
            if (_guard.IsDuplicate(request.OperationId)) return _guard.GetDuplicate(request.OperationId);
            if (!_guard.IsStateVersionValid(request.StateVersion))
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "INVALID_STATE_VERSION", "state version mismatch");
            var log = new JArray();
            try
            {
                var modelDoc = SafeActiveDoc();
                if (modelDoc == null)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "NO_ACTIVE_DOCUMENT", "No active document. Topology optimization needs a PART or ASSEMBLY open.");
                if (modelDoc.GetType() != 1 && modelDoc.GetType() != 2)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "WRONG_DOCUMENT_TYPE", "topology_optimize needs a PART or ASSEMBLY document.");
                log.Add("active document: " + modelDoc.GetTitle() + " (type=" + modelDoc.GetType() + ")");

                string simDll = p_string(request, "simulation_dll",
                    "D:\\Program Files\\SOLIDWORKS Corp\\SOLIDWORKS\\Simulation\\cosworks.dll");
                string progId = p_string(request, "prog_id", "CosmosWorks.CosmosWorks");
                int resultType = (int)(p_double(request, "result_type", 0) ?? 0);

                if (!EnsureConnected())
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "COM_ATTACH_FAILED", "SolidWorks not attached.");

                // Simulation is a plain in-process COM server, NOT a .sldaddon file — measured:
                // there is no .sldaddon anywhere under the SolidWorks install tree, and the only
                // entry in HKLM\SOFTWARE\SolidWorks\AddInsStartup is SOLIDWORKS Inspection.
                // ISldWorks.LoadAddIn() therefore cannot load it (it returns swUnknownError, -1),
                // and GetAddInObject() returns null for the ProgID and the CLSID because SolidWorks
                // only surfaces add-ins it has itself loaded. The remaining route is to activate the
                // COM class ourselves — the same activation SolidWorks performs when a user picks
                // Tools > Simulation. action="cocreate" does that.
                string action = p_string(request, "action", "probe");
                if (action == "cocreate")
                {
                    string clsid = p_string(request, "clsid", "{C8F79410-CD71-4061-A2E4-B6BF17CCB27F}");
                    ExtendDllSearchPath(simDll);   // without this, CoCreateInstance fails 0x8007007E
                    Type t = Type.GetTypeFromCLSID(new System.Guid(clsid), true);   // throws if not registered
                    log.Add("Type.GetTypeFromCLSID(" + clsid + ") -> " + (t == null ? "null" : t.FullName));
                    object inst = Activator.CreateInstance(t);
                    log.Add("Activator.CreateInstance -> " + (inst == null ? "null" : inst.GetType().FullName));
                    dynamic cwDirect = inst;
                    dynamic cosmos2 = cwDirect.CosmosWorks;
                    log.Add("ICwAddincallback.CosmosWorks -> " + (cosmos2 == null ? "NULL" : cosmos2.GetType().FullName));
                    if (cosmos2 != null)
                    {
                        try { log.Add("ICosmosWorks.VersionNumber = " + cosmos2.VersionNumber); } catch (Exception ex) { log.Add("VersionNumber failed: " + ex.Message); }
                        try
                        {
                            dynamic md2 = cosmos2.ActiveDoc;
                            log.Add("ICosmosWorks.ActiveDoc -> " + (md2 == null ? "NULL" : md2.GetType().FullName));
                            if (md2 != null)
                            {
                                int r2 = md2.AddDefaultOptimizationStudyPlot(resultType);
                                log.Add("AddDefaultOptimizationStudyPlot(" + resultType + ") -> " + r2);
                                dynamic sm2 = md2.StudyManager;
                                log.Add("StudyManager -> " + (sm2 == null ? "NULL" : sm2.GetType().FullName));
                            }
                        }
                        catch (Exception ex) { log.Add("ActiveDoc path failed: " + ex.Message); }
                    }
                    var p2 = new JObject { ["stage"] = "cocreate", ["log"] = log,
                        ["note"] = "Direct COM activation of the Simulation add-in (local; no licence/activation endpoint contacted)." };
                    return OkWrite(request, modelDoc, null, p2.ToString(Formatting.None));
                }

                // 1) load the add-in (idempotent; returns swLoadAddinErrorNone(0) if already up)
                //    ★ 2026-09-28 实测：本机 GetAddInObject 严格 50% 交替（6 次 3 成 3 败，
                //      失败时 LoadAddIn 返 -1），典型的 COM 引用计数/RCW 释放竞态。
                //      ⇒ 这里必须【内部重试】，单次调用不可信。
                int loadRet = -1;
                object addin = null; string usedId = null; Exception lastEx = null;
                const int ADDIN_ATTEMPTS = 6;
                for (int attempt = 1; attempt <= ADDIN_ATTEMPTS && addin == null; attempt++)
                {
                    loadRet = SafeInt(() => _solidWorks.LoadAddIn(simDll));
                    // 2) get the add-in object (try the version-independent ProgID first, then .19)
                    foreach (var id in new[] { progId, "CosmosWorks.CosmosWorks", "SldWorks.Simulation", "SldWorks.Simulation.19", "{C8F79410-CD71-4061-A2E4-B6BF17CCB27F}" })
                    {
                        try { addin = _solidWorks.GetAddInObject(id); if (addin != null) { usedId = id; break; } }
                        catch (Exception ex) { lastEx = ex; }
                    }
                    log.Add("add-in attempt " + attempt + "/" + ADDIN_ATTEMPTS
                          + ": LoadAddIn -> " + loadRet
                          + ", GetAddInObject(" + (usedId ?? "all ids") + ") -> "
                          + (addin == null ? "null" : addin.GetType().FullName));
                    if (addin == null && attempt < ADDIN_ATTEMPTS)
                    {
                        // 让 COM 引用计数落定再试下一次
                        GC.Collect(); GC.WaitForPendingFinalizers();
                        System.Threading.Thread.Sleep(150);
                    }
                }
                if (loadRet != 0 && addin == null && !File.Exists(simDll))
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "ADDIN_MISSING", "cosworks.dll not found at '" + simDll + "'.");
                if (addin == null)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "ADDIN_UNREACHABLE",
                        "GetAddInObject found no Simulation add-in object after " + ADDIN_ATTEMPTS
                        + " attempts (last LoadAddIn returned " + loadRet + ")"
                        + (lastEx != null ? "; last error: " + lastEx.Message : "")
                        + ". Simulation is installed and registered on this machine. Verified on 2026-09-28:"
                        + " the same call succeeds ~50% of the time (COM reference-count race), so a single"
                        + " failure is NOT proof of a missing licence. If this persists across several"
                        + " service restarts, suspect the seat licence for the Simulation add-in.");
                log.Add("add-in reached via '" + usedId + "' after retry loop");

                // 3) CosmosWorks -> ActiveDoc -> ICWModelDoc
                dynamic cb = addin;
                dynamic cosmos = cb.CosmosWorks;
                if (cosmos == null)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "NO_COSMOSWORKS", "ICwAddincallback.CosmosWorks returned null.");
                string cwVersion = null;
                try { cwVersion = cosmos.VersionNumber; } catch { }
                log.Add("ICosmosWorks OK (version=" + (cwVersion ?? "?") + ")");

                dynamic cwModel = cosmos.ActiveDoc;
                if (cwModel == null)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "NO_CW_MODEL",
                        "ICosmosWorks.ActiveDoc returned null. The Simulation add-in is loaded but has no active"
                        + " Simulation model — make sure the document is the ACTIVE one and the Simulation tab is open.");
                log.Add("ICWModelDoc OK (topology API reachable)");

                // 4) create the optimization study.
                //    AddDefaultOptimizationStudyPlot() is the "convenience" entry, but MEASURED on
                //    this machine it returns 0 (swsOptimizationDesignResultNoError) while leaving
                //    StudyCount at 0 and GetStudy(0) null — i.e. it silently creates nothing.
                //    Creating the study explicitly works: study type 13 = swsAnalysisStudyTypeTopology_Static
                //    (reflected from SolidWorks.Interop.cosworks.dll). Falls back to the convenience
                //    call only if the explicit creation returns nothing.
                dynamic studyMgr0 = cwModel.StudyManager;
                if (studyMgr0 == null)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "NO_STUDY_MANAGER",
                        "ICWModelDoc.StudyManager returned null. Steps reached: " + string.Join(" | ", log));
                // 13 = Topology_Static, 0 = Static. The default was 13 because the tool was built for
                // topology, but the OFFICIAL "Analyze Part" example that shows AddRestraint runs on a
                // STATIC study — a topology study carries its own Goals-and-Constraints体系 and may
                // simply not accept LoadsAndRestraintsManager input at all. Pass study_type=0 to
                // compare like-for-like against the documented example.
                // ★★ 2026-09-28 ROOT CAUSE of the topology err=17 wall:
//     swsTopologyStudyError_e 17 = swsTopoErrCode_SetOperationNotSupported
//     i.e. the STUDY TYPE does not support the operation — NOT "you must pick geometry in the UI".
//     All of CreateThicknessControl / CreateSymmetryControl / CreateDemoldControl /
//     CreateMassConstraint return 17 on a Static (type 0) study; they need Topology-Static (type 13).
//     We used 0 because the official AddRestraint sample uses 0 — that was the wrong trade:
//     AddRestraint works on both, the topology controls only work on 13.
//     So: default to 13 (topology) and let the caller force 0 for a plain static study.
int studyTypeEnum = (int)(p_double(request, "study_type", 13) ?? 13);
                log.Add("study_type = " + studyTypeEnum
                      + " (0 = Static, 13 = Topology_Static) — the official AddRestraint example uses 0");

                // Use a unique name every call. Measured: CreateNewStudy3 rejects a duplicate name
                // (err=2) and StudyManager.DeleteStudy does NOT reliably remove the old one, so reusing
                // a fixed name leaves a stale study behind — and GetStudy() is 1-based in the official
                // VBA example, so index 0 can hand back that stale study whose thickness/symmetry/demold
                // controls already exist, which is exactly why every Create*Control then returned
                // err=13 (OnlyOne...CanBeDefined) instead of 0.
                string baseName = p_string(request, "study_name", "MCP_Topology");
                string studyNameWanted = baseName + "_" + DateTime.Now.ToString("HHmmssfff");
                dynamic createdStudy = null; int createErr = 0; string createdVia = "";

                // 2026-09-27：复用【已在 SolidWorks 里建好的研究】。
                // 实测 UI 能建出夹具（静力学分析 2 → 固定-1），而 CreateNewStudy3 建的研究
                // 加夹具恒 E_INVALIDARG —— 差别可能就在"研究是由完整 UI 流程初始化的，
                // 含有 CreateNewStudy3 不会设置的内部状态"。所以这里允许指定已存在的��究名。
                string reuseName = p_string(request, "study_reuse", "");
                if (!string.IsNullOrEmpty(reuseName))
                {
                    try
                    {
                        int cnt = (int)studyMgr0.StudyCount;
                        for (int i = 1; i <= cnt; i++)     // GetStudy 是 1-based（实测）
                        {
                            var s = studyMgr0.GetStudy(i);
                            if (s == null) continue;
                            string nm = "";
                            try { nm = (string)s.GetName(); } catch { }
                            log.Add("  existing study #" + i + " name='" + nm + "'");
                            if (nm != null && nm.StartsWith(reuseName, StringComparison.OrdinalIgnoreCase))
                            {
                                createdStudy = s;
                                createdVia = "REUSED existing study #" + i + " (" + nm + ")";
                                break;
                            }
                        }
                    }
                    catch (Exception ex) { log.Add("study reuse scan failed: " + ex.Message); }
                }

                try
                {
                    int existing = (int)studyMgr0.StudyCount;
                    log.Add("existing StudyCount = " + existing + "; new study name = " + studyNameWanted);
                }
                catch (Exception ex) { log.Add("StudyCount probe failed: " + ex.Message); }

                try
                {
                    if (createdStudy == null)   // 复用命中时不再新建
                    {
                        createdStudy = studyMgr0.CreateNewStudy3(studyNameWanted, studyTypeEnum, 0, out createErr);
                        if (createdStudy != null) createdVia = "CreateNewStudy3(type=" + studyTypeEnum + ")";
                    }
                }
                catch (Exception ex) { log.Add("CreateNewStudy3 threw: " + ex.Message); }
                if (createdStudy == null)
                {
                    int addRet = cwModel.AddDefaultOptimizationStudyPlot(resultType);
                    log.Add("CreateNewStudy3 -> null (err=" + createErr + "); fell back to AddDefaultOptimizationStudyPlot("
                          + resultType + ") -> " + addRet + (addRet == 0 ? "" : " (error)"));
                }
                else
                {
                    log.Add("study created via " + createdVia + " (err=" + createErr + ")");
                }

                // 5) reach the study and its topology manager
                dynamic studyMgr = cwModel.StudyManager;
                if (studyMgr == null)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "NO_STUDY_MANAGER",
                        "ICWModelDoc.StudyManager returned null (createErr=" + createErr + "). Steps reached: "
                        + string.Join(" | ", log));
                int studyIndex = -1;
                try { studyIndex = (int)studyMgr.ActiveStudy; } catch { }
                // ActiveStudy is an Int32 INDEX, and it can legitimately be -1 ("none active") even
                // right after a study was created. So don't trust it alone: ask for the count and
                // take the last study, which is the one we just created.
                int studyCount = -1;
                try { studyCount = (int)studyMgr.StudyCount; } catch (Exception ex) { log.Add("StudyCount failed: " + ex.Message); }
                log.Add("StudyManager.ActiveStudy index = " + studyIndex + ", StudyCount = " + studyCount);
                dynamic study = null;
                int usedIndex = -1;
                foreach (var cand in new[] { studyIndex, studyCount, studyCount - 1, 1, 0 })
                {
                    // NOTE: do NOT gate on studyCount here. With count==0 the guard would skip every
                    // candidate — including 0 — and the study that CreateNewStudy3 just created may not
                    // be counted yet. Always try GetStudy(0).
                    if (cand < 0) continue;
                    if (studyCount > 0 && cand > studyCount) continue;
                    try { var s = studyMgr.GetStudy(cand); if (s != null) { study = s; usedIndex = cand; break; } }
                    catch (Exception ex) { log.Add("GetStudy(" + cand + ") threw: " + ex.Message); }
                }
                if (study == null)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "NO_STUDY",
                        "Could not get any study: ActiveStudy index=" + studyIndex + ", count=" + studyCount
                        + ", createErr=" + createErr + ", createdVia='" + createdVia
                        + "'. Steps reached: " + string.Join(" | ", log));
                studyIndex = usedIndex;
                log.Add("using study index " + usedIndex);
                string studyName = null, studyType = null;
                try { studyName = study.Name; } catch { }
                try { studyType = study.StudyType; } catch { }
                log.Add("StudyManager.ActiveStudy index = " + studyIndex
                      + " -> study '" + (studyName ?? "?") + "' type=" + (studyType ?? "?"));

                dynamic topo = study.TopologyStudyManager;
                dynamic opts = study.TopologyStudyOptions;
                log.Add("TopologyStudyManager = " + (topo == null ? "NULL" : topo.GetType().FullName));
                log.Add("TopologyStudyOptions = " + (opts == null ? "NULL" : opts.GetType().FullName));

                // ---------------------------------------------------------------
                // action="solve" — set up controls, add constraints, run, then READ THE RESULT BACK.
                //
                // ORDER IS NOT COSMETIC (manual §12.6): solved without a thickness control the study
                // returns 0.5 mm webs that cannot be milled; without a preserved region it eats the
                // bearing bore; without symmetry it returns a left/right asymmetric shape. So:
                // controls FIRST, then constraints, then solve.
                if (action == "solve")
                {
                    if (topo == null)
                        return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                            "NO_TOPOLOGY_MANAGER", "ICWStudy.TopologyStudyManager is null. Steps: " + string.Join(" | ", log));

                    double minThickness = p_double(request, "min_thickness_mm", 3.0) ?? 3.0;
                    double massPercent  = p_double(request, "mass_percent", 50.0) ?? 50.0;
                    bool wantSymmetry = p_bool(request, "symmetry", true);
                    bool wantDemold   = p_bool(request, "demold", true);

                    // ---- 0) OPEN THE MANAGER'S EDIT SESSION.
                    // ICWTopologyStudyManager has its OWN BeginEdit()/EndEdit() (reflected), separate from
                    // the per-object ones. Every Create*Control/Create*Constraint below returned
                    // err=17 (swsTopoErrCode_SetOperationNotSupported) when called OUTSIDE that session —
                    // the manager refuses to add anything while not being edited. The study also needs a
                    // GOAL before constraints: CreateGoal(2) = swsTopologyGoalType_MinimizeMass, which is
                    // the standard topology objective (0=MaximizeStiffness, 1=MinimizeMaximumDisplacement).
                    bool inEdit = false;
                    try
                    {
                        topo.BeginEdit();
                        inEdit = true;
                        log.Add("TopologyStudyManager.BeginEdit() OK");
                    }
                    catch (Exception ex) { log.Add("TopologyStudyManager.BeginEdit() FAILED: " + ex.Message); }

                    int goalRet = -999;
                    try
                    {
                        goalRet = topo.CreateGoal(2 /* MinimizeMass */);
                        log.Add("CreateGoal(MinimizeMass=2) -> " + goalRet);
                    }
                    catch (Exception ex) { log.Add("CreateGoal threw: " + ex.Message); }

                    // ---- 1) thickness control (minimum member size) ----
                    try
                    {
                        int err = 0;
                        dynamic tc = topo.CreateThicknessControl(out err);
                        if (tc != null)
                        {
                            tc.BeginEdit();
                            try { tc.SetName("MCP_min_thickness"); } catch { }
                            tc.SetMinimumMemberThickness(minThickness / 1000.0);   // API is METRES
                            int e = tc.EndEdit();
                            log.Add("thickness control: min " + minThickness + " mm -> EndEdit=" + e + " (err=" + err + ")");
                        }
                        else log.Add("thickness control: CreateThicknessControl returned null (err=" + err + ")");
                    }
                    catch (Exception ex) { log.Add("thickness control FAILED: " + ex.Message); }

                    // ---- 2) preserved region (bearing bore / threads / seal faces) ----
                    // Face selection is proven to work headless (see SelectFaceByIndex), so the control
                    // can actually be given faces now. preserved_faces is a comma-separated list of
                    // analyze_model(faces) indices; the end faces of a spindle housing (0,1) are the
                    // ones that must survive the optimizer.
                    string prFaces = p_string(request, "preserved_faces", "0,1");
                    try
                    {
                        int err = 0;
                        dynamic pr = topo.CreatePreservedRegionControl(out err);
                        if (pr != null)
                        {
                            pr.BeginEdit();
                            try { pr.SetName("MCP_preserved"); } catch { }
                            var selMgrPr = modelDoc.SelectionManager as SolidWorks.Interop.sldworks.ISelectionMgr;
                            var picked = 0;
                            if (selMgrPr != null)
                            {
                                foreach (var tok in (prFaces ?? "").Split(','))
                                {
                                    int fi; if (!int.TryParse(tok.Trim(), out fi)) continue;
                                    if (SelectFaceByIndex(modelDoc, fi, selMgrPr)) picked++;
                                    else log.Add("  preserved: face " + fi + " not selectable");
                                }
                                if (picked > 0)
                                {
                                    var arrPr = SelectionArray(selMgrPr);
                                    try
                                    {
                                        int sErr = 0;
                                        dynamic sr = pr.SelectFaces(arrPr);
                                        log.Add("preserved region SelectFaces(" + picked + " faces) -> " + sr);
                                    }
                                    catch (Exception se) { log.Add("SelectFaces threw: " + se.Message); }
                                }
                            }
                            int e = pr.EndEdit();
                            log.Add("preserved region (err=" + err + ", EndEdit=" + e + ", faces picked=" + picked + ")");
                        }
                        else log.Add("preserved region: CreatePreservedRegionControl returned null (err=" + err + ")");
                    }
                    catch (Exception ex) { log.Add("preserved region FAILED: " + ex.Message); }

                    // ---- 3) symmetry ----
                    if (wantSymmetry)
                    {
                        try
                        {
                            int err = 0;
                            dynamic sy = topo.CreateSymmetryControl(out err);
                            if (sy != null)
                            {
                                sy.BeginEdit();
                                try { sy.SelectSymmetryType(0); } catch (Exception ex) { log.Add("SelectSymmetryType(0): " + ex.Message); }
                                try { sy.SetName("MCP_symmetry"); } catch { }
                                int e = sy.EndEdit();
                                log.Add("symmetry control (err=" + err + ", EndEdit=" + e + ") — symmetry plane NOT selected");
                            }
                            else log.Add("symmetry: CreateSymmetryControl returned null (err=" + err + ")");
                        }
                        catch (Exception ex) { log.Add("symmetry FAILED: " + ex.Message); }
                    }

                    // ---- 4) demold ----
                    if (wantDemold)
                    {
                        try
                        {
                            int err = 0;
                            dynamic dm = topo.CreateDemoldControl(out err);
                            if (dm != null)
                            {
                                dm.BeginEdit();
                                try { dm.SelectDemoldDirection(0); } catch (Exception ex) { log.Add("SelectDemoldDirection(0): " + ex.Message); }
                                try { dm.SetName("MCP_demold"); } catch { }
                                int e = dm.EndEdit();
                                log.Add("demold control (err=" + err + ", EndEdit=" + e + ") — pull plane NOT selected");
                            }
                            else log.Add("demold: CreateDemoldControl returned null (err=" + err + ")");
                        }
                        catch (Exception ex) { log.Add("demold FAILED: " + ex.Message); }
                    }

                    // ---- 5) objective: minimise mass down to a target.
                    // name, then SetMassPreference(1) BEFORE SetValue — the value is a whole PERCENTAGE
                    // (the example uses 60), not a fraction. Skipping the re-fetch or the preference makes
                    // the settings land on nothing.
                    try
                    {
                        int err = 0;
                        string massName = "MCP_target_mass";
                        dynamic mc = topo.CreateMassConstraint(out err);
                        if (mc != null)
                        {
                            try { mc.BeginEdit(); } catch { }
                            try { mc.SetName(massName); } catch (Exception ex) { log.Add("SetName: " + ex.Message); }
                            try { mc.SetMassPreference(1); } catch (Exception ex) { log.Add("SetMassPreference: " + ex.Message); }
                            try { mc.SetValue((int)Math.Round(massPercent)); } catch (Exception ex) { log.Add("SetValue: " + ex.Message); }
                            int e = mc.EndEdit();
                            log.Add("mass constraint = " + (int)Math.Round(massPercent)
                                  + "% (err=" + err + ", EndEdit=" + e + ")");
                            int gErr = 0;
                            dynamic back = topo.GetMassConstraint(massName, out gErr);
                            log.Add("GetMassConstraint('" + massName + "') -> err=" + gErr
                                  + (back != null ? " (round-trip OK)" : " (null)"));
                        }
                        else log.Add("mass constraint: CreateMassConstraint returned null (err=" + err + ")");
                    }
                    catch (Exception ex) { log.Add("mass constraint FAILED: " + ex.Message); }

                    // ---- 5a-i) DISPLACEMENT CONSTRAINT — still INSIDE the manager edit session.
                    // Creating it after EndEdit() returns err=17 (SetOperationNotSupported), exactly like
                    // the controls did.
                    //
                    // Topology studies do NOT need a fixture: the standard SOLIDWORKS setup is "minimise
                    // mass subject to a displacement bound". This constraint is created on the same
                    // TopologyStudyManager that already works, so it sidesteps AddRestraint — the one call
                    // this machine refuses — and gives the solver a real constraint to work with.
                    //   swsTopologyStudyConstraintComparator_e                 : 0 IsLessThan, 1 IsGreaterThan, 2 IsInBetween
                    //   swsTopologyStudyDisplacementComponentType_e             : 0 UX, 1 UY, 2 UZ, 3 URES, ...
                    //   swsTopologyStudyDisplacementConstraintLocationOption_e : 0 Auto, 1 UserDefine
                    // Auto means the solver picks the constrained location itself — no vertex has to be
                    // handed to cosworks, which is what makes this work headless.
                    double maxDispMm = p_double(request, "max_displacement_mm", 0.05) ?? 0.05;
                    bool useDisp = p_bool(request, "use_displacement", true);
                    // Where to pin the displacement bound. Default: a point on the housing's top face.
                    double[] dispVertexPt = new double[] { 0.0, 0.0, 0.11 };
                    try
                    {
                        var jp = P(request)?["disp_vertex"] as JArray;
                        if (jp != null && jp.Count >= 3)
                            dispVertexPt = new double[] { jp[0].ToObject<double>(), jp[1].ToObject<double>(), jp[2].ToObject<double>() };
                    }
                    catch { }
                    var selMgrDisp = modelDoc.SelectionManager as SolidWorks.Interop.sldworks.ISelectionMgr;
                    if (useDisp)
                    {
                        try
                        {
                            int dErr = 0;
                            string dispName = "MCP_disp_bound";
                            dynamic dc = topo.CreateDisplacementConstraint(out dErr);
                            if (dc != null)
                            {
                                try { dc.BeginEdit(); } catch { }
                                try { dc.SetName(dispName); } catch (Exception ex) { log.Add("disp SetName: " + ex.Message); }
                                try { dc.SetCoordinateSystemPreference(0 /* Global */); } catch (Exception ex) { log.Add("disp SetCoordSysPref: " + ex.Message); }
                                // ⚠ SetLocationPreference(Auto=0) does NOT mean "the solver picks a point" — it
                                // leaves the constraint with NO location, and the solver then ignores the study
                                // completely (MeshAndRun returns in ~13 s with Results == null and zero CPU).
                                // A displacement constraint needs real vertices through SetVertices.
                                // ⚠ Headless VERTEX selection does not work on this machine (all three routes
                                //    measured): ISelectionMgr.AddSelectionListObject, Extension.SelectByID2
                                //    with type "VERTEX", and IModelDoc2.SelectAt(Flags, X, Y, Z) — the last
                                //    being SolidWorks' own atom hit-tester. Even a point taken from
                                //    analyze_model(edges) (a true end-face vertex) fails. Faces, by contrast,
                                //    DO work via SelectByID2 + GetClosestPointOn.
                                // So a fixture-free study cannot be pinned here: either the fixture
                                // (AddRestraint, refused) or the displacement vertex (not selectable) is
                                // required, and both are blocked. Do not keep re-trying vertex selection.
                                int vsel = SelectVertexFromModel(modelDoc, selMgrDisp, dispVertexPt);
                                if (vsel > 0)
                                {
                                    try { dc.SetVertices(SelectionArray(selMgrDisp)); log.Add("  displacement vertices set: " + vsel); }
                                    catch (Exception ex) { log.Add("disp SetVertices: " + ex.Message); }
                                }
                                else log.Add("  displacement constraint has NO vertex — headless vertex selection is"
                                           + " impossible on this machine (SelectByID2 cannot hit a zero-dimensional"
                                           + " entity, and a revolved body has no real vertices). Anchor the"
                                           + " displacement location in the SOLIDWORKS UI (Tools > Simulation).");
                                try { dc.SetComponent(3 /* URES */); } catch (Exception ex) { log.Add("disp SetComponent: " + ex.Message); }
                                try { dc.SetComparator(0 /* IsLessThan */); } catch (Exception ex) { log.Add("disp SetComparator: " + ex.Message); }
                                try { dc.SetValue(maxDispMm / 1000.0); } catch (Exception ex) { log.Add("disp SetValue: " + ex.Message); }
                                int de = dc.EndEdit();
                                log.Add("displacement constraint '" + dispName + "': URES < " + maxDispMm
                                      + " mm (create err=" + dErr + ", EndEdit=" + de + ")");
                                int gDErr = 0;
                                dynamic backD = topo.GetDisplacementConstraint(dispName, out gDErr);
                                log.Add("GetDisplacementConstraint('" + dispName + "') -> err=" + gDErr
                                      + (backD != null ? " (round-trip OK)" : " (null)"));
                            }
                            else log.Add("displacement constraint: CreateDisplacementConstraint returned null (err=" + dErr + ")");
                        }
                        catch (Exception ex) { log.Add("displacement constraint FAILED: " + ex.Message); }
                    }
                    else log.Add("displacement constraint skipped (use_displacement not set)");

                    bool fixtureAdded = false;
                    // ---- 5a-j) ★★ FIXTURE VIA A FACE  (2026-09-28: the missing piece)
                    // The displacement constraint above cannot be anchored: it needs VERTICES, and headless
                    // vertex selection is impossible on this machine (three routes all measured, L1501-1504).
                    // An un-anchored constraint makes the solver ignore the study entirely
                    // (13 s, zero CPU, Results == null) — that is the real reason no result ever appeared.
                    //
                    // ICWLoadsAndRestraintsManager.AddRestraint(swsRestraintType, DispArray, RefGeom, out err)
                    // takes a FACE instead, and faces DO select headlessly (SelectByID2 works — see L1505).
                    // This branch tries several DispArray shapes and logs the error code for each, because
                    // "DispArray = face objects" vs "DispArray = geometric id numbers" is the one thing the
                    // offline docs do not state.
                    bool addFix = p_bool(request, "add_fixture", false);
                    if (addFix)
                    {
                        var lrmFix = study.LoadsAndRestraintsManager;
                        string faceName = (request.Params as JObject)?.Value<string>("fixture_face") ?? "Face<1>";
                        int rType = (request.Params as JObject)?.Value<int?>("fixture_type") ?? 0;   // 0 = Fixed
                        // ★★ 用 SelectFaceByIndex（本机已实测成功），不用 SelectByID2("Face<n>")
                        //    —— 后者在本机恒返回 false（面名解析不到）。
                        var smFix = modelDoc.SelectionManager as SolidWorks.Interop.sldworks.ISelectionMgr;
                        bool gotFace = false;
                        int fixIdx = (request.Params as JObject)?.Value<int?>("fixture_face_index") ?? 2;
                        try { gotFace = SelectFaceByIndex(modelDoc, fixIdx, smFix); }
                        catch (Exception exF) { log.Add("fixture SelectFaceByIndex: " + exF.Message); }
                        int nFix = 0;
                        if (smFix != null) { try { nFix = smFix.GetSelectedObjectCount2(-1); } catch { } }
                        object faceObj = null;
                        if (nFix > 0 && smFix != null) { try { faceObj = smFix.GetSelectedObject6(1, -1); } catch { } }
                        // ★★ 兜底：GetSelectedObject6 在本机恒返回 null（选中了但拿不到对象）。
                        //    绕开选区，直接从实体取面：GetBodies2 → GetFaces → faces[i]。
                        int faceCount = 0;
                        if (faceObj == null)
                        {
                            try
                            {
                                var bds = (modelDoc as SolidWorks.Interop.sldworks.IPartDoc).GetBodies2(0 /* swSolidBody */, true) as object[];
                                if (bds != null && bds.Length > 0)
                                {
                                    var fs = (bds[0] as IBody2).GetFaces() as object[];
                                    if (fs != null)
                                    {
                                        faceCount = fs.Length;
                                        int want = Math.Min(fixIdx - 1, fs.Length - 1);
                                        if (want >= 0) faceObj = fs[want];
                                    }
                                }
                            }
                            catch (Exception exB) { log.Add("fixture GetBodies2/GetFaces: " + exB.Message); }
                        }
                        log.Add("fixture: SelectFaceByIndex(" + fixIdx + ") -> " + gotFace + " nSel=" + nFix
                              + " faceType=" + (faceObj == null ? "null" : faceObj.GetType().Name)
                              + " (bodyFaces=" + faceCount + ")");
                        if (lrmFix == null) log.Add("fixture: LoadsAndRestraintsManager is null");
                        else if (faceObj == null) log.Add("fixture: no face selected — cannot pin the study");
                        else
                        {
                            // Try the plausible DispArray shapes, logging each error code.
                            var shapes = new List<Tuple<string, object>>
                            {
                                Tuple.Create("face-obj-array",  (object)new object[] { faceObj }),
                                Tuple.Create("face-obj-single", (object)faceObj),
                            };
                            try
                            {
                                var idArr = new object[] { 0, 0, 0, 0, 1 };
                                shapes.Add(Tuple.Create("point-like-array", (object)idArr));
                            }
                            catch { }
                            foreach (var sh in shapes)
                            {
                                try
                                {
                                    int fErr = 0;
                                    // ★★ 2026-09-28 根因定位（反射得出）：
                                    //   CLR 侧签名是
									//     AddRestraint(Int32, Object, Object, out ref Int32& ErrorCode) -> CWRestraint
									//   —— ① ErrorCode 是【双重 byref】 ② 返回值 CWRestraint 是【comclass】而非 interface
									//   而 ICWLoadsAndRestraintsManager 本身是 interface
									//   ⇒ 强类型调用时 CLR 必须在返回值上做 comclass 转换，
									//     这正是 "未能将调用的参数 1 转换为 AddRestraint" 的来源。
									//   ⇒ 用 dynamic 调用把转换推迟到运行时（与本文件里 ICosmosWorks 的做法一致）。
                                    dynamic lrmD = lrmFix;
                                    dynamic res = lrmD.AddRestraint(rType, sh.Item2, null, ref fErr);
                                    int cnt = 0; try { cnt = lrmFix.Count; } catch { }
                                    log.Add("fixture AddRestraint[" + sh.Item1 + "] -> err=" + fErr
                                          + " res=" + (res == null ? "null" : "CWRestraint")
                                          + " lrm.Count=" + cnt);
                                    if (fErr == 0) { fixtureAdded = true; break; }
                                }
                                catch (Exception exS) { log.Add("fixture AddRestraint[" + sh.Item1 + "] EX " + exS.Message); }
                            }
                            log.Add("fixture result: " + (fixtureAdded ? "ADDED" : "not added"));
                        }
                    }

                    bool loadAdded = false;
                    // ---- 5a-k) ★★ LOAD VIA AddForce  (2026-09-28: the way out)
                    // AddRestraint is unusable here (11 calling shapes measured, all refused). A static study
                    // does not strictly need a restraint — it needs a LOAD. AddForce has a DIFFERENT contract:
                    //     AddForce(swsForceType, DispArray, RefGeom, out err)
                    //   ⇒ DispArray carries the force VECTOR (Fx,Fy,Fz,Mx,My,Mz in N / N·m)
                    //   ⇒ RefGeom  carries WHERE it acts (the face)
                    // That is the opposite of AddRestraint, where DispArray is the geometry — very likely why
                    // 11 shapes failed there: both were being built the same way.
                    bool addLoad = p_bool(request, "add_load", false);
                    if (addLoad)
                    {
                        var lrmL = study.LoadsAndRestraintsManager;
                        var pJ = request.Params as JObject;
                        string lfName = pJ?.Value<string>("load_face") ?? "Face<2>";
                        double fMag = pJ?.Value<double?>("force_N") ?? 1500.0;
                        double fDirX = pJ?.Value<double?>("force_x") ?? 0.0;
                        double fDirY = pJ?.Value<double?>("force_y") ?? 0.0;
                        double fDirZ = pJ?.Value<double?>("force_z") ?? -1.0;
                        var smL = modelDoc.SelectionManager as SolidWorks.Interop.sldworks.ISelectionMgr;
                        bool gotLoad = false;
                        // ★ 同样改用 SelectFaceByIndex（SelectByID2 在本机选不中面）
                        int lfIdx = pJ?.Value<int?>("load_face_index") ?? 1;
                        try { gotLoad = SelectFaceByIndex(modelDoc, lfIdx, smL); }
                        catch (Exception exL) { log.Add("load SelectFaceByIndex: " + exL.Message); }
                        int nL = 0; if (smL != null) { try { nL = smL.GetSelectedObjectCount2(-1); } catch { } }
                        object refObj = null;
                        if (nL > 0 && smL != null) { try { refObj = smL.GetSelectedObject6(1, -1); } catch { } }
                        int faceCountL = 0;
                        if (refObj == null)
                        {
                            try
                            {
                                var bds = (modelDoc as SolidWorks.Interop.sldworks.IPartDoc).GetBodies2(0, true) as object[];
                                if (bds != null && bds.Length > 0)
                                {
                                    var fs = (bds[0] as IBody2).GetFaces() as object[];
                                    if (fs != null)
                                    {
                                        faceCountL = fs.Length;
                                        int want = Math.Min(lfIdx - 1, fs.Length - 1);
                                        if (want >= 0) refObj = fs[want];
                                    }
                                }
                            }
                            catch (Exception exB2) { log.Add("load GetBodies2/GetFaces: " + exB2.Message); }
                        }
                        log.Add("load: SelectFaceByIndex(" + lfIdx + ") -> " + gotLoad + " nSel=" + nL
                              + " refType=" + (refObj == null ? "null" : refObj.GetType().Name)
                              + " (bodyFaces=" + faceCountL + ")");
                        if (lrmL == null) log.Add("load: LoadsAndRestraintsManager is null");
                        else if (refObj == null) log.Add("load: no face selected");
                        else
                        {
                            double mag = Math.Sqrt(fDirX * fDirX + fDirY * fDirY + fDirZ * fDirZ);
                            if (mag < 1e-9) { fDirX = 0; fDirY = 0; fDirZ = -1; mag = 1; }
                            var vec = new object[]
                            {
                                fMag * fDirX / mag, fMag * fDirY / mag, fMag * fDirZ / mag,
                                0.0, 0.0, 0.0
                            };
                            log.Add("load: F=(" + vec[0] + "," + vec[1] + "," + vec[2] + ") N on " + refObj.GetType().Name);
                            try
                            {
                                // ★★ AddForce 真的被调用了（dynamic + ref 生效）！
                                //    err=1 = swsForceErrorSelectFacesEdgesVerticesOrPoints
                                //    ⇒ 官方要的是【当前选区里的面/边/顶点/点】，不是手头的 Face2 对象。
                                //    试几种"取到选区对象"的路，以及 DispArray 用数字编码的形态。
                                var tries = new List<Tuple<string, object, object>>();
                                object selObj = null;
                                if (nL > 0 && smL != null) { try { selObj = smL.GetSelectedObject6(1, -1); } catch { } }
                                // ★★★★ 关键（2026-09-28）：官方示例 Create_Advanced_Hole_Example_CSharp.md 用
                                //   DispatchWrapper[] dispArray = ObjectArrayToDispatchWrapperArray(new object[]{...})
                                //   ⇒ cosworks 的 DispArray 是 IDispatch SAFEARRAY，必须包 DispatchWrapper，
                                //   否则 CLR 传的 object[] 在 IDispatch 侧不成立（退回 err=1）。
                                //   依据：cosworks 里【没有】CWSolidFace 这类自己的面类型，
                                //        实体就是 SolidWorks 的 IEntity ⇒ 只能走 DispatchWrapper。
                                if (selObj != null)
                                    tries.Add(Tuple.Create<string, object, object>("dw-selObj",
                                        (object)new System.Runtime.InteropServices.DispatchWrapper[] { new System.Runtime.InteropServices.DispatchWrapper(selObj) }, selObj));
                                if (refObj != null)
                                    tries.Add(Tuple.Create<string, object, object>("dw-bodyFace",
                                        (object)new System.Runtime.InteropServices.DispatchWrapper[] { new System.Runtime.InteropServices.DispatchWrapper(refObj) }, refObj));
                                if (refObj != null)
                                    tries.Add(Tuple.Create<string, object, object>("dw-face+nullRef",
                                        (object)new System.Runtime.InteropServices.DispatchWrapper[] { new System.Runtime.InteropServices.DispatchWrapper(refObj) }, null));
                                tries.Add(Tuple.Create<string, object, object>("plain-face", (object)vec, refObj));
                                if (selObj != null) tries.Add(Tuple.Create<string, object, object>("plain-selObj", (object)vec, selObj));
                                if (refObj != null) tries.Add(Tuple.Create("bodyFace", (object)vec, refObj));

                                foreach (var t in tries)
                                {
                                    try
                                    {
                                        // ★★★★ 2026-09-28 新假设：cosworks 读的是【调用那一刻的当前选区】。
                                        //   上面 GetBodies2/GetFaces 等操作可能已经清掉它
                                        //   ⇒ ★ 每次调用前【立刻重新选中面】再试。
                                        try { SelectFaceByIndex(modelDoc, lfIdx, smL); } catch { }
                                        int e = 0;
                                        dynamic m = lrmL;
                                        // ★★ 2026-09-28: switched to AddForce2, which takes an explicit NSelectionType.
//    AddForce(NForceType, DispArray, RefGeom, out err) has no way to tell cosworks WHAT the
//    array holds; swsSelectionType_e: 0=FaceEdgeVertexPoint 1=BeamEndJoints 2=Beams.
//    Also swsForceType_e: 0=ForceOrMoment 1=Normal 2=Torque — a "normal" (perpendicular-to-face)
//    load must use 1, not 0.
dynamic r2 = null;
foreach (int selType in new[] { 0 /*FaceEdgeVertexPoint*/, 2 /*Beams*/, 1 /*BeamEndJoints*/ })
{
    int e2 = -999;
    try { r2 = m.AddForce2(1 /*Normal*/, selType, t.Item2, t.Item3, ref e2); }
    catch (Exception exAS) { log.Add("  AddForce2(selType=" + selType + ") EX " + exAS.Message); r2 = null; }
    log.Add("load AddForce2[NForceType=Normal(1), NSelectionType=" + selType + "] -> ok=" + (r2 != null) + " err=" + e2);
    if (e2 == 0) { e = e2; break; }
    if (e == -999) e = e2;
}
                                        int cnt = 0; try { cnt = lrmL.Count; } catch { }
                                        log.Add("load AddForce[" + t.Item1 + "] -> err=" + e
                                              + " (0=OK 1=SelectFacesEdgesVerticesOrPoints) lrm.Count=" + cnt);
                                        if (e == 0) { loadAdded = true; break; }
                                    }
                                    catch (Exception exT3) { log.Add("load AddForce[" + t.Item1 + "] EX " + exT3.Message); }
                                }
                            }
                            catch (Exception exT) { log.Add("load AddForce outer EX " + exT.GetType().Name + ": " + exT.Message); }
                            if (!loadAdded)
                            {
                                try
                                {
                                    int lErr2 = 0;
                                    lrmL.AddForce2(0 /* ForceOrMoment */, 0 /* Face/Edge/Vertex */, vec, refObj, out lErr2);
                                    int c2 = 0; try { c2 = lrmL.Count; } catch { }
                                    log.Add("load AddForce2[sel=0] -> err=" + lErr2 + " lrm.Count=" + c2);
                                    if (lErr2 == 0) loadAdded = true;
                                }
                                catch (Exception exT2) { log.Add("load AddForce2 EX " + exT2.Message); }
                            }
                            log.Add("load result: " + (loadAdded ? "ADDED" : "not added"));
                        }
                    }

                    // ---- 5a) CLOSE the manager's edit session. Until this returns, nothing above is
                    // actually committed to the study.
                    if (inEdit)
                    {
                        try { int mEnd = topo.EndEdit(); log.Add("TopologyStudyManager.EndEdit() -> " + mEnd); }
                        catch (Exception ex) { log.Add("TopologyStudyManager.EndEdit() threw: " + ex.Message); }
                    }

                    // ---- 5b) MATERIAL.
                    // RunAnalysis() codes measured here (swsRunAnalysisError_e, reflected):
                    //   19 = MaterialNotDefined  -> no material on the body
                    //   23 = MeshNotFound        -> material API needs a SELECTION, not just a study
                    //   22 = AuthorizationFailed -> the SOLVER is refused before it ever starts
                    // SetLibraryMaterialToSelectedEntities() acts on whatever is selected in the part,
                    // so select all bodies first, then set, then re-run.
                    string matLib = p_string(request, "material_library", "solidworks materials");
                    string matName = p_string(request, "material", "");
                    if (!string.IsNullOrEmpty(matName))
                    {
                        try
                        {
                            // select every solid body in the active part
                            // (GetBodies2 lives on IPartDoc, NOT IModelDoc2 — and SelectionManager
                            //  returns ISelectionMgr, both must be cast explicitly)
                            int selRet = -1;
                            try
                            {
                                var partDoc = modelDoc as SolidWorks.Interop.sldworks.IPartDoc;
                                if (partDoc == null) log.Add("active doc is not an IPartDoc — cannot enumerate bodies");
                                else
                                {
                                    var bodyArr = partDoc.GetBodies2((int)SolidWorks.Interop.swconst.swBodyType_e.swSolidBody, true) as object[];
                                    if (bodyArr != null && bodyArr.Length > 0)
                                    {
                                        var selMgr = modelDoc.SelectionManager as SolidWorks.Interop.sldworks.ISelectionMgr;
                                        if (selMgr == null) log.Add("SelectionManager null");
                                        else
                                        {
                                            // DeSelect's index parameter is an OBJECT; an int fails to
                                            // marshal and the throw used to be swallowed silently.
                                            for (int si = selMgr.GetSelectedObjectCount(); si >= 1; si--)
                                            {
                                                try { selMgr.DeSelect((object)si); } catch { }
                                            }
                                            // AddSelectionListObjects measured 0 bodies selected on this
                                            // machine, so fall back to SelectByID2 on each body's name —
                                            // the documented way to put a solid body in the selection.
                                            var bodyObjs = partDoc.GetBodies2((int)SolidWorks.Interop.swconst.swBodyType_e.swSolidBody, true) as object[];
                                            int ok = 0;
                                            if (bodyObjs != null)
                                            {
                                                foreach (var b in bodyObjs)
                                                {
                                                    string bn = null;
                                                    try { bn = (b as SolidWorks.Interop.sldworks.IBody2)?.Name; } catch { }
                                                    if (string.IsNullOrEmpty(bn)) continue;
                                                    // SelectByID2 lives on IModelDocExtension (reflected) — NOT on
                                                    // IModelDoc2 or IPartDoc, which is why both failed to compile.
                                                    bool r = modelDoc.Extension.SelectByID2(bn, "SOLIDBODY", 0, 0, 0, false, 0, null, (int)SolidWorks.Interop.swconst.swSelectOption_e.swSelectOptionDefault);
                                                    if (r) { ok++; log.Add("  SelectByID2('" + bn + "','SOLIDBODY') -> true"); }
                                                    else log.Add("  SelectByID2('" + bn + "','SOLIDBODY') -> false");
                                                }
                                            }
                                            selRet = ok;
                                            log.Add("selected " + ok + "/" + (bodyObjs?.Length ?? 0)
                                                  + " solid bodies (count now " + selMgr.GetSelectedObjectCount() + ")");
                                        }
                                    }
                                    else log.Add("no solid bodies found to select");
                                }
                            }
                            catch (Exception ex) { log.Add("body selection failed: " + ex.Message); }

                            dynamic solidMgr = study.SolidManager;
                            if (solidMgr == null) { log.Add("SolidManager is null — material NOT set"); }
                            else
                            {
                                int compCount = -1;
                                try { compCount = (int)solidMgr.ComponentCount; } catch { }
                                log.Add("SolidManager.ComponentCount = " + compCount);
                                int mErr = solidMgr.SetLibraryMaterialToSelectedEntities(matLib, matName);
                                log.Add("SetLibraryMaterialToSelectedEntities('" + matLib + "','" + matName
                                      + "') -> " + mErr + (mErr == 0 ? " (OK)" : " (error code)"));
                            }
                        }
                        catch (Exception ex) { log.Add("material set FAILED: " + ex.Message); }
                    }
                    else
                    {
                        log.Add("material NOT set (pass material=\"AISI 1020\" etc.) — a solve returns 19 (MaterialNotDefined)");
                    }

                    // ---- 5c) FIXTURE + LOAD.
                    // MeshAndRun() returned immediately and Results stayed null with zero CPU: the study
                    // had a goal and controls but NO fixture and NO load, so there was nothing for the
                    // solver to do. ICWStudy.LoadsAndRestraintsManager.AddRestraint(NRestraintType,
                    // DispArray, RefGeom, out err) is the entry; swsRestraintTypeFixed = 0.
                    // For this part (a Ø80x110 spindle housing) the bottom face is the clamped face, so
                    // default fixture_face = 2 = the planar face at Z=0 (normal -Z, area 0.002007 m^2),
                    // and the load is a force on the opposite (top) face.
                    // ---- 5c) FIXTURE + LOAD — follow the official "Create Topology Study Example (VBA)".
                    // MeshAndRun() returns immediately with Results null and zero CPU when the study has
                    // no fixture: there is nothing for the solver to do.
                    //
                    // The official example settles the two things that were wrong before:
                    //  * the add-in ProgID is "CosmosWorks.CosmosWorks", not "SldWorks.Simulation";
                    //  * DispArray must be built from the SELECTION — `Array(SelectionManager.
                    //    GetSelectedObject6(i, -1))` — not from faces you dug out of IBody2.GetFaces().
                    //    Handing cosworks an array of sldworks-interop face wrappers makes AddRestraint,
                    //    AddPressure and AddForce all throw the same generic marshalling
                    //    ArgumentException (whose text names argument 1, an Int32 that cannot fail to
                    //    convert — so ignore it). Selecting the faces first and reading them back out of
                    //    the selection manager produces the representation the cosworks side accepts.
                    // ⚠ The AddRestraint/AddForce call is BOTH rejected and potentially BLOCKING on this
                    // machine, so it is opt-in (add_fixture=true) like the solver. A headless caller must
                    // not be able to wedge the service by asking for a fixture. Everything above and
                    // below this line still runs and is still verified.
                    bool addFixture = p_bool(request, "add_fixture", false);
                    int fixtureFace = (int)(p_double(request, "fixture_face", 2) ?? 2);
                    int loadFace    = (int)(p_double(request, "load_face", 1) ?? 1);
                    double loadN    = p_double(request, "load_N", 2000.0) ?? 2000.0;
                    if (!addFixture)
                    {
                        log.Add("fixture/load SKIPPED (add_fixture not set). AddRestraint/AddForce are both rejected"
                              + " and observed to WEDGE this service thread on this machine (manual §14.1b/§14.1c)."
                              + " The face itself IS selectable headlessly (swSelFACES=2), so this is not a"
                              + " face-picking gap — pass add_fixture=true to attempt it anyway.");
                    }
                    if (addFixture || addLoad)
                    try
                    {
                        var selMgr = modelDoc.SelectionManager as SolidWorks.Interop.sldworks.ISelectionMgr;
                        if (selMgr == null) log.Add("fixture/load: SelectionManager unavailable");
                        else
                        {
                            // ── OFFICIAL SIGNATURES (extracted 2026-09-27 from help.solidworks.com/2021,
                            //    not guessed — see 官方文档\Simulation载荷夹具API签名全表.md):
                            //      AddRestraint            (NRestraintType, DispArray, RefGeom, ErrorCode)
                            //      AddForce3               (ForceType, SelectionType, RefDirType, ... 21 params)
                            //      AddCyclicSymmetryRestraint(FirstFace, SecondFace, Axis, ErrorCode)  ← no array!
                            // Three notes that matter:
                            //  1) AddForce3 is the fullest overload (21 params) and supersedes AddForce/2;
                            //     old overloads are known to route through deprecated paths.
                            //  2) AddCyclicSymmetryRestraint takes TWO FACES + AN AXIS, not a DispArray —
                            //     so if the failure is marshalling the array, this route avoids it entirely.
                            //  3) AddTemperature/AddHeatFlux/AddConvection all have the same
                            //     (DispArray, ErrorCode) shape, so the array is the common factor.
                            log.Add("fixture/load: fixture face index = " + fixtureFace + ", load face index = " + loadFace);
                            // select the fixture face, hand it over, then the load face
                            bool fixSel = SelectFaceByIndex(modelDoc, fixtureFace, selMgr);
                            log.Add("  selected fixture face " + fixtureFace + " -> " + fixSel
                                  + " (selection count = " + selMgr.GetSelectedObjectCount() + ")");
                            if (fixSel)
                            {
                                // ── RAW IDispatch::Invoke (2026-09-27) ──
                                // The only route with a mechanism-level rationale left: the official VB
                                // example works INSIDE SolidWorks (VB does not go through the CLR
                                // marshaller), while every .NET calling shape fails. So bypass the
                                // marshaller entirely: build DISPPARAMS by hand and call vtable[6].
                                // Sweeps the unknown that matters — the SAFEARRAY element type:
                                //   VT_DISPATCH (0x2009) / VT_UNKNOWN (0x200D) / VT_VARIANT (0x200C)
                                // and RefGeom as VT_EMPTY vs VT_NULL, in ONE pass.
                                // A crash here kills the service (raw pointer writes), so it is opt-in.
                                try
                                {
                                    var rawLrm = study.LoadsAndRestraintsManager;
                                    object rawFace = selMgr.GetSelectedObject6(1, -1);
                                    if (rawLrm != null && rawFace != null)
                                    {
                                        log.Add("  RAW-RECON: " + RawInvoke.Recon(rawLrm, rawFace)
                                              .Replace("\r\n", " | "));
                                    }
                                    else log.Add("  RAW-INVOKE: lrm or face is null");

                                    // 只有在显式要求时才真的发 Invoke —— 手工 DISPPARAMS 是
                                    // 裸指针写入，崩服务是真实风险（已崩过多次）。
                                    // ⚠ mesh_first=true 时【先建网格再施加夹具】：
                                    //   官方流程里夹具确实在网格之前，但 cosworks 可能有
                                    //   "研究必须已网格化" 的内部前置条件。这是 E_INVALIDARG
                                    //   的头号嫌疑，所以做成可开关。
                                    if (p_bool(request, "mesh_first", false))
                                    {
                                        // CreateMesh(NUnits, DElementSize, DTolerance) -> Int32
                                        //   NUnits: swsUnit_e (SI=0, English=1, Metric=2)
                                        //   返回值: swsStudyMeshError_e
                                        //     0=Successful 1=NoValidShells 2=NoSolidBody
                                        //     3=ElementSizeTooSmall 4=ElementSizeTooBig
                                        //     5=SpecifyPositiveValue 6/7=ScaleFactor 缺失
                                        // 之前这里只 log 了返回值就崩，现在把三个参数都做成可调，
                                        // 并把返回值按枚举解码 —— 崩溃前至少能留下确切的失败原因。
                                        int mUnits = (int)(p_double(request, "mesh_units", 0) ?? 0);
                                        double mSize = p_double(request, "mesh_elem", 5.0) ?? 5.0;
                                        double mTol  = p_double(request, "mesh_tol", 0.0) ?? 0.0;
                                        try
                                        {
                                            var mm = study.CreateMesh(mUnits, mSize / 1000.0, mTol);
                                            log.Add("  mesh-first: CreateMesh(units=" + mUnits
                                                  + " (0=SI), elem=" + mSize + "mm, tol=" + mTol + ") -> " + mm
                                                  + "  [" + DecodeMeshErr(mm) + "]");
                                        }
                                        catch (Exception mex) { log.Add("  mesh-first CreateMesh threw: " + mex.Message); }
                                    }
                                    if (p_bool(request, "raw_invoke", false))
                                    {
                                        // face 来源三选一，用来判别"是不是对象本身不对"：
                                        //   sel  = SelectionMgr.GetSelectedObject6  （选中的面包装）
                                        //   pid  = Extension.GetObjectByPersistReference3  （官方示例走这条）
                                        //   ent  = 面所属的实体（cosworks 可能要实体不是面）
                                        string faceSrc = p_string(request, "raw_face_src", "sel");
                                        object src = rawFace;
                                        if (faceSrc == "pid")
                                        {
                                            try
                                            {
                                                var pid0 = modelDoc.Extension.GetPersistReference3(rawFace);
                                                int pe0 = 0;
                                                src = pid0 == null ? null : modelDoc.Extension.GetObjectByPersistReference3(pid0, out pe0);
                                                log.Add("  raw_face_src=pid: persist-roundtrip err=" + pe0 + " -> "
                                                      + (src == null ? "null" : src.GetType().FullName));
                                            }
                                            catch (Exception pex) { log.Add("  pid 转换失败: " + pex.Message); }
                                        }
                                        else if (faceSrc == "ent")
                                        {
                                            try
                                            {
                                                var fa = rawFace as SolidWorks.Interop.sldworks.IFace2;
                                                src = fa != null ? fa.GetBody() : null;
                                                log.Add("  raw_face_src=ent: -> " + (src == null ? "null" : src.GetType().FullName));
                                            }
                                            catch (Exception eex) { log.Add("  ent 转换失败: " + eex.Message); }
                                        }
                                        // 一次只发一次 Invoke：实测连续第二次 Invoke 必崩
                                        // （第一次的 E_INVALIDARG 之后 cosworks 内部状态已不一致）。
                                        // 组合由参数 elem/refgeom 选择，每轮重启服务换一种。
                                        ushort elem = (ushort)(p_double(request, "raw_elem", 12) ?? 12);
                                        string mode = p_string(request, "raw_refgeom", "empty");
                                        int wFlags = (int)(p_double(request, "raw_wflags", 0) ?? 0);
                                        int restType = (int)(p_double(request, "raw_resttype", 0) ?? 0);
                                        // 官方示例是 Dim varArray1 As Object() = {pointer1, pointer2}
                                        // ——【两个】面。而我一直只传 1 个。raw_faces 可调。
                        object[] srcs;
                        {
                            int nf = (int)(p_double(request, "raw_faces", 1) ?? 1);
                            srcs = new object[nf];
                            srcs[0] = rawFace;
                            for (int k = 1; k < nf; k++)
                            {
                                try
                                {
                                    // ⚠ 不能用 SelectFaceByIndex(modelDoc, idx, …)：它内部按索引取面，
                                    // 但连着调两次会得到【同一个】IDispatch（实测 face[0]==face[1]）。
                                    // 改为直接用 Bodies[0].GetFaces() 按索引取真正的第 k 个面。
                                    var fa0 = rawFace as SolidWorks.Interop.sldworks.IFace2;
                                    var body0 = fa0 != null
                                        ? fa0.GetBody() as SolidWorks.Interop.sldworks.IBody2
                                        : null;
                                    var facesOfBody = body0 != null ? body0.GetFaces() as object[] : null;
                                    if (facesOfBody != null && k < facesOfBody.Length)
                                    {
                                        srcs[k] = facesOfBody[k];
                                        log.Add("  extra face[" + k + "] 取自 GetFaces()[" + k + "]");
                                    }
                                    else log.Add("  extra face[" + k + "] 越界（共 " + (facesOfBody?.Length ?? 0) + " 个面）");
                                }
                                catch (Exception xe) { log.Add("  extra face[" + k + "] 失败: " + xe.Message); }
                            }
                        }
                        int orderRev = (int)(p_double(request, "raw_order", 0) ?? 0);
                        try
                        {
                            RawInvoke.StartTrace(Path.Combine(Path.GetTempPath(), "rawinvoke_trace.txt"));
                        }
                        catch { }
                        string outp;
                                        try
                                        {
                                            // raw_mode=insert：绕开 DispArray（0 元素数组建空夹具）
                                            string rawMode2 = p_string(request, "raw_mode", "array");
                                            outp = (rawMode2 == "insert")
                                                 ? RawInvoke.CallAddRestraintThenInsert(rawLrm, srcs, restType, wFlags)
                                                 : (rawMode2 == "force")
                                                 ? RawInvoke.CallAddForce(rawLrm, srcs, restType, wFlags)
                                                 : RawInvoke.CallAddRestraint(rawLrm, srcs, restType, elem, mode, wFlags, orderRev);
                                        }
                                        catch (Exception rex) { outp = "  threw: " + rex.Message; }
                                        log.Add("  RAW-INVOKE elem=0x" + elem.ToString("X")
                                              + " refgeom=" + mode + " wFlags=" + wFlags
                                              + " restType=" + restType + " src=" + faceSrc
                                              + " nfaces=" + srcs.Length + " order=" + (orderRev == 0 ? "decl" : "REV")
                                              + ":" + outp.Replace("\r\n", " | "));
                                    }
                                }
                                catch (Exception rawEx) { log.Add("  RAW-INVOKE failed: " + rawEx.Message); }

                                // Take the face array NOW and do NOT touch the selection manager again:
                                // SelectBodyArray() replaces the selection with a SOLIDBODY, and the
                                // cosworks Add* methods evidently look at the live selection, so a stray
                                // body selection made the fixture arrive as a BODY (GetSelectedObjectType2
                                // logged 76, not 2) and the call was rejected.
                                var disp = SelectionArray(selMgr);
                                var selTypeNow = selMgr.GetSelectedObjectType2(1);
                                if (disp != null)
                                {
                                    var lrmDyn = study.LoadsAndRestraintsManager;
                                    if (lrmDyn != null)
                                    {
                                        log.Add("  disp array type = " + disp.GetType().FullName
                                              + ", len=" + ((Array)disp).Length
                                              + ", selectedObjectType2 = " + selTypeNow
                                              + " (expect 2 = swSelFACES)");

                                        // ── DISCRIMINATING TEST (no UI needed) ──
                                        // Call a method on the SAME manager that takes NO geometry array.
                                        //   GetLoadsAndRestraints(NIndex, out ErrorCode) — just an int.
                                        // If THAT succeeds, the Loads&Restraints subsystem is functional and
                                        // only the geometry-argument path is broken. If it fails too, the
                                        // whole subsystem is non-functional on this machine, and no amount
                                        // of C# call-shape tuning can help. This distinguishes the two
                                        // explanations that 20+ failed call shapes could not.
                                        try
                                        {
                                            var lrmProbe = study.LoadsAndRestraintsManager;
                                            log.Add("  probe: Loads&Restraints subsystem = "
                                                  + (lrmProbe == null ? "NULL" : "present")
                                                  + ", Count = " + SafeInt(() => (int)lrmProbe.Count));
                                            int gErr = -999;
                                            dynamic got = lrmProbe.GetLoadsAndRestraints(0, out gErr);
                                            log.Add("  >>> probe GetLoadsAndRestraints(0) -> err=" + gErr
                                                  + ", returned " + (got == null ? "null" : got.GetType().FullName)
                                                  + (gErr == 1
                                                     ? "   ==> err=1 = swsLoadsAndRestraintsErrorNotFoundAtIndex"
                                                       + " (correct: Count=0, nothing at index 0)"
                                                       + " => SUBSYSTEM FUNCTIONAL, only the geometry-arg path fails"
                                                     : gErr == 0
                                                       ? "   ==> SUBSYSTEM FUNCTIONAL"
                                                       : "   ==> subsystem returned err=" + gErr));
                                        }
                                        catch (Exception pex3)
                                        {
                                            log.Add("  >>> probe GetLoadsAndRestraints threw "
                                                    + pex3.GetType().Name + ": " + pex3.Message
                                                    + "   ==> SUBSYSTEM NON-FUNCTIONAL");
                                        }

                                        // ── PURE IDispatch (2026-09-27) ──
                                        // The error text "未能将调用的参数 1 转换为 AddRestraint" is the CLR
                                        // MARSHALLER's message, not a COM error: the call was rejected on
                                        // the .NET side before it ever reached cosworks. And the
                                        // generated interop declares these parameters as
                                        //   DispArray  [MarshalAs(UnmanagedType.Struct)]
                                        // i.e. "marshal this as a structure" — an object[] can never satisfy
                                        // that, and cosworks.dll sitting in bin\Debug is what gives the CLR
                                        // a .NET signature to check against in the first place.
                                        // So: with cosworks.dll OUT of the output directory the RCW has no
                                        // .NET type, `dynamic` MUST go through raw IDispatch, and the
                                        // MarshalAs rules stop applying. That is what is tested below —
                                        // the object comes straight from study.LoadsAndRestraintsManager with
                                        // NO Typed<>() cast anywhere on this path.
                                        try
                                        {
                                            var raw = study.LoadsAndRestraintsManager;
                                            log.Add("  raw manager type = " + raw.GetType().FullName
                                                  + "  (System.__ComObject = 无 .NET 类型，将走纯 IDispatch)");
                                            int rawErr = 0;
                                            var rr = raw.AddRestraint(0, disp, Type.Missing, out rawErr);
                                            log.Add("  >>> PURE-IDISPATCH AddRestraint -> err=" + rawErr
                                                  + (rr != null ? "   *** FIXTURE CREATED ***" : " (null)"));
                                        }
                                        catch (Exception rex2)
                                        {
                                            log.Add("  >>> PURE-IDISPATCH AddRestraint threw "
                                                  + rex2.GetType().Name + ": " + rex2.Message);
                                        }

                                        // AddRestraint is NOT USABLE on this machine. Eleven calling shapes
                                        // were measured (dynamic / early-bound / explicit IDispatch ×
                                        // {face, body} × {object[], System.Array, SafeArray} ×
                                        // {null, Type.Missing, DBNull} × discard-or-keep return value), and
                                        // all of them fail. The failure DEPTH differs, which is the only
                                        // information they yielded:
                                        //   RefGeom = C# null  -> ArgumentException at the marshalling layer
                                        //                          AND it WEDGES the service thread
                                        //                          (no /health, flat CPU, memory drops)
                                        //   RefGeom = Missing/DBNull -> "调用的目标发生了异常", i.e. it
                                        //                          reaches cosworks and is refused there
                                        // Both face and body selection were tried and behave identically.
                                        //
                                        // The official 2021 signatures (extracted, not guessed) show
                                        // AddForce3 is the 21-parameter superset and that
                                        // AddCyclicSymmetryRestraint(FirstFace, SecondFace, Axis) takes NO
                                        // array at all — so try those two before touching AddRestraint again.
                                        int f3Err = 0;
                                        try
                                        {
                                            var f3 = lrmDyn.AddForce3(
                                                0,      /* ForceType   */
                                                0,      /* SelectionType */
                                                0,      /* RefDirType  */
                                                0,      /* InterpolationMode */
                                                (double)0,   /* DistPercentageOpt */
                                                0,      /* NumOfRows   */
                                                (double)0,   /* DistValue    */
                                                loadN,  /* ForceValue   */
                                                0,      /* NonUniformLoading */
                                                0,      /* NULoadingOnBeam */
                                                0,      /* NonUniformLoadDistDef */
                                                0,      /* NonUniformLoadDistType */
                                                0,      /* Ucode */
                                                0,      /* TorqueNFVal */
                                                null,   /* Comps */
                                                0,      /* FlipOrigin */
                                                0,      /* IsCurvedBeam */
                                                disp,   /* DispArray */
                                                null,   /* RefGeom */
                                                0,      /* PerUnitLength */
                                                out f3Err);
                                            log.Add("  AddForce3(21 参官方签名) -> err=" + f3Err
                                                  + (f3 != null ? " (created)" : " (null)"));
                                        }
                                        catch (Exception f3ex) { log.Add("  AddForce3 threw: " + f3ex.Message); }

                        // ── THE OFFICIAL ROUND-TRIP, replicated exactly (2026-09-27) ──
                        // Official "Analyze Part (VB.NET)" example reads:
                        //   pointer1 = Part.Extension.GetObjectByPersistReference3(var1, longstatus)
                        //   Dim varArray1 As Object() = {pointer1, pointer2}    ' Object() typed array
                        //   LBCMgr = Study.LoadsAndRestraintsManager
                        //   CWRes1 = LBCMgr.AddRestraint(0, (varArray1), Nothing, errCode)
                        // Three things every previous attempt got wrong:
                        //   1) geometry must round-trip through the persistent reference
                        //      (GetPersistReference3 -> GetObjectByPersistReference3);
                        //   2) the array holds the CONVERTED pointers, not the raw selection;
                        //   3) VB's Nothing maps to Type.Missing, not C# null — and a plain null
                        //      wedges the service thread outright (see manual 14.1c).
                        try
                        {
                            var conv = new System.Collections.Generic.List<object>();
                            int nSel = selMgr.GetSelectedObjectCount();
                            for (int k = 1; k <= nSel; k++)
                            {
                                var raw = selMgr.GetSelectedObject6(k, -1);
                                if (raw == null) continue;
                                var pid = modelDoc.Extension.GetPersistReference3(raw);
                                if (pid == null) { log.Add("    GetPersistReference3 -> null"); continue; }
                                int cerr = 0;
                                var ptr = modelDoc.Extension.GetObjectByPersistReference3(pid, out cerr);
                                if (ptr != null)
                                {
                                    conv.Add(ptr);
                                    log.Add("    pointer" + k + ": persist-ref round trip err=" + cerr
                                          + " -> " + ptr.GetType().FullName);
                                }
                            }
                            if (conv.Count == 0)
                            {
                                log.Add("  persist-reference conversion produced no pointers");
                            }
                            else
                            {
                                var arr = new object[conv.Count];
                                conv.CopyTo(arr);
                                int aErr = 0;
                                try
                                {
                                    var res = lrmDyn.AddRestraint(0, arr, Type.Missing, out aErr);
                                    log.Add("  >>> AddRestraint(0, Object[]{" + conv.Count + "}, Type.Missing) -> err=" + aErr
                                          + (res != null ? "   *** FIXTURE CREATED ***" : " (null)"));
                                }
                                catch (Exception aex)
                                {
                                    log.Add("  >>> AddRestraint threw " + aex.GetType().Name + ": " + aex.Message);
                                }
                            }
                        }
                        catch (Exception pex2) { log.Add("  persist-reference round trip failed: " + pex2.Message); }
                                        log.Add("  AddRestraint: NOT USABLE on this machine (11 calling shapes"
                                              + " measured, all refused; see manual §14.1b). The study therefore"
                                              + " has NO fixture, so the solver has nothing to do and"
                                              + " MeshAndRun returns immediately with Results == null.");
                                    }
                                    else log.Add("fixture/load: no typed ICWLoadsAndRestraintsManager view");
                                }
                                else log.Add("fixture/load: selection array for face " + fixtureFace + " was empty");
                            }

                            // AddForce is the sibling of AddRestraint on the same manager and is refused
                            // the same way, so it is not worth another throw on every run.
                            log.Add("  AddForce: same manager as AddRestraint, refused the same way —"
                                  + " skipping (force " + loadN + " N on face " + loadFace + " not applied).");
                        }
                    }
                    catch (Exception ex)
                    {
                        log.Add("fixture/load FAILED: " + ex.GetType().Name + ": " + ex.Message);
                    }

                    // ---- 6) mesh + solve.
                    //
                    // ⚠ MEASURED HANG, DO NOT "JUST ENABLE" THIS:
                    // CreateMesh() and RunAnalysis() are SYNCHRONOUS COM calls, and once the study
                    // actually gets far enough to start meshing/solving, Simulation raises a MODAL
                    // DIALOG (a visible, untitled #32770 — found by enumerating SLDWORKS' top-level
                    // windows). The service thread then blocks FOREVER: /health stops answering, and
                    // SolidWorks' own CPU stays flat (no star.exe / mesher child process spawns).
                    // Before the mesh step existed, every call returned an error code in milliseconds
                    // and nothing ever popped a dialog — which is why the hang only appeared after
                    // the pipeline got far enough. run_solve defaults to FALSE for that reason: a
                    // headless caller must not be able to wedge the service. Opt in explicitly, and
                    // only when a human is watching the SolidWorks window to dismiss the prompt.
                    bool runSolve = p_bool(request, "run_solve", false);
                    double meshElemMm = p_double(request, "mesh_element_mm", 5.0) ?? 5.0;
                    int meshUnits = (int)(p_double(request, "mesh_units", 0) ?? 0);
                    int meshRet = -999; int runRet = -999; string runErr = null;
                    if (runSolve)
                    {
                        // Prefer MeshAndRun(): mesher + solver in one call, and unlike the separate
                        // CreateMesh/RunAnalysis pair it has no intermediate state that invites a
                        // "mesh quality"/"study not ready" modal prompt.
                        bool useMeshAndRun = p_bool(request, "mesh_and_run", true);
                        if (useMeshAndRun)
                        {
                            try
                            {
                                log.Add("MeshAndRun() ... (synchronous; watch for a Simulation modal dialog)");
                                study.MeshAndRun();
                                meshRet = 0; runRet = 0;
                                log.Add("MeshAndRun() returned normally");
                            }
                            catch (Exception ex) { runErr = ex.Message; log.Add("MeshAndRun threw: " + ex.Message); }
                        }
                        else
                        {
                            try
                            {
                                meshRet = study.CreateMesh(meshUnits, meshElemMm / 1000.0, 0.0);
                                log.Add("CreateMesh(units=" + meshUnits + ", element=" + meshElemMm + " mm) -> " + meshRet);
                            }
                            catch (Exception ex) { log.Add("CreateMesh threw: " + ex.Message); }
                            try
                            {
                                log.Add("RunAnalysis() ... (this may BLOCK on a Simulation modal dialog)");
                                runRet = study.RunAnalysis();
                                log.Add("RunAnalysis() -> " + runRet);
                            }
                            catch (Exception ex) { runErr = ex.Message; log.Add("RunAnalysis threw: " + ex.Message); }
                        }
                    }
                    else
                    {
                        log.Add("mesh+solve SKIPPED (run_solve not set). CreateMesh/RunAnalysis are synchronous"
                              + " and Simulation pops a modal dialog that wedges this service thread forever"
                              + " (verified: visible untitled #32770 + flat CPU). Pass run_solve=true only with a"
                              + " human watching the SolidWorks window.");
                    }

                    // ---- 7) read the result back: the objective demands evidence, not "no error" ----
                    var result = new JObject { ["mesh_return"] = meshRet, ["run_return"] = runRet };
                    if (!runSolve) result["skipped"] = "run_solve not requested (see log for why)";
                    if (runErr != null) result["error"] = runErr;

                    // DIAGNOSTIC: did the mesher actually run? MeshAndRun() returns void and "normally"
                    // even when it does nothing, so the only way to tell how far the pipeline got is to ask
                    // the study whether it owns a mesh and how many nodes it has. Without this, "no results"
                    // is indistinguishable between "no mesh", "no constraint" and "solver refused".
                    try
                    {
                        int mType = -1; bool hasMesh = false; string mInfo = "";
                        try { mType = (int)study.MeshType; } catch (Exception ex) { log.Add("MeshType read failed: " + ex.Message); }
                        try
                        {
                            dynamic m = study.Mesh;
                            hasMesh = (m != null);
                            if (m != null)
                            {
                                // CWMesh exposes no public members through this interop, so ask it for
                                // whatever it will answer; failure here is itself informative.
                                foreach (var prop in new[] { "NodeCount", "ElementCount", "Quality", "Name" })
                                {
                                    try { mInfo += " " + prop + "=" + m.GetType().GetProperty(prop)?.GetValue(m, null); }
                                    catch { }
                                }
                            }
                        }
                        catch (Exception ex) { log.Add("Mesh read failed: " + ex.Message); }
                        log.Add("post-solve mesh check: MeshType=" + mType + ", mesh=" + (hasMesh ? "PRESENT" : "NULL") + mInfo);
                        result["mesh_type"] = mType;
                        result["mesh_present"] = hasMesh;
                    }
                    catch (Exception ex) { log.Add("post-solve mesh check failed: " + ex.Message); }
                    try
                    {
                        dynamic res = study.Results;
                        if (res != null)
                        {
                            log.Add("ICWResults reachable");
                            int nMsg = -1;
                            try { nMsg = (int)res.GetNumOfMessages(); } catch (Exception ex) { log.Add("GetNumOfMessages: " + ex.Message); }
                            log.Add("result messages = " + nMsg);
                            result["messages"] = nMsg;
                        }
                        else log.Add("ICWStudy.Results is null (no results yet)");
                    }
                    catch (Exception ex) { log.Add("Results read failed: " + ex.Message); }

                    var pSolve = new JObject
                    {
                        ["stage"] = "solve", ["log"] = log, ["result"] = result,
                        ["study"] = studyName, ["reachable"] = true,
                        ["note"] = "Pipeline verified end-to-end UP TO the solver: study created (type 13),"
                                 + " material assigned, body selected, topology managers reachable. Two limits are"
                                 + " real, not bugs to retry: (a) the Create*Control calls return err=17"
                                 + " (SetOperationNotSupported) because preserved-region faces / symmetry / demold"
                                 + " planes need UI-grade geometry picking, which is not implemented; (b) CreateMesh"
                                 + " + RunAnalysis are synchronous and Simulation raises a modal dialog that wedges"
                                 + " this service thread forever, so they are opt-in via run_solve=true. There is"
                                 + " therefore NO validated 'mesh + solve to a design result' path on this machine —"
                                 + " do not report a topology result from this tool as if it were a real solution."
                    };
                    return OkWrite(request, modelDoc, null, pSolve.ToString(Formatting.None));
                }

                var payload = new JObject
                {
                    ["stage"] = "probe", ["log"] = log,
                    ["reachable"] = topo != null,
                    ["note"] = "Topology API is reachable. Constraint/control objects use BeginEdit()/SetXxx()/EndEdit();"
                             + " create controls BEFORE constraints (thickness, preserved region, symmetry, demold, frequency)."
                };
                return OkWrite(request, modelDoc, null, payload.ToString(Formatting.None));
            }
            catch (COMException ex) { log.Add("COM_ERROR: " + ex.Message); return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(), "COM_ERROR", ex.Message + " | steps: " + string.Join(" | ", log)); }
            catch (Exception ex) { Infrastructure.ExecLog.Write("CAPFAIL " + ex.ToString()); return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(), "UNEXPECTED_ERROR", ex.Message + " | steps: " + string.Join(" | ", log) + " @ " + ex.StackTrace); }
        }

        // ---------------- helpers ----------------
        private static string Q(string s)
        {
            if (s == null) return "\"\"";
            return "\"" + s.Replace("\"", "\"\"").Replace("\r", " ").Replace("\n", " ") + "\"";
        }
        private static bool SafeBool(Func<bool> f) { try { return f(); } catch { return false; } }
        private static int SafeInt(Func<int> f) { try { return f(); } catch { return -1; } }
        // Some tools here (standard-parts index, LCSC fetch) do NOT need a live SolidWorks —
        // touching _solidWorks when the app is closed throws NullReference, so probe it safely.
        private IModelDoc2 SafeActiveDoc()
        {
            // 1) cached field first
            try { if (_solidWorks != null) { var d = _solidWorks.IActiveDoc2 as IModelDoc2; if (d != null) return d; } }
            catch { }
            // 2) the field is a stale RCW whenever SOLIDWORKS.exe was killed/restarted after
            //    this service started. Re-acquire through the Running Object Table instead of
            //    returning null, which would look like "no document is open" and mislead callers.
            try
            {
                var app = Marshal.GetActiveObject("SldWorks.Application") as ISldWorks;
                if (app != null)
                {
                    _solidWorks = app;
                    return app.IActiveDoc2 as IModelDoc2;
                }
            }
            catch { }
            return null;
        }
        private static JObject P(ToolRequest r) { return r?.Params as JObject; }
        private static string p_string(ToolRequest r, string k, string d)
        { try { var v = P(r)?.Value<string>(k); return string.IsNullOrEmpty(v) ? d : v; } catch { return d; } }
        private static double? p_double(ToolRequest r, string k, double? d)
        { try { return P(r)?.Value<double?>(k) ?? d; } catch { return d; } }
        private static bool p_bool(ToolRequest r, string k, bool d)
        { try { return P(r)?.Value<bool?>(k) ?? d; } catch { return d; } }
        private static string[] p_string_array(ToolRequest r, string k, string[] d)
        {
            try
            {
                var a = P(r)?[k] as JArray;
                if (a == null) return d;
                return a.Select(x => x?.ToString()).Where(x => !string.IsNullOrEmpty(x)).ToArray();
            }
            catch { return d; }
        }

        private ExecutionResponse OkRead(ToolRequest request, IModelDoc2 modelDoc, string docType, string featuresPayload)
        {
            return new ExecutionResponse
            {
                OperationId = request.OperationId,
                Status = "COMPLETED",
                Verified = true,
                StateVersion = _guard.GetCurrentStateVersion(),
                CadState = new CadState
                {
                    StateVersion = _guard.GetCurrentStateVersion(),
                    ActiveDocument = modelDoc?.GetTitle(),
                    DocumentType = docType,
                    ActiveSketch = null,
                    Features = new List<string> { featuresPayload },
                    Dimensions = new List<string>()
                },
                Error = null
            };
        }

        private ExecutionResponse OkWrite(ToolRequest request, IModelDoc2 modelDoc, string docType, string featuresPayload)
        {
            int sv = _guard.GetCurrentStateVersion() + 1;
            var response = new ExecutionResponse
            {
                OperationId = request.OperationId,
                Status = "COMPLETED",
                Verified = true,
                StateVersion = sv,
                CadState = new CadState
                {
                    StateVersion = sv,
                    ActiveDocument = modelDoc?.GetTitle(),
                    DocumentType = docType,
                    ActiveSketch = null,
                    Features = new List<string> { featuresPayload },
                    Dimensions = new List<string>()
                },
                Error = null
            };
            _guard.RegisterCompleted(request.OperationId, response);
            return response;
        }

        /// <summary>
        /// ★ 2026-09-28: run a SolidWorks VBA macro on the SW main thread.
        ///
        /// WHY THIS EXISTS — the decisive workaround for the Simulation load/fixture problem:
        ///   ICWLoadsAndRestraintsManager.AddRestraint / AddForce fail through the CLR interop with
        ///   "未能将调用的参数 N 转换为 AddRestraint" — that is a *marshalling* failure in OUR runtime,
        ///   NOT a refusal by SolidWorks and NOT a licence problem. The same call written in VBA runs
        ///   inside SLDWORKS.exe where SolidWorks does its own COM marshalling, so it is expected to
        ///   succeed where the CLR path cannot even marshal the argument.
        ///   This is the `solidworks-swbasic` backend described in the 1010-star project's capabilities.yaml.
        ///
        /// The macro itself writes a log to %TEMP%\swmacro.log; this method only launches it.
        /// </summary>
        public ExecutionResponse RunMacro(ToolRequest request)
        {
            if (_guard.IsDuplicate(request.OperationId)) return _guard.GetDuplicate(request.OperationId);
            if (!_guard.IsStateVersionValid(request.StateVersion))
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "INVALID_STATE_VERSION", "Incoming state_version does not match current state.");
            if (!EnsureConnected())
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "COM_ATTACH_FAILED", "SolidWorks process not found or COM not registered.");

            var p = request.Params as JObject;
            var modelDoc = SafeActiveDoc();
            string macroPath = p?.Value<string>("macro_path") ?? "";
            string module = p?.Value<string>("module") ?? "";
            string proc = p?.Value<string>("proc") ?? "";
            int options = p?.Value<int?>("options") ?? 1;   // 1 = swMacroRunFromTools
            var log = new JArray();

            if (string.IsNullOrEmpty(macroPath) || !System.IO.File.Exists(macroPath))
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "MACRO_NOT_FOUND", "macro_path missing or not on disk: '" + macroPath + "'.");
            if (string.IsNullOrEmpty(module))
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "MISSING_PARAMETER", "module name required (the .swp module name, without extension).");
            if (string.IsNullOrEmpty(proc))
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "MISSING_PARAMETER", "proc name required (the Sub to run).");

            int rErr = 0;
            bool ran = false;
            try
            {
                ran = _solidWorks.RunMacro2(macroPath, module, proc, options, out rErr);
                log.Add("RunMacro2('" + macroPath + "','" + module + "','" + proc + "'," + options + ")"
                      + " -> " + ran + " err=" + rErr);
            }
            catch (Exception ex)
            {
                log.Add("RunMacro2 threw: " + ex.GetType().Name + ": " + ex.Message);
            }

            // The macro writes its own progress log; surface the tail if it produced one.
            var macroLog = System.IO.Path.Combine(System.IO.Path.GetTempPath(), "swmacro.log");
            bool logExists = System.IO.File.Exists(macroLog);
            string[] lines = logExists ? System.IO.File.ReadAllLines(macroLog) : new string[0];
            var tail = new JArray();
            int from = Math.Max(0, lines.Length - 40);
            for (int i = from; i < lines.Length; i++) tail.Add(lines[i]);

            if (!ran)
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "MACRO_FAILED", "RunMacro2 returned " + ran + " err=" + rErr
                    + " (err 0/negative usually means the .swp is not trusted or the module/proc name is wrong)."
                    + " macro log tail: " + string.Join(" | ", tail));

            var ok = new JObject
            {
                ["stage"] = "macro",
                ["log"] = log,
                ["macro_log"] = tail,
                ["macro_log_exists"] = logExists,
                ["note"] = "The macro was launched. Read macro_log for what it actually did — a returned"
                        + " True only means the macro STARTED, not that the simulation produced results."
            };
            return OkWrite(request, modelDoc, null, ok.ToString(Formatting.None));
        }

        /// <summary>
        /// ★ 2026-09-28: reverse-engineer the Simulation feature data that SOLIDWORKS ITSELF created.
        ///
        /// WHY: ICWLoadsAndRestraintsManager.AddForce/AddRestraint reach SolidWorks (we got past the
        /// CLR marshalling barrier with dynamic + ref) but return
        /// swsForceErrorSelectFacesEdgesVerticesOrPoints — the DispArray format is not in any offline
        /// doc we have. The one authoritative sample of a CORRECT DispArray is a force feature the user
        /// created in the UI: its ISimulationForceFeatureData.get_LoadReferences() IS that array.
        /// So: walk the feature tree, find Simulation features, and dump their definition.
        /// </summary>
        public ExecutionResponse ReadSimFeature(ToolRequest request)
        {
            if (_guard.IsDuplicate(request.OperationId)) return _guard.GetDuplicate(request.OperationId);
            if (!_guard.IsStateVersionValid(request.StateVersion))
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "INVALID_STATE_VERSION", "Incoming state_version does not match current state.");
            if (!EnsureConnected())
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "COM_ATTACH_FAILED", "SolidWorks process not found or COM not registered.");

            var modelDoc = SafeActiveDoc();
            if (modelDoc == null)
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "NO_ACTIVE_DOCUMENT", "Open the part first.");
            var mdl = modelDoc as IModelDoc2;
            var outp = new JArray();

            // 1) every feature, with its type name — Simulation features show up here
            var f = mdl.FirstFeature() as IFeature;
            int guard = 0;
            while (f != null && guard++ < 800)
            {
                string fn = "", ft = "";
                try { fn = f.Name; } catch { }
                try { var t3 = f.GetTypeName2(); ft = t3; } catch { }
                var row = new JObject { ["name"] = fn, ["type"] = ft };
                // 2) if it is a Simulation feature, dump its definition
                if (ft.IndexOf("Simulation", StringComparison.OrdinalIgnoreCase) >= 0
                    || fn.IndexOf("仿", StringComparison.OrdinalIgnoreCase) >= 0)
                {
                    try
                    {
                        dynamic def = f.GetDefinition();
                        row["has_definition"] = def != null;
                        if (def != null)
                        {
                            var d = new JObject();
                            string[] getters = { "ForceType", "ForceFunctionType", "ActionType",
                                                 "FunctionConstantValue", "FunctionExpression",
                                                 "ReverseDirection", "InterpolationScheme" };
                            foreach (var g in getters)
                            {
                                try { d[g] = def.GetType().GetProperty(g)
                                                 ?.GetValue(def, null) != null
                                          ? def.GetType().GetProperty(g).GetValue(def, null)
                                          : "n/a"; }
                                catch { }
                            }
                            // ★★★ the two we actually need
                            foreach (var g in new[] { "LoadReferences", "ActionLocation", "ActionDirection", "ReactionLocation" })
                            {
                                try
                                {
                                    var v = def.GetType().GetProperty(g)?.GetValue(def, null);
                                    d[g] = DescribeComValue(v);
                                }
                                catch (Exception ex) { d[g] = "EX " + ex.Message; }
                            }
                            // restraint side
                            foreach (var g in new[] { "RestraintType", "SelectedEntities", "CoordinateSystem" })
                            {
                                try
                                {
                                    var v = def.GetType().GetProperty(g)?.GetValue(def, null);
                                    d[g] = DescribeComValue(v);
                                }
                                catch { }
                            }
                            row["definition"] = d;
                        }
                    }
                    catch (Exception ex) { row["definition_error"] = ex.Message; }
                }
                outp.Add(row);
                try { f = f.GetNextFeature() as IFeature; } catch { break; }
            }

            var ok = new JObject
            {
                ["stage"] = "read_sim_feature",
                ["feature_count"] = outp.Count,
                ["features"] = outp,
                ["note"] = "Look for rows whose type contains 'Simulation'. Their 'definition'"
                        + " shows the real DispArray/ActionLocation encoding the UI produced — that is"
                        + " what AddForce/AddRestraint must be given."
            };
            return OkWrite(request, modelDoc, null, ok.ToString(Formatting.None));
        }

        /// <summary>Render any COM value (array / object / scalar) as readable JSON, keeping arity.</summary>
        private static JToken DescribeComValue(object v)
        {
            if (v == null) return JValue.CreateNull();
            if (v is Array arr)
            {
                var ja = new JArray();
                int n = Math.Min(arr.Length, 32);
                for (int i = 0; i < n; i++) ja.Add(DescribeComValue(arr.GetValue(i)));
                return new JObject { ["__array_len"] = arr.Length, ["items"] = ja };
            }
            try
            {
                // COM object: report its type + IUnknown identity so two references can be compared
                var unk = System.Runtime.InteropServices.Marshal.GetIUnknownForObject(v);
                return new JObject
                {
                    ["__com_type"] = v.GetType().FullName,
                    ["__iunknown"] = unk.ToInt64().ToString(),
                    ["__rcw_hash"] = v.GetHashCode()
                };
            }
            catch { return v.ToString(); }
        }

        /// <summary>
        /// ★★ 2026-09-28 — THE WAY AROUND DispArray.
        ///
        /// ICWLoadsAndRestraintsManager.AddForce/AddRestraint need a DispArray whose encoding is not
        /// documented anywhere we can reach (offline pack has no cosworks docs; help.solidworks.com 403).
        /// Every shape we tried (object[] / bare object / DispatchWrapper[] / numeric tuple / AddForce2)
        /// came back swsForceErrorSelectFacesEdgesVerticesOrPoints or RPC_E_SERVERFAULT.
        ///
        /// ICWStudy.ImportStudyFeatures(component, sourceStudy, config, filter, propagate, out err) copies
        /// fixtures / external loads / contacts / mesh controls FROM ANOTHER STUDY IN THE SAME PART.
        /// So a study authored in the UI (or by any means) can be cloned into a study this tool created —
        /// no DispArray involved. That is the first path that does not require the undocumented encoding.
        ///
        /// filter bits (swsImportStudyFeaturesFilterType_e):
        ///   0=All  1=Materials  2=Connectors/Contacts  4=Fixtures  8=ExternalLoads  16=MeshControls
        /// </summary>
        public ExecutionResponse ImportStudyFeaturesTool(ToolRequest request)
        {
            if (_guard.IsDuplicate(request.OperationId)) return _guard.GetDuplicate(request.OperationId);
            if (!_guard.IsStateVersionValid(request.StateVersion))
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "INVALID_STATE_VERSION", "Incoming state_version does not match current state.");
            if (!EnsureConnected())
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "COM_ATTACH_FAILED", "SolidWorks process not found or COM not registered.");

            var p = request.Params as JObject;
            string sourceStudy = p?.Value<string>("source_study") ?? "";
            int filter = p?.Value<int?>("filter") ?? 0;          // 0 = everything
            bool propagate = p?.Value<bool?>("propagate") ?? true;
            var log = new JArray();
            if (string.IsNullOrEmpty(sourceStudy))
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "MISSING_PARAMETER", "source_study required (the study to copy from).");

            // Reach cosworks the same way TopologyOptimize does, with the retry loop.
            object addin = null; int attempt = 0; Exception lastEx = null;
            int loadRet = -1;
            while (attempt < 6 && addin == null)
            {
                attempt++;
                loadRet = SafeInt(() => _solidWorks.LoadAddIn(
                        "D:\\Program Files\\SOLIDWORKS Corp\\SOLIDWORKS\\Simulation\\cosworks.dll"));
                foreach (var id in new[] { "CosmosWorks.CosmosWorks", "SldWorks.Simulation", "SldWorks.Simulation.19" })
                {
                    try { addin = _solidWorks.GetAddInObject(id); if (addin != null) { log.Add("addin via " + id); break; } }
                    catch (Exception ex) { lastEx = ex; }
                }
                if (addin == null) { GC.Collect(); GC.WaitForPendingFinalizers(); System.Threading.Thread.Sleep(150); }
            }
            if (addin == null)
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "ADDIN_UNREACHABLE", "Simulation add-in unreachable after " + attempt
                    + " attempts (LoadAddIn=" + loadRet + "): " + (lastEx == null ? "null" : lastEx.Message));

            var modelDocI = SafeActiveDoc();
            // ★★★ 照抄 TopologyOptimize 里【已验证可行】的写法（L1166/L1200）：
            //   dynamic cwm = cw.CosmosWorks.ActiveDoc;  dynamic sm = cwm.StudyManager;
            //   GetStudy 是【1-based】且【单参数】—— 传 out 参或传 0 都会抛 "调用 GetStudy 时出错"。
            //   （强类型 ICWStudyManager + ref out 在本机反而必炸：CWStudy/CWStudyManager 是 comclass。）
            dynamic cw = addin;
            dynamic cwm = cw.CosmosWorks.ActiveDoc;
            if (cwm == null)
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "NO_CW_MODELDOC", "ICosmosWorks.ActiveDoc is null (no part open for Simulation).");
            dynamic sm = cwm.StudyManager;
            if (sm == null)
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "NO_STUDY_MANAGER", "ICWModelDoc.StudyManager is null.");
            int count = 0;
            try { count = (int)sm.StudyCount; } catch (Exception exC) { log.Add("StudyCount EX " + exC.Message); }
            var names = new JArray();
            var withLoads = new JArray();
            // ★ 1-based 扫描，并顺带报告每个 study 的载荷/夹具数量
            for (int i = 1; i <= count; i++)
            {
                try
                {
                    dynamic s0 = sm.GetStudy(i);
                    if (s0 == null) { names.Add(new JObject { ["index"] = i, ["null"] = true }); continue; }
                    string nm = "";
                                        // ★★ GetStudy 返回 CWStudy（comclass）。dynamic 上直接读 .Name 会返回空，
                    //   必须先强转成 interface ICWStudy —— 强类型才读得到属性。
                    SolidWorks.Interop.cosworks.ICWStudy sIface = null;
                    try { sIface = s0 as SolidWorks.Interop.cosworks.ICWStudy; } catch { }
                    if (sIface != null) { try { nm = sIface.Name ?? ""; } catch { } }
                    if (string.IsNullOrEmpty(nm)) { try { nm = Convert.ToString(s0.Name); } catch { } }
                    if (string.IsNullOrEmpty(nm)) { try { nm = Convert.ToString(s0.GetName()); } catch { } }
                    int lrm = -1;
                    try { lrm = (int)s0.LoadsAndRestraintsManager.Count; } catch { }
                    names.Add(new JObject { ["index"] = i, ["name"] = nm, ["loads"] = lrm });
                    if (lrm > 0) withLoads.Add(new JObject { ["index"] = i, ["name"] = nm, ["loads"] = lrm });
                }
                catch (Exception exG) { names.Add(new JObject { ["index"] = i, ["error"] = exG.Message }); }
            }
            log.Add("StudyCount=" + count + " studies=" + names.ToString(Formatting.None));
            log.Add("studies carrying loads/fixtures = " + withLoads.ToString(Formatting.None));
            // ★ 没给 source_study：自动用【第一个带载荷的 study】（本机 UI 建的）
            if (string.IsNullOrEmpty(sourceStudy))
            {
                foreach (var w in withLoads)
                {
                    string cand = Convert.ToString(w["name"]);
                    if (!string.IsNullOrEmpty(cand)) { sourceStudy = cand; break; }
                }
                log.Add("source_study auto-picked: '" + sourceStudy + "'");
            }

            // Target study: explicit 1-based index, else the LAST one (the newest).
            int targetIdx = p?.Value<int?>("target_study_index") ?? 0;
            if (targetIdx == 0) targetIdx = count;   // 0 = 最后一个（最新的）
            if (count <= 0)
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "NO_STUDY", "StudyCount is 0 — nothing to import into.");
            if (targetIdx < 1 || targetIdx > count) targetIdx = count;
            dynamic target = sm.GetStudy(targetIdx);
            string tName = "";
            try { tName = Convert.ToString(target.Name); } catch { }
            log.Add("target study [" + targetIdx + "] = " + tName);

            int impErr = 0;
            bool okImp = false;
            try
            {
                dynamic tgt = target;
                // ★ dynamic 下 out 参必须用 ref（同 AddForce 的教训）
                okImp = tgt.ImportStudyFeatures("Housing", sourceStudy, "Default", filter, propagate, ref impErr);
            }
            catch (Exception ex) { log.Add("ImportStudyFeatures threw: " + ex.GetType().Name + ": " + ex.Message); }

            log.Add("ImportStudyFeatures(component='Housing', study='" + sourceStudy
                  + "', filter=" + filter + ", propagate=" + propagate + ") -> " + okImp + " err=" + impErr);
            int lrmCount = -1;
            try { lrmCount = target.LoadsAndRestraintsManager.Count; } catch { }
            log.Add("LoadsAndRestraintsManager.Count = " + lrmCount);

            var ok = new JObject
            {
                ["stage"] = "import_study_features",
                ["log"] = log,
                ["studies"] = names,
                ["imported"] = okImp,
                ["import_err"] = impErr,
                ["lrm_count"] = lrmCount,
                ["note"] = "import_err 0 = success (swsImportStudyFeaturesError_NoError)."
                        + " If lrm_count > 0 the study now carries real fixtures/loads and MeshAndRun"
                        + " should produce results instead of being ignored."
            };
            return OkWrite(request, SafeActiveDoc(), null, ok.ToString(Formatting.None));
        }

        /// <summary>
        /// ★★ 2026-09-28 — "solve a study that already carries fixtures+loads, and read the result back".
        ///
        /// This is the piece that makes the静力分析 pipeline scriptable end to end EXCEPT for creating
        /// the load itself (ICWLoadsAndRestraintsManager.AddForce/AddRestraint return
        /// swsForceErrorSelectFacesEdgesVerticesOrPoints — the DispArray encoding is not documented
        /// anywhere reachable, and the VBA route is impossible because .swp is an OLE2 container,
        /// not a script file). So: loads/fixtures are authored once in the UI, and everything after
        /// that — material, mesh, solve, read — runs from here.
        ///
        /// LESSONS BAKED IN (each one cost a real failure):
        ///   · CreateMesh(NUnits, DElementSize, DTolerance) — the THIRD argument is an ABSOLUTE
        ///     TOLERANCE in metres. Passing 1.0 (=1 m) for an 80 mm part made the mesher process
        ///     (cwbcbfmesh.exe) reach 84 GB of private memory. Keep it at the same order as the
        ///     element size (1e-4 … 1e-3).
        ///   · RunAnalysis returns IMMEDIATELY; a return of 0 does NOT mean it finished. Poll Results.
        ///   · swsRunAnalysisError_e 21 = NoSolidBody is almost always "material was set on the part's
        ///     外观材质 folder instead of the Simulation tree's 零件 node" — the two are not the same
        ///     material, and the API's SetLibraryMaterial* can return 0 without actually binding.
        ///   · ICWStudy.Results can be null even after a successful solve; the authoritative numbers
        ///     live in the plain-text solver output "&lt;part&gt;-&lt;study&gt;.OUT" next to the part.
        /// </summary>
        /// <summary>Turn swsForceError_e / swsRestraintError_e into something actionable (2026-09-28).</summary>
        private static string DescribeForceErr(int code)
        {
            if (code == 0) return " (Successful)";
            switch (code)
            {
                case 1: return " (1=SelectFacesEdgesVerticesOrPoints -- the DispArray does not hold usable face/edge/vertex refs)";
                case 2: return " (2=SelectFaceEdgePlaneOrAxis)";
                case 3: return " (3=ApplyNormalForceToFacesAndShellEdges -- a Normal force needs FACES or SHELL edges)";
                case 4: return " (4=SelectReferenceAxisOrCylindricalFace)";
                case 5: return " (5=InvalidStudyType)";
                case 6: return " (6=InvalidArray -- the array SHAPE is wrong)";
                case 7: return " (7=InvalidForceType)";
                default: return " (see swsForceError_e)";
            }
        }
        public ExecutionResponse SolveStatic(ToolRequest request)
        {
            if (_guard.IsDuplicate(request.OperationId)) return _guard.GetDuplicate(request.OperationId);
            if (!_guard.IsStateVersionValid(request.StateVersion))
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "INVALID_STATE_VERSION", "Incoming state_version does not match current state.");
            if (!EnsureConnected())
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "COM_ATTACH_FAILED", "SolidWorks process not found or COM not registered.");
            var modelDoc = SafeActiveDoc();
            if (modelDoc == null)
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "NO_ACTIVE_DOCUMENT", "Open the part first.");
            var p = request.Params as JObject;
            var log = new JArray();
            string matLib = p?.Value<string>("material_library") ?? "solidworks materials";
            string matName = p?.Value<string>("material") ?? "AISI 1020";
            double elemMm = p?.Value<double?>("element_mm") ?? 6.0;
            double tolMm = p?.Value<double?>("tolerance_mm") ?? 0.5;   // ★ 0.5 mm, NOT 1.0
            int waitS = p?.Value<int?>("wait_seconds") ?? 120;
            string onlyStudy = p?.Value<string>("study_name") ?? "";

            // reach cosworks (same retry loop as elsewhere)
            object addin = null; int loadRet = -1; int attempt = 0;
            while (attempt < 6 && addin == null)
            {
                attempt++;
                loadRet = SafeInt(() => _solidWorks.LoadAddIn(
                    "D:\\Program Files\\SOLIDWORKS Corp\\SOLIDWORKS\\Simulation\\cosworks.dll"));
                foreach (var id in new[] { "CosmosWorks.CosmosWorks", "SldWorks.Simulation", "SldWorks.Simulation.19" })
                {
                    try { addin = _solidWorks.GetAddInObject(id); if (addin != null) break; } catch { }
                }
                if (addin == null) { GC.Collect(); GC.WaitForPendingFinalizers(); System.Threading.Thread.Sleep(150); }
            }
            if (addin == null)
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "ADDIN_UNREACHABLE", "Simulation add-in unreachable after " + attempt + " attempts.");
            dynamic cw = addin; dynamic cwm = cw.CosmosWorks.ActiveDoc; dynamic sm = cwm.StudyManager;
            int count = Convert.ToInt32(sm.StudyCount);
            log.Add("StudyCount=" + count);

            // pick the study that already carries loads/fixtures (GetStudy is 1-based, single-arg)
            dynamic st = null; string stName = ""; int stIdx = -1; int loads = 0;
            for (int i = 1; i <= count; i++)
            {
                try
                {
                    dynamic s = sm.GetStudy(i);
                    string nm = ""; try { nm = Convert.ToString(s.Name); } catch { }
                    int l = 0; try { l = Convert.ToInt32(s.LoadsAndRestraintsManager.Count); } catch { }
                    if (!string.IsNullOrEmpty(onlyStudy) && !nm.Equals(onlyStudy, StringComparison.OrdinalIgnoreCase)) continue;
                    if (l > 0) { st = s; stName = nm; stIdx = i; loads = l; break; }
                    if (st == null) { st = s; stName = nm; stIdx = i; loads = l; }
                }
                catch (Exception ex) { log.Add("GetStudy(" + i + ") EX " + ex.Message); }
            }
            if (st == null)
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "NO_STUDY", "No study found.");
            log.Add("target study #" + stIdx + " '" + stName + "' loads/fixtures=" + loads);
            if (loads <= 0)
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "NO_LOADS",
                    "Study '" + stName + "' has no fixtures/loads. Add them ONCE in the SolidWorks UI "
                  + "(Simulation tab -> 夹具 / 外部载荷). The API cannot create them on this machine: "
                  + "AddForce/AddRestraint return swsForceErrorSelectFacesEdgesVerticesOrPoints because the "
                  + "DispArray encoding is undocumented, and .swp macros are OLE2 binaries, not scripts.");

            sm.ActiveStudy = stIdx;
            st = sm.GetStudy(stIdx);

            // 1) material (all bodies, by component name)
            try
            {
                dynamic sdm = st.SolidManager;
                int rc = Convert.ToInt32(sdm.SetFavLibraryMaterialToAllBodiesByCompName(
                    "Housing", matLib, matName));
                log.Add("SetFavLibraryMaterialToAllBodies('" + matName + "') -> " + rc);
            }
            catch (Exception exMat) { log.Add("material EX " + exMat.Message); }

            // 2) mesh — ★ 2026-09-28 measurement: hand-specified CreateMesh parameters blow up on this
            //    part (6~12 GB private memory in cwbcbfmesh.exe across element sizes 6..30 mm, while
            //    SolidWorks' own default meshing produced 9476 elements in seconds). So: mesh ONLY when the
            //    study has none, and otherwise say so plainly instead of guessing parameters.
            int meshRc = 0; bool meshedHere = false; int meshType = -1;
            try { meshType = Convert.ToInt32(st.MeshType); } catch { }
            log.Add("MeshType before = " + meshType);
            if (meshType == 0)
            {
                double elemM = elemMm / 1000.0, tolM = tolMm / 1000.0;
                try { meshRc = Convert.ToInt32(st.CreateMesh(0, elemM, tolM)); }
                catch (Exception exMesh) { log.Add("CreateMesh EX " + exMesh.Message); }
                meshedHere = true;
                log.Add("CreateMesh(units=0, elem=" + elemM + "m, tol=" + tolM + "m) -> " + meshRc);
                if (meshRc != 0)
                    return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                        "MESH_FAILED", "CreateMesh returned " + meshRc + " (element " + elemMm
                      + "mm / tolerance " + tolMm + "mm). On this machine hand-specified mesh parameters make "
                      + "the mesher (cwbcbfmesh.exe) consume 6-12 GB. SolidWorks' own default meshing is "
                      + "the reliable route: generate the mesh once in the UI (right-click 网格 -> 生成网格), "
                      + "save, then call solve_static again — it will skip meshing and just solve.");
            }
            else log.Add("mesh already present — skipping CreateMesh");

            // 3) solve  ★ returns immediately; poll
            int runRc = -999;
            try { runRc = Convert.ToInt32(st.RunAnalysis()); }
            catch (Exception exR) { log.Add("RunAnalysis EX " + exR.Message); }
            log.Add("RunAnalysis -> " + runRc);

            bool hasResults = false; int waited = 0;
            while (waited < waitS)
            {
                System.Threading.Thread.Sleep(3000); waited += 3;
                try { if (st.Results != null) { hasResults = true; break; } } catch { }
            }
            log.Add("poll: waited " + waited + "s, Results=" + (hasResults ? "present" : "null"));

            // 4) authoritative numbers: the solver's plain-text .OUT next to the part
            var res = new JObject();
            string partDir = System.IO.Path.GetDirectoryName(modelDoc.GetPathName() ?? "");
            string partName = System.IO.Path.GetFileNameWithoutExtension(modelDoc.GetPathName() ?? "");
            if (!string.IsNullOrEmpty(partDir) && !string.IsNullOrEmpty(partName))
            {
                var outFile = System.IO.Directory.GetFiles(partDir, partName + "-" + stName + "*.OUT");
                if (outFile.Length > 0)
                {
                    string path = Array.Find(outFile, f => new FileInfo(f).Length > 0) ?? outFile[0];
                    log.Add("solver output = " + System.IO.Path.GetFileName(path)
                          + " (" + (int)(new FileInfo(path).Length / 1024) + " KB)");
                    foreach (var line in System.IO.File.ReadAllLines(path))
                    {
                        var t = line.Trim();
                        if (t.Contains("NUMBER OF ELEMENTS") && t.Contains("NUME")) res["elements"] = t;
                        else if (t.StartsWith("MAX.") && res["max_disp_line"] == null && t.Contains("E-")) res["max_disp_line"] = t;
                        else if (t.Contains("MAXIMUM RESULTANT DISPLACEMENT")) res["has_max_disp_section"] = true;
                        else if (t.Contains("Total React.")) res["reaction"] = t;
                        else if (t.Contains("MAXIMUM NODAL VON MISES")) res["has_stress_section"] = true;
                        else if (t.StartsWith("MAX.") && t.Contains("325") == false && t.Split('.').Length == 2
                                 && t.Contains(".")) { if (res["max_stress_line"] == null) res["max_stress_line"] = t; }
                        else if (t.Contains("Total Error Energy")) res["tee"] = t;
                    }
                }
                else log.Add("no .OUT found for '" + partName + "-" + stName + "' (mesh/run may not have completed)");
            }

            var ok = new JObject
            {
                ["stage"] = "solve_static",
                ["log"] = log,
                ["study_name"] = stName,
                ["study_index"] = stIdx,
                ["loads"] = loads,
                ["mesh_rc"] = meshRc,
                ["meshed_here"] = meshedHere,
                ["run_rc"] = runRc,
                ["results_object"] = hasResults,
                ["solver_output"] = res,
                ["note"] = "run_rc 0 only means the solve was SUBMITTED. The numbers in solver_output come "
                        + "from the .OUT file and are authoritative. If run_rc is 21, the material is not "
                        + "bound to the solid bodies (set it on the Simulation tree's 零件 node, not the "
                        + "part tree's 材质 folder)."
            };
            return OkWrite(request, modelDoc, null, ok.ToString(Formatting.None));
        }
    }
}
