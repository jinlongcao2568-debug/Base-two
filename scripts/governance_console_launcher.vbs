Option Explicit

Const PythonwPath = "C:\Users\92407\AppData\Local\Programs\Python\Python311\pythonw.exe"
Const LauncherScript = "D:\Base One\Base-two\AX9\scripts\governance_console_launcher.py"

Dim shell
Set shell = CreateObject("WScript.Shell")
shell.Run Quote(PythonwPath) & " " & Quote(LauncherScript), 0, False

Function Quote(value)
  Quote = Chr(34) & value & Chr(34)
End Function
