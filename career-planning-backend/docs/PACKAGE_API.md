# Package 套餐管理 API 文档

## 概述
套餐管理模块提供了对系统套餐的完整增删查改功能，支持积分套餐和会员套餐两种类型。

## API 接口列表

### 1. 添加套餐
**POST** `/package/add`

**请求体示例：**
```json
{
  "type": 1,
  "amount": 9.99,
  "points": 100,
  "name": "积分套餐-小",
  "description": "100积分",
  "status": 1
}
```

**响应示例：**
```json
{
  "code": 200,
  "msg": "套餐添加成功",
  "data": null
}
```

**参数说明：**
| 参数 | 类型 | 必需 | 说明 |
|------|------|------|------|
| type | Integer | 是 | 套餐类型：1-积分套餐，2-会员套餐 |
| amount | BigDecimal | 是 | 套餐金额 |
| points | Integer | 否 | 积分数量（仅积分套餐） |
| name | String | 是 | 套餐名称 |
| description | String | 否 | 套餐描述 |
| status | Integer | 否 | 是否启用：0-禁用，1-启用（默认1） |

---

### 2. 删除套餐
**DELETE** `/package/delete/{id}`

**路径参数：**
| 参数 | 类型 | 说明 |
|------|------|------|
| id | Long | 套餐ID |

**响应示例：**
```json
{
  "code": 200,
  "msg": "套餐删除成功",
  "data": null
}
```

---

### 3. 更新套餐
**PUT** `/package/update`

**请求体示例：**
```json
{
  "id": 1,
  "type": 1,
  "amount": 11.99,
  "points": 120,
  "name": "积分套餐-小升级",
  "description": "120积分",
  "status": 1
}
```

**响应示例：**
```json
{
  "code": 200,
  "msg": "套餐更新成功",
  "data": null
}
```

---

### 4. 查询单个套餐
**GET** `/package/{id}`

**路径参数：**
| 参数 | 类型 | 说明 |
|------|------|------|
| id | Long | 套餐ID |

**响应示例：**
```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "id": 1,
    "type": 1,
    "amount": 9.99,
    "points": 100,
    "name": "积分套餐-小",
    "description": "100积分",
    "status": 1
  }
}
```

---

### 5. 查询所有启用的套餐
**GET** `/package/list/all`

**响应示例：**
```json
{
  "code": 200,
  "msg": "success",
  "data": [
    {
      "id": 1,
      "type": 1,
      "amount": 9.99,
      "points": 100,
      "name": "积分套餐-小",
      "description": "100积分",
      "status": 1
    },
    {
      "id": 4,
      "type": 2,
      "amount": 29.99,
      "points": null,
      "name": "会员套餐-月度VIP",
      "description": "享受一个月VIP权限",
      "status": 1
    }
  ]
}
```

---

### 6. 按类型查询套餐
**GET** `/package/list/type/{type}`

**路径参数：**
| 参数 | 类型 | 说明 |
|------|------|------|
| type | Integer | 套餐类型：1-积分套餐，2-会员套餐 |

**响应示例：**
```json
{
  "code": 200,
  "msg": "success",
  "data": [
    {
      "id": 1,
      "type": 1,
      "amount": 9.99,
      "points": 100,
      "name": "积分套餐-小",
      "description": "100积分",
      "status": 1
    },
    {
      "id": 2,
      "type": 1,
      "amount": 49.99,
      "points": 600,
      "name": "积分套餐-中",
      "description": "600积分，超值优惠",
      "status": 1
    }
  ]
}
```

---

## 说明

### 关键特性

1. **MyBatis-Plus 集成**
   - 使用 BaseMapper 实现基础 CURD 操作
   - 支持 Lambda 查询和更新，代码简洁

2. **事务管理**
   - 添加、删除、更新操作使用 @Transactional 注解确保数据一致性

3. **参数验证**
   - DTO 使用 @Valid 和 Jakarta validation 注解进行验证
   - 自动验证必填字段和数据合法性

4. **日志记录**
   - 使用 Slf4j 记录关键业务操作
   - 便于问题排查和审计

5. **异常处理**
   - 统一的 Result 响应格式
   - 详细的错误日志和错误信息

### 套餐类型说明

- **类型 1：积分套餐**
  - 用户支付金额后获得对应积分
  - `points` 字段不能为空
  
- **类型 2：会员套餐**
  - 用户支付金额后获得会员权限
  - `points` 字段可为空

### 状态说明

- `0`：禁用（套餐不可购买）
- `1`：启用（套餐正常显示和购买）

### 前后端交互建议

1. **前端展示套餐**
   ```
   调用 GET /package/list/all 或 GET /package/list/type/{type}
   获取启用的套餐列表展示给用户
   ```

2. **用户购买套餐**
   ```
   前端获取套餐 ID → 调用支付接口 → 支付成功后保存用户购买记录
   ```

3. **管理后台管理套餐**
   ```
   调用 POST /package/add 添加新套餐
   调用 PUT /package/update 编辑套餐
   调用 DELETE /package/delete/{id} 删除套餐
   调用 GET /package/{id} 查看套餐详情
   ```

