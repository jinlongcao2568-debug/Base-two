Option Explicit

Const ConsoleUrl = "http://127.0.0.1:8765/"
Const PythonwPath = "C:\Users\92407\AppData\Local\Programs\Python\Python311\pythonw.exe"
Const ConsoleScript = "D:\Base One\Base-two\AX9\scripts\governance_console.py"
Const WaitAttempts = 50
Const WaitSleepMs = 100

Dim shell
Set shell = CreateObject("WScript.Shell")

If Not IsConsoleReachable(ConsoleUrl) Then
  shell.Run Quote(PythonwPath) & " " & Quote(ConsoleScript) & " --no-browser", 0, False
  WaitForConsole ConsoleUrl, WaitAttempts, WaitSleepMs
End If

shell.Run ConsoleUrl, 1, False

Function Quote(value)
  Quote = Chr(34) & value & Chr(34)
End Function

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
