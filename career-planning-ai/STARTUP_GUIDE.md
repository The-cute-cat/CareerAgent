# 项目启动指南

## 一、安装依赖

### 1. Python 依赖（使用 Poetry）

#### 首次安装或更新依赖
```bash
# 进入项目目录
cd d:/develop/code/CareerAgent/career-planning-ai

# 安装所有Python依赖
poetry install

# 或者，如果想更新所有依赖到最新版本
poetry update
```

#### 指定Python版本（如果需要）
```bash
# 激活特定的Python环境
poetry env use D:\IDE\Python\3.12\python.exe

# 或使用系统默认Python
poetry env use python
```

#### 常用Poetry命令
```bash
# 查看已安装的依赖
poetry show

# 查看依赖树
poetry show --tree

# 添加新依赖
poetry add <package-name>

# 添加开发依赖
poetry add --group dev <package-name>

# 更新特定依赖
poetry update <package-name>
```

### 2. Node.js 依赖（如果需要）

```bash
# 安装package.json中的依赖
npm install

# 或使用淘宝镜像
npm install --registry=https://registry.npmmirror.com
```

## 二、配置环境

### 1. 修改配置文件
编辑 `config.yaml` 文件，填入你的配置：
```yaml
database:
  host: mysql6.sqlpub.com
  port: 3311
  database: career_backend
  user: <USER>
  password: <PASSWORD>

communication:
  token:
    secret: <SECRET>  # 必须与Java端的secret一致
    expire: 1800

llm:
  model_name: qwen3.5-plus
  base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
  timeout: 30
  max_retries: 3
  extra:
    temperature: 0.7

path_config:
  temp: <TEMP_PATH>  # 临时文件路径
  is_clean: true
  log: <LOG_PATH>    # 日志路径
  prompt: <PROMPT_PATH>  # prompt路径
  data: <DATA_PATH>  # 数据路径
```

### 2. 重要配置说明

#### Token密钥配置
**必须确保Python和Java的token secret一致！**

- **Python配置**: `config.yaml` 中的 `communication.token.secret`
- **Java配置**: `application.yaml` 中的 `communication.token.secret`

## 三、启动服务

### 方法1: 使用Poetry启动（推荐）

```bash
# 开发模式（带热重载）
poetry run uvicorn main:app --host 0.0.0.0 --port 9000 --reload

# 生产模式
poetry run uvicorn main:app --host 0.0.0.0 --port 9000

# 指定workers数量（生产环境）
poetry run uvicorn main:app --host 0.0.0.0 --port 9000 --workers 4
```

### 方法2: 直接使用Python

```bash
# 确保已激活虚拟环境
poetry shell

# 然后启动服务
python -m uvicorn main:app --host 0.0.0.0 --port 9000 --reload
```

### 方法3: 直接运行（不推荐）

```bash
# 不使用Poetry环境
python -m uvicorn main:app --host 0.0.0.0 --port 9000 --reload
```

## 四、验证服务

### 1. 检查服务是否启动
访问: http://localhost:9000/

预期响应:
```json
{
  "code": 200,
  "state": true,
  "msg": null,
  "data": "Emptiness is also an attitude!(=^･ω･^=)"
}
```

### 2. 测试聊天接口

#### 使用HTTP文件测试
打开 `test_chat.http` 文件，点击 "Send Request" 测试

#### 使用curl测试
```bash
curl -X POST "http://localhost:9000/chat/message" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "Authorization: Bearer <token>" \
  -d "message=你好&conversationId=123"
```

#### 通过Java后端测试
```bash
curl -X POST "http://localhost:8080/chat/message" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "message=你好&conversationId=123"
```

## 五、常见问题

### 1. 模块导入错误
**错误**: `ModuleNotFoundError: No module named 'ai_service'`

**解决**: 确保所有导入路径使用 `from src.ai_service.xxx` 格式

### 2. Poetry环境问题
**错误**: `The lock file is not up to date with the latest changes in pyproject.toml`

**解决**:
```bash
# 更新lock文件
poetry lock

# 然后重新安装
poetry install
```

### 3. 端口被占用
**错误**: `Address already in use: ('0.0.0.0', 9000)`

**解决**:
```bash
# Windows - 查找占用端口的进程
netstat -ano | findstr :9000

# 杀掉进程（替换PID为实际进程ID）
taskkill /PID <PID> /F

# 或使用其他端口
poetry run uvicorn main:app --host 0.0.0.0 --port 9001
```

### 4. 依赖冲突
**解决**:
```bash
# 清除Poetry缓存
poetry cache clear pypi --all

# 删除虚拟环境重新创建
poetry env remove <env-name>
poetry install
```

## 六、开发建议

### 1. 使用虚拟环境
始终在Poetry虚拟环境中开发，避免污染全局Python环境

### 2. 依赖更新策略
- 开发环境可以定期 `poetry update` 更新依赖
- 生产环境应该锁定版本，使用 `poetry install` 而不是 `poetry update`

### 3. IDE配置
确保IDE使用Poetry创建的虚拟环境：
- VSCode: 选择正确的Python解释器
- PyCharm: 设置Poetry虚拟环境为项目解释器

### 4. 日志调试
查看服务日志，定位问题：
```bash
# 日志会输出到控制台
# 也可以配置日志文件路径
```

## 七、完整启动流程

```bash
# 1. 进入项目目录
cd d:/develop/code/CareerAgent/career-planning-ai

# 2. 安装/更新依赖
poetry install

# 3. 检查配置文件
# 确保 config.yaml 中的配置正确

# 4. 启动服务
poetry run uvicorn main:app --host 0.0.0.0 --port 9000 --reload

# 5. 验证服务
# 浏览器访问 http://localhost:9000/
```

## 八、停止服务

- 开发模式: 在终端按 `Ctrl + C`
- 如果在后台运行，使用 `taskkill` 命令（Windows）或 `kill` 命令（Linux/Mac）
