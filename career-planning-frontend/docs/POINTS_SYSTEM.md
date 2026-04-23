# 积分与会员系统实现文档

## 一、功能概述

本系统实现了完整的积分和会员功能，包括积分消费、会员折扣、积分充值、积分明细等功能。

## 二、核心功能

### 1. 积分系统

#### 功能积分消耗配置
| 功能 | 消耗积分 |
|------|---------|
| AI职业测评 | 30积分/次 |
| 岗位推荐分析 | 20积分/次 |
| 简历优化 | 50积分/次 |
| 简历一键生成 | 60积分/次 |
| 模拟面试 | 80积分/次 |
| 生涯规划报告 | 100积分/次 |
| AI问答 | 10积分/次 |

#### 新用户注册
- 注册成功后自动赠送 **500积分**
- 显示欢迎弹窗提示

#### 积分消费流程
1. 用户点击功能按钮
2. 系统检查积分余额
3. 积分充足 → 显示消费确认弹窗
4. 用户确认 → 扣除积分并执行功能
5. 积分不足 → 显示积分不足弹窗

### 2. 会员系统

#### 会员类型
| 类型 | 开通赠送 | 每月赠送 | 折扣率 | 价格 |
|------|---------|---------|--------|------|
| 月度会员 | 1000积分 | 1000积分 | 9折 | ¥29.9 |
| 季度会员 | 3500积分 | 1200积分 | 8折 | ¥79.9 |
| 年度会员 | 15000积分 | 1500积分 | 7折 | ¥299.9 |

#### 会员权益
- 积分消耗享受折扣优惠
- 开通即赠大量积分
- 每月自动发放积分

#### 会员标签颜色
- 普通用户：灰色
- 月度会员：蓝色
- 季度会员：紫色
- 年度会员：金色

## 三、核心文件说明

### 1. Mock数据层
**文件**: `src/mock/mockdata/Points_mockdata.ts`
- 积分账户数据模拟
- 积分流水记录
- 会员信息管理
- 积分充值/消费API模拟

### 2. 组合式函数
**文件**: `src/composables/usePoints.ts`
- 统一管理积分相关逻辑
- 提供积分检查、消费、充值方法
- 管理弹窗状态

### 3. 弹窗组件
**目录**: `src/components/PointsDialogs/`

| 组件 | 功能 |
|------|------|
| InsufficientPointsDialog.vue | 积分不足弹窗 |
| ConsumeConfirmDialog.vue | 积分消费确认弹窗 |
| WelcomeGiftDialog.vue | 新用户欢迎弹窗 |
| index.vue | 弹窗容器统一管理 |

### 4. 演示组件
**文件**: `src/components/PointsDemo/PointsDemoButtons.vue`
- 首页积分功能演示
- 测试积分消费和充值

### 5. 会员面板
**文件**: `src/components/CProfile_Component/MemberPlanPanel.vue`
- 积分余额展示
- 积分明细列表
- 功能积分消耗说明
- 会员套餐购买

## 四、使用方法

### 1. 在组件中使用积分消费

```typescript
import { usePoints } from '@/composables/usePoints'

const { 
  consumePoints, 
  showConsumeConfirmDialog,
  hasEnoughPoints 
} = usePoints()

// 方式一：直接消费（带确认弹窗）
const handleUseFunction = () => {
  showConsumeConfirmDialog('aiChat', () => {
    // 用户确认后的回调
    console.log('功能使用成功')
  })
}

// 方式二：检查后再消费
const handleUseFunction2 = async () => {
  if (!hasEnoughPoints(30)) {
    // 积分不足处理
    return
  }
  
  const result = await consumePoints('careerAssessment')
  if (result.success) {
    // 消费成功
  }
}
```

### 2. 充值积分（模拟）

```typescript
const { rechargePoints } = usePoints()

// 充值1000积分
await rechargePoints(1000, '测试充值')
```

### 3. 开通会员

```typescript
const { upgradeMember } = usePoints()

// 开通月度会员
await upgradeMember('monthly')

// 开通季度会员
await upgradeMember('quarterly')

// 开通年度会员
await upgradeMember('yearly')
```

## 五、数据接口预留

### 1. 用户积分余额
```typescript
interface AccountPointsData {
  userId: number
  pointsBalance: number
  totalConsumed: number
  updateTime: string
}
```

### 2. 会员信息
```typescript
interface MemberInfo {
  userId: number
  memberType: 'normal' | 'monthly' | 'quarterly' | 'yearly'
  memberExpireAt: string | null
  monthlyPoints: number
  discountRate: number
}
```

### 3. 积分流水
```typescript
interface PointsRecord {
  id: number
  userId: number
  type: 'earn' | 'consume' | 'recharge' | 'gift' | 'refund'
  amount: number
  balance: number
  description: string
  createTime: string
}
```

## 六、集成说明

1. **App.vue** 已引入全局弹窗容器 `<PointsDialogs />`
2. **顶部导航栏** 已显示积分和会员状态
3. **个人中心** 已集成会员积分面板
4. **注册页面** 已实现新用户积分赠送
5. **登录页面** 已实现欢迎弹窗显示

## 七、注意事项

1. 当前为模拟数据实现，实际对接后端时需：
   - 修改 `src/api/points/index.ts` 中的API调用
   - 移除或修改 `src/mock/mockdata/Points_mockdata.ts` 中的模拟逻辑

2. 积分消费为异步操作，注意处理loading状态

3. 会员过期检查在获取积分时自动进行
