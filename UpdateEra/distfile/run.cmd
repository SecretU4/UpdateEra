@ECHO OFF

SET UEBINPATH=.\bin\UpdateEra.exe
SET CONFPATH=%1

IF "%CONFPATH%"=="" SET CONFPATH=base_without_srs.conf

ECHO.
ECHO [[%CONFPATH% ������ �̿��մϴ�.]]
ECHO.
PAUSE



%UEBINPATH% %CONFPATH%
PAUSE
