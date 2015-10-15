pyinstaller -F kindo/kindo.py --upx-dir=kindo --clean -i kindo/app.ico --distpath=bin && rd /s /q build && del /q /s kindo.spec
