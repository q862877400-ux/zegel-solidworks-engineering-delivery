// =======================================================================
// ProductProbe — 通用产品线 add-in 可达性探测（2026-09-28）
//
// 为什么需要它（实测记录）：
//   · 从 PowerShell 直连 SolidWorks 走不通：New-Object -ComObject 会【新建空壳实例】
//     （连 RevisionNumber() 都报 TYPE_E_ELEMENTNOTFOUND 0x8002802B），
//     pwsh 也没有 Marshal.GetActiveObject（.NET Core 移除了它）。
//   · 唯一可靠的宿主是本服务：它持有正确实例 + STA 线程 + 消息泵。
//   · 各产品的 add-in【不需要注册到 HKCU\...\AddinsStartup】也能用
//     LoadAddIn + GetAddInObject 激活 —— Simulation 当初就是这么跑通的
//     （实测：注册表里全空，topology_optimize 仍 reachable=true）。
//
// 用法：Call 'product_probe' @{ }  或  @{ action='probe'; products='Simulation,Costing' }
// =======================================================================
using System;
using System.Collections.Generic;
using System.Linq;
using System.Reflection;
using System.Text;
using Newtonsoft.Json.Linq;
using SolidworksExecution.Infrastructure;
using SolidworksExecution.Models;

namespace SolidworksExecution.Services
{
    public partial class SolidWorksService
    {
        /// <summary>候选 add-in 名 → （人类可读产品名，提示用的 dll 相对路径）</summary>
        private static readonly Dictionary<string, string[]> ProductCandidates = new Dictionary<string, string[]>
        {
            // addin 名候选                              { 产品名, 可能的 dll（相对 SOLIDWORKS 目录） }
            { "SldWorks.Simulation",     new[]{ "Simulation",       @"Simulation\cosworks.dll" } },
            { "CosmosWorks.CosmosWorks", new[]{ "Simulation(别名)",  null } },
            { "SldWorks.Electrical",     new[]{ "Electrical",       @"Electrical\SwElectrical.dll" } },
            { "SldWorks.FlowSimulation", new[]{ "Flow Simulation",  null } },
            { "SldWorks.Costing",        new[]{ "Costing",          null } },
            { "SldWorks.Sustainability", new[]{ "Sustainability",   null } },
            { "SldWorks.3DPrinter",      new[]{ "3D Printer",       null } },
            { "SldWorks.DimXpert",       new[]{ "DimXpert",         null } },
            { "SldWorks.DesignChecker",  new[]{ "Design Checker",   null } },
            { "SldWorks.Routing",        new[]{ "Routing",          null } },
            { "SldWorks.PDM",            new[]{ "PDM",              null } },
            { "SldWorks.CAM",            new[]{ "CAM",              null } },
        };

        public ExecutionResponse ProductProbe(ToolRequest request)
        {
            if (_guard.IsDuplicate(request.OperationId)) return _guard.GetDuplicate(request.OperationId);
            if (!_guard.IsStateVersionValid(request.StateVersion))
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "INVALID_STATE_VERSION", "Incoming state_version does not match current state.");
            if (!EnsureConnected())
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "COM_ATTACH_FAILED", "SolidWorks process not found or COM not registered.");

            var log = new List<string>();
            try
            {
                var sw = _solidWorks;
                log.Add("SolidWorks RevisionNumber = " + sw.RevisionNumber());

                // 只探请求里点名的产品；不给就全探
                string want = p_string(request, "products", null);
                var wanted = string.IsNullOrEmpty(want)
                    ? ProductCandidates.Keys.ToList()
                    : want.Split(new[] { ',' }, StringSplitOptions.RemoveEmptyEntries)
                            .Select(s => s.Trim()).Where(s => ProductCandidates.ContainsKey(s)).ToList();

                // interop DLL 目录 —— 顺带报告每个 interop 能不能加载（= 该产品线有没有 API）
                string redist = EnvRedistDir();

                var results = new JArray();
                foreach (var key in wanted)
                {
                    var meta = ProductCandidates[key];
                    string product = meta[0], dllRel = meta[1];
                    var row = new JObject
                    {
                        ["addin"] = key,
                        ["product"] = product,
                    };

                    // (1) 先试直接 GetAddInObject（add-in 可能已随 SolidWorks 启动加载）
                    object obj = null; string err = null;
                    try { obj = sw.GetAddInObject(key); }
                    catch (Exception e) { err = e.GetType().Name + ": " + e.Message; }

                    if (obj != null)
                    {
                        row["reachable"] = true;
                        row["via"] = "GetAddInObject(已加载)";
                        // 证明对象真的活着：打一次动态调用
                        try
                        {
                            var t = obj.GetType();
                            row["clrType"] = t.FullName ?? t.Name;
                        }
                        catch { }
                    }
                    else
                    {
                        // (2) 试 LoadAddIn(dll) 再取
                        if (!string.IsNullOrEmpty(dllRel))
                        {
                            try
                            {
                                string full = System.IO.Path.Combine(SwDir(), dllRel);
                                if (System.IO.File.Exists(full))
                                {
                                    int r = sw.LoadAddIn(full);
                                    row["loadAddIn"] = r;
                                    try { obj = sw.GetAddInObject(key); } catch { }
                                }
                                else row["dllMissing"] = full;
                            }
                            catch (Exception e) { row["loadEx"] = e.GetType().Name; }
                        }
                        if (obj != null)
                        {
                            row["reachable"] = true;
                            row["via"] = "LoadAddIn + GetAddInObject";
                        }
                        else
                        {
                            row["reachable"] = false;
                            if (err != null) row["err"] = err;
                        }
                    }
                    results.Add(row);
                    log.Add($"  {(row["reachable"] != null && (bool)row["reachable"] ? "OK  " : "--  ")} {product,-18} {key}" +
                            (row["via"] != null ? "  via " + (string)row["via"] : ""));
                }

                // (3) interop DLL 盘点：哪些产品线【有 API 程序集】
                var interop = new JArray();
                foreach (var f in System.IO.Directory.GetFiles(redist, "*.dll"))
                {
                    var n = System.IO.Path.GetFileName(f);
                    if (!n.StartsWith("SolidWorks.Interop.", StringComparison.OrdinalIgnoreCase)) continue;
                    if (n.EndsWith("swconst.dll", StringComparison.OrdinalIgnoreCase)) continue; // 枚举库
                    try
                    {
                        var asm = System.Reflection.Assembly.LoadFrom(f);
                        int ifaces = asm.GetExportedTypes().Count(t => t.IsInterface);
                        interop.Add(new JObject
                        {
                            ["dll"] = n,
                            ["interfaces"] = ifaces,
                            ["loaded"] = true,
                        });
                    }
                    catch (Exception e)
                    {
                        interop.Add(new JObject { ["dll"] = n, ["loaded"] = false, ["err"] = e.GetType().Name });
                    }
                }

                var payload = new JObject
                {
                    ["stage"] = "product_probe",
                    ["swRevision"] = sw.RevisionNumber(),
                    ["results"] = results,
                    ["interopDlls"] = interop,
                    ["log"] = new JArray(log.ToArray()),
                    ["note"] = "add-in 不需要注册到 HKCU\\...\\AddinsStartup；LoadAddIn + GetAddInObject 即可激活" +
                               "（Simulation 当初就是这么跑通的：注册表全空但 reachable=true）。",
                };

                return new ExecutionResponse
                {
                    OperationId = request.OperationId,
                    Status = "COMPLETED",
                    Verified = true,
                    StateVersion = _guard.GetCurrentStateVersion(),
                    CadState = new CadState
                    {
                        StateVersion = _guard.GetCurrentStateVersion(),
                        ActiveDocument = null,
                        DocumentType = "product_probe",
                        Features = new List<string> { payload.ToString() },
                        Dimensions = new List<string>(),
                    },
                };
            }
            catch (Exception ex)
            {
                ExecLog.Write("product_probe EX: " + ex);
                return BuildFailed(request.OperationId, _guard.GetCurrentStateVersion(),
                    "PROBE_FAILED", ex.GetType().Name + ": " + ex.Message);
            }
        }

        private static string EnvRedistDir()
        {
            return @"D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\api\redist";
        }
        private static string SwDir()
        {
            return @"D:\Program Files\SOLIDWORKS Corp\SOLIDWORKS";
        }
    }
}
