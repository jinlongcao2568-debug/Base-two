Option Explicit

Const ConsoleUrl = "http://127.0.0.1:8765/"
Const PythonwPath = "C:\Users\92407\AppData\Local\Programs\Python\Python311\pythonw.exe"
Const ConsoleScript = "D:\Base One\Base-two\AX9\scripts\governance_console.py"
Const WaitAttempts = 50
Const WaitSleepMs = 100

Dim shell
Dim fso
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

If Not IsConsoleReachable(ConsoleUrl) Then
  shell.Run Quote(PythonwPath) & " " & Quote(ConsoleScript) & " --no-browser", 0, False
  WaitForConsole ConsoleUrl, WaitAttempts, WaitSleepMs
End If

LaunchConsoleWindow ConsoleUrl

Function Quote(value)
  Quote = Chr(34) & value & Chr(34)
End Function

Function BrowserProfileDir()
  BrowserProfileDir = shell.ExpandEnvironmentStrings("%LOCALAPPDATA%") & "\AX9\GovernanceConsoleBrowser"
End Function

Sub EnsureFolder(path)
  If Len(path) = 0 Or fso.FolderExists(path) Then
    Exit Sub
  End If

  Dim parentPath
  parentPath = fso.GetParentFolderName(path)
  If Len(parentPath) > 0 And Not fso.FolderExists(parentPath) Then
    EnsureFolder parentPath
  End If

  fso.CreateFolder path
End Sub

Function DetectBrowserPath()
  Dim candidates
  candidates = Array( _
    shell.ExpandEnvironmentStrings("%ProgramFiles%\Google\Chrome\Application\chrome.exe"), _
    shell.ExpandEnvironmentStrings("%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"), _
    shell.ExpandEnvironmentStrings("%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"), _
    shell.ExpandEnvironmentStrings("%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"), _
    shell.ExpandEnvironmentStrings("%ProgramFiles%\Microsoft\Edge\Application\msedge.exe") _
  )

  Dim candidate
  For Each candidate In candidates
    If fso.FileExists(candidate) Then
      DetectBrowserPath = candidate
      Exit Function
    End If
  Next

  DetectBrowserPath = ""
End Function

Function BuildBrowserCommand(browserPath, url, profileDir)
  BuildBrowserCommand = Quote(browserPath) _
    & " --app=" & Quote(url) _
    & " --user-data-dir=" & Quote(profileDir) _
    & " --disable-extensions" _
    & " --disable-component-extensions-with-background-pages" _
    & " --new-window" _
    & " --no-first-run" _
    & " --no-default-browser-check"
End Function

Sub LaunchConsoleWindow(url)
  Dim browserPath
  browserPath = DetectBrowserPath()
  If Len(browserPath) = 0 Then
    shell.Run url, 1, False
    Exit Sub
  End If

  Dim profileDir
  profileDir = BrowserProfileDir()
  EnsureFolder profileDir
  shell.Run BuildBrowserCommand(browserPath, url, profileDir), 1, False
End Sub

Function IsConsoleReachable(url)
  On Error Resume Next
  Dim http
  Set http = CreateObject("WinHttp.WinHttpRequest.5.1")
  http.SetTimeouts 250, 250, 250, 250
  http.Open "GET", url, False
  http.Send
  IsConsoleReachable = (Err.Number = 0 And http.Status > 0)
  Err.Clear
  Set http = Nothing
  On Error GoTo 0
End Function

Sub WaitForConsole(url, attempts, sleepMs)
  Dim index
  For index = 1 To attempts
    If IsConsoleReachable(url) Then
      Exit Sub
    End If
    WScript.Sleep sleepMs
  Next
End Sub
