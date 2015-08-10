# kindo
A simple tool for packaging and deploying your code to linux with just a command. it can be used on windows and linux.

## 安装方式

Linux：

```shell
wget https://github.com/shenghe/kindo/raw/master/dist/kindo_setup_latest.rpm
rpm -i kindo_setup_latest.rpm
```

Windows:

```shell
https://github.com/shenghe/kindo/raw/master/dist/kindo_setup_latest.exe
```

## 运行方式

### BUILD

```shell
kindo [example.kic]     -o [outfolder/outfile]
kindo [input folder]    -o [outfolder/outfile]
```

### install

```shell
kindo [example.ki] -h [account@host:port] -p [password] --[varible]=[value]
```

## kindo file structure

### ki

it's a custom extension tar.gz package, the package structure like this:

```txt
conf
    example1.kibc
    example2.kibc
    ...
deps
    example_dep1.tar.gz
    ...
manifest.json
```

### kibc

it's a binary file by pickled with json. the json structure is:

```json
[
    {
        "action": "ADD|RUN|CHECK|ENV|EXPOSE|VOLUME|WORKDIR",
        "args": {},
        "variables": [
            {
                "symbol": "${varible:default}"
                "varible": "",
                "default": ""
            }
        ]
    }
]
```

### kic

it's a file like dockfile. will be compiled to kibc.

```txt
# it's a description
ADD [from] [to]
RUN [command]
CHECK [port1] [port2] [file1] [file2]
ENV [env name] [env value]
EXPOSE [port1] [port2] [port3]
VOLUME [from] [to]
WORKDIR [dir]
```


### kindo

```txt
    dist
        kindo_setup_lasted.rpm
        kindo_setup_lasted.exe
    example
        nginx
            nginx.kic
            deps
                nginx-src.tar.gz
        ...
    src
        ...
    README.txt
```


