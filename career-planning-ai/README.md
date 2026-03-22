# 激活环境

```shell
poetry env use D:\IDE\Python\3.12\python.exe
```

```shell
poetry env use python
```

# 安装依赖

```shell
poetry install --sync
```

# 启动服务

```shell
poetry run uvicorn main:app --host 127.0.0.1 --port 9000 --reload
```

# 移除没有被任何包依赖的包

```shell
poetry sync
```