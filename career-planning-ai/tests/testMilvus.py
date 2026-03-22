from pymilvus import connections, utility

# 连接 Milvus
connections.connect(
    host="192.168.3.128",  # 服务器 IP
    port="19530"           # 端口
)

# 验证连接
print("✓ 连接成功！")
print(f"集合列表：{utility.list_collections()}")