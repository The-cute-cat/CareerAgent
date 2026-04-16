# 文件解析 API 使用文档

> 定位: 文件内容解析与结构化提取接口
> 更新时间: 2026-04-16

---

## 一、API 端点总览

| 方法 | 路径 | 功能 | 方式 |
|------|------|------|------|
| POST | `/parse/file` | 解析单个文件 | 阻塞 |
| POST | `/parse/files` | 解析多个文件 | 阻塞 |

> 所有接口均需认证: `Authorization: Bearer <token>`

---

## 二、通用参数说明

### 认证方式

```
Authorization: Bearer <token>
```

### 统一响应格式

**成功:**
```json
{
  "code": 200,
  "state": true,
  "msg": "Success! (=^･ω･^=)",
  "data": { ... }
}
```

**失败:**
```json
{
  "code": <错误码>,
  "state": false,
  "msg": "错误描述",
  "data": null
}
```

### 支持的文件类型

| 类型 | 扩展名 | 说明 |
|------|--------|------|
| PDF | `.pdf` | PDF 文档 |
| Word | `.doc`, `.docx` | Microsoft Word 文档 |
| 图片 | `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.webp` | 图片文件（支持 OCR） |
| 纯文本 | `.txt`, `.md`, `.json`, `.csv`, `.xml`, `.html` | 纯文本文件（UTF-8 编码） |

> 文件类型通过魔数（Magic Number）检测真实类型，防止文件伪装攻击
>
> **纯文本文件检测**：系统使用 `binaryornot` 库判断文件是否为纯文本，所有纯文本文件统一按 UTF-8 编码读取

### 常见错误码

| code | 说明 |
|------|------|
| 400 | 文件格式不支持或文件损坏 |
| 401 | Token 无效或过期 |
| 422 | 请求参数验证失败 |
| 500 | 服务器内部错误 |

---

## 三、接口详情

### 3.1 解析单个文件

```http
POST /parse/file
Content-Type: multipart/form-data
Authorization: Bearer <token>
```

**请求参数 (Form):**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| file | file | **是** | — | 上传的文件 |
| cache_enabled | boolean | 否 | true | 是否启用缓存 |

**处理流程:**

1. **安全检测**: 基于魔数识别文件真实类型
2. **缓存检查**: 检查是否有相同文件的缓存结果（基于文件内容 SHA256 指纹）
3. **文本提取**: 调用 `extract_from_file()` 提取文件文本内容
4. **结构化提取**: 调用 `struct_text_extractor.extract_from_text_to_user_form()` 进行结构化提取
5. **缓存保存**: 异步保存结果到 Redis
6. **返回结果**: 返回结构化数据

**成功响应:**
```json
{
  "code": 200,
  "state": true,
  "msg": "Success! (=^･ω･^=)",
  "data": {
    "education": "本科",
    "major": "计算机科学与技术",
    "graduation_date": "2026-06",
    "skills": [
      {"name": "Python", "level": "熟练", "years": 2},
      {"name": "Java", "level": "了解", "years": 1}
    ],
    "tools": [
      {"name": "Git", "level": "熟练"},
      {"name": "Docker", "level": "了解"}
    ],
    "certificates": ["CET-6", "计算机二级"],
    "languages": [
      {"name": "英语", "level": "CET-6"}
    ],
    "projects": [
      {
        "name": "电商系统",
        "role": "后端开发",
        "description": "负责订单模块开发，使用 Django 框架"
      }
    ],
    "internships": [
      {
        "company": "某科技公司",
        "position": "后端开发实习生",
        "duration": "6个月"
      }
    ],
    "code_links": ["https://github.com/user/project"],
    "target_job": "后端开发工程师",
    "target_industries": ["互联网", "金融科技"],
    "priorities": ["技术成长", "薪资", "稳定"]
  }
}
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| education | string | 学历：高中/专科/本科/硕士/博士/其他 |
| major | string | 专业类别 |
| graduation_date | string | 毕业日期，YYYY-MM 格式 |
| skills | array | 技能列表 |
| skills[].name | string | 技能名称 |
| skills[].level | string | 掌握程度：了解/熟悉/熟练/精通 |
| skills[].years | int | 使用年限 |
| tools | array | 工具列表 |
| tools[].name | string | 工具名称 |
| tools[].level | string | 掌握程度 |
| certificates | string[] | 证书列表 |
| languages | array | 语言能力列表 |
| languages[].name | string | 语言名称 |
| languages[].level | string | 等级/水平 |
| projects | array | 项目经历列表 |
| projects[].name | string | 项目名称 |
| projects[].role | string | 担任角色 |
| projects[].description | string | 项目描述 |
| internships | array | 实习经历列表 |
| internships[].company | string | 公司名称 |
| internships[].position | string | 职位 |
| internships[].duration | string | 时长 |
| code_links | string[] | 代码仓库链接列表 |
| target_job | string | 目标岗位 |
| target_industries | string[] | 期望行业列表 |
| priorities | string[] | 核心价值观优先级列表 |

**示例:**
```bash
curl -X POST "http://localhost:9000/parse/file" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@resume.pdf" \
  -F "cache_enabled=true"
```

---

### 3.2 解析多个文件

```http
POST /parse/files
Content-Type: multipart/form-data
Authorization: Bearer <token>
```

**请求参数 (Form):**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| files | file[] | **是** | — | 上传的文件列表 |
| cache_enabled | boolean | 否 | true | 是否启用缓存 |

**并发限制:** 使用信号量（Semaphore）限制最多 3 个文件同时处理

**处理流程:**

1. **安全检测**: 对每个文件进行魔数检测
2. **缓存检查**: 基于所有文件内容的组合 SHA256 指纹检查缓存
3. **并发提取**: 使用 `asyncio.gather()` 并发提取所有文件的文本内容
4. **文本合并**: 将多个文件的文本内容合并，使用分隔符区分
5. **结构化提取**: 对合并后的文本进行结构化提取
6. **缓存保存**: 异步保存结果到 Redis
7. **返回结果**: 返回结构化数据

**文本合并格式:**
```
--- 文件分隔 ---

文件名：resume_1.pdf

文件内容：...

--- 文件分隔 ---

文件名：resume_2.pdf

文件内容：...
```

**成功响应:**
```json
{
  "code": 200,
  "state": true,
  "msg": "Success! (=^･ω･^=)",
  "data": {
    "education": "硕士",
    "major": "计算机科学",
    "skills": [
      {"name": "Python", "level": "精通", "years": 4},
      {"name": "Java", "level": "熟练", "years": 2},
      {"name": "Go", "level": "了解", "years": 1}
    ],
    "projects": [
      {
        "name": "电商系统",
        "role": "后端开发",
        "description": "负责订单模块开发"
      },
      {
        "name": "数据分析平台",
        "role": "全栈开发",
        "description": "负责前后端开发"
      }
    ]
  }
}
```

**示例:**
```bash
curl -X POST "http://localhost:9000/parse/files" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "files=@resume_1.pdf" \
  -F "files=@resume_2.pdf" \
  -F "files=@certificate.pdf" \
  -F "cache_enabled=true"
```

---

## 四、缓存机制

### 缓存键生成

缓存基于文件内容的 SHA256 指纹生成：

1. **单文件**: 计算单个文件的 SHA256 指纹
2. **多文件**: 
   - 计算每个文件的 SHA256 指纹
   - 将所有指纹排序后拼接
   - 对拼接字符串计算 SHA256 作为最终缓存键

### 缓存生命周期

缓存超时时间由配置文件 `settings.redis.cache_timeout.file_parse` 控制。

### 缓存策略

| 场景 | 行为 |
|------|------|
| `cache_enabled=true` | 优先读取缓存，缓存不存在则重新解析并异步保存 |
| `cache_enabled=false` | 跳过缓存，直接解析 |

---

## 五、文件安全机制

### 魔数检测

文件上传后，系统不依赖文件扩展名，而是通过魔数（Magic Number）检测真实文件类型：

| 文件类型 | 魔数签名 |
|---------|---------|
| PDF | `%PDF-` |
| DOCX | `50 4B 03 04` (ZIP 格式) |
| PNG | `89 50 4E 47` |
| JPEG | `FF D8 FF` |
| 纯文本 | 无固定魔数，通过 `binaryornot` 库检测 |

### 纯文本文件检测逻辑

对于没有固定魔数签名的文件（如 `.txt`, `.md`, `.json`, `.csv` 等），系统采用以下检测策略：

1. **魔数快速匹配**: 先尝试匹配预定义的文件签名（如 `xml` 的 `<?xml`、`html` 的 `<!DOCTYPE`）
2. **二进制检测**: 使用 `binaryornot.is_binary()` 判断文件是否为纯文本
3. **统一处理**: 所有纯文本文件统一按 UTF-8 编码读取

### 安全优势

- **防止伪装攻击**: 恶意用户无法通过修改扩展名绕过限制
- **真实类型校验**: 确保文件内容与声明类型一致

---

## 六、Java 调用示例

### 解析单个文件（使用 File 对象）

```java
@Autowired
private AiServiceClient aiServiceClient;

// 使用 File 对象
File file = new File("/path/to/resume.pdf");
Map<String, Object> extraParams = new HashMap<>();
extraParams.put("cache_enabled", true);

AiChatResponse response = aiServiceClient.chatWithFiles(
    "/parse/file",
    0L,  // userId（此接口不强制要求）
    Collections.singletonList(file),
    null,  // conversationId
    extraParams,
    false  // enableRetry
);

if (response.isSuccess()) {
    Map<String, Object> data = response.getData();
    String education = (String) data.get("education");
    String major = (String) data.get("major");
    List<Map<String, Object>> skills = (List<Map<String, Object>>) data.get("skills");
}
```

### 解析单个文件（使用 MultipartFile）

```java
// 使用 MultipartFile（前端直接上传）
MultipartFile multipartFile = ...;  // 从 Controller 接收
Map<String, Object> extraParams = new HashMap<>();
extraParams.put("cache_enabled", true);

AiChatResponse response = aiServiceClient.chatWithMultipartFiles(
    "/parse/file",
    0L,  // userId
    Collections.singletonList(multipartFile),
    null,  // conversationId
    extraParams,
    false  // enableRetry
);
```

### 解析多个文件（使用 File 列表）

```java
// 使用 File 列表
List<File> files = Arrays.asList(
    new File("/path/to/resume_1.pdf"),
    new File("/path/to/resume_2.pdf")
);
Map<String, Object> extraParams = new HashMap<>();
extraParams.put("cache_enabled", true);

AiChatResponse response = aiServiceClient.chatWithFiles(
    "/parse/files",
    0L,  // userId
    files,
    null,  // conversationId
    extraParams,
    false  // enableRetry
);
```

### 解析多个文件（使用 MultipartFile 列表）

```java
// 使用 MultipartFile 列表（前端直接上传）
List<MultipartFile> multipartFiles = ...;  // 从 Controller 接收
Map<String, Object> extraParams = new HashMap<>();
extraParams.put("cache_enabled", true);

AiChatResponse response = aiServiceClient.chatWithMultipartFiles(
    "/parse/files",
    0L,  // userId
    multipartFiles,
    null,  // conversationId
    extraParams,
    false  // enableRetry
);
```

---

## 七、注意事项

1. **并发限制**: 多文件解析接口最多同时处理 3 个文件
2. **文件大小**: 由服务端配置和 Nginx 双重控制
3. **缓存复用**: 相同文件内容可复用缓存，建议开启缓存以提升响应速度
4. **文件类型**: 支持 PDF、DOC/DOCX、PNG/JPG/JPEG/GIF/BMP/WEBP、以及纯文本文件（TXT/MD/JSON/CSV/XML/HTML）
5. **结构化提取**: 解析后会自动提取用户表单所需的字段
6. **多文件合并**: 多文件内容会合并后统一提取，输出单一结构化结果
7. **纯文本编码**: 纯文本文件统一按 UTF-8 编码读取，非 UTF-8 编码可能导致乱码
