# 配置详解

## 配置文件

配置文件位于 `career-planning-ai/config.yaml`

## 配置项说明

### 1. 调试模式

```yaml
debug: true
```

控制日志输出级别和调试信息。

---

### 2. 数据库配置 (database)

```yaml
database:
  host: mysql6.sqlpub.com
  port: 3311
  database: career_backend
  user: <USER>
  password: <PASSWORD>
  pool_size: 10           # 连接池基础大小
  max_overflow: 20        # 连接池最大溢出量
  pool_pre_ping: true     # 连接池预检查
  pool_recycle: 3600      # 连接池回收时间（秒）
```

---

### 3. 通信配置 (communication)

```yaml
communication:
  token:
    secret: <SECRET>      # Token密钥（需与Java端一致）
    expire: 1800          # Token过期时间（秒）
```

**重要**: Python 和 Java 端的 `secret` 必须保持一致！

---

### 4. LLM 配置 (llm)

```yaml
llm:
  model_name: qwen-max
  base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
  timeout: 120            # 超时时间（秒）
  max_retries: 3          # 最大重试次数
  max_concurrent_requests: 3  # 最大并发请求数
  extra:
    temperature: 0.7
```

---

### 5. 向量模型配置 (vector)

```yaml
vector:
  model_name: text-embedding-v4
  llm_model_name: qwen-max
  llm_long_model_name: qwen-long
```

---

### 6. LiteLLM 配置 (lite_llm)

```yaml
lite_llm:
  model_name: dashscope/qwen-max
  qwen:
    model_name: dashscope/qwen3.5-plus
  deepseek:
    model_name: dashscope/deepseek-v3-plus
  image:
    model_name: dashscope/qwen-vl-plus
```

---

### 7. PDF 处理配置 (pdf)

```yaml
pdf:
  model_name: qwen-vl-plus
  extra:
    temperature: 0.1
```

---

### 8. 图片处理配置 (image)

```yaml
image:
  model_name: qwen-vl-plus
  suffix: ["JPG", "JPEG", "PNG", "BMP", "GIF"]
  max_size: 10            # 最大尺寸（MB）
  max_dimension: 4096     # 最大分辨率
  extra:
    temperature: 0.7
```

---

### 9. 测试题配置 (test_question)

```yaml
test_question:
  model_name: qwen-max
  timeout: 120
  extra:
    temperature: 0.7
```

---

### 10. 成长计划 Agent 配置 (growth_plan_agent)

```yaml
growth_plan_agent:
  model_name: glm-5
  extra:
    temperature: 0.3
    recursion_limit: 30   # 最大递归深度
```

---

### 11. 路径配置 (path_config)

```yaml
path_config:
  temp:
    path: <TEMP_PATH>            # 临时文件路径
    exit_is_clean: true          # 程序退出时清理临时文件
    run_is_clean: false          # 运行时清理临时文件
    expire: 900                  # 临时文件过期时间（秒）
    cleanup_interval: 60         # 清理间隔（秒）
  log: <LOG_PATH>                # 日志路径
  prompt: <PROMPT_PATH>          # Prompt模板路径
  data: <DATA_PATH>              # 数据路径
```

---

### 12. Milvus 配置 (milvus)

```yaml
milvus:
  force_local: false             # true=强制本地模式
  local:
    host: 49.235.164.243
    port: 19530
  cloud:
    url: <url>
    token: <token>
```

---

### 13. ChromaDB 配置 (chroma_config)

```yaml
chroma_config:
  save_path: <SAVE_PATH>
  model_name: text-embedding-v4
  k: 5                           # 检索返回数量
  collection_name:
    default: default_collection
    project_collection: open_source_projects
    intern_collection: internships
    book_collection: books
    video_collection: videos
  extra:
    temperature: 0.7
```

---

### 14. 代码能力评估配置 (code_ability)

```yaml
code_ability:
  model_name: qwen-max
  extra:
    temperature: 0.3
  github_token: <GITHUB_TOKEN>
  gitee_token: <GITEE_TOKEN>
```

---

### 15. 匹配分析配置 (match_analyzer)

```yaml
match_analyzer:
  extra:
    temperature: 0.2
```

---

### 16. Redis 配置 (redis)

```yaml
redis:
  host: <HOST>
  port: 6379
  username: <USERNAME>
  password: <PASSWORD>
  connect_timeout: 2000          # 连接超时（毫秒）
  cache_timeout:
    default: 86400               # 默认缓存时间（秒）
    file_parse: 86400
    code_ability: 7200
    report: 3600
    question: 3600
```

---

### 17. Neo4j 配置 (neo4j)

```yaml
neo4j:
  url: neo4j+s://xxx.databases.neo4j.io
  username: <USERNAME>
  password: <PASSWORD>
```

---

### 18. 对话记忆配置 (conversation)

```yaml
conversation:
  memory:
    save_path: <SAVE_PATH>
    short:
      max_messages: 20           # 最大消息数量
      max_tokens: 10000          # 最大Token数量
      compression_trigger_raito: 0.8  # 压缩触发比例
      keep_recent_messages: 8    # 压缩时保留最近消息数
      extra:
        temperature: 0.2
    long:
      max_memory_count: 50       # 最多记忆条数
      min_score: 0.6             # 最低记忆分数
      collection_name: user_memories
      extra:
        temperature: 0.2
    extraction:
      extra:
        temperature: 0.2
    compression:
      extra:
        temperature: 0.2
  agent:
    model_name: deepseek-reasoner
    base_url: https://api.deepseek.com
    extra:
      temperature: 0.7
```

---

### 19. 知识图谱配置 (knowledge_graph)

```yaml
knowledge_graph:
  analysis:
    model_name: glm-5
    extra:
      temperature: 0.3
  explain:
    model_name: glm-5
    extra:
      temperature: 0.3
```

---

### 20. 报告助手配置 (report_assistant)

```yaml
report_assistant:
  extra:
    temperature: 0.3
```

---

### 21. 其他配置 (other)

```yaml
other:
  ssl_verify: false
```

---

## 环境变量

敏感配置建议使用环境变量或占位符：

| 占位符 | 说明 |
|--------|------|
| `<USER>` | 数据库用户名 |
| `<PASSWORD>` | 数据库密码 |
| `<SECRET>` | Token密钥 |
| `<TEMP_PATH>` | 临时文件路径 |
| `<LOG_PATH>` | 日志路径 |
| `<GITHUB_TOKEN>` | GitHub Token |
| `<GITEE_TOKEN>` | Gitee Token |

## 配置最佳实践

1. **生产环境**: 使用环境变量替换敏感信息
2. **Token密钥**: 确保 Python 和 Java 端一致
3. **路径配置**: 使用绝对路径
4. **超时设置**: 根据实际网络情况调整
5. **并发控制**: 根据服务器性能调整 `max_concurrent_requests`
