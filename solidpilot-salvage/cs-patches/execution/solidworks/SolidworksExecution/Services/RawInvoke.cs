// 纯原生 IDispatch::Invoke 探针 —— 完全绕开 CLR 封送
// 目标：ICWLoadsAndRestraintsManager::AddRestraint (DispId=3)
using System;
using System.Runtime.InteropServices;
using System.Reflection;
using System.Text;

public static class RawInvoke
{
    // ---- IDispatch vtable ----
    // QueryInterface(0) AddRef(1) Release(2) GetTypeInfoCount(3) GetTypeInfo(4) GetIDsOfNames(5) Invoke(6)
    [UnmanagedFunctionPointer(CallingConvention.StdCall)]
    delegate uint QI([MarshalAs(UnmanagedType.Interface)] object self, ref Guid iid, out IntPtr ppv);
    [UnmanagedFunctionPointer(CallingConvention.StdCall)]
    delegate uint AddRef([MarshalAs(UnmanagedType.Interface)] object self);
    [UnmanagedFunctionPointer(CallingConvention.StdCall)]
    delegate uint Release([MarshalAs(UnmanagedType.Interface)] object self);
    [UnmanagedFunctionPointer(CallingConvention.StdCall)]
    delegate uint GetTypeInfoCount([MarshalAs(UnmanagedType.Interface)] object self, out uint n);
    [UnmanagedFunctionPointer(CallingConvention.StdCall)]
    delegate uint GetTypeInfo([MarshalAs(UnmanagedType.Interface)] object self, uint iTInfo, uint lcid, [MarshalAs(UnmanagedType.Interface)] out object ppTI);
    [UnmanagedFunctionPointer(CallingConvention.StdCall)]
    delegate uint GetIDsOfNames([MarshalAs(UnmanagedType.Interface)] object self, [MarshalAs(UnmanagedType.LPArray, ArraySubType = UnmanagedType.LPStr)] string[] rgszNames,
                                uint cNames, int lcid, out int[] rgDispId);
    [UnmanagedFunctionPointer(CallingConvention.StdCall)]
    delegate uint Invoke([MarshalAs(UnmanagedType.Interface)] object self, int dispIdMember, ref Guid riid,
                         int lcid, int wFlags, IntPtr pDispParams, IntPtr pVarResult,
                         IntPtr pExcepInfo, out int puArgErr);

    // ---- oleaut32 ----
    [DllImport("oleaut32.dll")]
    static extern IntPtr SafeArrayCreateVector(ushort vt, ulong l, ulong ulElems);
    [DllImport("oleaut32.dll")]
    static extern uint SafeArrayPutElement(IntPtr psa, IntPtr rgk, IntPtr pv);
    [DllImport("oleaut32.dll")]
    static extern int SafeArrayAccessData(IntPtr psa, out int ppvData);
    [DllImport("oleaut32.dll")]
    static extern void SafeArrayUnaccessData(IntPtr psa);
    [DllImport("oleaut32.dll")]
    static extern uint SafeArrayDestroy(IntPtr psa);
    [DllImport("oleaut32.dll")]
    static extern void VariantInit(IntPtr pvarg);
    [DllImport("oleaut32.dll")]
    static extern void VariantClear(IntPtr pvarg);
    [DllImport("oleaut32.dll")]
    static extern void VariantCopy(IntPtr pvDest, IntPtr pvSrc);
    [DllImport("oleaut32.dll")]
    static extern int VariantCopyInd(IntPtr pvarg, IntPtr pvarSrc);

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode)]
    static extern IntPtr LoadLibraryW(string f);

    public const ushort VT_EMPTY = 0, VT_NULL = 1, VT_I2 = 2, VT_I4 = 3, VT_R4 = 4, VT_R8 = 5,
                      VT_BSTR = 8, VT_DISPATCH = 9, VT_BOOL = 11, VT_VARIANT = 12, VT_UNKNOWN = 13, VT_UI1 = 17;
    public const ushort VT_ARRAY = 0x2000, VT_BYREF = 0x4000;

    public static void AddDllDir(string dir) { LoadLibraryW(dir); }

    /// <summary>取 IDispatch* 指针（真正的裸指针，绕开所有 RCW 类型信息）</summary>
    public static IntPtr GetIDispatch(object comObject)
    {
        IntPtr pUnk = Marshal.GetIUnknownForObject(comObject);
        if (pUnk == IntPtr.Zero) return IntPtr.Zero;
        Guid iid = new Guid("00020400-0000-0000-C000-000000000046");
        IntPtr p;
        // 不用 Marshal.QueryInterface：它的 ref/in 重载在不同编译器下签名不同
        // （.NET Framework 的 csc 要 ref，Core 的 csc 要 in；本项目里
        //  #if NETCOREAPP 不生效）。直接走 vtable[0] 手工 QI。
        int hr = ManualQI(pUnk, iid, out p);
        Marshal.Release(pUnk);
        return hr == 0 ? p : IntPtr.Zero;
    }

    [UnmanagedFunctionPointer(CallingConvention.StdCall)]
    delegate int QIraw(IntPtr self, IntPtr riid, out IntPtr ppv);

    static int ManualQI(IntPtr self, Guid iid, out IntPtr ppv)
    {
        IntPtr vtbl = Marshal.ReadIntPtr(self);
        IntPtr fn = Marshal.ReadIntPtr(vtbl, 0);
        var f = (QIraw)Marshal.GetDelegateForFunctionPointer(fn, typeof(QIraw));
        IntPtr pIid = Marshal.AllocHGlobal(16);
        try
        {
            Marshal.Copy(iid.ToByteArray(), 0, pIid, 16);
            return f(self, pIid, out ppv);
        }
        finally { Marshal.FreeHGlobal(pIid); }
    }

    static Delegate GetVtbl(IntPtr self, int index, Type t)
    {
        IntPtr vtbl = Marshal.ReadIntPtr(self);                 // vtable 指针
        IntPtr fn = Marshal.ReadIntPtr(vtbl, index * IntPtr.Size);
        return Marshal.GetDelegateForFunctionPointer(fn, t);
    }

    /// <summary>只做只读侦察：取 DispId、验证 vtable 指针，不发任何 Invoke。
    /// 用来在可能崩进程的路径上先确认前提成立。</summary>
    public static string Recon(object lrm, object faceComObject)
    {
        var sb = new StringBuilder();
        // 第一步只做最安全的事：取 IDispatch*。
        // 读 vtable / GetIDsOfNames 都会 dereference 裸指针，一旦对象不是标准
        // COM 对象就会直接 AccessViolation（已实测崩服务），所以分步来。
        IntPtr pUnkLrm = Marshal.GetIUnknownForObject(lrm);
        IntPtr pUnkFace = Marshal.GetIUnknownForObject(faceComObject);
        sb.Append("IUnknown*(lrm)=").Append(pUnkLrm)
          .Append(" IUnknown*(face)=").Append(pUnkFace);
        if (pUnkLrm == IntPtr.Zero || pUnkFace == IntPtr.Zero) return sb.ToString();

        IntPtr pDispLrm = GetIDispatch(lrm);
        IntPtr pDispFace = GetIDispatch(faceComObject);
        sb.Append(" IDispatch*(lrm)=").Append(pDispLrm)
          .Append(" IDispatch*(face)=").Append(pDispFace);
        if (pDispLrm == IntPtr.Zero) { sb.Append(" lrm QI->IDispatch 失败"); return sb.ToString(); }

        // vtable 读取：只比对指针是否非零，不调任何函数
        IntPtr vtbl = Marshal.ReadIntPtr(pDispLrm);
        sb.Append(" vtable=").Append(vtbl);
        if (vtbl != IntPtr.Zero)
        {
            IntPtr f0 = Marshal.ReadIntPtr(vtbl, 0);
            IntPtr f6 = Marshal.ReadIntPtr(vtbl, 6 * IntPtr.Size);
            sb.Append(" vtbl[0](QI)=").Append(f0).Append(" vtbl[6](Invoke)=").Append(f6);
        }
        return sb.ToString();
    }

    /// <summary>用名字拿 DispId（比硬编码 3 更稳）</summary>
    public static int GetDispId(object comObject, string name, out uint hrOut)
    {
        IntPtr p = GetIDispatch(comObject);
        if (p == IntPtr.Zero) { hrOut = 0x80004005; return -1; }
        var f = (GetIDsOfNames)GetVtbl(p, 5, typeof(GetIDsOfNames));
        int[] ids = new int[1];
        uint hr = f(comObject, new string[] { name }, 1, 0, out ids);
        hrOut = hr;
        return ids[0];
    }

    /// <summary>建 SAFEARRAY(VT_DISPATCH) 变体</summary>
    public static IntPtr MakeArrayVariant(IntPtr[] dispPtrs, out IntPtr psaOut)
    {
        psaOut = IntPtr.Zero;
        if (dispPtrs == null || dispPtrs.Length == 0) return IntPtr.Zero;
        IntPtr psa = SafeArrayCreateVector(VT_DISPATCH, 0, (ulong)dispPtrs.Length);
        if (psa == IntPtr.Zero) return IntPtr.Zero;
        for (int i = 0; i < dispPtrs.Length; i++)
        {
            IntPtr idx = Marshal.AllocHGlobal(sizeof(int));
            try
            {
                Marshal.WriteInt32(idx, 0, i);
                uint hr = SafeArrayPutElement(psa, idx, dispPtrs[i]);
                if (hr != 0) { SafeArrayDestroy(psa); return IntPtr.Zero; }
            }
            finally { Marshal.FreeHGlobal(idx); }
        }
        psaOut = psa;
        IntPtr pv = Marshal.AllocCoTaskMem(24);
        VariantInit(pv);
        Marshal.WriteInt16(pv, 0, (short)(VT_ARRAY | VT_DISPATCH));
        Marshal.WriteIntPtr(pv, 8, psa);
        return pv;
    }

    public static IntPtr MakeEmptyVariant()
    {
        IntPtr pv = Marshal.AllocCoTaskMem(24);
        VariantInit(pv);
        Marshal.WriteInt16(pv, 0, (short)VT_EMPTY);
        return pv;
    }

    /// <summary>24 字节 VARIANT 按位复制（x64 布局 vt@0 / union@8）。不 AddRef。</summary>
    static void ZeroMemory(IntPtr p, int n)
    {
        for (int i = 0; i < n; i++) Marshal.WriteByte(p + i, 0);
    }

    static void CopyVariant(IntPtr dest, IntPtr src)
    {
        for (int off = 0; off < 24; off += 8)
            Marshal.WriteInt64(dest + off, Marshal.ReadInt64(src + off));
    }

    public static IntPtr MakeI4Variant(int v)
    {
        IntPtr pv = Marshal.AllocCoTaskMem(24);
        VariantInit(pv);
        Marshal.WriteInt16(pv, 0, (short)VT_I4);
        Marshal.WriteInt32(pv, 8, v);
        return pv;
    }

    /// <summary>AddRestraint 的完整手工调用。数组元素类型 elemVt 可选 VT_DISPATCH(9) / VT_UNKNOWN(13) / VT_VARIANT(12)</summary>
    // 崩溃追踪：AccessViolation 挡不住（进程级），只能把进度实时落盘，崩了也能定位到哪一步。
    static string _tracePath = null;
    public static void StartTrace(string path) { _tracePath = path; try { System.IO.File.WriteAllText(path, "start\n"); } catch { } }
    static void T(string s)
    {
        if (_tracePath == null) return;
        try { System.IO.File.AppendAllText(_tracePath, s + "\n"); } catch { }
    }

    /// <summary>
    /// 路线 B（2026-09-27）：绕开 AddRestraint 的 DispArray。
    ///
    /// ICWRestraint 上有 InsertEntity(Object) / SetReferenceGeometry(Object) / RemoveEntity(int)，
    /// 语义是"建好夹具之后再往里塞几何"。所以先用【0 元素 SAFEARRAY】建一个空夹具，
    /// 再逐个 InsertEntity —— 这样 AddRestraint 的数组参数不再是变量。
    ///
    /// 若 DispArray 的形态问题（VT_VARIANT 元素布局、数组指针层级）是 E_INVALIDARG 的真因，
    /// 0 元素数组不含任何元素、不触发解包，这条路就能通过。
    /// </summary>
    public static string CallAddRestraintThenInsert(object lrm, object[] faces, int restraintType, int wFlagsParam)
    {
        var sb = new StringBuilder();
        IntPtr pLrm = GetIDispatch(lrm);
        if (pLrm == IntPtr.Zero) return sb.AppendLine("  lrm QI 失败").ToString();

        // ---- 第 1 步：用【0 元素】SAFEARRAY(VT_VARIANT) 调 AddRestraint ----
        IntPtr psaEmpty = SafeArrayCreateVector(VT_VARIANT, 0, 0);
        IntPtr vArrayEmpty = Marshal.AllocCoTaskMem(24);
        VariantInit(vArrayEmpty);
        Marshal.WriteInt16(vArrayEmpty, 0, (short)(VT_ARRAY | VT_VARIANT));   // 0x200C
        Marshal.WriteIntPtr(vArrayEmpty, 8, psaEmpty);
        sb.AppendLine("  [1] DispArray = 0 元素 SAFEARRAY(VT_VARIANT)（不做任何元素解包）");

        IntPtr vType = MakeI4Variant(restraintType);
        IntPtr vRef = Marshal.AllocCoTaskMem(24);
        VariantInit(vRef);                                   // VT_EMPTY（Nothing）

        IntPtr errCell = Marshal.AllocHGlobal(sizeof(int));
        Marshal.WriteInt32(errCell, 0, 0x7FFFFFFF);
        IntPtr vErr = Marshal.AllocCoTaskMem(24);
        VariantInit(vErr);
        Marshal.WriteInt16(vErr, 0, (short)(VT_I4 | VT_BYREF));
        Marshal.WriteIntPtr(vErr, 8, errCell);

        IntPtr rgvarg = Marshal.AllocCoTaskMem(4 * 24);
        ZeroMemory(rgvarg, 4 * 24);
        CopyVariant(rgvarg + 0, vType);
        CopyVariant(rgvarg + 24, vArrayEmpty);
        CopyVariant(rgvarg + 48, vRef);
        CopyVariant(rgvarg + 72, vErr);

        IntPtr pars = Marshal.AllocCoTaskMem(20);
        ZeroMemory(pars, 20);
        Marshal.WriteIntPtr(pars, 0, rgvarg);
        Marshal.WriteIntPtr(pars, 8, IntPtr.Zero);
        Marshal.WriteInt32(pars, 16, 4);

        IntPtr pVarResult = Marshal.AllocCoTaskMem(24);
        VariantInit(pVarResult);
        int argErr = 0;
        var inv = (Invoke)GetVtbl(pLrm, 6, typeof(Invoke));
        Guid iidNull = Guid.Empty;
        T("B: about-to-Invoke AddRestraint(0-elem array)");
        uint hr = inv(lrm, 3, ref iidNull, 0, wFlagsParam, pars, pVarResult, IntPtr.Zero, out argErr);
        T("B: invoke-returned hr=0x" + hr.ToString("X8"));
        sb.AppendLine("  [1] Invoke(0 元素数组) -> hr=0x" + hr.ToString("X8")
                    + " argErr=" + argErr
                    + " ErrorCode=" + Marshal.ReadInt32(errCell, 0)
                    + " result.vt=0x" + Marshal.ReadInt16(pVarResult, 0).ToString("X4"));

        // 清理第 1 步的内存（pVarResult 还要用，单独清）
        Marshal.FreeCoTaskMem(rgvarg); Marshal.FreeCoTaskMem(pars);
        Marshal.FreeCoTaskMem(vType); Marshal.FreeCoTaskMem(vArrayEmpty);
        Marshal.FreeCoTaskMem(vRef); Marshal.FreeCoTaskMem(vErr);
        Marshal.FreeHGlobal(errCell);
        if (psaEmpty != IntPtr.Zero) SafeArrayDestroy(psaEmpty);

        if (hr != 0) { VariantClear(pVarResult); Marshal.FreeCoTaskMem(pVarResult); return sb.ToString(); }

        // ---- 第 2 步：拿到返回的 CWRestraint（先只报告，InsertEntity 留待第 1 步通过） ----
        if (Marshal.ReadInt16(pVarResult, 0) != VT_DISPATCH)
        {
            sb.AppendLine("  [2] 返回值不是对象（vt=0x" + Marshal.ReadInt16(pVarResult, 0).ToString("X4") + "）");
        }
        else
        {
            IntPtr pRes = Marshal.ReadIntPtr(pVarResult, 8);
            sb.AppendLine("  [2] ★ 拿到 CWRestraint IDispatch* = " + pRes
                        + "  ⇒ AddRestraint 用 0 元素数组【成功】，DispArray 形态问题已绕开");
        }
        VariantClear(pVarResult);
        Marshal.FreeCoTaskMem(pVarResult);
        return sb.ToString();
    }

    /// <summary>
    /// 判别实验（2026-09-27）：AddRestraint 传【0 元素】数组仍是 E_INVALIDARG
    /// ⇒ 元素布局假设被彻底排除（没有元素可解包）。
    /// 那么"读操作成功、写操作全失败"吗？用 AddForce（DispId=4，同接口、同数组形态）
    /// 做对照：若它也失败 ⇒ 是 LoadsAndRestraintsManager 的写操作整体被拒
    /// （许可 / 研究未激活），而不是 AddRestraint 特有。
    /// </summary>
    public static string CallAddForce(object lrm, object[] faces, int forceType, int wFlagsParam)
    {
        var sb = new StringBuilder();
        IntPtr pLrm = GetIDispatch(lrm);
        if (pLrm == IntPtr.Zero) return sb.AppendLine("  lrm QI 失败").ToString();

        // 同样用 0 元素数组，隔离变量
        IntPtr psa = SafeArrayCreateVector(VT_VARIANT, 0, 0);
        IntPtr vArray = Marshal.AllocCoTaskMem(24);
        VariantInit(vArray);
        Marshal.WriteInt16(vArray, 0, (short)(VT_ARRAY | VT_VARIANT));
        Marshal.WriteIntPtr(vArray, 8, psa);

        IntPtr vType = MakeI4Variant(forceType);          // NForceType
        IntPtr vRef = Marshal.AllocCoTaskMem(24);
        VariantInit(vRef);                                  // RegGeom = VT_EMPTY

        IntPtr errCell = Marshal.AllocHGlobal(sizeof(int));
        Marshal.WriteInt32(errCell, 0, 0x7FFFFFFF);
        IntPtr vErr = Marshal.AllocCoTaskMem(24);
        VariantInit(vErr);
        Marshal.WriteInt16(vErr, 0, (short)(VT_I4 | VT_BYREF));
        Marshal.WriteIntPtr(vErr, 8, errCell);

        IntPtr rgvarg = Marshal.AllocCoTaskMem(4 * 24);
        ZeroMemory(rgvarg, 4 * 24);
        CopyVariant(rgvarg + 0, vType);
        CopyVariant(rgvarg + 24, vArray);
        CopyVariant(rgvarg + 48, vRef);
        CopyVariant(rgvarg + 72, vErr);

        IntPtr pars = Marshal.AllocCoTaskMem(20);
        ZeroMemory(pars, 20);
        Marshal.WriteIntPtr(pars, 0, rgvarg);
        Marshal.WriteIntPtr(pars, 8, IntPtr.Zero);
        Marshal.WriteInt32(pars, 16, 4);

        IntPtr pvr = Marshal.AllocCoTaskMem(24);
        VariantInit(pvr);
        int argErr = 0;
        var inv = (Invoke)GetVtbl(pLrm, 6, typeof(Invoke));
        Guid iid = Guid.Empty;
        T("AddForce: about-to-Invoke DispId=4");
        uint hr = inv(lrm, 4, ref iid, 0, wFlagsParam, pars, pvr, IntPtr.Zero, out argErr);
        T("AddForce: hr=0x" + hr.ToString("X8"));
        sb.AppendLine("  AddForce(0 元素数组, DispId=4) -> hr=0x" + hr.ToString("X8")
                    + " argErr=" + argErr
                    + " ErrorCode=" + Marshal.ReadInt32(errCell, 0)
                    + " result.vt=0x" + Marshal.ReadInt16(pvr, 0).ToString("X4"));

        Marshal.FreeCoTaskMem(rgvarg); Marshal.FreeCoTaskMem(pars);
        Marshal.FreeCoTaskMem(vType); Marshal.FreeCoTaskMem(vArray);
        Marshal.FreeCoTaskMem(vRef); Marshal.FreeCoTaskMem(vErr);
        Marshal.FreeHGlobal(errCell);
        if (psa != IntPtr.Zero) SafeArrayDestroy(psa);
        VariantClear(pvr); Marshal.FreeCoTaskMem(pvr);
        return sb.ToString();
    }

    public static string CallAddRestraint(object lrm, object[] faces, int restraintType, ushort elemVt, string mode, int wFlagsParam, int orderRev)
    {
        var sb = new StringBuilder();
        IntPtr pLrm = GetIDispatch(lrm);
        sb.AppendLine("  IDispatch*(lrm) = " + pLrm);
        if (pLrm == IntPtr.Zero) return sb.AppendLine("  lrm QI 失败").ToString();
        if (faces == null || faces.Length == 0) return sb.AppendLine("  没有几何").ToString();

        // 先把所有面转成 IDispatch*（任何一个失败就停下，不送半个数组进去）
        IntPtr[] dispPtrs = new IntPtr[faces.Length];
        for (int i = 0; i < faces.Length; i++)
        {
            dispPtrs[i] = GetIDispatch(faces[i]);
            sb.AppendLine("  IDispatch*(face[" + i + "]) = " + dispPtrs[i]);
            if (dispPtrs[i] == IntPtr.Zero) return sb.AppendLine("  face[" + i + "] QI 失败").ToString();
        }

        // 1) 元素指针按 elemVt 摆进 SAFEARRAY
        IntPtr psa = IntPtr.Zero;
        IntPtr vArray = IntPtr.Zero;

        if (elemVt == VT_VARIANT)
        {
            // SAFEARRAY(VT_VARIANT)：每个元素是【24 字节的 VARIANT】（x64），
            // 不是 8 字节指针 —— 之前按 8 字节布局写就是这个分支崩掉的原因。
            // VB 的 `Dim myArray()` 就是 Variant 数组，VB 运行时封的正是这个。
            // 元素 VARIANT 布局：vt@0(2) rsv@2(6) union@8(16)，pdispVal 在 @8
            IntPtr psaV = SafeArrayCreateVector(VT_VARIANT, 0, (ulong)dispPtrs.Length);
            if (psaV == IntPtr.Zero) return sb.AppendLine("  SAFEARRAY(VT_VARIANT) 创建失败").ToString();
            int pvD;
            int hrA2 = SafeArrayAccessData(psaV, out pvD);
            if (hrA2 < 0 || pvD == 0) { SafeArrayDestroy(psaV); return sb.AppendLine("  AccessData 失败").ToString(); }
            IntPtr pvD2 = new IntPtr(pvD);
            const int ELEM = 24;                       // 每个元素 24 字节 VARIANT (x64)
            for (int i = 0; i < dispPtrs.Length; i++)
            {
                IntPtr el = pvD2 + i * ELEM;
                VariantInit(el);
                Marshal.WriteInt16(el, 0, (short)VT_DISPATCH);
                Marshal.WriteIntPtr(el + 8, dispPtrs[i]);
            }
            sb.AppendLine("  SAFEARRAY(VT_VARIANT) n=" + dispPtrs.Length
                        + " 元素=24B VARIANT(vt=VT_DISPATCH) pvData=" + pvD2);
            psa = psaV;
            vArray = Marshal.AllocCoTaskMem(24);
            VariantInit(vArray);
            Marshal.WriteInt16(vArray, 0, (short)(VT_ARRAY | VT_VARIANT));   // 0x200C
            Marshal.WriteIntPtr(vArray, 8, psa);
        }
        else
        {
            // SAFEARRAY(VT_DISPATCH) 或 (VT_UNKNOWN)
            ushort outer = elemVt == VT_DISPATCH ? VT_DISPATCH : VT_UNKNOWN;
            // ⚠ SafeArrayCreateVector 建的是【惰性】数组：此时 pvData 可能还是 NULL
            // （实测本机就是这样），必须 SafeArrayAccessData 把它真正分配出来。
            psa = SafeArrayCreateVector(outer, 0, (ulong)dispPtrs.Length);
            if (psa == IntPtr.Zero) return sb.AppendLine("  SafeArrayCreateVector 失败").ToString();
            int pvDataRaw;
            int hrA = SafeArrayAccessData(psa, out pvDataRaw);
            IntPtr pvDataPtr = new IntPtr(pvDataRaw);
            sb.AppendLine("  SafeArrayCreateVector(0x" + outer.ToString("X") + ", n=" + dispPtrs.Length
                          + ") + AccessData hr=" + hrA + " pvData=" + pvDataPtr);
            if (hrA < 0 || pvDataPtr == IntPtr.Zero) { SafeArrayDestroy(psa); return sb.ToString(); }
            // 元素是 8 字节指针，布局已知，直接写，避开 PutElement 的解引用风险
            for (int i = 0; i < dispPtrs.Length; i++)
                Marshal.WriteInt64(pvDataPtr + i * 8, dispPtrs[i].ToInt64());
            vArray = Marshal.AllocCoTaskMem(24);
            VariantInit(vArray);
            Marshal.WriteInt16(vArray, 0, (short)(VT_ARRAY | outer));
            Marshal.WriteIntPtr(vArray, 8, psa);
        }

        // 2) RefGeom / DispArray 的空值形态。
        //    关键线索（2026-09-27 搜到的成功案例 alisamsam/Solidworks-MCP 的
        //    apply_fixture_fixed）：它调 AddRestraint3(0, None, errCode) —— 第二个参数
        //    传【None】，注释写 "Uses current selection"（面预先在 SW 里选中）。
        //    也就是说 cosworks 期望的用法是"走当前选择集"，而不是手工塞几何数组。
        //    AddRestraint3 在 2026 interop 里不存在，但这个"空值走选择集"的语义
        //    很可能对 AddRestraint 的 DispArray 同样成立 —— 从没试过。
        //    mode: empty=VT_EMPTY, null=VT_NULL, sel=VT_DISPATCH(空指针), miss=VT_ERROR
        //          arr=原来的 SAFEARRAY
        IntPtr vRef = Marshal.AllocCoTaskMem(24);
        VariantInit(vRef);
        if (mode == "sel")
        {
            Marshal.WriteInt16(vRef, 0, (short)VT_DISPATCH);
            Marshal.WriteIntPtr(vRef, 8, IntPtr.Zero);   // 空 IDispatch
        }
        else if (mode == "real")
        {
            // ★ 2026-09-27 论文（cosworks_paper.pdf p.114）证实：工作代码里
            //   RefGeom1 = CWBaseExcitationEntity  —— 一个【真实 COM 对象】（VT_DISPATCH 指向活对象）
            // 而不是 Nothing/VT_EMPTY。我此前只试过 VT_EMPTY / VT_NULL / 空 IDispatch 指针，
            // 从没试过"传真实对象"，这可能就是 E_INVALIDARG 的原因。
            IntPtr rp = dispPtrs.Length > 0 ? dispPtrs[dispPtrs.Length - 1] : IntPtr.Zero;
            Marshal.WriteInt16(vRef, 0, (short)VT_DISPATCH);
            Marshal.WriteIntPtr(vRef, 8, rp);
            sb.AppendLine("  RefGeom = VT_DISPATCH(真实面 IDispatch*) = " + rp);
        }
        else if (mode == "miss")
        {
            Marshal.WriteInt16(vRef, 0, (short)0x000A);         // VT_ERROR
            Marshal.WriteInt64(vRef, 8, unchecked((long)0x80020004));  // DISP_E_PARAMNOTFOUND
        }
        else
        {
            Marshal.WriteInt16(vRef, 0, (short)(mode == "null" ? VT_NULL : VT_EMPTY));
        }

        // DispArray 同样做成可选：mode=="sel2" 时 DispArray 也传 VT_DISPATCH 空指针，
        // 让 cosworks 完全走"当前选择集"路径（复刻 AddRestraint3 的 None 语义）。
        if (mode == "sel2")
        {
            VariantInit(vArray);
            Marshal.WriteInt16(vArray, 0, (short)VT_DISPATCH);
            Marshal.WriteIntPtr(vArray, 8, IntPtr.Zero);
            sb.AppendLine("  DispArray = VT_DISPATCH(NULL)  => 请求走【当前选择集】");
        }

        // 3) ErrorCode：先按【普通 VT_I4】传（不是 byref）。
        //    byref 结果参数在 COM 里走 pVarResult / 或需要 VT_I4|VT_BYREF 指向调用方缓冲区，
        //    （下方已改用正确的 VT_I4|VT_BYREF）

        IntPtr vType = MakeI4Variant(restraintType);

        // ErrorCode 反射确认是 Int32&[out] ⇒ COM 里必须是 VT_I4|VT_BYREF，
        // 指向调用方缓冲区。之前为避崩改成了普通 VT_I4（按值），那本身就是错的形态 ——
        // cosworks 收到的是"值"而不是"可写回的引用"，E_INVALIDARG 完全说得通。
        // 之前 byref 版本崩的原因是 SAFEARRAY 惰性分配（pvData=NULL），现已用
        // AccessData 修掉，可以安全用 byref 了。
        IntPtr errCell = Marshal.AllocHGlobal(sizeof(int));
        Marshal.WriteInt32(errCell, 0, 0x7FFFFFFF);      // 哨兵：调用后若被写回，说明 byref 生效
        IntPtr vErr = Marshal.AllocCoTaskMem(24);
        VariantInit(vErr);
        Marshal.WriteInt16(vErr, 0, (short)(VT_I4 | VT_BYREF));
        Marshal.WriteIntPtr(vErr, 8, errCell);

        // 4) DISPPARAMS。VARIANT x64 = 24 字节：vt@0(2) + rsv@2(6) + union@8(16)
        //    用按位复制而不是 VariantCopy —— 后者会 AddRef 源里 memcpy 进去的指针。
        //
        //    ⚠ 顺序做成可切换（raw_order）来【实测判定】，不靠争论：
        //      order=0 声明顺序：rgvarg[0]=第一个参数
        //              （这是 COM 规范的做法，.NET 自动封送也是这么填的）
        //      order=1 逆序：  rgvarg[0]=最后一个参数
        //              （有外部建议认为该逆序，理由是 stdcall 压栈顺序）
        IntPtr rgvarg = Marshal.AllocCoTaskMem(4 * 24);
        if (orderRev != 0)
        {
            CopyVariant(rgvarg + 0, vErr);      // [0] ErrorCode
            CopyVariant(rgvarg + 24, vRef);     // [1] RefGeom
            CopyVariant(rgvarg + 48, vArray);   // [2] DispArray
            CopyVariant(rgvarg + 72, vType);    // [3] NRestraintType
            sb.AppendLine("  rgvarg 顺序 = 【逆序】(ErrorCode,RefGeom,DispArray,NRestraintType)");
        }
        else
        {
            CopyVariant(rgvarg + 0, vType);     // [0] NRestraintType
            CopyVariant(rgvarg + 24, vArray);   // [1] DispArray
            CopyVariant(rgvarg + 48, vRef);     // [2] RefGeom
            CopyVariant(rgvarg + 72, vErr);     // [3] ErrorCode
            sb.AppendLine("  rgvarg 顺序 = 【声明顺序】(NRestraintType,DispArray,RefGeom,ErrorCode)");
        }

        // DISPPARAMS。⚠ 这里必须回到【20 字节】：曾改成 24 字节（补上 cNamedArgs）后，
        // 同一个组合从"返回 E_INVALIDARG"变成"Invoke 内部崩溃"（追踪文件证实崩在 Invoke 里）。
        // x64 下前三个字段是 rgvarg(8)+rgdispidNamedArgs(8)+cArgs(4)=20；第 4 个 cNamedArgs
        // 不写时 cosworks 并不读它（无名参数本来就该是 0）。保持 20 字节是已验证可用的。
        IntPtr pars = Marshal.AllocCoTaskMem(20);
        ZeroMemory(pars, 20);
        Marshal.WriteIntPtr(pars, 0, rgvarg);
        Marshal.WriteIntPtr(pars, 8, IntPtr.Zero);      // rgdispidNamedArgs 必须 NULL
        Marshal.WriteInt32(pars, 16, 4);                // cArgs = 4
        sb.AppendLine("  DISPPARAMS(20B): cArgs=4 rgdispidNamedArgs=NULL");

        IntPtr pVarResult = Marshal.AllocCoTaskMem(24);
        VariantInit(pVarResult);
        IntPtr pExcep = IntPtr.Zero;
        int argErr = 0;

        var inv = (Invoke)GetVtbl(pLrm, 6, typeof(Invoke));
        Guid iidNull = Guid.Empty;                 // riid = IID_NULL ⇒ 取返回值
        int wFlags = wFlagsParam;
        T("about-to-Invoke order=" + (orderRev == 0 ? "DECL" : "REV")
          + " elem=0x" + elemVt.ToString("X") + " wFlags=" + wFlags
          + " nfaces=" + (faces == null ? 0 : faces.Length));
        uint hr = inv(lrm, 3, ref iidNull, 0, wFlags, pars, pVarResult, pExcep, out argErr);
        T("invoke-returned hr=0x" + hr.ToString("X8"));

        sb.AppendLine("  Invoke(DispId=3, wFlags=" + wFlags + ") hr=0x" + hr.ToString("X8")
                    + " argErr=" + argErr);
        sb.AppendLine("  ErrorCode(byref 写回) = " + Marshal.ReadInt32(errCell, 0)
                    + (Marshal.ReadInt32(errCell, 0) != 0x7FFFFFFF ? "   *** 被写回 ⇒ byref 生效 ***" : "   (未被写回)"));
        short rvt = Marshal.ReadInt16(pVarResult, 0);
        sb.AppendLine("  pVarResult.vt = 0x" + rvt.ToString("X4")
                    + (rvt == VT_DISPATCH ? "  *** 返回了 COM 对象 ⇒ 调用成功 ***"
                     : rvt == VT_EMPTY ? " (无返回值)" : " (其它)"));
        if (hr == 0 && rvt == VT_DISPATCH)
            sb.AppendLine("  返回指针 = " + Marshal.ReadIntPtr(pVarResult, 8));

        // 清理：⚠ 不用 VariantClear(rgvarg) —— 里面的指针是我们 memcpy 进去的
        // （没有 AddRef），VariantClear 会 Release 它们 ⇒ 二次释放 ⇒ 崩。
        // 直接释放内存；psa 由 SafeArrayDestroy 负责（它会 Release 元素）。
        Marshal.FreeCoTaskMem(rgvarg); Marshal.FreeCoTaskMem(pars);
        VariantClear(pVarResult);
        Marshal.FreeCoTaskMem(pVarResult);
        Marshal.FreeCoTaskMem(vType); Marshal.FreeCoTaskMem(vArray);
        Marshal.FreeCoTaskMem(vRef); Marshal.FreeCoTaskMem(vErr);
        Marshal.FreeHGlobal(errCell);
        SafeArrayUnaccessData(psa);
        SafeArrayDestroy(psa);
        return sb.ToString();
    }
}


