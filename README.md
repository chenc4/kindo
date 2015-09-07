## Geting Started

### Download Kindo

if you will use kindo on windows, download from this url:

```txt
https://github.com/shenghe/kindo/blob/master/dist/kindo_setup.exe?raw=true
```

### Install Kindo

if you will install kindo on windows, just press a step until the installation is finished. the kindo command will be installed in environment path.


### Search Command

try to use kindo, firstly, you can search a kindo package. for example, run this demo package as follows:

```txt
# Windows
kindo.exe search demo

# Linux
kindo search demo
```

### Run Command

if the kindo package installed on your system,  can run the package to your target linux system as follows:

```shell
# Windows
kindo.exe demo.ki -h 192.168.1.10 -p examplepwd

# Linux
kindo demo.ki -h 192.168.1.10 -p examplepwd
```

or

```shell
# Windows
kindo.exe run demo

# Linux
kindo run demo
```

or

```shell
# Windows
kindo.exe run demo.ki

# Linux
kindo run demo.ki
```

### Build Image

if you can't search kindo package that you want, writing it is also very easy.

firstly, create a text file that named `example.kic`. the example content like this:

```txt
# Author: shenghe
# Version: 1.0
# Summay: an example kindo package
# Website: https://github.com/shenghe/kindo
# License: Apache 2.0

RUN echo "Hello World"

```

second, build `example.kic` as follows, `example.ki` will be created:

```shell
# Windows
kindo.exe example.kic

# Linux
kindo example.kic
```

or

```shell
# Windows
kindo.exe build example.kic

# Linux
kindo build example.kic
```

or

```shell
# Windows
kindo.exe build example

# Linux
kindo build example
```


### Register Account

the *example.ki* was successfully builded, you can create an account for uploading this package through a list of tips.

```shell
# Windows
kindo.exe register

# Linux
kindo register
```

### Push Image

an account created, then you can upload it to the kindo's repository that everyone can search.

```shell
# Windows
kindo.exe push example.ki

# Linux
kindo push example.ki
```

or

```shell
# Windows
kindo.exe push C:/example.ki

# Linux
kindo push ~/example.ki
```

or


```shell
# Windows
kindo.exe push shenghe/example:1.0

# Linux
kindo push shenghe/example:1.0
```
