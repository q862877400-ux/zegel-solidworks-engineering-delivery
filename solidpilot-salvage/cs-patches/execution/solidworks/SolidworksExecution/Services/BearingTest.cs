// 判别实验：AddBearingLoad(CoordinateSystem, FirstFace, out err) —— 3 个参数，【无数组】
// 若它能成功，就证明 24 轮 AddRestraint 失败的症结是"传 DispArray"，而非许可或研究状态。
using System;
using System.Collections.Generic;
using System.Text;
using System.Runtime.InteropServices;using System.Reflection;
using Newtonsoft.Json.Linq;
public static class BearingTest
{
    static object _lrm; static object _study; static JArray _log;

    static void L(string s) { _log.Add(s); }

    public static string Run(string partPath, double loadN)
    {
        _log = new JArray();
        var sw = (SolidWorks.Interop.sldworks.ISldWorks)
            Marshal.GetActiveObject("SldWorks.Application");

        // 用已激活的文档，不自己 OpenDoc6 —— OpenDoc6 的 ref/out 参数在 interop 里
        // 语义不匹配，会在日志建立前就抛 DISP_E_BADINDEX。
        dynamic m = null;
        try
        {
            object act = sw.IActiveDoc;
            L("IActiveDoc: " + (act == null ? "null" : "ok"));
            m = act;
        }
        catch (Exception ex) { L("取 IActiveDoc 失败: " + ex.Message); return _log.ToString(); }
        if (m == null) { L("没有激活的文档 —— 先用 open_document 打开零件"); return _log.ToString(); }
        try { L("当前文档: " + m.GetTitle()); }
        catch (Exception ex) { L("GetTitle 失败: " + ex.Message); }

        // Simulation 链
        object addin = sw.GetAddInObject("SldWorks.Simulation.19");
        if (addin == null) { L("GetAddInObject 返回 null"); return _log.ToString(); }
        L("add-in 拿到");

        dynamic cb = null;
        // 通过 ICwAddincallback 拿 CosmosWorks（每步都包 try，COM 异常一抛后面日志全丢）
        dynamic cosObj = null;
        try
        {
            var iCb = (SolidWorks.Interop.cosworks.ICwAddincallback)addin;
            cosObj = iCb.CosmosWorks;
        }
        catch (Exception ex) { L("取 CosmosWorks 失败: " + ex.Message); return _log.ToString(); }
        L("CosmosWorks: " + (cosObj == null ? "null" : "ok"));
        if (cosObj == null) return _log.ToString();

        dynamic activeDoc = null;
        try { activeDoc = cosObj.ActiveDoc; }
        catch (Exception ex) { L("取 ActiveDoc 失败: " + ex.Message); return _log.ToString(); }
        L("ActiveDoc: " + (activeDoc == null ? "null" : "ok"));
        if (activeDoc == null) return _log.ToString();

        dynamic studyMgr = null;
        try { studyMgr = activeDoc.StudyManager; L("StudyManager 拿到"); }
        catch (Exception ex) { L("取 StudyManager 失败: " + ex.Message); return _log.ToString(); }

        int cnt = -1;
        try { cnt = (int)studyMgr.StudyCount; L("StudyCount = " + cnt); }
        catch (Exception ex) { L("读 StudyCount 失败: " + ex.Message); return _log.ToString(); }

        dynamic study = null;
        for (int i = 1; i <= cnt; i++)
        {
            object sObj = null;
            try { sObj = studyMgr.GetStudy(i); }
            catch (Exception ex) { L("  study[" + i + "] GetStudy 抛: " + ex.Message); continue; }
            if (sObj == null) { L("  study[" + i + "] = null"); continue; }

            // GetStudy 返回的裸 __ComObject 上【没有】GetName —— dynamic 会报
            // "未包含 GetName 的定义"。必须转成强类型 ICWStudy 才有方法。
            // 这与 AddRestraint 24 轮里"dynamic/强绑定/IDispatch 三条路都试过"是同一类问题。
            SolidWorks.Interop.cosworks.ICWStudy typed = null;
            try
            {
                IntPtr pu = Marshal.GetIUnknownForObject(sObj);
                typed = (SolidWorks.Interop.cosworks.ICWStudy)
                    Marshal.GetTypedObjectForIUnknown(pu, typeof(SolidWorks.Interop.cosworks.ICWStudy));
            }
            catch (Exception ex) { L("  study[" + i + "] 转 ICWStudy 失败: " + ex.Message); continue; }

            string nm = "";
            try { nm = typed.Name; } catch (Exception ex) { L("    GetName 抛: " + ex.Message); }
            L("  study[" + i + "] name = '" + nm + "'");
            // ★ 实际名字是「静应力分析 2」不是「静力学分析」（SolidWorks 内部命名）
            if (nm != null && (nm.Contains("应力") || nm.Contains("静力"))) { study = typed; L("    ★ 选中这个"); }
        }
        if (study == null) { L("没找到静力学研究（StudyCount=" + cnt + "）"); return _log.ToString(); }
        L("用研究: " + ((SolidWorks.Interop.cosworks.ICWStudy)study).Name);

        object lrmObj = null;
        try { lrmObj = ((SolidWorks.Interop.cosworks.ICWStudy)study).LoadsAndRestraintsManager; }
        catch (Exception ex) { L("取 LoadsAndRestraintsManager 失败: " + ex.Message); return _log.ToString(); }
        L("LoadsAndRestraintsManager: " + (lrmObj == null ? "null" : "ok"));
        if (lrmObj == null) return _log.ToString();

        // ---- 取坐标系：零件的原点 ----
        // 全程强类型：裸 __ComObject 上 dynamic 找不到方法（同 GetName 的问题）
        var mdl = m as SolidWorks.Interop.sldworks.IModelDoc2;
        if (mdl == null) { L("拿不到 IModelDoc2"); return _log.ToString(); }

        SolidWorks.Interop.sldworks.Feature originFeat = null;
        try
        {
            // FirstFeature() 在 interop 里返回 object，必须每一步转成强类型 Feature，
            // 否则裸 __ComObject 上没有 Name / GetNextFeature（dynamic 也找不到）。
            var f = mdl.FirstFeature() as SolidWorks.Interop.sldworks.Feature;
            int guard = 0;
            while (f != null && guard++ < 200)
            {
                string n = "";
                try { n = f.Name; } catch (Exception ex) { L("    读特征名失败: " + ex.Message); }
                if (n == "原点" || n == "Origin") { originFeat = f; break; }
                try { f = f.GetNextFeature() as SolidWorks.Interop.sldworks.Feature; }
                catch (Exception ex) { L("    GetNextFeature 失败: " + ex.Message); break; }
            }
        }
        catch (Exception ex) { L("遍历特征失败: " + ex.Message); }
        L("原点特征: " + (originFeat == null ? "未找到" : originFeat.Name));
        if (originFeat == null) { L("拿不到坐标系，AddBearingLoad 需要它"); return _log.ToString(); }

        object cs = null;
        try { cs = ((SolidWorks.Interop.sldworks.Feature)originFeat).GetSpecificFeature2(); }
        catch (Exception ex) { L("GetSpecificFeature2 失败: " + ex.Message); return _log.ToString(); }
        L("坐标系对象: " + (cs == null ? "null" : cs.GetType().FullName));
        if (cs == null) { L("坐标系是 null"); return _log.ToString(); }

        // ---- 取一个圆柱面（内孔 Ø62）----
        // GetBodies2 在 IPartDoc 上，不在 IModelDoc2 上
        var partDoc = mdl as SolidWorks.Interop.sldworks.IPartDoc;
        if (partDoc == null) { L("拿不到 IPartDoc"); return _log.ToString(); }
        object[] bodies = null;
        try { bodies = partDoc.GetBodies2(0, false) as object[]; }
        catch (Exception ex) { L("GetBodies2 失败: " + ex.Message); return _log.ToString(); }
        if (bodies == null || bodies.Length == 0) { L("没有实体"); return _log.ToString(); }
        L("实体数 = " + bodies.Length);

        object[] faces = null;
        try
        {
            var b0 = bodies[0] as SolidWorks.Interop.sldworks.IBody2;
            faces = b0.GetFaces() as object[];
        }
        catch (Exception ex) { L("GetFaces 失败: " + ex.Message); }
        if (faces == null) { L("拿不到面"); return _log.ToString(); }
        L("面数 = " + faces.Length);

        object cylFace = null;
        for (int i = 0; i < faces.Length; i++)
        {
            try
            {
                var f2 = faces[i] as SolidWorks.Interop.sldworks.IFace2;
                if (f2 == null) continue;
                var surf = f2.GetSurface() as SolidWorks.Interop.sldworks.ISurface;
                if (surf != null && surf.IsCylinder()) { cylFace = faces[i]; L("找到圆柱面 [" + i + "]"); break; }
            }
            catch (Exception ex) { L("  面[" + i + "] 检查失败: " + ex.Message); }
        }
        if (cylFace == null) { L("没找到圆柱面"); return _log.ToString(); }

        // ---- 关键调用：AddBearingLoad(坐标系, 面, out err) —— 无数组 ----
        try
        {
            int bErr = -999;
            L(">>> 调 AddBearingLoad（3 参数，无 DispArray）...");
            var bl = lrmObj as SolidWorks.Interop.cosworks.ICWLoadsAndRestraintsManager;
            if (bl == null) { L("转 ICWLoadsAndRestraintsManager 失败"); return _log.ToString(); }
            var bearing = bl.AddBearingLoad(cs, cylFace, ref bErr);
            L("    err = " + bErr);
            L("    返回 = " + (bearing == null ? "null" : bearing.GetType().FullName));
            if (bearing != null && bErr == 0)
            {
                L("  ★★★ 成功！证明症结是『传 DispArray』");
                // 设值
                var blv = bearing as SolidWorks.Interop.cosworks.ICWBearingLoad;
                blv.XDirectionValue = loadN;
                L("  XDirectionValue 已设 = " + blv.XDirectionValue);
                blv.DistributionType = 1;   // 正弦分布
                L("  DistributionType = " + blv.DistributionType);
                _study = study;
            }
        }
        catch (Exception ex) { L("AddBearingLoad 抛: " + ex.GetType().Name + ": " + ex.Message); }

        return _log.ToString();
    }
}



