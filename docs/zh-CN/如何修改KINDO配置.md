# 如何设置KINDO的配置

kindo默认情况下，不需要任何配置即可正常运行。如果需要自定义一些参数，可以根据此文档做相应修改。kindo的配置分为多部分，一部分通过环境变量设置，一部分通过配置文件设置。

## 环境变量

### KINDO_CACHES_PATH

设置kindo缓存目录，不同操作系统，默认目录不同：

WINDOWS:
    %APPDATA%/kindo/caches

LINUX:
    /var/cache/kindo

### KINDO_KICS_PATH

设置脚本仓库地址，为了方便管理自己的KINDO脚本，可以把所有的脚本都放在此目录。不同操作系统，默认目录不同：

WINDOWS:
    %APPDATA%/kindo/kics

LINUX:
    /var/opt/kindo/kics


### KINDO_IMAGES_PATH

设置存放下载或安装的部署包目录，建议放到较大空间的目录，不同操作系统，默认目录不同：

WINDOWS:
    %APPDATA%/kindo/images

LINUX:
    /var/opt/kindo/images

### KINDO_SETTINGS_PATH

设置配置文件存放目录，不同的操作系统，默认目录不同：

WINDOWS:
    %APPDATA/kindo/settings

LINUX:
    /etc/opt/kindo

## 配置文件

kindo配置文件，都存放在*KINDO_SETTINGS_PATH*环境变量设置的目录。

### kindo.ini

用于设置kindo的基础配置，所写配置可以被命令行参数覆盖。

**index**: 设置kindo hub域名

**timeout**: 设置运行部署包时，命令超时时间，默认为：60 * 30

**ignore**: 设置`ADDONRUN`在文件不存在时是否抛出异常，默认忽略

**username**: 设置登录kindo hub的帐号

**password**: 设置登录kindo hub的密码

### hosts.ini

kindo支持批量部署，或者指定机器组部署。所有的机器分组信息都在此配置文件设置。格式为：

```txt
[机器分组名]
帐号@地址:端口=密码
```

### images.ini

安装或下载部署包后，此文件内即写入相应的信息。

## 查看配置信息

可以通过如下命令快速查看当前配置：

```shell
kindo info
```

