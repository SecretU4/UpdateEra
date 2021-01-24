rd /s /q build
rd /s /q dist
D:\dev\ActivePython-2.7.2.5-win32-x86\python.exe -O setup.py py2exe 

ren dist bin
md dist
move bin dist

copy distfile\*.* dist

cd dist
md new_original
md new_translated
md old_original
md old_translated
md simplesrs_source

REM simplesrs용 나머지 source
cd bin
md empty
