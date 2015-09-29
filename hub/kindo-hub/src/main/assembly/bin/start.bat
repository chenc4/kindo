@echo off
cd ..
SET BASE_DIR=%cd%

java -Xms64m -Xmx1024m -XX:MaxPermSize=64M -jar %BASE_DIR%/lib/kindo-hub-${project.version}.jar --spring.config.location=file:%BASE_DIR%/conf/application.properties

:end
pause
