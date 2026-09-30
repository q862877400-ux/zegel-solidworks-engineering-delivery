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
                var comp = asmDoc.AddComponent5(path, 2 /*swAddComponentConfigOptions_CurrentSelectedConfig*/,
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

                string kind = p_string(request, "study", "explode") ?? "explode";   // explode | rotation | motion
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

                dynamic study = mgr.GetMotionStudy(name);
                if (study == null) { study = mgr.CreateMotionStudy(name); if (study == null) return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(), "NOT_AVAILABLE", "CreateMotionStudy returned null."); }

                var log = new JArray();
                try
                {
                    if (kind == "explode")
                    {
                        for (int i = 1; i <= steps; i++)
                        {
                            double t0 = (double)(i - 1) / steps, t1 = (double)i / steps;
                            try { study.CreateByCollapse(false, t0, t1); log.Add("collapse " + t0 + "->" + t1); }
                            catch (Exception ex) { log.Add("collapse " + t0 + " FAILED: " + ex.Message); }
                        }
                    }
                    else if (kind == "rotation")
                    {
                        study.CreateByRotateModel(false, 0.0, 0.0, 1.0, angle, 0.0, 0.0, 0.0, 0.0);
                        log.Add("rotate about Z by " + angle);
                    }
                    else
                    {
                        log.Add("motion study created (no definition added — supply load/contact data via SOLIDWORKS UI)");
                    }
                }
                catch (Exception ex) { log.Add("define failed: " + ex.Message); }

                try { study.Duration = duration; } catch { }
                try { mgr.ActivateMotionStudy(name); } catch { }
                try { study.Calculate(); log.Add("calculated"); } catch (Exception ex) { log.Add("calculate failed: " + ex.Message); }

                if (!string.IsNullOrEmpty(avi))
                {
                    try
                    {
                        string dir = Path.GetDirectoryName(avi);
                        if (!string.IsNullOrEmpty(dir)) Directory.CreateDirectory(dir);
                        dynamic aviParam = mgr.CreateAVIParameter();
                        study.SaveToAVI(avi, aviParam);
                        log.Add("avi -> " + avi);
                    }
                    catch (Exception ex) { log.Add("avi failed: " + ex.Message); }
                }

                var payload = new JObject
                {
                    ["study"] = name, ["kind"] = kind, ["log"] = log,
                    ["note"] = "Motion = kinematics/explode/rotate/AVI. NOT FEA (SOLIDWORKS Simulation is a separate API + licence)."
                };
                return OkWrite(request, modelDoc, null, payload.ToString(Formatting.None));
            }
            catch (COMException ex) { return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(), "COM_ERROR", ex.Message); }
            catch (Exception ex) { Infrastructure.ExecLog.Write("CAPFAIL " + ex.ToString()); return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(), "UNEXPECTED_ERROR", ex.Message + " @ " + ex.StackTrace); }
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
    }
}
