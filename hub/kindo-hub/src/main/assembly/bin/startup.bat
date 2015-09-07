@echo off
cd ..
SET BASE_DIR=%cd%

java -Xms64m -Xmx1024m -XX:MaxPermSize=64M -jar %BASE_DIR%/lib/kindo-hub-${project.version}.jar -classpath %BASE_DIR%/conf

:end
pause
