# echat
在学习Python socket时候，通过动手实现一个命令行在线聊天室项目，加深对socket编程>和网络编程的理解。主要使用到了`socket`和`select`模块来监听多客户端接入。

## 项目目录结构

```
├── client
│   ├── display.py
│   ├── __init__.py
│   ├── modes
│   │   ├── base.py
│   │   ├── chat.py
│   │   ├── command.py
│   │   ├── contact.py
│   │   ├── __init__.py
│   │   ├── login.py
│   │   ├── query.py
│   │   └── register.py
│   └── statements.py
├── commands.py
├── config.json
├── config.py
├── database.db
├── database.py
├── iface.py
├── messages.py
├── models.py
├── README.md
├── run_client.py
├── run_server.py
├── secure_channel.py
└── server
    ├── __init__.py
    ├── memory.py
    └── routes.py
```

## C/S 架构
![聊天室架构](/images/聊天室架构.png)

主要实现两个部分：

- Client：聊天客户端，将用户输入转换成命令发送给服务器。
- Server：聊天服务器，负责与用户建立连接，处理客户端命令，并加入数据库模块，具备信息存储功能。

服务器设计思路:

1. 服务器监听连接队列：
    `select.select(list(map(lambda x: x.socket, secure_channels))+ self.inputs, [], [])`
2. 当服务器`soctet`有数据可读时：表示有的新的客户端接入。把客户端`socket`添加到监听队列。
3. 当客户端`socket`有数据可读时：表示客户端发送了命令。
4. 从字节序列的`socket stream`解析出`命令`和`参数`。
5. 设计一套WEB框架类似的`路由机制`,根据`命令`找到对应的处理函数。
6. 在服务器端，把`socket`连接和用户信息放到内存中，使用数据库存储用户，聊天室，好友和聊天记录等数据。

客户端设计思路：

1. 客户端连接到服务器，并监听终端输入和服务器连接。
2. 客户端会处于不同的模式模式，在不同的模式下，对于终端输入和服务端消息做不同的处理。
3. 客户端把好友，聊天室以及聊天记录存放到内存中，可以查看。


## 聊天协议

在Socket API上包装了一套简单的应用层协议：采用分层设计，先发送长度后发送内容以及AES数据加密的原则。

数据包格式：
```
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
| Length of Message Body(4Bytes)| AES padding_n(1Bytes)| AES IV(16Bytes)|
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|                        Command(4Bytes)                                |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|     Type of Parameter(1Bytes)     |     Length of Body(4Bytes)        |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
|         int/str/bool/loat类型的字节序列    list和dict特殊处理             |
+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
```

- 对于list类型的参数：每个item都相当于处理第三层的数据包。
- 对于dict类型的参数：
    - key格式为：`|--Length of Key(1Byte)--|--Key--|`；
    - value值相当于第三层的数据包。

源代码：[messages.py](https://github.com/zhongshangwu/E-Chat/blob/master/messages.py)

### AES加密以及DH密钥交换

使用AES加密算法对传输的数据进行加密。在加密之前通过Diffie Hellman密钥交换算法，计算客户端和服务器的共享密钥。

源代码：[secure_channel.py](https://github.com/zhongshangwu/E-Chat/blob/master/secure_channel.py)


## Command 路由

在服务器端，模仿WEB框架的URL路由机制，实现一套Command路由机制。主要使用到Python中的装饰器模式。
(可以尝试的做法：传输的参数和HTTP协议的请求参数一样，统一按照键值对处理。那么根据函数内省机制，请求参数可以自动填充到函数调用中。)

源代码：[routes.py](https://github.com/zhongshangwu/E-Chat/blob/master/server/routes.py)

```
