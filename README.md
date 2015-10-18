# Kindo [:cn:](https://github.com/shenghe/kindo/blob/master/README-CN.md) :uk:  

Kindo is a lightweight automated deployment tool developed with python that can be cross-platform and easier to bulk deployment.Just with one command, you can manager a lot of servers and update applications with no agents on systems, and writing scripts like dockerfile can be used to solve complex operations.

## Features

* easy to use： less commands and easier to write scripts that grammar is simple and like dockerfile.
* cross platform: developed with python and available for all major operating systems.
* free and open-source：the client and server are free and open-source that can be easy to develop again.
* no agents：using ssh protocol, with no agents to install on remote systems.

## Related

[Kindo Hub](https://github.com/shenghe/kindo-hub): Open Source Kindo Index (aka Kindo Hub) written in Java

[Kindo Explore](https://shenghe.github.io/kindo): Search Kindo Packages  

## Installation

you can download the binary file or installation package that can be runned on windows and linux from [Releases](https://github.com/shenghe/kindo/releases).

### Windows

download the setup installation package，click next until finished. After the package is installed, the kindo command will be appended the environment variable.

### Linux

download the binary file for linux and make it excetuable, at last, editing the PATH environment variable and add the kindo command path, then run directly. as follows:

```shell
# download binary file to /usr/local/kindo, then:
cd /usr/local/kindo
chmod +x kindo

# vi /etc/profile
export PATH="$PATH:/usr/local/kindo"
source /etc/profile
```

or download the sources directly and install it with python：

```shell
wget https://github.com/shenghe/kindo/archive/master.tar.gz
tar -xzvf master.tar.gz 
cd master/kindo && python setup.py install
```


## Common Concepts

### Deployment Script

Kindo deployment script is a text file with *kic* as a suffix，and write it with a similar Dockerfile grammar.so just learn shell, you can master the script grammar.

Grammar Guide：[Grammar guide](https://github.com/shenghe/kindo/wiki/%E5%A6%82%E4%BD%95%E5%86%99%E8%87%AA%E5%8A%A8%E5%8C%96%E9%83%A8%E7%BD%B2%E8%84%9A%E6%9C%AC)

Scripts Example：[the examples of Kindo deploy scripts](https://github.com/shenghe/kindo/tree/master/examples)

### Deployment Package

Kindo deployment package is an compression file with *ki* as a suffix that can be extracted with winzip or unzip. It's the compiled results of script.

Package naming conventions: `author/name:version`。

Search package: [Explore](https://shenghe.github.io/kindo)

### Remote Repository

you can upload, storage, search and download package after installed the kindo hub on system, the default kindo hub's storage engine is file system.

the kindo can connect to the hub after [configured](https://github.com/shenghe/kindo/wiki/%E5%A6%82%E4%BD%95%E4%BF%AE%E6%94%B9KINDO%E9%85%8D%E7%BD%AE).

### Local Repository

you can specify the local folder to storage packages as caches after downloaded. the folder called local repository.

## Common Commands

### Search Package

In addition to the [website](https://shenghe.github.io/kindo), but also through kindo command can search and download package directly:

```shell
kindo search kindo/demo:1.0
```

Surely, you can only write some words to complete the search, but usually get more results. and then input the package number to download the specified package.

### Run Package

you can use the whole name to run package directly. if the remote repository had the package and it didn't exist on the local repository，the command will download it automatically.

```shell
kindo run kindo/demo:1.0 -h [account@ip:port] -p [password]
```

Surely, allow to specific the full path to run package:

```shell
kindo run ~/kindo-demo-1.0.ki -h [account@ip:port] -p [password]
```

If you configured the server information in the configuration file, you can omit the corresponding parameter.

### Compile Script

If no scripts can be found on the remote repository, meaningly you will write scripts by yourself, at example:

```txt
# Author: kindo
# Name: demo
# Version: 1.0

RUN echo "hello kindo"
```

after the completion of the kindo script, run these commands to compile it:

```shell
kindo build demo.kic
```

### Ad Hoc

if you wanted to run commands without scripts, you might type in to do something really quick as follows:

```shell
kindo shell "echo hello world" -h [account@ip:port] -p [password]
```

If you configured the server information in the configuration file, you can omit the corresponding parameter.


more commands and documents, refer to [kindo command document](https://github.com/shenghe/kindo/wiki/%E5%A6%82%E4%BD%95%E6%89%A7%E8%A1%8CKINDO%E5%91%BD%E4%BB%A4)


## Get Involved

if you have good ideas and improvement suggestion, summit new issues.

if you want to involve in developing, fork and push requests.

if you had writed one script, compile and run `kindo push [package_name]`


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
