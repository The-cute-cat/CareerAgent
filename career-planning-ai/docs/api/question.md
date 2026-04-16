# 题目生成 API 使用文档

> 定位: 测试题生成与答案检查接口
> 更新时间: 2026-04-16

---

## 一、API 端点总览

| 方法 | 路径 | 功能 | 方式 |
|------|------|------|------|
| POST | `/question/generate` | 生成测试题 | 阻塞 |
| POST | `/question/check_student_answer` | 检查学生答案 | 阻塞 |

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

### 常见错误码

| code | 说明 |
|------|------|
| 401 | Token 无效或过期 |
| 422 | 请求参数验证失败 |
| 500 | 服务器内部错误 |

---

## 三、接口详情

### 3.1 生成测试题

```http
POST /question/generate
Content-Type: multipart/form-data
Authorization: Bearer <token>
```

**请求参数 (Form):**

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| content | string | 否 | null | 技能或工具名称 |
| question_type | string | 否 | null | 题目类型：`skill` / `tool` |
| cache_enabled | boolean | 否 | false | 是否启用缓存 |

**题目类型说明:**

| 类型 | 说明 | content 示例 |
|------|------|-------------|
| `skill` | 基于技能生成测试题 | Python、Java、SQL |
| `tool` | 基于工具生成测试题 | Git、Docker、Kubernetes |

**内部处理流程:**

1. 检查缓存（`cache_enabled=true` 时）
2. 根据题目类型调用 Agent 生成题目
3. 自动检查生成的题目质量
4. 如检查不通过，自动修改题目
5. 保存缓存并返回结果

**成功响应:**
```json
{
  "code": 200,
  "state": true,
  "msg": "Success! (=^･ω･^=)",
  "data": [
    {
      "question": "Python 中列表和元组的主要区别是什么？",
      "options": [
        "A. 列表可变，元组不可变",
        "B. 列表不可变，元组可变",
        "C. 没有区别",
        "D. 元组只能存储数字"
      ],
      "answer": "A",
      "explanation": "列表是可变序列，元组是不可变序列。列表使用方括号 []，元组使用圆括号 ()。"
    },
    {
      "question": "以下哪个是 Python 的可变数据类型？",
      "options": [
        "A. 字符串",
        "B. 元组",
        "C. 列表",
        "D. 整数"
      ],
      "answer": "C",
      "explanation": "列表是可变数据类型，可以在原位置修改其内容..."
    }
  ]
}
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| question | string | 题目内容 |
| options | string[] | 选项列表 |
| answer | string | 正确答案（A/B/C/D） |
| explanation | string | 答案解释 |

**示例:**
```bash
curl -X POST "http://localhost:9000/question/generate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "content=Python" \
  -F "question_type=skill" \
  -F "cache_enabled=true"
```

---

### 3.2 检查学生答案

```http
POST /question/check_student_answer
Content-Type: multipart/form-data
Authorization: Bearer <token>
```

**请求参数 (Form):**

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| questions | string | 否 | 题目内容（JSON 字符串） |
| evaluation_criteria | string | 否 | 评分标准 |
| student_answer | string | 否 | 学生答案 |

**请求参数示例:**

```bash
# questions 为 JSON 字符串
questions='[{"question":"...","options":[...],"answer":"A","explanation":"..."}]'

# evaluation_criteria 为评分标准描述
evaluation_criteria="每题20分，共100分"

# student_answer 为学生的作答
student_answer='{"1":"A","2":"B","3":"C"}'
```

**成功响应:**
```json
{
  "code": 200,
  "state": true,
  "msg": "Success! (=^･ω･^=)",
  "data": {
    "total_score": 85,
    "correct_count": 4,
    "wrong_count": 1,
    "details": [
      {
        "question_id": 1,
        "question": "Python 中列表和元组的主要区别是什么？",
        "student_answer": "A",
        "correct_answer": "A",
        "is_correct": true,
        "score": 20,
        "feedback": "回答正确，理解到位"
      },
      {
        "question_id": 2,
        "question": "以下哪个是 Python 的可变数据类型？",
        "student_answer": "B",
        "correct_answer": "C",
        "is_correct": false,
        "score": 0,
        "feedback": "答案错误，正确答案是 C。列表是可变数据类型..."
      }
    ],
    "summary": "整体表现良好，基础扎实，建议加强对可变/不可变数据类型的理解"
  }
}
```

**响应字段说明:**

| 字段 | 类型 | 说明 |
|------|------|------|
| total_score | int | 总得分 |
| correct_count | int | 正确题数 |
| wrong_count | int | 错误题数 |
| details | array | 每题详细结果 |
| details[].question_id | int | 题目序号 |
| details[].question | string | 题目内容 |
| details[].student_answer | string | 学生答案 |
| details[].correct_answer | string | 正确答案 |
| details[].is_correct | boolean | 是否正确 |
| details[].score | int | 该题得分 |
| details[].feedback | string | 反馈说明 |
| summary | string | 整体评价 |

**示例:**
```bash
curl -X POST "http://localhost:9000/question/check_student_answer" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F 'questions=[{"question":"Python中列表和元组的区别？","options":["A.列表可变","B.元组可变"],"answer":"A"}]' \
  -F "evaluation_criteria=每题20分" \
  -F 'student_answer={"1":"A"}'
```

---

## 四、缓存机制

### 缓存键生成

缓存基于 `content` 参数的文本指纹（Fingerprint）生成。

### 缓存生命周期

缓存超时时间由配置文件 `settings.redis.cache_timeout.question` 控制。

### 缓存策略

| 场景 | 行为 |
|------|------|
| `cache_enabled=true` | 优先读取缓存，缓存不存在则重新生成并异步保存 |
| `cache_enabled=false` | 跳过缓存，直接生成 |

---

## 五、题目质量检查流程

生成题目后会自动进行质量检查：

1. **生成题目**: 调用 `test_question_agent.generate_test_questions()`
2. **检查题目**: 调用 `test_question_agent.check_test_questions()`
3. **判断结果**: 
   - 如果 `review_result == "Pass"`，直接返回
   - 如果 `review_result == "Fail"`，调用 `modify_test_questions()` 修改题目
4. **返回结果**: 返回最终检查通过的题目

---

## 六、Java 调用示例

### 生成测试题

```java
@Autowired
private AiServiceClient aiServiceClient;

// 构建请求参数
Map<String, Object> params = new HashMap<>();
params.put("content", "Python");
params.put("question_type", "skill");
params.put("cache_enabled", true);

// 调用接口（Form 表单格式）
AiChatResponse response = aiServiceClient.chatWithOther(
    "/question/generate",
    params,
    false  // enableRetry
);

if (response.isSuccess()) {
    List<Map<String, Object>> questions = (List<Map<String, Object>>) response.getData();
    for (Map<String, Object> q : questions) {
        String question = (String) q.get("question");
        List<String> options = (List<String>) q.get("options");
        String answer = (String) q.get("answer");
        String explanation = (String) q.get("explanation");
    }
}
```

### 检查学生答案

```java
// 构建请求参数（JSON 字符串）
Map<String, Object> params = new HashMap<>();
params.put("questions", questionJsonString);  // JSON 字符串
params.put("evaluation_criteria", "每题20分，共100分");
params.put("student_answer", answerJsonString);  // JSON 字符串

// 调用接口
AiChatResponse response = aiServiceClient.chatWithOther(
    "/question/check_student_answer",
    params,
    false  // enableRetry
);

if (response.isSuccess()) {
    Map<String, Object> result = response.getData();
    int totalScore = (int) result.get("total_score");
    String summary = (String) result.get("summary");
}
```

---

## 七、注意事项

1. **题目类型**: `question_type` 参数必须为 `skill` 或 `tool`
2. **内容参数**: `content` 参数应该是有意义的技能或工具名称
3. **JSON 字符串**: `questions` 和 `student_answer` 参数需要传递有效的 JSON 字符串
4. **缓存建议**: 对于相同的技能或工具，建议开启缓存以提升响应速度
5. **自动修改**: 如果生成的题目质量不达标，系统会自动修改并重新检查
