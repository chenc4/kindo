# Kindo

Kindo是采用Python开发，基于SSH协议的轻量级自动化部署工具，具有跨平台运行、依赖打包、批量部署、代码包仓库管理且等功能。是目前最为轻量级的开源自动化部署工具，实现一行命令即可批量化部署软件、运行命令，而复杂操作可采用类似dockerfile语法的脚本实现。

## 特性

* 简单易上手：命令少，一行命令即可部署软件;自动化部署脚本语法简单，采用类似dockerfile的语法，仅需要学习shell即可，基本没有额外的学习成本。
* 运行跨平台：采用python开发，支持在各大主流操作系统运行
* 开源免费：客户端及Kindo hub均开源，可方便的基于现有代码做二次开发
* 无需代理：基于SSH协议，无需在服务器安装Agent即可运行

## 安装

你可以从[Releases](https://github.com/shenghe/kindo/releases)下载二进制文件或安装包，Kindo目前支持在Windows和Linux上通过二进制安装。

### Windows

下载Setup安装包，点击下一步即可。安装完成，自动注册kindo命令到环境变量。

### Linux

下载kindo二进制文件，赋予可执行命令，然后直接运行即可。建议手工把kindo所在路径写入环境变量，命令如下。

```shell
# download binary file to /usr/local/kindo, then:
cd /usr/local/kindo
chmod +x kindo

# vi /etc/profile
export PATH=$PATH;/usr/local/kindo
source /etc/profile
```

或者，直接下载源代码，然后通过python安装：

```shell
wget https://github.com/shenghe/kindo/archive/master.tar.gz
tar -xzvf master.tar.gz 
cd master/kindo && python setup.py install
```

## 常用名词

### 部署脚本

Kindo部署脚本是以*kic*为后缀的文本文件，采用类似Dockerfile的语法，支持注释，并以shell命令执行。

语法手册：[Grammar guide](https://github.com/shenghe/kindo/wiki/%E5%A6%82%E4%BD%95%E5%86%99%E8%87%AA%E5%8A%A8%E5%8C%96%E9%83%A8%E7%BD%B2%E8%84%9A%E6%9C%AC)

脚本范例：[the examples of Kindo deploy scripts](https://github.com/shenghe/kindo/tree/master/examples)

### 部署包

Kindo部署包是以*ki*为后缀的压缩文件，可用任意支持zip解压的软件解压，其是通过部署脚本编译后的产物。

部署包的完整命名规范为：`作者名称/包名:版本`。

搜索部署包：[Explore](https://shenghe.github.io/kindo)

### 远程仓库

在服务器上部署好Kindo Hub后，即可以提供上传、存储、搜索、下载部署包的功能，默认仅支持本地文件系统作为存储引擎。

通过[配置kindo](https://github.com/shenghe/kindo/wiki/%E5%A6%82%E4%BD%95%E4%BF%AE%E6%94%B9KINDO%E9%85%8D%E7%BD%AE)，即可与Kindo Hub服务交互，因此我们称Kindo Hub服务为远程仓库。

### 本地仓库

Kindo搜索下载部署包后，都会默认存放在本地指定文件夹作为缓存，因此我们称缓存部署包的文件夹为本地仓库。

## 常用操作

### 搜索部署包

除了通过[网站](https://shenghe.github.io/kindo)搜索部署包外，还可以通过命令直接搜索并下载：

```shell
kindo search kindo/demo:1.0
```

当然，你也可以只写部分单词完成搜索，通常得到较多结果，按照提示输入相应序号选择想要的部署包，即可直接下载到本地仓库。

### 运行部署包

你可以通过部署包全名，直接运行。如果远程仓库存在指定的部署包，且没有下载到本地仓库，此命令会自动下载并运行。

```shell
kindo run kindo/demo:1.0 -h [账号@服务器IP:SSH端口号] -p [密码]
```

当然，如果你下载或编译的部署包没有安装到本地仓库，你也可以通过指定部署包路径运行。

```shell
kindo run ~/kindo-demo-1.0.ki -h [账号@服务器IP:SSH端口号] -p [密码]
```

### 编译部署脚本

如果在远程仓库搜索不到想要的部署包，可以通过自己写脚本编译得到部署包，以如下部署脚本(demo.kic)为例：

```txt
# Author: kindo
# Name: demo
# Version: 1.0

RUN echo "hello kindo"
```

编写完成后，在脚本所在目录运行如下命令生成部署包：

```shell
kindo build demo.kic
```

更多的命令和用法，参考[Kindo 命令文档](https://github.com/shenghe/kindo/wiki/%E5%A6%82%E4%BD%95%E6%89%A7%E8%A1%8CKINDO%E5%91%BD%E4%BB%A4)


## 参与方法

如果你对Kindo有好的想法和改进意见，欢迎ISSUES中提出。

如果你想参与开发或者贡献文档，直接fork and push requests即可。

如果你写了Kindo脚本，编译好后，提交到仓库中吧（`kindo push [你的包名]`）


## License

Copyright 2015 shenghe

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
