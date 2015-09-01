pyinstaller -F src/kindo.py --upx-dir=src --clean -i src/app.ico --distpath=dist && rd /s /q build && del /q /s kindo.spec
