# KINDO FAQ

## 相比ansible，kindo有何不同？

答：kindo和ansible都是基于python fabric库开发的一套自动化部署工具，都不需要在服务器端安装客户端，利用SSH即可运行。但是kindo的学习门槛更低，基本不需要另外学习其他的脚本语言，使用shell脚本即可完成部署工作。同时，kindo的安装更为方便，在Windows上，仅需要运行一个exe即可，linux上直接作为一个python标准库安装即可运行，非常轻量级。

## kindo有何优势？

答：

1. 跨平台且安装方便。windows上直接运行exe即可，linux上直接运行`python setup.py install`，整个代码没有过多的依赖第三方库
2. 学习成本低。kindo设计上参考了docker，命令甚至脚本语法都非常简单，基本上可以做到安装即用
3. 部署方便。Linux上不需要安装客户端，仅需要sshd安装即可，基本所有的Linux操作系统均可使用。脚本支持把所有源代码的依赖打包，如果部署了私有仓库，在任意地方，带上kindo.exe就可以部署相应的代码
4. 开源免费。kindo代码开源，你可以部署自己的私有仓库，也可以自定义添加新的命令和功能，完全开源
5. 安全加密。支持对打包的image进行加密，甚至可以对上传到仓库的代码添加提取码，满足一些对安全有较高要求的场景
6. 批量部署。支持一条命令部署多台机器，满足批量部署的场景

## 如何自定义安装包的下载位置

答：设置环境变量`KINDO_IMAGES_PATH`, 则通过search或pull命令下载的安装包，都回安装到指定的文件夹下。默认情况下，Windows目录为*%APPDATA%/kindo/images*;Linux目录为*/var/opt/kindo/images*

## 如何自定义缓存文件夹

答：设置环境变量`KINDO_CACHES_PATH`, 每次运行run命令，都会解压安装包的文件到此目录。默认情况下，Windows目录为*%APPDATA%/kindo/caches*;Linux目录为*/var/cache/kindo*

## 如何自定义私有仓库地址

答：设置环境变量`KINDO_SETTINGS_PATH`, 即可设置配置文件的存放目录. 默认情况下，Windows目录为*%APPDATA%/kindo/settings*;Linux目录为*/etc/opt/kindo*。在此目录下找到*kindo.ini*，修改default组的index为私有仓库地址即可。

## 如何修改上传帐号的信息

答：在配置文件存放目录，找到*kindo.ini*，修改default组的username和password即可。


