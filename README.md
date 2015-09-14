# Kindo

Kindo是采用Python开发，基于SSH协议的轻量级自动化部署工具，具有跨平台运行、依赖打包、批量部署、代码包仓库管理且等功能。是目前最为简单的开源自动化部署工具，实现一行命令即可批量化部署软件、运行命令，而复杂操作可采用类似dockerfile语法的脚本实现。

## 特性

* 简单易上手：命令少，一行命令即可部署软件;自动化部署脚本语法简单，采用类似dockerfile的语法，仅需要学习shell即可，基本没有额外的学习成本。
* 运行跨平台：采用python开发，支持在各大主流操作系统运行
* 开源免费：客户端及Kindo hub均开源，可方便的基于现有代码做二次开发
* 无需代理：基于SSH协议，无需在服务器安装Agent即可运行

## 快速上手

### 安装

1. Windows

[Kindo Setup](https://github.com/shenghe/kindo/blob/master/dist/kindo_setup.exe?raw=true)

下载完成点击下一步即可，安装完成自动在环境变量中注册地址。

2. Linux

[Kindo Setup](https://github.com/shenghe/kindo/blob/master/dist/kindo?raw=true)

下载完成后，复制二进制文件到服务器上，并赋予可执行权限即可，命令如下：

```shell
chmod +x kindo
```

当然，如果你已经在windows中安装好了Kindo，Linux上的kindo可利用如下命令安装：

```shell
kindo pull shenghe/kindo:1.0
kindo run shenghe/kindo:1.0 -h [账号@服务器地址:端口号] -p [密码]
```

### 常见操作

1. 搜索仓库中的Kindo包

如果第一次运行kindo，可以通过关键词搜索相应的部署包，找到相应包后按照提示操作即可下载到本地，例如：

```shell
kindo search demo
```

2. 运行仓库中的Kindo包

通过搜索下载好Kindo包后（如果知道仓库中的Kindo包全称，无需搜索下载），你可以直接指定部署包全称在服务器地址和密码运行，例如：

```shell
kindo run shenghe/demo:1.0 -h [账号@服务器IP:SSH端口号] -p [密码]
```

3. 编译Kindo脚本

很多时候，仓库无法找到想要的部署包，我们可以自己写相应的Kindo脚本并编译成Kindo包，然后运行。
[Kindo脚本](https://github.com/shenghe/kindo/wiki/%E5%A6%82%E4%BD%95%E5%86%99%E8%87%AA%E5%8A%A8%E5%8C%96%E9%83%A8%E7%BD%B2%E8%84%9A%E6%9C%AC)是以**.kic**为后缀的普通文本文件，例如**demo.kic**：

```txt
# Author: shenghe
# Name: demo
# Version: 1.0

RUN echo "hello kindo"
```

编写完成后，在脚本所在目录运行运行如下命令即可编译成Kindo包：

```shell
kindo build demo
```

4. 运行本地Kindo包

生成Kindo包，你有两种方式运行Kindo包。一种，直接指定Kindo包本地绝对地址；第二种，安装Kindo包到本地仓库，然后通过包的名称运行。
第一种，命令如下：

```shell
kindo run ~/shenghe-demo-1.0.ki -h [账号@服务器IP:SSH端口号] -p [密码]
```

第二种，命令如下：

```shell
kindo commit ~/shenghe-demo-1.0.ki
kindo run shenghe/demo:1.0 -h [账号@服务器IP:SSH端口号] -p [密码]
```

更多的命令和用法，参考[Kindo 命令文档](https://github.com/shenghe/kindo/wiki/%E5%A6%82%E4%BD%95%E6%89%A7%E8%A1%8CKINDO%E5%91%BD%E4%BB%A4)

## 你的想法

如果你对Kindo有好的想法和改进意见，欢迎ISSUES中提出。
如果你想参与开发或者贡献文档，直接fork and push requests即可。
如果你写了Kindo脚本，编译好后，提交到仓库中吧（`kindo push [你的包名]`）

## License

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
