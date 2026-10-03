# api-10 · Routing + PDM + 动画导出（AVI）契约抄录

> **抄录员纪律**（本文件全程遵守）
> 1. 每条都标**文件名 + 可搜索的原文片段**；★ **不写行号**（会漂移）。
> 2. **查不到就说查不到**；名字缺席 = 本机两套官方源里没有。
> 3. **不给建议、不下结论** —— 只抄。
>
> **来源代号**
> · **[T]** = `C:\swapi\types\<接口>\<成员>.md`（结构化签名）
> · **[E]** = `C:\swapi\examples\*.md`（官方例子）
> · **[N]** = `C:\swapi\enums\*.md`（枚举）
> · **[C]** = `D:\AI\SW\AI Solidworks\官方文档\SWhelp\<子目录>\<页面>`（CHM 解包）
> · **[D]** = `C:\swapi\docs\toolboxapi\*.md`
>
> **本机两套源的实测覆盖面（抄之前先核过）**
> · `C:\swapi\types\` 下与本路相关的目录只有 **4 个**：`IRoutingSettings` / `IConnectionPointFeatureData` / `IPDMDocManager` / `IPrimaryMemberPathSegmentFeatureData`。
> · **`IRoute\*` 目录：不存在**（`Get-ChildItem C:\swapi\types -Directory | ? {$_.Name -like "IRoute*"}` 返回空）。
> · **`IRouting*` 目录：不存在**（`? {$_.Name -like "IRout*"}` 只命中 `IRoutingSettings`）。
> · **`IEdm*` 目录：不存在**（全仓 grep `IEdm` 零命中）。
> · CHM 目录只有 `cosworks` / `sldworksapi` / `sldworksapivb6` / `swconst` **四个**，**没有 swmotionstudyapi**（`Get-ChildItem -Recurse -Directory | ? {$_.Name -match 'motion'}` 返回空）⇒ `IMotionStudy` / `IAVIParameter` 的**中文说明页在本机 CHM 里不存在**，只有 [T] 与 [E]。
> · `C:\swapi\enums\` 下**没有** `swUserPreferenceRouting*`、`swSaveAVIImageSize_e`、`swRoutingComponentGroupOption_e`。

---

# 一、Routing

## 1. `ISldWorks.GetRoutingSettings`（拿到 Routing 设置对象的入口）

**来源**：[T] `C:\swapi\types\ISldWorks\GetRoutingSettings.md`

1. **精确签名**（**0 个参数**）：
```
System.object / RoutingSettings GetRoutingSettings()
```
★ 该 .md 的 `**Signature**` 行逐字为：`RoutingSettings GetRoutingSettings()`；**Returns 段写 `[[IRoutingSettings]]`** —— 返回类型名与 Returns 段不一致，两处都抄在此。

2. **`## Remarks` 逐字摘录**：**该 .md 没有 `## Remarks` 段** ⇒ 查不到。

3. **官方例子的调用序** —— **[E] `Get_and_Save_Routing_Settings_Example_VB.md`**：
```vbnet
    Set swApp = Application.SldWorks
    Set routingSettings = swApp.GetRoutingSettings
```
★ 可搜索片段：`Set routingSettings = swApp.GetRoutingSettings`。
★ 例子的 **Preconditions** 第 1 条逐字：`1. In SOLIDWORKS, click Tools > Add-Ins, select SOLIDWORKS Routing, and` / `    click OK.`；第 2 条逐字：`2. In the IDE, click Tools > References and select` / `    SOLIDWORKS version Routing Type Library.`

4. **枚举**：签名里无枚举。

5. **废弃链**：无 Obsolete 标记。

**前置一句话**：官方例子的 Preconditions 要求先在 `Tools > Add-Ins` 里选中 **SOLIDWORKS Routing**，并在 IDE 里引用 **SOLIDWORKS version Routing Type Library**。
**配方一句话**：`swApp.GetRoutingSettings` 直接拿到 `RoutingSettings`，例子里紧接着用同一个对象调 `SaveRoutingSettingsToFile("c:\temp\routingSettings.sqy")`。

---

## 2. `IRoutingSettings`（13 个方法全抄）

**接口概述**：[T] `C:\swapi\types\IRoutingSettings\_overview.md`
· Description 逐字：`Allows access to various routing settings including those specified in **Tools > Options > System Options > Routing****.`
· front-matter 逐字：`method_count: 13`；`## Members` 段只有 `- **Methods**: 13`。
· 该 `_overview.md` **没有 `## Remarks` 段**。

### 2.1 `SaveRoutingSettingsToFile`

1. **精确签名**（**1 个参数**）：
```
System.bool SaveRoutingSettingsToFile( System.string RoutingSettingsFilename )
```
2. **`## Remarks`**：**该 .md 没有 `## Remarks` 段** ⇒ 查不到。
3. **例子调用序**（[E] `Get_and_Save_Routing_Settings_Example_VB.md`）：`boolstatus = routingSettings.SaveRoutingSettingsToFile("c:\temp\routingSettings.sqy")`
★ 可搜索片段：`SaveRoutingSettingsToFile("c:\temp\routingSettings.sqy")`；Postconditions 逐字：`1. Saves routing settings to c:\temp\routingSettings.sqy.`
4. **枚举**：无。
5. **废弃链**：无。

**前置一句话**：参数表逐字写 `file name must have an extension of **.sqy**`，例子的 Preconditions 第 3 条逐字 `3. Ensure that c:\temp exists.`
**配方一句话**：先 `Set routingSettings = swApp.GetRoutingSettings`，再 `SaveRoutingSettingsToFile("c:\temp\routingSettings.sqy")`。

### 2.2 `LoadRoutingSettingsFromFile`

1. **精确签名**（**1 个参数**）：`System.bool LoadRoutingSettingsFromFile( System.string RoutingSettingsFilename )`
2. **`## Remarks`**：无 ⇒ 查不到。
3. **例子调用序**：该 .md 的 `## Examples` 段为空；[E] `Get_and_Save_Routing_Settings_Example_VB.md` 里**没有调用它** ⇒ 例子里的实参 **查不到**。
4. **枚举**：无。
5. **废弃链**：无。

**前置一句话**：参数表逐字 `Full path name of the **.sqy** file from which to load the routing settings`。
**配方一句话**：查不到 —— 两套源里都没有给出调用它的例子。

### 2.3 `LoadDefaultRoutingSettings`

1. **精确签名**（**0 个参数**）：`void LoadDefaultRoutingSettings()`
2. **`## Remarks`**：无 ⇒ 查不到。
3. **例子调用序**：[E] `Get_and_Save_Routing_Settings_Example_VB.md` 未调用 ⇒ 查不到。
4. **枚举**：无。
5. **废弃链**：无。

**前置一句话**：查不到 —— 该 .md 除标题、Signature、See Also 外没有别的正文。
**配方一句话**：查不到。

### 2.4 `GetRoutingUserPreferenceIntegerValue`

1. **精确签名**（**1 个参数**）：`System.int GetRoutingUserPreferenceIntegerValue( System.int UserPreferenceValue )`
2. **`## Remarks`**：无 ⇒ 查不到。
3. **例子调用序**（[E] `Get_and_Save_Routing_Settings_Example_VB.md`，两个实参取值逐字）：
```vbnet
    Debug.Print "Rotation increment in degrees: " & routingSettings.GetRoutingUserPreferenceIntegerValue(swUserPreferenceRoutingInteger_e.swComponentRotationIncrementDegrees)
    Debug.Print "Enable minimum bend radius checks: " & routingSettings.GetRoutingUserPreferenceIntegerValue(swUserPreferenceRoutingInteger_e.swEnableMinimumBendRadiusChecks)
```
★ C# 版同段可搜索片段：`GetRoutingUserPreferenceIntegerValue((int)swUserPreferenceRoutingInteger_e.swComponentRotationIncrementDegrees)`（[E] `Get_and_Save_Routing_Settings_Example_CSharp.md`）。
4. **枚举**：参数表逐字 `User preference as defined in [[swUserPreferenceRoutingInteger_e]]`。
★ **`swUserPreferenceRoutingInteger_e` 的成员与数值：查不到** —— `C:\swapi\enums\` 下无该文件（全仓 grep 只命中 examples 与 members 的**引用**）；CHM `swconst` 目录里也没有 `swUserPreferenceRouting*` 页面。
5. **废弃链**：无。

**前置一句话**：参数表只点名枚举 `swUserPreferenceRoutingInteger_e`，**没有写任何“必须先加载 SOLIDWORKS Routing 加载项”以外的额外前置**。
**配方一句话**：传 `swUserPreferenceRoutingInteger_e.swComponentRotationIncrementDegrees` 或 `swEnableMinimumBendRadiusChecks`（例子里的两个实参；这两项的**数值抄不到**，见第 4 条）。

### 2.5 `SetRoutingUserPreferenceIntegerValue`

1. **精确签名**（**2 个参数**）：`System.bool SetRoutingUserPreferenceIntegerValue( System.int UserPreferenceValue, System.int Value )`
2. **`## Remarks`**：无 ⇒ 查不到。
3. **例子调用序**：[E] `Get_and_Save_Routing_Settings_Example_VB.md` **没有调用 Set 版** ⇒ 实参查不到。
4. **枚举**：`[[swUserPreferenceRoutingInteger_e]]`；**成员与数值查不到**（同 2.4）。
5. **废弃链**：无。

**前置一句话**：查不到 —— 只有参数表与 See Also。
**配方一句话**：查不到 —— 官方例子只读不写。

### 2.6 `GetRoutingUserPreferenceDoubleValue`

1. **精确签名**（**1 个参数**）：`System.double GetRoutingUserPreferenceDoubleValue( System.int UserPreferenceValue )`
2. **`## Remarks`**：无 ⇒ 查不到。
3. **例子调用序**（逐字）：
```vbnet
    Debug.Print "Slack %: " & routingSettings.GetRoutingUserPreferenceDoubleValue(swUserPreferenceRoutingDouble_e.swSlackPercentage)
    Debug.Print "Text size for connection and route points: " & routingSettings.GetRoutingUserPreferenceDoubleValue(swUserPreferenceRoutingDouble_e.swTextSizeForConnectionAndRoutePoints)
```
4. **枚举**：`[[swUserPreferenceRoutingDouble_e]]`；**成员与数值查不到**（`C:\swapi\enums\` 无该文件）。
5. **废弃链**：无。

**前置一句话**：查不到 —— 参数表只点名枚举。
**配方一句话**：传 `swUserPreferenceRoutingDouble_e.swSlackPercentage`（例子里形如 `"Slack %: "` 的那一句）；该项数值查不到。

### 2.7 `SetRoutingUserPreferenceDoubleValue`

1. **精确签名**（**2 个参数**）：`System.bool SetRoutingUserPreferenceDoubleValue( System.int UserPreferenceValue, System.double Value )`
2. **`## Remarks`**：无 ⇒ 查不到。
3. **例子调用序**：例子未调用 ⇒ 查不到。
4. **枚举**：`[[swUserPreferenceRoutingDouble_e]]`；数值查不到。
5. **废弃链**：无。

**前置一句话**：查不到。**配方一句话**：查不到。

### 2.8 `GetRoutingUserPreferenceStringValue`

1. **精确签名**（**2 个参数**）：`System.string GetRoutingUserPreferenceStringValue( System.int UserPreference, System.bool UseDefaultVal )`
★ 逐字含参数名 `UseDefaultVal`（**与 Set 版的 `Value` 不同名**）。
2. **`## Remarks`**：无 ⇒ 查不到。
3. **例子调用序**（逐字，第 2 个实参一律是 `True`）：
```vbnet
    Debug.Print "  Assembly template: " & routingSettings.GetRoutingUserPreferenceStringValue(swUserPreferenceRoutingFileLocations_e.swFileLocationsRoutingAssemblyTemplate, True)
    Debug.Print "  Cable library: " & routingSettings.GetRoutingUserPreferenceStringValue(swUserPreferenceRoutingFileLocations_e.swFileLocationsRoutingCableLibrary, True)
    Debug.Print "  Component library: " & routingSettings.GetRoutingUserPreferenceStringValue(swUserPreferenceRoutingFileLocations_e.swFileLocationsRoutingComponentLibrary, True)
    Debug.Print "  Covering library: " & routingSettings.GetRoutingUserPreferenceStringValue(swUserPreferenceRoutingFileLocations_e.swFileLocationsRoutingCoveringLibrary, True)
    Debug.Print "  Interconnects library: " & routingSettings.GetRoutingUserPreferenceStringValue(swUserPreferenceRoutingFileLocations_e.swFileLocationsRoutingInterconnectsLibrary, True)
    Debug.Print "  Pipe tube covering library: " & routingSettings.GetRoutingUserPreferenceStringValue(swUserPreferenceRoutingFileLocations_e.swFileLocationsRoutingPipeTubeCoveringLibrary, True)
    Debug.Print "  Standard cable: " & routingSettings.GetRoutingUserPreferenceStringValue(swUserPreferenceRoutingFileLocations_e.swFileLocationsRoutingStandardCable, True)
    Debug.Print "  Standard tubes: " & routingSettings.GetRoutingUserPreferenceStringValue(swUserPreferenceRoutingFileLocations_e.swFileLocationsRoutingStandardTubes, True)
    Debug.Print "  Tag schemes: " & routingSettings.GetRoutingUserPreferenceStringValue(swUserPreferenceRoutingFileLocations_e.swFileLocationsRoutingTagSchemes, True)
    Debug.Print "  Routing library path: " & routingSettings.GetRoutingUserPreferenceStringValue(swUserPreferenceRoutingFileLocations_e.swRoutingLibraryPath, True)
```
4. **枚举**：`[[swUserPreferenceRoutingFileLocations_e]]`；**成员与数值查不到**（`C:\swapi\enums\` 无该文件）。
5. **废弃链**：无。

**前置一句话**：参数表逐字 `UseDefaultVal: True to use the default, false to not`。
**配方一句话**：例子对 10 个库路径项一律 `(…, True)`，即第二个实参恒为 `True`。

### 2.9 `SetRoutingUserPreferenceStringValue`

1. **精确签名**（**2 个参数**）：`System.bool SetRoutingUserPreferenceStringValue( System.int UserPreference, System.string Value )`
2. **`## Remarks`**：无 ⇒ 查不到。
3. **例子调用序**：例子未调用 ⇒ 查不到。
4. **枚举**：`[[swUserPreferenceRoutingFileLocations_e]]`；数值查不到。
5. **废弃链**：无。

**前置一句话**：查不到。**配方一句话**：查不到。

### 2.10 `GetRoutingUserPreferenceToggle`

1. **精确签名**（**1 个参数**）：`System.bool GetRoutingUserPreferenceToggle( System.int UserPreferenceToggle )`
★ 形参名 `UserPreferenceToggle`（**与 Set 版的 `UserPreferenceValue` 不同名**）。
2. **`## Remarks`**：无 ⇒ 查不到。
3. **例子调用序**（逐字，15 个实参）：
```vbnet
    Debug.Print "Always use default document template? " & routingSettings.GetRoutingUserPreferenceToggle(swUserPreferenceRoutingToggle_e.swAlwaysUseDefaultDocumentTemplate)
    Debug.Print "Automatically add dimensions to route stubs? " & routingSettings.GetRoutingUserPreferenceToggle(swUserPreferenceRoutingToggle_e.swAutomaticallyAddDimensionToRouteStubs)
    Debug.Print "Automatically create sketch fillets? " & routingSettings.GetRoutingUserPreferenceToggle(swUserPreferenceRoutingToggle_e.swAutomaticallyCreateSketchFillets)
    Debug.Print "Automatically route on drop of clips? " & routingSettings.GetRoutingUserPreferenceToggle(swUserPreferenceRoutingToggle_e.swAutomaticallyRouteOnDropOfClips)
    Debug.Print "Automatically route on drop of flange connectors? " & routingSettings.GetRoutingUserPreferenceToggle(swUserPreferenceRoutingToggle_e.swAutomaticallyRouteOnDropOfFlangeConnectors)
    Debug.Print "Create custom fittings? " & routingSettings.GetRoutingUserPreferenceToggle(swUserPreferenceRoutingToggle_e.swCreateCustomFittings)
    Debug.Print "Create pipes on open line segments? " & routingSettings.GetRoutingUserPreferenceToggle(swUserPreferenceRoutingToggle_e.swCreatePipesOnOpenLineSegments)
    Debug.Print "Display error balloons? " & routingSettings.GetRoutingUserPreferenceToggle(swUserPreferenceRoutingToggle_e.swDisplayErrorBalloons)
    Debug.Print "Enable route error checking? " & routingSettings.GetRoutingUserPreferenceToggle(swUserPreferenceRoutingToggle_e.swEnableRouteErrorChecking)
    Debug.Print "Include coverings in bills of material? " & routingSettings.GetRoutingUserPreferenceToggle(swUserPreferenceRoutingToggle_e.swIncludeCoveringsInBOM)
    Debug.Print "Save route assembly externally? " & routingSettings.GetRoutingUserPreferenceToggle(swUserPreferenceRoutingToggle_e.swSaveRouteAssemblyExternally)
    Debug.Print "Save route parts externally? " & routingSettings.GetRoutingUserPreferenceToggle(swUserPreferenceRoutingToggle_e.swSaveRoutePartsExternally)
    Debug.Print "Use automatic naming for route parts? " & routingSettings.GetRoutingUserPreferenceToggle(swUserPreferenceRoutingToggle_e.swUseAutomaticNamingForRouteParts)
    Debug.Print "User centerline dimension? " & routingSettings.GetRoutingUserPreferenceToggle(swUserPreferenceRoutingToggle_e.swUseCenterlineDim)
    Debug.Print "Use triad to position and orient components? " & routingSettings.GetRoutingUserPreferenceToggle(swUserPreferenceRoutingToggle_e.swUseTriadToPosAndOrientComp)
```
4. **枚举**：`[[swUserPreferenceRoutingToggle_e]]`；**成员与数值查不到**。
5. **废弃链**：无。

**前置一句话**：Returns 段逐字 `True if on, false if off`。
**配方一句话**：例子把 15 个 toggle 项各读一遍（枚举成员名见上，数值查不到）。

### 2.11 `SetRoutingUserPreferenceToggle`

1. **精确签名**（**2 个参数**）：`void SetRoutingUserPreferenceToggle( System.int UserPreferenceValue, System.bool OnFlag )`
2. **`## Remarks`**：无 ⇒ 查不到。
3. **例子调用序**：例子未调用 ⇒ 查不到。
4. **枚举**：`[[swUserPreferenceRoutingToggle_e]]`；数值查不到。
5. **废弃链**：无。

**前置一句话**：查不到 —— 该 .md 连 `## Returns` 段都没有（返回 `void`）。
**配方一句话**：查不到。

### 2.12 `GetFromToListHeaderDefinitions`

1. **精确签名**（**12 个参数，全部 `out string`**）：
```
System.bool GetFromToListHeaderDefinitions( out System.string WireNameHdr, out System.string FromRefHdr, out System.string FromPinHdr, out System.string FromPartnoHdr, out System.string ToRefHdr, out System.string ToPinHdr, out System.string ToPartnoHdr, out System.string CableNameHdr, out System.string CoreNameHdr, out System.string ColourHdr, out System.string WireSpecHdr, out System.string OtherAttribHdr )
```
2. **`## Remarks`**：无 ⇒ 查不到。
3. **例子调用序**（[E] `Get_and_Save_Routing_Settings_Example_VB.md`）—— ★ **VBA 例子里把 `out` 形参按值传**，实参先全置空串：
```vbnet
    wireNameHdr = ""
    fromRefHdr = ""
    ...
    otherAttribHdr = ""
    Set swApp = Application.SldWorks
    Set routingSettings = swApp.GetRoutingSettings
    boolstatus = routingSettings.SaveRoutingSettingsToFile("c:\temp\routingSettings.sqy")
    boolstatus = routingSettings.GetFromToListHeaderDefinitions(wireNameHdr, fromRefHdr, fromPinHdr, fromPartNoHdr, toRefHdr, toPinHdr, toPartNoHdr, cableNameHdr, coreNameHdr, colourHdr, wireSpecHdr, otherAttribHdr)
```
★ 声明逐字：`Dim wireNameHdr As String, fromRefHdr As String, fromPinHdr As String, fromPartNoHdr As String, toRefHdr As String, toPinHdr As String, toPartNoHdr As String, cableNameHdr As String, coreNameHdr As String, colourHdr As String, wireSpecHdr As String, otherAttribHdr As String`
★ 注意形参名拼写：签名是 `FromPartnoHdr`（小写 n 的 no），例子的变量是 `fromPartNoHdr`（大写 N）—— 两处都抄。
4. **枚举**：无。
5. **废弃链**：无。

**前置一句话**：查不到 —— 12 个 `out` 形参没有写任何“必须先有什么”的前置。
**配方一句话**：先声明 12 个 `As String` 并全赋 `""`，再按序传进去（例子里就是这个顺序）。

### 2.13 `SetFromToListHeaderDefinitions`

1. **精确签名**（**12 个参数，全部 `string`（非 out）**）：
```
System.bool SetFromToListHeaderDefinitions( System.string WireNameHdr, System.string FromRefHdr, System.string FromPinHdr, System.string FromPartnoHdr, System.string ToRefHdr, System.string ToPinHdr, System.string ToPartnoHdr, System.string CableNameHdr, System.string CoreNameHdr, System.string ColourHdr, System.string WireSpecHdr, System.string OtherAttribHdr )
```
2. **`## Remarks`**：无 ⇒ 查不到。
3. **例子调用序**：[E] `Get_and_Save_Routing_Settings_Example_VB.md` **只调了 Get 版**，没有调 Set 版 ⇒ 查不到。
4. **枚举**：无。
5. **废弃链**：无。

**前置一句话**：查不到。
**配方一句话**：查不到 —— 官方例子只演示 Get 版（12 个 `out` 形参）。

---

## 3. `IAssemblyDoc.GetRouteManager`（拿 SOLIDWORKS Routing API 的入口）

**来源**：[T] `C:\swapi\types\IAssemblyDoc\GetRouteManager.md`

1. **精确签名**（**0 个参数**）：`System.object GetRouteManager()`
2. **`## Remarks`**：该 .md **没有 `## Remarks` 段** ⇒ 查不到。
3. **官方例子的调用序** —— ★ **[C] `sldworksapi\Create_Auto_Route_Example_VB.htm`**（★ **[E] `Create_Auto_Route_Example_VB.md` 的 `## Code` 段是空的** —— 逐字只有 `Sub main()` / `End Sub`，**调用序只能从 CHM 那页拿**）：
```vbnet
Dim swModel As SldWorks.ModelDoc2
Dim swTopLevelAssembly As SldWorks.AssemblyDoc
Dim rtRouteManager As SWRoutingLib.RouteManager
Dim autoRoute As SWRoutingLib.autoRoute
Dim resultCode, boolstatus As Long
' Get the RouteManager from the top-level assembly
Set rtRouteManager = swTopLevelAssembly.GetRouteManager
If rtRouteManager Is Nothing Then
Debug.Print "No RouteManager found in top-level document: " & swTopLevelAssembly.GetPathName
Exit Sub
End If
rtRouteManager.EditRoute
Set autoRoute = rtRouteManager.GetAutoRoute
autoRoute.ShowGuidelines
boolstatus = swModel.Extension.SelectByID2("Point3", "SKETCHPOINT", -0.457835, 0.10795, -0.2032, True, 0, Nothing, 0)
boolstatus = swModel.Extension.SelectByID2("Point8", "SKETCHPOINT", -0.218948, 0.0508, -0.470281, True, 0, Nothing, 0)
resultCode = autoRoute.CreatePointToPointAutoRoute(swOrthogonalMode)
rtRouteManager.ExitRoute
swTopLevelAssembly.EditAssembly
```
★ **接口名与类型库名在这里是 `SWRoutingLib.RouteManager` / `SWRoutingLib.autoRoute`**（不是 `IRouteManager`）。
★ Preconditions 逐字：`1. In SOLIDWORKS Design, click Tools > Add-Ins > SOLIDWORKS Routing.` / `6. Select the assembly that contains Route1 in the FeatureManager design tree.`
4. **枚举**：签名里无枚举。例子的实参用 `swOrthogonalMode`（该常量的**归属与数值查不到** —— `C:\swapi\enums\` 里没有对应文件）。
5. **废弃链**：无 Obsolete 标记。

**前置一句话**：**`IRouteManager` 的成员逐条抄不到** —— `C:\swapi\types\` 下**没有 `IRouteManager` 目录**，CHM `sldworksapi` 目录里也**没有 `IRouteManager` 页面**（只有 `IAssemblyDoc~GetRouteManager.html`）；`EditRoute` / `GetAutoRoute` / `ShowGuidelines` / `CreatePointToPointAutoRoute` / `ExitRoute` 这几个调用**只出现在例子里，没有签名页**。
**配方一句话**：`GetRouteManager` → `rtRouteManager.EditRoute` → `GetAutoRoute` → `ShowGuidelines` → **先选两个 `SKETCHPOINT`** → `CreatePointToPointAutoRoute(swOrthogonalMode)` → `ExitRoute` → `swTopLevelAssembly.EditAssembly`。

---

## 4. `IAssemblyDoc.IsRouteAssembly`

**来源**：[T] `C:\swapi\types\IAssemblyDoc\IsRouteAssembly.md`

1. **精确签名**（**0 个参数**）：`System.bool IsRouteAssembly()`
2. **`## Remarks`**：无 ⇒ 查不到。
3. **例子调用序**：该 .md 的 `## Examples` 段为空；[C] `Create_Auto_Route_Example_VB.htm` 里也没有出现 `IsRouteAssembly` ⇒ 查不到。
4. **枚举**：无。
5. **废弃链**：无。

**前置一句话**：查不到。
**配方一句话**：查不到 —— 两套源的例子里都没有调用它。

---

## 5. `IModelDoc2.InsertRoutePoint`

**来源**：[T] `C:\swapi\types\IModelDoc2\InsertRoutePoint.md`

1. **精确签名**（**0 个参数**）：`void InsertRoutePoint()`
2. **`## Remarks` 逐字摘录**（★ 这是本节最关键的前置，原文两句）：
   > `If the selection set is not complete, then the **Insert Route Point** dialog is displayed.`
   >
   > `The route point is the point on the fitting that aligns with the sketch point when the fitting is inserted.`
3. **例子调用序**：[T] 该 .md 的 `## Examples` 段为空；[E] 三个 Routing 例子里都没有调它 ⇒ 查不到。
4. **枚举**：无。
5. **废弃链**：无。

**前置一句话**：Remarks 第一句逐字点明 —— **选区不完整就会弹「Insert Route Point」对话框**。
**配方一句话**：查不到 —— 官方例子没给调用序；Remarks 只说明“选区不完整 ⇒ 弹窗”，没有给实参。

---

## 6. `IModelDoc2.EditRoute`

**来源**：[T] `C:\swapi\types\IModelDoc2\EditRoute.md`

1. **精确签名**（**0 个参数**）：`void EditRoute()`
2. **`## Remarks`**：该 .md **没有 `## Remarks` 段** ⇒ 查不到。
3. **例子调用序**：[T] 该 .md 的 `## Examples` 段为空；★ 但 **[C] `Create_Auto_Route_Example_VB.htm`** 里出现了**同名不同宿主**的调用（落在 RouteManager 上，不是 IModelDoc2）：`rtRouteManager.EditRoute` / `rtRouteManager.ExitRoute` / `swTopLevelAssembly.EditAssembly` ⇒ **`IModelDoc2.EditRoute` 本身的调用序查不到**。
4. **枚举**：无。
5. **废弃链**：无。

**前置一句话**：查不到 —— 只有一句 Description 逐字 `Makes the last selected route the active route.`
**配方一句话**：查不到。

---

## 7. `IModelDocExtension.GetRoutingComponentManager`

**来源**：[T] `C:\swapi\types\IModelDocExtension\GetRoutingComponentManager.md`

1. **精确签名**（**0 个参数**）：`System.object GetRoutingComponentManager()`
2. **`## Remarks`**：无 ⇒ 查不到。
3. **例子调用序**：该 .md 的 `## Examples` 段为空 ⇒ 查不到。
4. **枚举**：无。
5. **废弃链**：无。

**前置一句话**：查不到。
**配方一句话**：查不到。
★ **返回接口 `IRoutingComponentManager` 的成员逐条抄不到** —— `C:\swapi\types\` 下**没有该目录**；CHM 里只有 [C] `sldworksapi\SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IModelDocExtension~GetRoutingComponentManager.html` 这一页方法页，**没有接口页**。

---

## 8. `IFeatureManager.InsertConnectionPoint`（Routing 建连接点的主入口，14 个参数）

**来源**：[T] `C:\swapi\types\IFeatureManager\InsertConnectionPoint.md`

1. **精确签名**（**14 个参数**）：
```
System.bool InsertConnectionPoint( System.int Type, System.int SubType, System.bool ReverseDirection, System.double Diameter, System.double StubLength, System.double MinimumStraight, System.double EndLengthAdjustment, System.double ConductorSplitLength, System.string SchematicPinID, System.double CableWidth, System.double CableThickness, System.bool SwitchPin1Position, System.string SpecificationFieldName, System.string SpecificationValue )
```
2. **`## Remarks` 逐字摘录**（★ 前置与 mark 都在这里）：
   > `This method only works when the SOLIDWORKS Routing add-in is loaded (click **Tools > Add-Ins**  and select **SOLIDWORKS Routing**). This method currently supports part documents only.`
   >
   > `Use [[IModelDocExtension::SelectByID2]] with:`
   >
   > `- Mark = 1, which can be any one of the following entities to indicate the origin of a route:`
   > `  - Circular edge`
   > `  - Circular face`
   > `  - Face or plane plus a sketch point or vertex (select the plane or face where the routing segment exits the fitting, then select the sketch point that defines the end of the adjoining route segment)`
   >
   > `- Mark = 2, which can be a reference axis or edge to indicate which entity to align the width of the cable (for ribbon cables only)`
   >
   > `See the SOLIDWORKS Help for details about connection points and routing.`

   ★ **[C] 交叉核对**：`sldworksapi\SolidWorks.Interop.sldworks~SolidWorks.Interop.sldworks.IFeatureManager~InsertConnectionPoint.html` 的 Remarks 段逐字含同一句 `Mark = 1, which can be any one of the following entities to indicate the origin of a route:` 与 `Mark = 2, which can be a&nbsp;reference axis or edge&nbsp;to indicate which entity to align the width of the cable (for ribbon cables only)` —— 两源一致。
   ★ ★ 参数表里还有一条逐字的 **NOTE**：`For ribbon cables, leave stub length at 0 or set it to a value greater than half the width of the cable to assure that folds made near the connector can be created properly.`
3. **官方例子的调用序** —— ★ **[E] `Insert_Connection_Point_Example_VB.md` 的 `## Code` 段是空的**（逐字只有 `Sub main()` / `End Sub`）。它的 Preconditions 逐字：
   `' 1. Load the SOLIDWORKS Routing Add-in (click` / `' Tools > Add-Ins > SOLIDWORKS Routing).`
   ⇒ **实参调用序在 [E] 里查不到**。
4. **枚举**：
   · `Type` 逐字：`Route type as defined in [[swConnectionPointType_e]]`
     ★ [N] `C:\swapi\enums\swConnectionPointType_e.md`（`enum_member_count: 4`，Description 逐字 `Connection point types.`）：

     | Member | Value |
     | --- | --- |
     | `swConnectionPoint_Electrical` | 3 |
     | `swConnectionPoint_FabricatedPipe` | 2 |
     | `swConnectionPoint_Tube` | 1 |
     | `swConnectionPoint_UserDefined` | 4 |

   · `SubType` 逐字：`Electrical route sub-type as defined in [[swElectricalConnectionPointType_e]]`
     ★ [N] `C:\swapi\enums\swElectricalConnectionPointType_e.md`（`enum_member_count: 6`，Description 逐字 `Electrical connection point types.`）：

     | Member | Value |
     | --- | --- |
     | `swElectricalConnectionPoint_CableOrWire` | 2 |
     | `swElectricalConnectionPoint_CableTray` | 5 |
     | `swElectricalConnectionPoint_Conduit` | 3 |
     | `swElectricalConnectionPoint_Harness` | 1 |
     | `swElectricalConnectionPoint_RibbonCable` | 4 |
     | `swElectricalConnectionPoint_Trunking` | 6 |

   ★ ★ **[C] 交叉核对**：`swconst\SolidWorks.Interop.swconst~SolidWorks.Interop.swconst.swConnectionPointType_e.html` 与 `swconst\SolidWorks.Interop.swconst~SolidWorks.Interop.swconst.swElectricalConnectionPointType_e.html` 两页**存在**。
5. **废弃链**：无 Obsolete 标记。

**前置一句话**：Remarks 第一句逐字 —— 必须先加载 **SOLIDWORKS Routing 加载项**，且**当前只支持零件文档**。
**配方一句话**：用 `IModelDocExtension.SelectByID2` 选实体并**打 mark：mark=1 给路由起点（圆边 / 圆面 / 面或基准面+草图点或顶点）**，**mark=2 给线缆宽度对齐用的参考轴或边（仅带状电缆）**；14 个实参里 `Type` 取 `swConnectionPoint_*`、`SubType` 取 `swElectricalConnectionPoint_*`。

---

## 9. `IConnectionPointFeatureData`（12 个成员全抄）

**接口概述**：[T] `C:\swapi\types\IConnectionPointFeatureData\_overview.md`
· Description 逐字：`Allows access to a connection point feature.`
· **`## Remarks` 逐字**（只有一句）：
  > `See SOLIDWORKS Help for more information about connection point features.`
· front-matter 逐字：`property_count: 9` / `method_count: 3`。

> ★ **名字注意**：本机两套源里**没有 `IConnectionPoint` 这个接口**，只有 **`IConnectionPointFeatureData`**；官方例子里的变量类型也写作 `SldWorks.ConnectionPointFeatureData`（无 `I`）。

### 9.1 `RouteType`

1. **精确签名**（属性，**0 个参数**）：`System.int RouteType {get; set;}`
2. **`## Remarks`**：无 ⇒ 查不到。
3. **例子调用序**（[E] `Get_and_Set_Connection_Point_Feature_Data_Example_VB.md`，★ 实参是**裸数字**）：
```vbnet
        Debug.Print "Get route type = " & cPointData.RouteType
        cPointData.RouteType = 2
        Debug.Print "Set route type = " & cPointData.RouteType
```
4. **枚举**：Returns 段逐字 `Route type as defined in [[swModelRouteType_e]]`。
   ★ [N] `C:\swapi\enums\swModelRouteType_e.md`（`enum_member_count: 9`，Description 逐字 `Route types for connection points.`）：

   | Member | Value |
   | --- | --- |
   | `swModelRouteType_AnyRouteType` | 7 = Any |
   | `swModelRouteType_Electrical` | 6 = Electrical |
   | `swModelRouteType_FabricatedPipe` | 2 = Fabricated pipe |
   | `swModelRouteType_FormedPipe` | 3 = Formed pipe |
   | `swModelRouteType_Harness` | 0 = Harness |
   | `swModelRouteType_MixedRouteType` | 8 = Mixed |
   | `swModelRouteType_Trunking` | 4 = Trunking |
   | `swModelRouteType_Tube` | 1 = Tube |
   | `swModelRouteType_UnknownRouteType` | 5 = Unknown |

   ★ 例子里的 `= 2` 与 `swModelRouteType_FabricatedPipe = 2` **对得上**（只抄事实，不断言）。
   ★ **[C] 交叉核对**：`swconst\SolidWorks.Interop.swconst~SolidWorks.Interop.swconst.swModelRouteType_e.html` 存在。
5. **废弃链**：无。

**前置一句话**：查不到 —— 只有 Description + Returns，没有 Remarks。
**配方一句话**：例子直接写 `cPointData.RouteType = 2`。

### 9.2 `RouteSubType`

1. **精确签名**（**0 个参数**）：`System.int RouteSubType {get; set;}`
2. **`## Remarks`**：无 ⇒ 查不到。
3. **例子调用序**：`cPointData.RouteSubType = 3`
4. **枚举**：Returns 段逐字 `Electrical route sub-type as defined in [[swElectricalSubType_e]]`。
   ★ [N] `C:\swapi\enums\swElectricalSubType_e.md`（`enum_member_count: 6`，Description 逐字 `Electrical route sub types for connection points.`）：

   | Member | Value |
   | --- | --- |
   | `swElectricalSubType_ElectricalCableWire` | 1 = Cable wire |
   | `swElectricalSubType_ElectricalConduit` | 2 = Conduit |
   | `swElectricalSubType_ElectricalHarness` | 0 = Harness |
   | `swElectricalSubType_ElectricalRibbonCable` | 30 = Ribbon cable |
   | `swElectricalSubType_ElectricalStandardCable` | 3 = Standard cable |
   | `swElectricalSubType_NotElectrical` | 20 = Not electrical |

5. **废弃链**：无。

**前置一句话**：查不到。
**配方一句话**：例子直接写 `cPointData.RouteSubType = 3`。

### 9.3 `RouteDiameter`

1. **精确签名**（**0 个参数**）：`System.double RouteDiameter {get; set;}`
2. **`## Remarks`**：无 ⇒ 查不到。
3. **例子调用序**（逐字）：
```vbnet
                Debug.Print "Get diameter = " & cPointData.RouteDiameter
        cPointData.RouteDiameter = 0.011
        Debug.Print "Set diameter = " & cPointData.RouteDiameter
```
4. **枚举**：无。
5. **废弃链**：无。

**前置一句话**：查不到。
**配方一句话**：例子写 `0.011`（**米制值，未做单位换算**；只抄原文）。

### 9.4 `StubLength`

1. **精确签名**（**0 个参数**）：`System.double StubLength {get; set;}`
2. **`## Remarks`**：无 ⇒ 查不到。
3. **例子调用序**：`cPointData.StubLength = 0.009`
4. **枚举**：无。
5. **废弃链**：无。

**前置一句话**：查不到。
**配方一句话**：例子写 `0.009`。

### 9.5 `PortID`

1. **精确签名**（**0 个参数**）：`System.string PortID {get; set;}`
2. **`## Remarks`**：无 ⇒ 查不到。
3. **例子调用序**：`cPointData.PortID = "newPortID"`
4. **枚举**：无。
5. **废弃链**：无。

**前置一句话**：查不到。**配方一句话**：例子写 `"newPortID"`。

### 9.6 `ElectricalPinID`

1. **精确签名**（**0 个参数**）：`System.string ElectricalPinID {get; set;}`
2. **`## Remarks`**：无 ⇒ 查不到。
3. **例子调用序**：`cPointData.ElectricalPinID = "zxc"`
4. **枚举**：无。
5. **废弃链**：无。

**前置一句话**：查不到。**配方一句话**：例子写 `"zxc"`。

### 9.7 `Name2`

1. **精确签名**（**0 个参数**）：`System.string Name2 {get; set;}`
2. **`## Remarks`**：无 ⇒ 查不到。
3. **例子调用序**：
```vbnet
        Debug.Print "Get CPoint name = " & cPointData.Name2
        cPointData.Name2 = "myCPoint"
        Debug.Print "Set CPoint name = " & cPointData.Name2
```
4. **枚举**：无。
5. **废弃链**：无。

**前置一句话**：查不到。
**配方一句话**：例子写 `"myCPoint"`，Postconditions 逐字 `2. CPoint1 is now MyCPoint in the FeatureManager design tree.`

### 9.8 `Location`

1. **精确签名**（**0 个参数**）：`System.object Location {get;}` —— **只有 get，没有 set**。
2. **`## Remarks`**：无 ⇒ 查不到。
3. **例子调用序**（★ 官方按 0/1/2 下标取 Variant）：
```vbnet
        vLocation = cPointData.Location
        xLoc = vLocation(0)
        yLoc = vLocation(1)
        zLoc = vLocation(2)
        Debug.Print "Get location: " & xLoc & " " & yLoc & " " & zLoc
```
4. **枚举**：无。
5. **废弃链**：无。

**前置一句话**：查不到。
**配方一句话**：返回值按 `vLocation(0)/(1)/(2)` 下标拆成 x/y/z。

### 9.9 `Direction`

1. **精确签名**（**0 个参数**）：`System.object Direction {get;}` —— **只有 get**。
2. **`## Remarks`**：无 ⇒ 查不到。
3. **例子调用序**：`xDir = vDirection(0)` / `yDir = vDirection(1)` / `zDir = vDirection(2)`（前一行 `vDirection = cPointData.Direction`）。
4. **枚举**：无。
5. **废弃链**：无。

**前置一句话**：查不到。**配方一句话**：同 Location，按下标拆 3 个 double。

### 9.10 `AccessSelections`

1. **精确签名**（**2 个参数**）：`System.bool AccessSelections( System.object TopDoc, System.object Component )`
2. **`## Remarks` 逐字摘录**（★ 前置表 + 回滚状态都在这里）：
   > `**To modify a feature in a...**` / `**Then...**`
   >
   > `Part`
   > `- TopDoc argument is the [[IModelDoc2]] for the part`
   > `- Component argument is NULL`
   >
   > `Assembly`
   > `- TopDoc is the [[IModelDoc2]] object for the assembly`
   > `- Component argument is the [[IComponent2]] object in which the feature is to be modified`
   >
   > `This method puts the model into a rollback state to allow access to the selections that define this feature. You must use either of the following methods to restore the rollback state:`
   > `- [[IFeature::ModifyDefinition]] and [[IFeature::IModifyDefinition2]] if you modified the feature`
   > `- [[IConnectionPointFeatureData::ReleaseSelectionAccess]] if you did not`
3. **例子调用序**：★ **[E] `Get_and_Set_Connection_Point_Feature_Data_Example_VB.md` 里的例子根本没有调 `AccessSelections`**（它直接 `Set cPointData = featData`）⇒ 调用序查不到。例子逐字用的是另一条路：
```vbnet
        boolstatus = Part.Extension.SelectByID2("CPoint1", "CONNECTIONPOINT", 0, 0, 0, False, 0, Nothing, 0)
        selCount = selMgr.GetSelectedObjectCount2(-1)
    If (selCount > 0) Then
        selType = selMgr.GetSelectedObjectType3(1, -1)
        Set selObj = selMgr.GetSelectedObject6(1, -1)
        If (selType = SwConst.swSelCONNECTIONPOINTS) Then
            Set selFeat = selObj
        End If
    End If
        Part.ClearSelection2 True
        Dim featData As Object
    Set featData = selFeat.GetDefinition()
        Dim cPointData As SldWorks.ConnectionPointFeatureData
    Set cPointData = featData
```
★ 收尾逐字：`Part.ForceRebuild3(false)`。
4. **枚举**：无。
5. **废弃链**：无。

**前置一句话**：Remarks 逐字 —— 零件文档传 `IModelDoc2` + `Component=NULL`；装配体传装配体的 `IModelDoc2` + 待改特征所在的 `IComponent2`；**调用后模型进入回滚状态**。
**配方一句话**：要么用 `ModifyDefinition`/`IModifyDefinition2` 收尾，要么用 `ReleaseSelectionAccess` 收尾（Remarks 原话二选一）。

### 9.11 `IAccessSelections`

1. **精确签名**（**2 个参数**）：`System.bool IAccessSelections( ModelDoc2 TopDoc, Component2 Component )`
★ **参数类型不是 `System.object`** —— 与 9.10 逐字不同（`ModelDoc2` / `Component2`）。
2. **`## Remarks`**：与 9.10 **逐字相同**（同一段表 + 同一段回滚说明）。
3. **例子调用序**：例子未调用 ⇒ 查不到。
4. **枚举**：无。
5. **废弃链**：无。

**前置一句话**：Remarks 与 `AccessSelections` 逐字相同（回滚状态 + 二选一收尾）。
**配方一句话**：查不到 —— 官方例子没调它。

### 9.12 `ReleaseSelectionAccess`

1. **精确签名**（**0 个参数**）：`void ReleaseSelectionAccess()`
2. **`## Remarks` 逐字摘录**：
   > `[[IConnectionPointFeatureData::AccessSelections]] and [[IConnectionPointFeatureData::IAccessSelections]] put the model into a rollback state to allow access to the selections that define the connection point feature.`
   >
   > `Use this method to restore the rollback state if you did not modify the feature or use [[IFeature::ModifyDefinition]] or [[IFeature::IModifyDefinition2]] if you did.`
3. **例子调用序**：例子未调用 ⇒ 查不到。
4. **枚举**：无。
5. **废弃链**：无。

**前置一句话**：Remarks 逐字 —— 它是**恢复回滚状态**的那一个（没改特征时用）。
**配方一句话**：查不到 —— 官方例子没调它。

---

## 10. `IBomFeature.RoutingComponentGrouping`

**来源**：[T] `C:\swapi\types\IBomFeature\RoutingComponentGrouping.md`

1. **精确签名**（**0 个参数**）：`System.int RoutingComponentGrouping {get; set;}`
2. **`## Remarks`**：无 ⇒ 查不到。
3. **例子调用序**（[E] `Get_and_Set_Routing_Component_Grouping_Options_for_BOM_Table_Example_VB.md`，★ **先选中 BOMFEATURE 再取对象**）：
```vbnet
    status = swModelDocExt.SelectByID2("Bill of Materials1", "BOMFEATURE", 0, 0, 0, False, 0, Nothing, 0)
    Set swSelMgr = swModel.SelectionManager
    Set swBomFeature = swSelMgr.GetSelectedObject6(1, -1)
    Debug.Print "Name of configuration used for BOM table: " & swBomFeature.Configuration
    'Get current routing component grouping options
    Debug.Print "Current routing component grouping options: " & swBomFeature.RoutingComponentGrouping
    'Set new routing component grouping options
    options = swRoutingComponentGroupingOption_e.swShowOnlyRoutingComponentsInBOM + swRoutingComponentGroupingOption_e.swDisplayUnitsInBOM
    swBomFeature.RoutingComponentGrouping = options
    Debug.Print "Modified routing component grouping options: " & swBomFeature.RoutingComponentGrouping
```
★ Preconditions 逐字：`1. Open public_documents\samples\tutorial\api\AutoRouteThroughSketchEntities.sldddrw.`
4. **枚举**：Returns 段逐字 `Routing component grouping options as defined in [[swRoutingComponentGroupOption_e]]`
   ★ ★ **名字不一致，如实抄**：[T] 写的是 `swRoutingComponentGroupOption_e`（**`Group` 后面没有 `ing`**），而**存在**的枚举文件与**例子用的**都是 **`swRoutingComponentGroupingOption_e`**；`C:\swapi\enums\swRoutingComponentGroupOption_e.md` **不存在**。
   ★ [N] `C:\swapi\enums\swRoutingComponentGroupingOption_e.md`（`enum_member_count: 4`，Description 逐字 `Routing components grouping options. [Bitmask]`）：

   | Member | Value |
   | --- | --- |
   | `swDisplayUnitsInBOM` | 4 or 0x4 |
   | `swGroupPipesOrTubesWithTheSameDiameterAndSchedule` | 2 or 0x2 |
   | `swRoutingGroupSpoolComponents` | 8 or 0x8 |
   | `swShowOnlyRoutingComponentsInBOM` | 1 or 0x1 |

   ★ 例子用的是 `swShowOnlyRoutingComponentsInBOM + swDisplayUnitsInBOM`（`1 + 4`）。
5. **废弃链**：无。

**前置一句话**：查不到 —— 必须有带 Routing 组件的装配体工程图并选中 BOM 表，Remarks 一句都没写。
**配方一句话**：先 `SelectByID2("Bill of Materials1", "BOMFEATURE", ...)`，再 `GetSelectedObject6(1, -1)` 取 `swBomFeature`，然后写 `swRoutingComponentGroupingOption_e.swShowOnlyRoutingComponentsInBOM + swRoutingComponentGroupingOption_e.swDisplayUnitsInBOM`。

---

## 11. `IPrimaryMemberPathSegmentFeatureData`（4 个成员）

> ★ **归类如实抄**：该接口 front-matter 的 `category` 是 `Feature Interfaces/Structure Systems`，Description 逐字 `Allows access to a structure system member created along path segments in a sketch.` —— **不是 Routing 类别**。

**接口概述**：[T] `C:\swapi\types\IPrimaryMemberPathSegmentFeatureData\_overview.md`
· `## Remarks` 逐字：`See the [[IStructureSystemFolder]] Remarks.` / `For more information, see the **SOLIDWORKS Design user-interface help > Weldments and Structure System > Structure System > PrimaryMember PropertyManager** topic.`

### 11.1 `GetPathSegments`

1. **精确签名**（**0 个参数**）：`System.object GetPathSegments()`
2. **`## Remarks`**：无 ⇒ 查不到。
3. **例子调用序**：该 .md 的 `## Examples` 段指向 `Create Path Segment SSMember (VB.NET)` / `(C#)`；[E] 目录里**没有这两个文件名**（`Get-ChildItem C:\swapi\examples | ? {$_.Name -like "*Path_Segment*"}` 无命中）⇒ 调用序查不到。
4. **枚举**：无。
5. **废弃链**：无。

**前置一句话**：查不到。**配方一句话**：查不到 —— 例子文件在本机 `C:\swapi\examples\` 下不存在。

### 11.2 `GetPathSegmentsTypes`

1. **精确签名**（**0 个参数**）：`System.object GetPathSegmentsTypes()`
2. **`## Remarks`**：无 ⇒ 查不到。
3. **例子调用序**：查不到（理由同 11.1）。
4. **枚举**：Returns 段逐字 —— `Array of path segment types as defined by [[swSelectType_e]]:` 后跟三条：`swSelSKETCHES` / `swSelEDGES` / `swSelREFCURVES`。
   ★ ★ **这三个成员的数值抄不到** —— `C:\swapi\enums\swSelectType_e.md` 的具体内容本轮**未读**，`swSelSKETCHES`/`swSelEDGES`/`swSelREFCURVES` 的数值**查不到**（本文件不做推断）。
5. **废弃链**：无。

**前置一句话**：查不到。**配方一句话**：查不到。

### 11.3 `SetPathSegments`

1. **精确签名**（**1 个参数**）：`System.bool SetPathSegments( System.object PathSegments )`
2. **`## Remarks` 逐字摘录**：
   > `For .NET applications, you must marshal the PathSegments array to IDispatch object arrays before calling this method. See [IDispatch Object Arrays as Input in .NET](<../../docs/Programming with the SOLIDWORKS API/IDispatch Object Arrays as Input in .NET.md>).`
3. **例子调用序**：查不到（理由同 11.1）。
4. **枚举**：无。
5. **废弃链**：无。

**前置一句话**：Remarks 逐字 —— **.NET 必须先把 `PathSegments` 数组 marshal 成 IDispatch 对象数组**。
**配方一句话**：查不到。

### 11.4 `MergeTangentMembers`

1. **精确签名**（**0 个参数**）：`System.bool MergeTangentMembers {get; set;}`
2. **`## Remarks` 逐字摘录**（★ 明确的“valid only if”）：
   > `This property is valid only when creating the structure system path segment member.`
3. **例子调用序**：查不到（理由同 11.1）。
4. **枚举**：无。
5. **废弃链**：无。

**前置一句话**：Remarks 逐字 —— **只在“创建结构系统路径段构件”时有效**。
**配方一句话**：查不到。

---

# 二、PDM

## 12. `IApplication.PDMDocManager`（swbrowser 命名空间，拿到 PDM 文档管理器的入口）

**来源**：[T] `C:\swapi\types\IApplication\PDMDocManager.md`
★ 注意 **[T] 有两个 `IApplication` 目录**：本节这个是 **`SolidWorks.Interop.swbrowser`** 命名空间的（`_overview.md` front-matter 逐字 `assembly: SolidWorks.Interop.swbrowser` / `namespace: SolidWorks.Interop.swbrowser`）。

1. **精确签名**（属性，**0 个参数**）：`PDMDocManager PDMDocManager {get;}`
2. **`## Remarks` 逐字摘录**：`Available only if you installed SOLIDWORKS Toolbox.`
3. **官方例子的调用序** —— **[D] `C:\swapi\docs\toolboxapi\GettingStarted-toolboxapi.md`**（不是 [E]）第 3 步逐字：
   > `In the add-in's ConnectToSW():`
   > `1. Call [ISldWorks::GetAddInObject](../../types/ISldWorks/GetAddInObject.md), passing in the GUID of the SOLIDWORKS Toolbox Browser add-in type library (**Registry Editor >** **Computer\HKEY_CLASSES_ROOT\TypeLib\\{ED783340-D5DB-11d4-BD5A-00C04F019809}**), to get a Dispatch pointer to the IApplication object and connect to the SOLIDWORKS Toolbox Browser.`

   ```cpp
   LPDISPATCH pDisp = NULL;
   HRESULT hres = pSldWorks->GetAddInObject("{ED783340-D5DB-11d4-BD5A-00C04F019809}" , &pDisp);
   ```
   > `2. Cast the Dispatch pointer to **SOLIDWORKS.Interop.swbrowser.IApplication** to gain access to the SOLIDWORKS Toolbox Browser API.`
4. **枚举**：无。
5. **废弃链**：无。

**前置一句话**：Remarks 逐字 `Available only if you installed SOLIDWORKS Toolbox.`；[D] 的步骤逐字是先 `ISldWorks::GetAddInObject("{ED783340-D5DB-11d4-BD5A-00C04F019809}", &pDisp)` 再 cast。
**配方一句话**：`GetAddInObject(ToolboxBrowser 的 TypeLib GUID)` → cast 成 `swbrowser.IApplication` → 读 `.PDMDocManager`。

> ★ **API 面清单（[D] 逐字抄）**：
> `SOLIDWORKS Toolbox Browser API (**SOLIDWORKS.Interop.swbrowser.dll**):` 下只有 `IApplication` 与 `IPDMDocManager`；
> `SOLIDWORKS Toolbox Configurator API (**SOLIDWORKS.Interop.sldtoolboxconfigureaddin.dll**):` 下是 `IToolboxConfiguratorAddin` 与 `IToolBoxConfiguratorApplication`。

---

## 13. `IPDMDocManager`（3 个成员）

**接口概述**：[T] `C:\swapi\types\IPDMDocManager\_overview.md`
· front-matter 逐字：`assembly: SolidWorks.Interop.swbrowser` / `namespace: SolidWorks.Interop.swbrowser` / `method_count: 3`。
· Description 逐字：`Provides access to the SOLIDWORKS Toolbox document manager.`
· **`## Remarks` 逐字摘录**：
  > `This interface is available only if SOLIDWORKS Toolbox Browser add-in is an active SOLIDWORKS add-in.`
  >
  > `Events are implemented with delegates in the Microsoft .NET Framework. See the [[Overview]] topic for a list of delegates for this interface.`

### 13.1 `SetManagedDocument`

1. **精确签名**（**1 个参数**）：`System.bool SetManagedDocument( System.string fileName )`
★ 形参名是**小写 `fileName`**（逐字）。
2. **`## Remarks` 逐字摘录**：`Available only if you installed SOLIDWORKS Toolbox.`
   参数表逐字：`Document path and file name; the location in the vault does not need to be writable`
3. **调用序**（[D] `GettingStarted-toolboxapi.md`，第 79–87 行段“Insert SmartFastener”第 2 步逐字）：
   > `In the PreInsertDocument event handler, the PDM application must call [IPDMDocManager::SetManagedDocument](../../types/IPDMDocManager/SetManagedDocument.md), passing the path name of the PDM-managed version of the document (if it can be made writable) or a copy of the managed document that can be written to by SOLIDWORKS Toolbox Browser (if it cannot be made writable).`
4. **枚举**：无。
5. **废弃链**：无。

**前置一句话**：Remarks 逐字 `Available only if you installed SOLIDWORKS Toolbox.`；[D] 逐字 —— **在 `PreInsertDocument` 事件处理器里调**。
**配方一句话**：传“PDM 受管版本”的路径；若该路径不可写，就传一份可写副本的路径（[D] 原话二选一）。

### 13.2 `SetDocumentStatus`

1. **精确签名**（**1 个参数**）：`System.bool SetDocumentStatus( System.int status )`
2. **`## Remarks` 逐字摘录**：`Available only if you installed SOLIDWORKS Toolbox.`
3. **调用序**（[D] `GettingStarted-toolboxapi.md`，两处逐字）：
   > `In the BeforeWritingToDocument event handler, the PDM application must ensure that the file that was previously passed to IAssemblyDoc::SetDroppedFileName is writable and call [IPDMDocManager::SetDocumentStatus](../../types/IPDMDocManager/SetDocumentStatus.md), passing [swPDMStatus_e.swPDMStatusKnownAndAvailable](../../enums/swPDMStatus_e.md). If the application passes any other status value, SOLIDWORKS Toolbox Browser generates an error and stops the file drop.`
   （另见第 98 段 Toolbox Configurator 用例：`It must then call [IPDMDocManager::SetDocumentStatus](…), passing [swPDMStatus_e.swPDMStatusKnownAndAvailable](…) before returning.`）
4. **枚举**：参数表逐字 `Document status as defined in [[swPDMStatus_e]]`。
   ★ [N] `C:\swapi\enums\swPDMStatus_e.md`（`enum_member_count: 4`，`assembly: SolidWorks.Interop.swbrowser`，Description 逐字 `PDM document statuses.`）：

   | Member | Value |
   | --- | --- |
   | `swPDMStatusError` | 0 |
   | `swPDMStatusKnownAndAvailable` | 2 = Document is known to PDM and writable |
   | `swPDMStatusKnownAndUnavailable` | 3 = Document is known to PDM and not writable |
   | `swPDMStatusUnknown` | 1 = Document is unknown to PDM |

5. **废弃链**：无。

**前置一句话**：Remarks 逐字 `Available only if you installed SOLIDWORKS Toolbox.`；[D] 逐字 —— **在 `BeforeWritingToDocument` 事件处理器里调**。
**配方一句话**：传 `swPDMStatus_e.swPDMStatusKnownAndAvailable`（=2）；[D] 原话明确 —— **传别的值 Toolbox Browser 会报错并中止文件拖放**。

### 13.3 `SetCancelOperation`

1. **精确签名**（**1 个参数**）：`System.bool SetCancelOperation( System.int cancelOp )`
2. **`## Remarks` 逐字摘录**：`Available only if you installed SOLIDWORKS Toolbox.`
   参数表逐字：`cancelOp: True to cancel the current operation, false to continue the operation`
   Description 逐字：`Cancels the current operation after any notifications are returned.`
3. **调用序**：**[D] `GettingStarted-toolboxapi.md` 里没有提到 `SetCancelOperation`** ⇒ 查不到。
4. **枚举**：**签名里没有枚举**，参数是 `System.int`，参数表也**没有点名任何枚举** ⇒ 查不到。
5. **废弃链**：无。

**前置一句话**：Remarks 逐字 `Available only if you installed SOLIDWORKS Toolbox.`
**配方一句话**：查不到 —— [D] 的事件流程里没有出现它，`cancelOp` 该取什么常量也查不到（形参是 `int` 且官方没点名枚举）。

---

## 14. `IEdm*`

**查不到。**

· `Get-ChildItem C:\swapi\types -Directory | ? {$_.Name -match 'Edm|PDM|Pdm'}` → **只返回 `IPDMDocManager`**。
· 全 `C:\swapi` 递归 grep `IEdm` → **零命中**。
· CHM 目录 `sldworksapi` / `sldworksapivb6` / `cosworks` / `swconst` 下按 `Edm|PDM|Toolbox` 过滤 → **没有任何 `IEdm*` 页面**。
· `[D] GettingStarted-toolboxapi.md` 给出的全部 PDM 相关接口只有 4 个：`IApplication`、`IPDMDocManager`、`IToolboxConfiguratorAddin`、`IToolBoxConfiguratorApplication`。

⇒ **`IEdm*` 接口在本机两套官方源里不存在 ⇒ 查不到**（不拿 `IPDMDocManager` 顶替）。

**前置一句话**：查不到。**配方一句话**：查不到。

---

# 三、动画导出（AVI）· 与 SaveAs3

## 15. `IModelDocExtension.SaveAs3`（7 个参数）

**来源**：[T] `C:\swapi\types\IModelDocExtension\SaveAs3.md`

1. **精确签名**（**7 个参数**）：
```
System.bool SaveAs3( System.string Name, System.int Version, System.int Options, System.object ExportData, System.object AdvancedSaveAsOptions, out System.int Errors, out System.int Warnings )
```
★ **形参 6 与 7 是 `out int`**；形参名逐字 `Name` / `Version` / `Options` / `ExportData` / `AdvancedSaveAsOptions` / `Errors` / `Warnings`。

2. **`## Remarks` 逐字摘录**（★ 前置段逐字）：
   > `The difference between this method and the now obsolete [[IModelDocExtension::SaveAs2]] is that this method uses an IAdvancedSaveAsOptions object to specify advanced options. For example:`
   > `- Saving a subset of configurations`
   > `- Renaming and/or relocating individual component references`
   > `- Specifying the prefix and/or suffix for all component reference names`
   >
   > `To specify the AdvancedSaveAsOptions parameter of this method, call [[IModelDocExtension::GetAdvancedSaveAsOptions]] to create an IAdvancedSaveAsOptions object.`
   >
   > `To save as an IGES, STL, or STEP file, the document to convert must be the active document. Before calling this method:`
   > `1. Call [[ISldWorks::ActivateDoc3]] to make the document to convert the active document.`
   > `2. Call [[ISldWorks::ActiveDoc]] to get the active document.`
   >
   > `This method:`
   > `- Exports the entire model, unless faces or bodies are selected, in which case, it exports only those. Call [[IModelDoc2::ClearSelection2]] before calling this method to clear the selection list and export the entire model.`
   > `- Overwrites existing files unless they are read only.`
   > `- Results in the FileSaveNotify event being sent to any application listening.`
   > `- Removes any configuration-specific bitmap previews, except the current configuration's.`
   >
   > `Use Name to specify the full pathname of the saved document. If you specify only the file name, then it is saved in the active document's directory. The filename extension indicates the conversion that should be performed (for example, **Part1.igs** to save to IGES).`
   >
   > `Use ExportData to specify which drawings sheets to save to PDF. If ExportData is Nothing or null, then all sheets are saved to PDF. Saving a document as PDF when the document is open as view-only is not supported.`
   >
   > `Use Options to specify save options. You can specify additional options using [[ISldWorks::SetUserPreferenceIntegerValue]]. For example:`
   >
   > ```vb
   > ' Save assembly as multibody part and save exterior faces as surface bodies
   > swApp.SetUserPreferenceIntegerValue swSaveAssemblyAsPartOptions, _
   > swSaveAsmAsPart_ExteriorFaces
   > swModelDocExt.SaveAs "H:\Assem1.SLDPRT", swSaveAsCurrentVersion, _
   > swSaveAsOptions_Silent, Nothing, nErrors, nWarnings
   > ```
   > `- or -`
   > ```vb
   > ' Save all drawing sheets in active drawing document as an eDrawings file
   > swApp.SetUserPreferenceIntegerValue swEdrawingsSaveAsOption, swEdrawingSaveAll
   > swModelDocExt.SaveAs "H:\Grid.edrw", swSaveAsCurrentVersion, _
   > swSaveAsOptions_Silent, Nothing, nWarnings
   > ```
   >
   > `If the file is saved successfully, then the returned value is true and Errors is 0. If the save is not successful, then the returned value is false and Errors contains a bitwise OR of the error codes that were generated in saving the document. Check the masks against the Errors enumeration. If you do not want SOLIDWORKS to return error information, set Errors to Nothing or null.`
   >
   > `Even if the file is saved successfully, there might be warnings or information that occur during the save operation in which you might be interested. Warnings contains a bitwise OR of the warning codes that were generated when saving the document.`
   >
   > `Use [[IModelDoc2::Save3]] to save a file using its current name.`

   ★ ★ **官方自己的代码片段用的是 `SaveAs`（6 参旧名），不是 `SaveAs3`（7 参）** —— 两处都抄，不改写。

3. **官方例子的调用序** —— ★ **查不到**：该 .md 的 `## Examples` 段**为空**（只有 `## See Also`，见 `SaveDeFeaturedFile` / `ISldWorks` 那几条）。
   ⇒ 但**Remarks 里自带两段官方代码**（上面已逐字抄），它们给的是 `SaveAs` 的 6 参实参：`"H:\Assem1.SLDPRT", swSaveAsCurrentVersion, swSaveAsOptions_Silent, Nothing, nErrors, nWarnings` 与 `"H:\Grid.edrw", swSaveAsCurrentVersion, swSaveAsOptions_Silent, Nothing, nErrors, nWarnings`。

4. **枚举**（签名里出现的 4 个，逐字 + 全表）：

   · `Version` → `[[swSaveAsVersion_e]]`
     [N] `C:\swapi\enums\swSaveAsVersion_e.md`（`enum_member_count: 5`）：

     | Member | Value |
     | --- | --- |
     | `swSaveAsCurrentVersion` | 0 = This is the typical save behavior. |
     | `swSaveAsDetachedDrawing` | 4 |
     | `swSaveAsFormatProE` | 2 |
     | `swSaveAsStandardDrawing` | 3 |
     | `swSaveAsSW98plus` | **Obsolete and no longer supported.** |

   · `Options` → `[[swSaveAsOptions_e]]`
     [N] `C:\swapi\enums\swSaveAsOptions_e.md`（`enum_member_count: 13`，Description 逐字 `Save As options. [Bitmask]`；`## Remarks` 逐字 `These options only apply to saving to native SOLIDWORKS file formats.`）：

     | Member | Value |
     | --- | --- |
     | `swSaveAsOptions_AvoidRebuildOnSave` | 8 or 0x8 |
     | `swSaveAsOptions_Copy` | 2 or 0x2; Save the document as a copy and continue editing |
     | `swSaveAsOptions_CopyAndOpen` | 512 or 0x200; Save the document as a copy and open it |
     | `swSaveAsOptions_DetachedDrawing` | **Obsolete.** |
     | `swSaveAsOptions_ExportTo2DPdfFromInspection` | 2048 or 0x800; Export drawing sheets from Inspection to 2DPdf |
     | `swSaveAsOptions_IgnoreBiography` | 256 or 0x100; Prune a SOLIDWORKS file's revision history to just the current file name |
     | `swSaveAsOptions_IncludeVirtualSubAsmComps` | 1024 or 0x400; Save regular components in virtual subassemblies |
     | `swSaveAsOptions_OverrideSaveEmodel` | 32 or 0x20; … |
     | `swSaveAsOptions_PropagateVisualProperties` | 4096 or 0x1000; Export drawing sheets from Inspection to 2DPdf |
     | `swSaveAsOptions_SaveEmodelData` | **Obsolete.** |
     | `swSaveAsOptions_SaveReferenced` | 4 or 0x4; … |
     | `swSaveAsOptions_Silent` | 1 or 0x1 |
     | `swSaveAsOptions_UpdateInactiveViews` | 16 or 0x10; Not a valid option for [[IPartDoc::SaveToFile2]]; … |

   · `Errors` → `[[swFileSaveError_e]]`
     [N] `C:\swapi\enums\swFileSaveError_e.md`（`enum_member_count: 17`，`## Remarks` 逐字 `Not all of these return codes are fatal errors. The return code is a bitmask of different conditions that can occur during the operation, some of which are fatal and some are informational or warnings.`）：

     | Member | Value |
     | --- | --- |
     | `swFileLockError` | 16 or 0x10 |
     | `swFileNameContainsAtSign` | 8 or 0x8 = File name cannot contain the at symbol (@) |
     | `swFileNameEmpty` | 4 or 0x4 = File name cannot be empty |
     | `swFileSaveAsBadEDrawingsVersion` | 1024 or 0x400 |
     | `swFileSaveAsDetachedDrawingsNotSupported` | 16384 or 0x4000 |
     | `swFileSaveAsDoNotOverwrite` | 128 or 0x80 |
     | `swFileSaveAsInvalidFileExtension` | 256 or 0x100 |
     | `swFileSaveAsNameExceedsMaxPathLength` | 2048 or 0x800 = File name cannot exceed 255 characters |
     | `swFileSaveAsNoSelection` | 512 or 0x200 |
     | `swFileSaveAsNotSupported` | 4096 or 0x1000 |
     | `swFileSaveDoNotUpgradeError` | 32768 or 0x8000 |
     | `swFileSaveFormatNotAvailable` | 32 or 0x20 = Save As file type is not valid |
     | `swFileSaveIncompatibleItemsError` | 65536 or 0x10000 |
     | `swFileSaveRequiresSavingReferences` | 8192 or 0x2000 |
     | `swFileSaveWithRebuildError` | **Obsolete = See [[swFileSaveWarning_e]]** |
     | `swGenericSaveError` | 1 or 0x1 |
     | `swReadOnlySaveError` | 2 or 0x2 |

   · `Warnings` → `[[swFileSaveWarning_e]]`
     [N] `C:\swapi\enums\swFileSaveWarning_e.md`（`enum_member_count: 12`，Description 逐字 `Values for **File, Save** warnings that can be returned from the [[IModelDoc2]] Save methods. These warnings do not cause the **File, Save** operation to fail. [Bitmask].`）：

     | Member | Value |
     | --- | --- |
     | `swFileSaveWarning_AnimatorCameraViews` | 128 or 0x80 |
     | `swFileSaveWarning_AnimatorFeatureEdits` | 16 or 0x10 |
     | `swFileSaveWarning_AnimatorLightEdits` | 64 or 0x40 |
     | `swFileSaveWarning_AnimatorNeedToSolve` | 8 or 0x8 |
     | `swFileSaveWarning_AnimatorSectionViews` | 256 or 0x100 |
     | `swFileSaveWarning_EdrwingsBadSelection` | 32 or 0x20 |
     | `swFileSaveWarning_MissingOLEObjects` | 512 or 0x200 |
     | `swFileSaveWarning_NeedsRebuild` | 2 or 0x2 |
     | `swFileSaveWarning_OpenedViewOnly` | 1024 or 0x400 |
     | `swFileSaveWarning_RebuildError` | 1 or 0x1 |
     | `swFileSaveWarning_ViewsNeedUpdate` | 4 or 0x4 |
     | `swFileSaveWarning_XmlInvalid` | 2048 or 0x800 |

   ★ 顺带抄到：[N] 里有 **5 个 `Animator*` 警告位**（`AnimatorCameraViews` / `AnimatorFeatureEdits` / `AnimatorLightEdits` / `AnimatorNeedToSolve` / `AnimatorSectionViews`）—— 这是本机两套源里**唯一**把「动画」和 `SaveAs` 直接连起来的地方。

5. **废弃链**（★ 只抄官方点名的后继，查不到就写查不到）：
   · **方法级**：Remarks 第一句逐字点名 `IModelDocExtension::SaveAs2` 是 **`the now obsolete`** 的那个 ⇒ **`SaveAs2` 已被 `SaveAs3` 取代**（`SaveAs3` 自己没标 Obsolete）。
   · **枚举级**（★ 官方**没有点名后继**的地方，一律写「查不到」）：
     · `swSaveAsSW98plus` = `Obsolete and no longer supported.` → **后继查不到**（官方只写“不支持”，没写替代项）。
     · `swSaveAsOptions_DetachedDrawing` = `Obsolete.` → **后继查不到**。
     · `swSaveAsOptions_SaveEmodelData` = `Obsolete.` → **后继查不到**。
     · `swFileSaveWithRebuildError` = `Obsolete = See [[swFileSaveWarning_e]]` → **后继点名了 = `swFileSaveWarning_e`**。
     · `swFileSaveError_e` 里 `swFileSaveAsNoSelection` 那条逐字：`…not a valid option for [[IModelDocExtension::SaveAs]]` —— **点名了 `SaveAs`**（不是废弃声明，只是适用范围）。

**前置一句话**：Remarks 逐字 —— 要传 `AdvancedSaveAsOptions` 就**先调 `IModelDocExtension::GetAdvancedSaveAsOptions`** 建对象；转 IGES/STL/STEP 时**必须先 `ISldWorks::ActivateDoc3` 把待转文档设为活动文档、再 `ISldWorks::ActiveDoc`**；想导出整个模型**必须先 `IModelDoc2::ClearSelection2` 清选区**。
**配方一句话**：官方 Remarks 自带的两段代码给的是 **6 参 `SaveAs`** —— `"H:\Assem1.SLDPRT", swSaveAsCurrentVersion, swSaveAsOptions_Silent, Nothing, nErrors, nWarnings`；**`SaveAs3` 的 7 参完整实参例子查不到**（该 .md 的 `## Examples` 为空）。

---

## 16. `IModelDocExtension.GetMotionStudyManager`（动画/AVI 的唯一入口）

**来源**：[T] `C:\swapi\types\IModelDocExtension\GetMotionStudyManager.md`

1. **精确签名**（**0 个参数**）：`System.object GetMotionStudyManager()`
2. **`## Remarks`**：**该 .md 没有 `## Remarks` 段** ⇒ 查不到。
3. **官方例子的调用序**（[E] `swmotionstudyapi__Duplicate,_Delete,_and_Create_Motion_Study_Example_VB.md`，★ **先取 Extension 再取 manager，并判 Nothing**）：
```vbnet
    Set swModelDocExt = swModel.Extension
    'Get the MotionManager
    Set swMotionMgr = swModelDocExt.GetMotionStudyManager()
    If (swMotionMgr Is Nothing) Then
          End
    End If
    'Get the motion study named Motion Study 1
    Set swMotionStudy1 = swMotionMgr.GetMotionStudy("Motion Study 1")
```
★ 同文件 Preconditions 逐字：`3. Click Tools > References > SOLIDWORKS version Motion Study Type Library.` / `2. Verify that a ray-trace rendering engine is active.`
★ ★ **[T] 该 .md 的 `## Examples` 段点名的 9 个例子文件名**（`Create_Motion_Studies_Example_VB.md` / `Get_COSMOSMotion_...` / `Get_Motion_Study_Example_VB.md` / `Add_Spring_...` / `Duplicate,_Delete,_and_Create_Motion_Study_...`）—— ★ **其中 `Get_Motion_Study_Example_VB.md` 在 `C:\swapi\examples\` 目录下**按名字**搜不到**（`Get-ChildItem | ? {$_.Name -like "*Get_Motion_Study*"}` 无命中）⇒ 查不到。
4. **枚举**：无。
5. **废弃链**：无。

**前置一句话**：查不到 —— 官方只在例子的 Preconditions 里写 `Click Tools > References > SOLIDWORKS version Motion Study Type Library`。
**配方一句话**：`swModel.Extension` → `GetMotionStudyManager()` → **判 `Is Nothing`** → `GetMotionStudy("Motion Study 1")`。

---

## 17. `IMotionStudy.SaveToAVI`（AVI 导出的本体）

**来源**：[T] `C:\swapi\types\IMotionStudy\SaveToAVI.md`

1. **精确签名**（**2 个参数**）：
```
System.bool SaveToAVI( System.string FileName, AVIParameter Parameter )
```
★ 形参 2 的类型是 **`AVIParameter`**（无 `I` 前缀、无命名空间）。
2. **`## Remarks`**：**该 .md 没有 `## Remarks` 段** ⇒ 查不到（★ 这是 AVI 这条护城河最需要的原话，本机两套源里**确实没有**）。
   ★ 唯一一句 Description 逐字：`Saves the animation to a .**avi**, .**bmp**, or .**tga** file.`
3. **官方例子的调用序**（[E] `swmotionstudyapi__Duplicate,_Delete,_and_Create_Motion_Study_Example_VB.md`，★ 先建参数对象再设 7 项，最后存盘）：
```vbnet
    'Set and save AVI parameters
    Set swSaveAVIData = swMotionMgr.CreateAVIParameter()
    swSaveAVIData.FramePerSecond = 7.5
    swSaveAVIData.SaveEntireAnimation = True
    swSaveAVIData.OutputType = swAnimationOutputType_e.swAnimationOutput_AVI
    swSaveAVIData.RendererType = swRendererType_e.swRendererType_Solidworks_Screen
    swSaveAVIData.MotionBlur = True
    swSaveAVIData.BlurLength = 10
    swSaveAVIData.BlurOffset = -100
    swMotionStudy1.Stop
    'Save animation as .avi file
    swMotionStudy1.SaveToAVI "C:\test\Anim1.avi", swSaveAVIData
```
★ 声明逐字：`Dim swSaveAVIData As SwMotionStudy.AVIParameter`
★ Postconditions 逐字：`5. Saves the motion study as c:\test\Anim1.avi.`
★ ★ **[C] 交叉核对**：`sldworksapi\Duplicate,_Delete,_and_Create_Motion_Study_Example_CSharp.htm` 里同一处逐字：
`//Save&nbsp;animation&nbsp;as&nbsp;.avi&nbsp;file` / `swMotionStudy1.<b>SaveToAVI</b>(<span style="color:#a31515;">&quot;C:\\test\\Anim1.avi&quot;</span>,&nbsp;swSaveAVIData);`
（VB6/VBNET 两版逐字相同：`swMotionStudy1.SaveToAVI("C:\test\Anim1.avi", swSaveAVIData)`）
4. **枚举**：签名里**没有**枚举（形参 2 是 `AVIParameter` 对象）；参数 `OutputType` 等在 `IAVIParameter` 上，见 17.x。
5. **废弃链**：无 Obsolete 标记。

**前置一句话**：查不到 —— `SaveToAVI` 的 .md **没有 Remarks**；官方只在例子里体现了三件事：`Click Tools > References > SOLIDWORKS version Motion Study Type Library`、**存盘前先 `swMotionStudy1.Stop`**、**要一个 ray-trace 渲染引擎处于 active**（后者是 `MotionBlur` 的前置，见下）。
**配方一句话**：`swMotionMgr.CreateAVIParameter()` → 设 `FramePerSecond=7.5` / `SaveEntireAnimation=True` / `OutputType=swAnimationOutput_AVI` / `RendererType=swRendererType_Solidworks_Screen` / `MotionBlur=True` / `BlurLength=10` / `BlurOffset=-100` → `swMotionStudy1.Stop` → `SaveToAVI "C:\test\Anim1.avi", swSaveAVIData`。

> ★ **另一处 AVI 口径**：[E] `swmotionstudyapi__Create_Motion_Studies_Example_VB.md` 里逐字
> `swSaveAVIData.OutputType = 1 ' Save as an .avi file`
> —— **用裸数字 1**，且**该例子只设 3 项**（`FramePerSecond = 7.5` / `SaveEntireAnimation = True` / `OutputType = 1`），**没有调 `SaveToAVI`**（它的 `## Code` 到 `End Sub` 就结束了）。

---

## 18. `IMotionStudyManager.CreateAVIParameter`

**来源**：[T] `C:\swapi\types\IMotionStudyManager\CreateAVIParameter.md`

1. **精确签名**（**0 个参数**）：`AVIParameter CreateAVIParameter()`
   ★ 返回类型写 **`AVIParameter`**（不是 `System.object`，也不是 `IAVIParameter`）。
2. **`## Remarks`**：无 ⇒ 查不到。唯一一句 Description 逐字：`Creates the object to use to set and save the AVI parameters of animation videos.`
3. **例子调用序**（[E] `swmotionstudyapi__Duplicate,_Delete,_and_Create_Motion_Study_Example_VB.md`）：
   `Set swSaveAVIData = swMotionMgr.CreateAVIParameter()` —— **紧跟在 `swMotionStudy1.Stop` 之后、`SaveToAVI` 之前**（见 17.3 的整段）。
4. **枚举**：无。
5. **废弃链**：无。

**前置一句话**：查不到 —— .md 只有标题、Signature、Returns、Examples、See Also。
**配方一句话**：`swMotionMgr.CreateAVIParameter()` 返回 `AVIParameter`；声明用 `Dim swSaveAVIData As SwMotionStudy.AVIParameter`。

---

## 19. `IMotionStudy.CreateByRotateModel`（AVI 之前必须先造出动画序列）

**来源**：[T] `C:\swapi\types\IMotionStudy\CreateByRotateModel.md`

1. **精确签名**（**6 个参数**）：
```
System.bool CreateByRotateModel( System.bool DeleteExistingPath, System.int Axis, System.int RotationCount, System.int Direction, System.double Duration, System.double StartTime )
```
2. **`## Remarks` 逐字摘录**（★ 前置/语义都在这里）：
   > `If you have existing animation sequences, then the start time of this animation should account for the total time of all previous sequences. If this is a new animation sequence, set StartTime to 0 to start the animation immediately, or type a value to delay the start of the sequence.`
   ★ 该 .md 的 Remarks 段**自带一整段官方 VBA 代码**，逐字（`GetMotionStudyManager` → `CreateMotionStudy` → `CreateByRotateModel` → `Play`）：
```vbnet
    Set swModelDocExt = swModel.Extension
    Set swMotionMgr = swModelDocExt.GetMotionStudyManager
    ' Create a new motion study
    Set swMotion = swMotionMgr.CreateMotionStudy
    ' Delete any existing animation sequences,
    ' set the animation duration to 5 seconds, and play
    ' the animation immediately when IMotionStudy::Play is called
    boolstatus = swMotion.CreateByRotateModel(True, swRotationAboutXAxis, 1, swRotationClockwise, 10, 0)
    ' Play the animation
    swMotion.Play
```
3. **例子调用序**（[E] `swmotionstudyapi__Duplicate,_Delete,_and_Create_Motion_Study_Example_VB.md`）：
```vbnet
    boolstatus = swMotionStudy1.CreateByRotateModel(True, swAnimatorAxisOfRotation_e.swRotationAboutYAxis, 1, swAnimatorDirectionOfRotation_e.swRotationClockwise, 10, 0)
```
★ 同一文件后面还逐字有 `CreateByExplode(False, 5, 0)` 与 `CreateByCollapse(False, 10, 5)`。
4. **枚举**：
   · `Axis` → `[[swAnimatorAxisOfRotation_e]]`
     [N] `C:\swapi\enums\swAnimatorAxisOfRotation_e.md`（`enum_member_count: 3`）：

     | Member | Value |
     | --- | --- |
     | `swRotationAboutXAxis` | 0 = About x axis |
     | `swRotationAboutYAxis` | 1 = About y axis |
     | `swRotationAboutZAxis` | 2 = About z axis |

   · `Direction` → `[[swAnimatorDirectionOfRotation_e]]`
     [N] `C:\swapi\enums\swAnimatorDirectionOfRotation_e.md`（`enum_member_count: 2`）：

     | Member | Value |
     | --- | --- |
     | `swRotationClockwise` | 0 = Clockwise |
     | `swRotationCounterClockwise` | 1 = Counter-clockwise |

5. **废弃链**：无 Obsolete 标记。`## See Also` 点名 `IMotionStudy::CreateByCollapse Method` / `IMotionStudy::CreateByExplode Method`。

**前置一句话**：Remarks 逐字 —— **已有动画序列时 `StartTime` 必须累计前面所有序列的总时长**；新序列则设 0 立即开始。
**配方一句话**：`(True, swRotationAboutXAxis|swRotationAboutYAxis, 1, swRotationClockwise, 10, 0)` —— 前两参是「删旧序列」+「绕哪根轴」，末两参是秒。

---

## 20. `IMotionStudy.Play`

**来源**：[T] `C:\swapi\types\IMotionStudy\Play.md`

1. **精确签名**（**0 个参数**）：`System.bool Play()`
2. **`## Remarks`**：无 ⇒ 查不到。唯一一句 Description 逐字：`Plays the animation; the start point is where the animation timebar is located.`
3. **例子调用序**（[E] `swmotionstudyapi__Duplicate,_Delete,_and_Create_Motion_Study_Example_VB.md`，★ 先设 PlayMode、再 `SetTime 0`、**再 Play**）：
```vbnet
    'Set play mode to Loop
    Dim nPlayMode As Long
    Debug.Print "New play mode: "
    SwMotionStudy.PlayMode = swAnimationPlayMode_e.swAnimationPlayModeLoop
    nPlayMode = SwMotionStudy.PlayMode
    ...
    'Set timebar to 0 on timeline
    SwMotionStudy.SetTime 0
    'Play the animation
    SwMotionStudy.Play
```
★ 同文件调用点逐字：`PlayAnimation swMotionStudy1`（三次），以及 `swMotionStudy1.Stop`（两次）。
★ ★ **[C] 交叉核对**：`sldworksapi\Create_Motion_Studies_Example_VB.htm` 里逐字 `swSaveAVIData.<b>OutputType</b> = 1 ' Save as an .avi file`。
4. **枚举**：`Play` 本身无枚举；同链上的 `PlayMode` 属性用 `[[swAnimationPlayMode_e]]`
   [N] `C:\swapi\enums\swAnimationPlayMode_e.md`（`enum_member_count: 3`，Description 逐字 `Modes to play animations.`）：

   | Member | Value |
   | --- | --- |
   | `swAnimationPlayModeLoop` | 2 = Play from beginning to end, from beginning to end, etc. |
   | `swAnimationPlayModeNormal` | 1 = Play from beginning to end once. |
   | `swAnimationPlayModeReciprocate` | 3 = Play from beginning to end, from end to beginning, beginning to end, etc. |

   （另抄 [N] `swAnimationPlaySpeed_e.md`，`enum_member_count: 3`，Description 逐字 `Speeds to play animations.`：`swAnimationPlaySpeedFast` = 3 / `swAnimationPlaySpeedNormal` = 1 / `swAnimationPlaySpeedSlow` = 2。★ **`IMotionStudy` 上用它的成员本轮未读到** —— 见第 21 条。）
5. **废弃链**：无。`## See Also` 点名 `IMotionStudy::IsPlaying Property` / `IMotionStudy::PlayMode Property` / `IMotionStudy::PlayFromStart Method` / `IMotionStudy::Stop Method`。

**前置一句话**：Description 逐字 —— **起点 = 时间轴当前所在位置**（例子里因此先 `SetTime 0`）。
**配方一句话**：先 `PlayMode = swAnimationPlayModeLoop`，再 `SetTime 0`，再 `Play`；停止用 `Stop`。

---

## 21. `IAVIParameter`（8 个属性）

**接口概述**：[T] `C:\swapi\types\IAVIParameter\_overview.md`
· front-matter 逐字：`assembly: SolidWorks.Interop.swmotionstudy` / `namespace: SolidWorks.Interop.swmotionstudy` / `category: Motion Studies` / `property_count: 15` / `method_count: 0`。
· Description 逐字：`Allows access to the parameters of a file containing an animation.`
· **`## Remarks`**：该 `_overview.md` **没有 `## Remarks` 段** ⇒ 查不到。
· 目录下**全部 15 个属性文件名**（`Get-ChildItem`）：`AspectRatio` `BlurLength` `BlurOffset` `EndTime` `FramePerSecond` `ImageSize` `MotionBlur` `OutputType` `PreserveRatio` `RendererType` `SaveEntireAnimation` `ScreenHeight` `ScreenRatio` `ScreenWidth` `StartTime`（+ `_overview.md`）。
★ **本节只抄官方例子实际用到的 8 个**；其余 7 个的签名/Remarks 本轮**未读** ⇒ 抄不到。

### 21.1 `OutputType`

1. **精确签名**（**0 个参数**）：`System.int OutputType {get; set;}`
2. **`## Remarks`**：无 ⇒ 查不到。
3. **例子调用序**：
   · [E] `swmotionstudyapi__Duplicate,_Delete,_and_Create_Motion_Study_Example_VB.md`：`swSaveAVIData.OutputType = swAnimationOutputType_e.swAnimationOutput_AVI`
   · [E] `swmotionstudyapi__Create_Motion_Studies_Example_VB.md`：`swSaveAVIData.OutputType = 1 ' Save as an .avi file`
4. **枚举**：Returns 段逐字 `File type as defined by [[swAnimationOutputType_e]]`。
   [N] `C:\swapi\enums\swAnimationOutputType_e.md`（`enum_member_count: 10`，Description 逐字 `Animation output type.`）：

   | Member | Value |
   | --- | --- |
   | `swAnimationOutput_AVI` | **1** = Microsoft AVI file (.**avi**) |
   | `swAnimationOutput_Series_of_BMP` | 2 = Series of Windows Bitmaps (**.bmp**) |
   | `swAnimationOutput_Series_of_FLV` | 9 = Flash video file |
   | `swAnimationOutput_Series_of_JPG` | 5 |
   | `swAnimationOutput_Series_of_LXO` | 10 = Luxology scene file |
   | `swAnimationOutput_Series_of_MKV` | 8 = Matroska video file |
   | `swAnimationOutput_Series_of_MP4` | 7 |
   | `swAnimationOutput_Series_of_PNG` | 4 |
   | `swAnimationOutput_Series_of_TGA` | 3 = Series of Truevision Targas (**.tga**) |
   | `swAnimationOutput_Series_of_TIF` | 6 |

   ★ Create_Motion_Studies 例子里的裸 `1` 与 `swAnimationOutput_AVI = 1` 对得上（只抄事实）。
5. **废弃链**：无。

**前置一句话**：查不到 —— 只有 Description + Returns。
**配方一句话**：`swAnimationOutputType_e.swAnimationOutput_AVI`（=1）；官方另一处例子直接写裸 `1`。

### 21.2 `FramePerSecond`

1. **精确签名**（**0 个参数**）：`System.double FramePerSecond {get; set;}` —— **是 `double`**。
2. **`## Remarks`**：无 ⇒ 查不到。
3. **例子调用序**：两个例子都逐字写 `swSaveAVIData.FramePerSecond = 7.5`。
4. **枚举**：无。
5. **废弃链**：无。

**前置一句话**：查不到。**配方一句话**：`7.5`。

### 21.3 `SaveEntireAnimation`

1. **精确签名**（**0 个参数**）：`System.bool SaveEntireAnimation {get; set;}`
2. **`## Remarks` 逐字摘录**：
   > `If this property is set to false, then specify the [[start time]] and [[end time]] of the time period of the animation to which to save to the animation file or files.`
3. **例子调用序**：`swSaveAVIData.SaveEntireAnimation = True`
4. **枚举**：无。
5. **废弃链**：无。`## See Also` 点名 `IAVIParameter::ScreenHeight Property` / `IAVIParameter::ScreenWidth Property`。

**前置一句话**：Remarks 逐字 —— 设成 `false` 就**必须同时给 start time 与 end time**。
**配方一句话**：`True`（官方例子）；设 `False` 时 `StartTime` / `EndTime` 的具体写法本轮未读 ⇒ 查不到。

### 21.4 `RendererType`

1. **精确签名**（**0 个参数**）：`System.int RendererType {get; set;}`
2. **`## Remarks` 逐字摘录**（★ 这句点到了一个枚举里**没有**的取值）：
   > `If the renderer type is set to **Custom**, then you can change the [[height]] and [[width]] of the animation, [[preserve the aspect ratio]] of the animation, and set the aspect ratio to either the [[screen ratio]] or a [[value]].`
   ★ ★ **矛盾如实抄**：Remarks 提到的 **`Custom`** 在 [N] `swRendererType_e.md` 的成员表里**不存在**（该表只有 2 个成员）。
3. **例子调用序**：`swSaveAVIData.RendererType = swRendererType_e.swRendererType_Solidworks_Screen`
4. **枚举**：Returns 段逐字 `Renderer type as defined by [[swRendererType_e]]`。
   [N] `C:\swapi\enums\swRendererType_e.md`（`enum_member_count: 2`，Description 逐字 `Renderer type.`）：

   | Member | Value |
   | --- | --- |
   | `swRendererType_Photoworks_Buffer` | 1 = Valid in documents created in SOLIDWORKS 2010 and earlier |
   | `swRendererType_Solidworks_Screen` | 0 |

5. **废弃链**：无。

**前置一句话**：Remarks 逐字 —— 设成 `Custom` 才能改画面高/宽与宽高比；**但 `Custom` 的数值查不到**（枚举表里没有这个成员）。
**配方一句话**：`swRendererType_e.swRendererType_Solidworks_Screen`（=0）。

### 21.5 `MotionBlur`

1. **精确签名**（**0 个参数**）：`System.bool MotionBlur {get; set;}`
2. **`## Remarks` 逐字摘录**（★ 明确的“valid only if”）：
   > `A ray-trace rendering engine must be active to enable motion blur when saving an animation rendered using the engine.`
3. **例子调用序**：`swSaveAVIData.MotionBlur = True`
   ★ 对应 [E] 同文件的 Preconditions 第 2 条逐字：`2. Verify that a ray-trace rendering engine is active.`
4. **枚举**：无。
5. **废弃链**：无。`## See Also` 点名 `IAVIParameter::BlurLength Property ()` / `IAVIParameter::BlurOffset Property ()`。

**前置一句话**：Remarks 逐字 —— **必须有 ray-trace 渲染引擎处于 active**，否则开不了运动模糊。
**配方一句话**：`True`。

### 21.6 `BlurLength`

1. **精确签名**（**0 个参数**）：`System.int BlurLength {get; set;}` —— 是 `int`。
2. **`## Remarks`**：无 ⇒ 查不到。
3. **例子调用序**：`swSaveAVIData.BlurLength = 10`
4. **枚举**：无。Returns 段逐字写取值域与默认值：`0 <= Length of the motion blur effect when rendering animations using a ray-trace rendering engine <= 100; default = 50`
5. **废弃链**：无。

**前置一句话**：取值域逐字 `0 <= … <= 100`、默认 `50`（写在 Returns 段，不是 Remarks）。
**配方一句话**：例子写 `10`。

### 21.7 `BlurOffset`

1. **精确签名**（**0 个参数**）：`System.int BlurOffset {get; set;}`
2. **`## Remarks`**：无 ⇒ 查不到。
3. **例子调用序**：`swSaveAVIData.BlurOffset = -100`
4. **枚举**：无。Returns 段是一张三行表，逐字：

   | Value | Effect |
   | --- | --- |
   | 0 | Centers the motion blur on the current rendered frame |
   | 100 | Moves the position forward one entire frame |
   | -100 | Moves the position back one entire frame |

5. **废弃链**：无。

**前置一句话**：查不到 —— 三档语义写在 Returns 段。
**配方一句话**：例子写 `-100`（= 向后挪一整帧）。

### 21.8 `ImageSize`

1. **精确签名**（**0 个参数**）：`System.int ImageSize {get; set;}`
2. **`## Remarks`**：无 ⇒ 查不到。
3. **例子调用序**：**官方两个例子都没有设 `ImageSize`** ⇒ 查不到。
4. **枚举**：Returns 段逐字 `Image size as defined by [[swSaveAVIImageSize_e]]`。
   ★ ★ **`swSaveAVIImageSize_e` 的成员与数值：查不到** —— `C:\swapi\enums\swSaveAVIImageSize_e.md` **不存在**（`Test-Path` 为 False）；全 `C:\swapi` grep `swSaveAVIImageSize` **只命中 `ImageSize.md` 这一处引用**，没有任何定义页。
5. **废弃链**：无。

**前置一句话**：查不到 —— 没有任何 Remarks 写出「什么时候必须设它」。
**配方一句话**：查不到 —— 官方例子没设它，而它引用的 `swSaveAVIImageSize_e` 在本机源里没有定义。

---

# 四、本轮「查不到」清单（按铁律 5 如实列出）

| 目标 | 结论 | 依据（可搜索片段） |
| --- | --- | --- |
| `IRoute*` 的**接口成员** | **查不到** | `C:\swapi\types\` 下无 `IRoute*` 目录；CHM `sldworksapi` 里只有 `IAssemblyDoc~GetRouteManager.html` 等**方法页**，无 `IRouteManager` 接口页 |
| `IRoutingComponentManager` 的**接口成员** | **查不到** | `C:\swapi\types\` 下无该目录；CHM 里只有 `IModelDocExtension~GetRoutingComponentManager.html` 一页 |
| `IEdm*` | **查不到** | 全 `C:\swapi` grep `IEdm` 零命中；CHM 四个目录里无任何 `IEdm*` 页面 |
| `swUserPreferenceRoutingInteger_e` / `…Double_e` / `…FileLocations_e` / `…Toggle_e` 的**成员与数值** | **查不到** | `Get-ChildItem C:\swapi\enums \| ? {$_.Name -like "swUserPreferenceRouting*"}` **无输出**；CHM `swconst` 下也无 `swUserPreferenceRouting*` 页面 |
| `swSaveAVIImageSize_e` 的**成员与数值** | **查不到** | `Test-Path C:\swapi\enums\swSaveAVIImageSize_e.md` = False；grep 全仓只命中引用 |
| `IMotionStudy.SaveToAVI` 的 **`## Remarks`** | **查不到** | `C:\swapi\types\IMotionStudy\SaveToAVI.md` **没有 Remarks 段**（只有 Description / Signature / Parameters / Returns / Examples / See Also）；CHM **没有 swmotionstudyapi 目录** |
| `IModelDocExtension.SaveAs3` 的 **`## Examples`** | **查不到** | 该 .md 的 Examples 段为空；`[E]` 目录里没有 SaveAs3 的例子文件 |
| `swRoutingComponentGroupOption_e`（[T] 里引用的那个拼法） | **查不到** | `Test-Path C:\swapi\enums\swRoutingComponentGroupOption_e.md` = False；**存在的是** `swRoutingComponentGroupingOption_e.md` |
| `swRendererType_e` 的 **`Custom`** 成员 | **查不到** | [N] `swRendererType_e.md` 的成员表只有 2 行（`swRendererType_Photoworks_Buffer` / `swRendererType_Solidworks_Screen`），没有 `Custom`；但 `IAVIParameter\RendererType.md` 的 Remarks 提到了它 |
| `swSelSKETCHES` / `swSelEDGES` / `swSelREFCURVES` 的**数值** | **查不到** | 本轮未读 `C:\swapi\enums\swSelectType_e.md`（只从 `IPrimaryMemberPathSegmentFeatureData\GetPathSegmentsTypes.md` 的 Returns 段抄到三个名字） |
| `IPrimaryMemberPathSegmentFeatureData` 的**例子调用序** | **查不到** | `_overview.md` 指向的 `Create_Path_Segment_SSMember_Example_VBNET.md` / `_CSharp.md` 在 `C:\swapi\examples\` 下**按名字搜不到** |
| `IFeatureManager.InsertConnectionPoint` 的**实参调用序** | **查不到** | `[E] Insert_Connection_Point_Example_VB.md` 的 `## Code` 段只有 `Sub main()` / `End Sub` |
| `swOrthogonalMode` 的**归属与数值** | **查不到** | 只在 [C] `Create_Auto_Route_Example_VB.htm` 的代码里出现一次，`C:\swapi\enums\` 下无对应文件 |

---

# 五、本轮抄录清单（成员计数）

| # | 成员 | 来源文件数 |
| --- | --- | --- |
| 1 | `ISldWorks.GetRoutingSettings` | 2 |
| 2 | `IRoutingSettings.GetFromToListHeaderDefinitions` | 2 |
| 3 | `IRoutingSettings.GetRoutingUserPreferenceDoubleValue` | 2 |
| 4 | `IRoutingSettings.GetRoutingUserPreferenceIntegerValue` | 2 |
| 5 | `IRoutingSettings.GetRoutingUserPreferenceStringValue` | 2 |
| 6 | `IRoutingSettings.GetRoutingUserPreferenceToggle` | 2 |
| 7 | `IRoutingSettings.LoadDefaultRoutingSettings` | 1 |
| 8 | `IRoutingSettings.LoadRoutingSettingsFromFile` | 1 |
| 9 | `IRoutingSettings.SaveRoutingSettingsToFile` | 2 |
| 10 | `IRoutingSettings.SetFromToListHeaderDefinitions` | 1 |
| 11 | `IRoutingSettings.SetRoutingUserPreferenceDoubleValue` | 1 |
| 12 | `IRoutingSettings.SetRoutingUserPreferenceIntegerValue` | 1 |
| 13 | `IRoutingSettings.SetRoutingUserPreferenceStringValue` | 1 |
| 14 | `IRoutingSettings.SetRoutingUserPreferenceToggle` | 1 |
| 15 | `IAssemblyDoc.GetRouteManager` | 2 |
| 16 | `IAssemblyDoc.IsRouteAssembly` | 1 |
| 17 | `IModelDoc2.InsertRoutePoint` | 1 |
| 18 | `IModelDoc2.EditRoute` | 2 |
| 19 | `IModelDocExtension.GetRoutingComponentManager` | 1 |
| 20 | `IFeatureManager.InsertConnectionPoint` | 3 |
| 21 | `IConnectionPointFeatureData.AccessSelections` | 2 |
| 22 | `IConnectionPointFeatureData.IAccessSelections` | 1 |
| 23 | `IConnectionPointFeatureData.ReleaseSelectionAccess` | 1 |
| 24 | `IConnectionPointFeatureData.RouteType` | 3 |
| 25 | `IConnectionPointFeatureData.RouteSubType` | 3 |
| 26 | `IConnectionPointFeatureData.RouteDiameter` | 2 |
| 27 | `IConnectionPointFeatureData.StubLength` | 2 |
| 28 | `IConnectionPointFeatureData.PortID` | 2 |
| 29 | `IConnectionPointFeatureData.ElectricalPinID` | 2 |
| 30 | `IConnectionPointFeatureData.Name2` | 2 |
| 31 | `IConnectionPointFeatureData.Location` | 2 |
| 32 | `IConnectionPointFeatureData.Direction` | 2 |
| 33 | `IBomFeature.RoutingComponentGrouping` | 3 |
| 34 | `IPrimaryMemberPathSegmentFeatureData.GetPathSegments` | 1 |
| 35 | `IPrimaryMemberPathSegmentFeatureData.GetPathSegmentsTypes` | 1 |
| 36 | `IPrimaryMemberPathSegmentFeatureData.SetPathSegments` | 1 |
| 37 | `IPrimaryMemberPathSegmentFeatureData.MergeTangentMembers` | 1 |
| 38 | `IApplication.PDMDocManager`（swbrowser） | 2 |
| 39 | `IPDMDocManager.SetManagedDocument` | 2 |
| 40 | `IPDMDocManager.SetDocumentStatus` | 3 |
| 41 | `IPDMDocManager.SetCancelOperation` | 1 |
| 42 | `IModelDocExtension.SaveAs3` | 5 |
| 43 | `IModelDocExtension.GetMotionStudyManager` | 2 |
| 44 | `IMotionStudy.SaveToAVI` | 4 |
| 45 | `IMotionStudyManager.CreateAVIParameter` | 2 |
| 46 | `IMotionStudy.CreateByRotateModel` | 4 |
| 47 | `IMotionStudy.Play` | 3 |
| 48 | `IAVIParameter.OutputType` | 3 |
| 49 | `IAVIParameter.FramePerSecond` | 2 |
| 50 | `IAVIParameter.SaveEntireAnimation` | 2 |
| 51 | `IAVIParameter.RendererType` | 3 |
| 52 | `IAVIParameter.MotionBlur` | 2 |
| 53 | `IAVIParameter.BlurLength` | 2 |
| 54 | `IAVIParameter.BlurOffset` | 2 |
| 55 | `IAVIParameter.ImageSize` | 1 |

**合计 55 个成员**（另有 1 条「`IEdm*`」以「查不到」立节）。