' ========================================
' Script de inicio silencioso (sin ventanas)
' App Datos Sensibles
' ========================================

' Este script ejecuta PM2 completamente en segundo plano
' sin abrir ninguna ventana de terminal

Set objShell = CreateObject("WScript.Shell")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Obtener directorio del script
scriptPath = objFSO.GetParentFolderName(WScript.ScriptFullName)
projectPath = objFSO.GetParentFolderName(scriptPath)

' Cambiar al directorio del proyecto
objShell.CurrentDirectory = projectPath

' Verificar si PM2 esta instalado
On Error Resume Next
pm2Check = objShell.Run("pm2 --version", 0, True)
On Error GoTo 0

If pm2Check <> 0 Then
    MsgBox "ERROR: PM2 no esta instalado." & vbCrLf & vbCrLf & _
           "Por favor ejecuta primero: scripts\install-service.bat" & vbCrLf & vbCrLf & _
           "Ese script instalara PM2 y las dependencias necesarias.", _
           vbCritical, "App Datos Sensibles"
    WScript.Quit 1
End If

' Verificar entorno virtual de Python (sin ventana)
If Not objFSO.FolderExists(projectPath & "\backend\venv") Then
    objShell.Run "cmd /c py -m venv backend\venv", 0, True
End If

' Instalar dependencias de Python (sin ventana)
objShell.Run "cmd /c backend\venv\Scripts\pip install -r backend\requirements.txt", 0, True

' Instalar dependencias de Node.js si no existen (sin ventana)
If Not objFSO.FolderExists(projectPath & "\node_modules") Then
    objShell.Run "cmd /c npm install", 0, True
End If

' Crear directorio de logs si no existe
If Not objFSO.FolderExists(projectPath & "\logs") Then
    objFSO.CreateFolder projectPath & "\logs"
End If

' Detener procesos anteriores (sin ventana)
objShell.Run "cmd /c pm2 delete all", 0, True

' Iniciar aplicaciones con PM2 (sin ventana)
objShell.Run "cmd /c pm2 start ecosystem.config.js", 0, True

' Esperar un momento para que los procesos inicien
WScript.Sleep 2000

' Guardar configuracion de PM2 (sin ventana)
objShell.Run "cmd /c pm2 save", 0, True

' Mostrar notificacion de exito (opcional - comentar si no quieres notificacion)
MsgBox "Servicios iniciados correctamente en segundo plano" & vbCrLf & vbCrLf & _
       "Frontend: http://localhost:3030" & vbCrLf & _
       "Backend: http://localhost:5000" & vbCrLf & vbCrLf & _
       "Para ver el estado: pm2 status" & vbCrLf & _
       "Para ver logs: pm2 logs", _
       vbInformation, "App Datos Sensibles"

WScript.Quit 0
