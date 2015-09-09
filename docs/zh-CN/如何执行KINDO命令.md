# 如何执行KINDO命令

kindo作为命令行工具，采用类似docker的命令来执行操作。

## 查看说明

```shell
kindo help
```

## 特殊说明

为了减轻学习成本，kindo支持根据输入的文件后缀选择相应的命令。例如：

```shell
# 检查到kic后缀，默认采用build命令编译
kindo text.kic
```

```shell
# 检查到ki后缀，默认采用run命令安装
kindo text.ki
```

## 支持的命令

### build

用法: kindo build [kic_path]

支持的参数：

    -d          开启DEBUG模式
    -o          指定输出文件夹
    -t          设置安装包名称，格式为:作者/名称:版本
    --kipwd     设置安装包运行密码 （后期支持）

编译KINDO脚本，如果为相对地址，则按照如下顺序搜索文件：

    1. 启动文件夹
    2. kindo命令所在文件夹的kics子文件夹
    3. kindo命令所在文件夹
    4. 本地脚本仓库

如果**kic_path**不存在，不输出任何内容。

### clean

用法：kindo clean

支持的参数：
    -d          开启DEBUG模式

清理缓存文件夹

### commit

用法：kindo commit [ki_path]

支持的参数：
    -d          开启DEBUG模式
    -t          设置安装包名称，格式为:作者/名称:版本

用于把安装包移到本地安装包仓库，方便管理和维护。

### help

用法：kindo help 或者 kindo help [command_name]

支持的参数：
    -d          开启DEBUG模式

输出命令用法

### images

用法：kindo images

支持的参数：
    -d          开启DEBUG模式

列出本地仓库的所有安装包

### info

用法：kindo info

支持的参数：
    -d          开启DEBUG模式

列出kindo当前所有配置信息

### login

用法：kindo login 或者 kindo login [username] 或者 kindo login [username] [password]

支持的参数：
    -d          开启DEBUG模式

登录kindo hub，`push`和`rm`命令依赖帐号信息。

### logout

用法：kindo logout

支持的参数：
    -d          开启DEBUG模式

登出，清理配置文件中的帐号信息。

### pull

用法：kindo pull [author/name:version]

支持的参数：
    -d          开启DEBUG模式
    --code      设置提取码

从kindo hub拉取指定的安装包，部分安装包可能设置的提取码，需要输入提取码才能下载。

### push

用法：kindo push [ki_path] 或者 kindo push [author/name:version]

支持的参数：
    -d          开启DEBUG模式
    --code      设置提取码
    --username  登录帐号
    --password  登录密码

把本地安装包推送到kindo hub中，方便其他人使用。如果不想所有人都能下载，可以设置提取码，仅有知道提取码的人才能使用。


### register

用法：kindo register 或者 kindo register [username] 或者 kindo register [username] [password]

支持的参数：
    -d          开启DEBUG模式

注册kindo hub账户


### rmi

用法：kindo rmi [author/name:version]

支持的参数：
    -d          开启DEBUG模式

删除本地仓库中的安装包


### rm

用法：kindo rm [author/name:version]

支持的参数：
    -d          开启DEBUG模式
    --username  登陆账号
    --password  登录密码

删除kindo hub中自己上传的安装包


### run

用法：kindo run [ki_path] 或者 kindo run [author/name:version]

支持的参数：
    -d          开启DEBUG模式
    -h          服务器登录信息，格式：帐号@IP:端口
    -p          服务器登录密码
    -g          服务器组名
    --kipwd     设置安装包运行密码 （后期支持）

运行安装包


### search

用法：kindo search [name]

支持的参数：
    -d          开启DEBUG模式

根据名称模糊搜索安装包

### version

用法：kindo version

支持的参数：
    -d          开启DEBUG模式

显示kindo版本信息
