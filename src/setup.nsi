!define PRODUCT_NAME "kindo"
!define PRODUCT_VERSION "1.0"
!define PRODUCT_PUBLISHER "shenghe"
!define PRODUCT_WEB_SITE "https://github.com/shenghe/kindo"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\kindo.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

SetCompressor lzma
RequestExecutionLevel admin
!include "MUI.nsh"
!include "WordFunc.nsh"

!define MUI_ABORTWARNING
!define MUI_ICON "app.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

!insertmacro MUI_PAGE_WELCOME

!insertmacro MUI_PAGE_COMPONENTS

!insertmacro MUI_PAGE_DIRECTORY

!insertmacro MUI_PAGE_INSTFILES

!insertmacro MUI_PAGE_FINISH


!insertmacro MUI_UNPAGE_INSTFILES


!insertmacro MUI_LANGUAGE "SimpChinese"


!insertmacro MUI_RESERVEFILE_INSTALLOPTIONS


Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "..\bin\kindo_setup.exe"
InstallDir "$PROGRAMFILES\kindo"
InstallDirRegKey HKLM "${PRODUCT_UNINST_KEY}" "UninstallString"
ShowInstDetails show
ShowUnInstDetails show
BrandingText "Kindo"

Section "Kindo" SEC01
  SetOutPath "$INSTDIR\${PRODUCT_VERSION}"
  SetOverwrite ifnewer
  CreateDirectory "$SMPROGRAMS\kindo"
  CreateShortCut "$SMPROGRAMS\kindo\kindo.lnk" "$INSTDIR\${PRODUCT_VERSION}\kindo.exe"
  CreateShortCut "$DESKTOP\kindo.lnk" "$INSTDIR\${PRODUCT_VERSION}\kindo.exe"


  File "..\bin\kindo.exe"
  
  ReadRegStr $0 HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "Path"
  WriteRegExpandStr HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "Path" "$0;$INSTDIR\${PRODUCT_VERSION}"
  SendMessage ${HWND_BROADCAST} ${WM_WININICHANGE} 0 "STR:Environment"
SectionEnd

Section -AdditionalIcons
  SetOutPath $INSTDIR
  WriteIniStr "$INSTDIR\${PRODUCT_NAME}.url" "InternetShortcut" "URL" "${PRODUCT_WEB_SITE}"
  CreateShortCut "$SMPROGRAMS\kindo\Website.lnk" "$INSTDIR\${PRODUCT_NAME}.url"
  CreateShortCut "$SMPROGRAMS\kindo\Uninstall.lnk" "$INSTDIR\${PRODUCT_VERSION}\uninst.exe"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\${PRODUCT_VERSION}\uninst.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\${PRODUCT_VERSION}\kindo.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\${PRODUCT_VERSION}\kindo.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "Publisher" "${PRODUCT_PUBLISHER}"
SectionEnd


!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC01} "a simple tool for packaging and deploying your codes"
!insertmacro MUI_FUNCTION_DESCRIPTION_END


Section Uninstall
  Delete "$INSTDIR\${PRODUCT_NAME}.url"
  Delete "$INSTDIR\${PRODUCT_VERSION}\uninst.exe"
  Delete "$INSTDIR\${PRODUCT_VERSION}\kindo.exe"


  Delete "$SMPROGRAMS\kindo\Uninstall.lnk"
  Delete "$SMPROGRAMS\kindo\Website.lnk"
  Delete "$DESKTOP\kindo.lnk"
  Delete "$SMPROGRAMS\kindo\kindo.lnk"

  RMDir /r /REBOOTOK "$SMPROGRAMS\kindo"
  RMDir /r /REBOOTOK "$INSTDIR\${PRODUCT_VERSION}"

  RMDir "$INSTDIR"

  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
  
  ReadRegStr $R0 HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "Path"
	${WordReplace} $R0 ";$INSTDIR\${PRODUCT_VERSION}" "" "+" $R1
	WriteRegExpandStr HKLM "SYSTEM\CurrentControlSet\Control\Session Manager\Environment" "Path" "$R1"

  SetAutoClose true
SectionEnd


Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "您确实要完全移除 $(^Name) ，及其所有的组件？" IDYES +2
  Abort
FunctionEnd

Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) 已成功地从您的计算机移除。"
FunctionEnd
