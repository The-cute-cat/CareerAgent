# 前端功能文档

## 1. 项目概述

本项目是一个面向大学生/求职用户的 AI 职业规划前端系统，核心目标是把“用户画像采集、岗位匹配、职业报告、发展路径、简历生成、会员积分、AI 助手”串成一个完整闭环。

当前前端技术栈：

- Vue 3 + TypeScript
- Vite
- Element Plus
- Pinia + pinia-plugin-persistedstate
- Axios
- ECharts

当前代码中同时存在两条主线模式：

- 学习模式：偏学习方向、能力补齐、成长规划
- 求职模式：偏岗位匹配、职业报告、简历与投递准备

模式状态由 `career-mode` 持久化保存，首页、职业表单等页面会根据模式切换文案和功能入口。

## 2. 核心业务闭环

系统前端围绕以下业务链路组织：

1. 未登录用户进入欢迎页，了解产品能力并进入登录/注册。
2. 登录后进入首页，可切换学习/求职模式并进入对应主流程。
3. 用户在职业表单页上传简历、补充教育/技能/经历/测评/职业意向信息。
4. 前端将表单转换为后端 DTO，提交后生成岗位匹配结果。
5. 岗位匹配结果进入“岗位匹配页”和“岗位详情页”，并可继续生成职业发展报告。
6. 报告支持本地按岗位缓存、编辑、AI 完整性检查、AI 润色、导出 PDF / Word。
7. 用户可继续查看职业发展地图、知识图谱、面试管理、个人中心、积分会员与支付能力。
8. AI 助手贯穿全局，支持流式对话和文件上传问答。

## 3. 路由与页面功能

### 3.1 公开页面

#### `/welcome`

欢迎落地页，主要用于产品介绍和转化。

功能点：

- 展示产品定位、核心能力、使用步骤、FAQ
- 展示职业规划、岗位匹配、职业路径等能力卖点
- 提供跳转登录入口

对应页面：

- `src/views/LandingPage.vue`

#### `/login`

登录页。

功能点：

- 用户名/邮箱 + 密码登录
- 登录成功后写入 `accessToken`、`refreshToken`、`userInfo`
- 登录成功后跳转首页
- 错误提示与成功通知

对应页面：

- `src/views/CUserLogin.vue`

#### `/register`

注册页。

功能点：

- 用户名、邮箱、密码、确认密码、验证码、邀请码
- 发送邮箱验证码倒计时
- 注册成功后清空本地登录信息并跳转登录页
- 注册成功提示赠送新人积分

对应页面：

- `src/views/CUserRegister.vue`

#### `/forgot-password`

忘记密码页。

功能点：

- 邮箱找回密码
- 与用户模块接口联动

对应页面：

- `src/views/CUserForgetPassword.vue`

### 3.2 登录后主框架页面

登录后默认进入 `Layout` 容器，整体由侧边栏、顶部栏、主内容区、全局 AI 助手组成。

对应组件：

- `src/components/Layout.vue`
- `src/components/Sidebar.vue`
- `src/components/CHeader.vue`
- `src/components/ChatBot.vue`

#### `/`

首页/工作台。

功能点：

- 根据学习模式/求职模式切换首页入口内容
- 展示快捷操作卡片
- 展示能力雷达图
- 展示系统使用指引
- 首页模式卡片与推荐面板联动

对应页面：

- `src/views/CHomePage.vue`

#### `/career-form/resume`
#### `/career-form/template`

职业画像采集与简历生成入口页，项目当前最重的业务页面之一。

功能点：

- 五步式信息采集
- 支持学习模式与求职模式两套文案
- 简历上传与解析
- 缺失字段提醒与补录聊天
- 语言、证书、技能、工具、项目、实习动态增删
- 素质测评与问卷
- 代码仓库链接录入
- GitHub/Gitee 代码能力评估
- 表单进度、画像完整度、步骤完成度计算
- 本地缓存职业表单数据
- 提交前转换 DTO
- 提交后生成人岗匹配结果并供后续页面消费
- 生成 JSON Resume
- 选择简历模板预览
- 导出简历 PDF / Word
- 跳转到独立简历编辑器

对应页面与组件：

- `src/views/CareerForm.vue`
- `src/components/CareerForm_Upload.vue`
- `src/components/ResumeMissingFieldsChat.vue`
- `src/components/Quenation.vue`
- `src/components/career/*`

#### `/career-form/voice`

语音/对话式职业表单辅助入口。

功能点：

- 读取当前缓存表单快照
- 展示表单进度、画像完整度、已完成步骤数
- 将数据传给语音表单组件

对应页面：

- `src/views/CareerFormVoice.vue`
- `src/components/CareerForm_Voice.vue`

#### `/resume-template`

简历模板展示页。

功能点：

- 展示三类简历模板卡片
- 提供预览、下载、使用模板入口
- 跳转独立简历编辑器

说明：

- 当前更偏展示与跳转入口，真正的编辑与导出能力在 `/resume-editor` 和职业表单页内实现。

对应页面：

- `src/views/ResumeTemplate.vue`

#### `/resume-editor`

独立简历编辑器。

功能点：

- 从职业表单缓存和 JSON Resume store 自动回填数据
- 支持示例数据一键填充
- 支持三种简历模板切换
- 基本信息、工作经历、项目经历、其他信息多标签编辑
- 实时简历预览
- 简历完整度校验
- 导出 PDF
- 导出 Word

对应页面：

- `src/views/ResumeEditor.vue`

#### `/job-matching`

岗位匹配结果页。

功能点：

- 从本地 `jobMatchResult` 读取匹配结果
- 按匹配分排序
- 顶部展示最佳匹配岗位
- 展示平均分、推荐投递比例、岗位数量
- 展示推荐岗位列表
- 每个岗位展示岗位画像、匹配分、可投递判断、技能差距、行动建议
- 跳转岗位详情页
- 可返回职业评估页重新生成结果

对应页面：

- `src/views/JobMatching.vue`

#### `/job-position`

单个岗位详情页。

功能点：

- 查看岗位细节、匹配信息和分析结果

说明：

- 当前路由直接挂载组件而不是视图文件。

对应组件：

- `src/components/JobMatching_Position.vue`

#### `/report`

职业发展报告页。

这是当前第二个核心业务页面。

功能点：

- 如果已有人岗匹配结果，先选择/切换目标岗位
- 按岗位维度读取本地缓存报告
- 可为某个岗位生成并切换职业报告
- 报告分章节展示：
  - 学生画像摘要
  - 能力差距分析
  - 目标岗位画像摘要
  - 短期行动计划
  - 中期发展规划
  - 行动清单
  - 资源与建议
- 报告工作台概览与章节导航
- 本地勾选行动完成度
- 章节编辑
- 单段 AI 润色
- 整体 AI 润色
- AI 完整性检查
- 保存报告到本地 store
- 导出 PDF
- 导出 Word

对应页面与组件：

- `src/views/CReport.vue`
- `src/components/CReport_Component/CReportEditor.vue`

#### `/report/edit`

报告编辑器页面。

功能点：

- 对报告指定章节进行富文本/结构化编辑

对应组件：

- `src/components/CReport_Component/CReportEditor.vue`

#### `/development-map`

职业发展地图页。

功能点：

- 支持纵向晋升图谱与横向转岗图谱切换
- 使用 ECharts Graph 展示职业路径
- 支持节点搜索
- 支持缩放、拖拽、重置、回到起点
- 支持路径快捷切换与高亮
- 点击节点查看岗位详情
- 点击边查看迁移分析
- 侧边详情面板展示：
  - 路径总结
  - 关键指标
  - 技能缺口
  - JD 原文上下文
  - 行动建议

对应页面：

- `src/views/DevelopmentMap.vue`

#### `/knowledge-base`

岗位知识图谱/学习路线页。

功能点：

- 列表态展示不同岗位学习路径
- 按分类筛选与关键字搜索
- 进入岗位详情后展示知识树
- 支持拖动画布
- 支持点击节点查看详情
- 详情侧栏展示知识说明、难度、学习时长、标签、资源、里程碑

当前数据状态：

- 以本地静态数据为主，Java 方向内容最完整，部分岗位树为空占位。

对应页面：

- `src/views/JobKnowledge.vue`

#### `/interviews/:type?`

面试管理页。

功能点：

- 面试日历
- 今日面试摘要
- 面试列表
- 面试复盘
- 根据路径参数切换全部/进行中/已完成/复盘/日历子视图

当前数据状态：

- 使用本地 mock 面试数据

对应页面与组件：

- `src/views/CInterviews.vue`
- `src/components/CInterviews_Component/*`

#### `/profile`
#### `/settings`

个人中心/设置中心。

功能点：

- 个人首页 Dashboard
- 个人资料编辑
- 会员积分面板
- 邀请好友
- 反馈建议
- 更多设置
- 移动端左侧菜单/右侧内容切换
- 拉取账户积分和邀请码
- 支持退出登录
- 支付成功后刷新用户信息与积分状态

对应页面与组件：

- `src/views/CProfile.vue`
- `src/components/CProfile_Component/*`

#### `/admin`

后台管理页。

功能点：

- 反馈管理
- 使用记录管理

对应组件：

- `src/components/AdminManager/AdminPanel.vue`
- `src/components/AdminManager/FeedbackManager.vue`
- `src/components/AdminManager/UsageRecordManager.vue`

## 4. 全局 AI 助手

全局悬浮聊天窗口挂载在主布局中，属于全站级能力。

核心能力：

- 流式对话
- 自动创建/复用 conversationId
- 支持文件上传
- 支持 PDF、DOCX、图片等文件问答
- 支持显示思考过程开关
- 支持消息复制、折叠展开、重试
- 支持拖拽移动窗口、缩放窗口、全屏
- 支持对话窗口和悬浮按钮位置持久化
- 支持自动打开、滚动触发、退出触发等配置项

接口说明：

- 文本消息走 `/chat/stream/message`
- 文本+文件走 `/chat/stream/message-and-files`
- 前端内置了 SSE / JSON 对象流解析逻辑

对应文件：

- `src/components/ChatBot.vue`
- `src/api/chatbot/index.ts`

## 5. 状态管理

### 5.1 用户状态 `useUserStore`

职责：

- 保存 `accessToken`
- 保存 `refreshToken`
- 保存 `userInfo`
- 计算 `isLoggedIn`
- 提供登录写入、清空用户信息等方法

特点：

- 整个 store 持久化

对应文件：

- `src/stores/modules/user.ts`

### 5.2 职业模式状态 `useCareerModeStore`

职责：

- 保存当前模式 `learning | job`
- 初始化并持久化模式

对应文件：

- `src/stores/careerMode.ts`

### 5.3 报告状态 `useCareerReportStore`

职责：

- 保存当前报告
- 按岗位 ID 分报告缓存
- 按岗位记录上次编辑章节
- 支持当前岗位切换与本地恢复

对应文件：

- `src/stores/modules/careerReport.ts`

### 5.4 JSON Resume 状态 `useJsonResumeStore`

职责：

- 保存简历额外资料
- 保存 JSON Resume 生成结果
- 提供从职业表单构建标准化简历的能力

对应文件：

- `src/stores/modules/jsonResume.ts`

## 6. 路由守卫与登录态

路由守卫实现于 `src/router/index.ts`。

当前行为：

- 已登录用户访问登录页或欢迎页时，自动跳转首页
- 未登录用户访问首页时，自动跳转欢迎页
- 若 store 标记已登录但缺少 `userInfo`，会主动调用接口补拉用户信息
- 支持读取 `redirect` 参数

说明：

- 当前代码中大多数业务页面没有统一声明 `meta.requiresAuth`
- 但首页与登录/欢迎页之间已有基础登录跳转逻辑

## 7. 接口分层

### 7.1 用户模块

能力：

- 注册
- 登录
- 获取用户信息
- 登出
- 忘记密码
- 更新头像

对应目录：

- `src/api/user/*`

### 7.2 职业表单模块

能力：

- 提交职业画像表单
- 表单转 DTO
- 代码能力评估
- 问卷获取与提交
- 简历上传与解析

对应目录：

- `src/api/career-form/*`

### 7.3 报告模块

能力：

- 生成职业发展报告
- 完整性检查
- 段落润色

对应目录：

- `src/api/report/index.ts`

### 7.4 积分/会员模块

能力：

- 获取积分账户
- 消费积分
- 积分充值
- 获取套餐
- 获取邀请码
- 注册邀请大使

对应目录：

- `src/api/points/*`

### 7.5 支付模块

能力：

- 创建支付订单
- 构建支付宝支付页
- 查询订单状态
- 处理本地当前订单号

特点：

- 支持 mock 模式
- 兼容后端返回 HTML 或 JSON 两种支付响应

对应目录：

- `src/api/payment/index.ts`

### 7.6 反馈模块

能力：

- 提交反馈
- 查看用户反馈历史
- 查看反馈详情
- 更新反馈
- 图片上传
- 管理员查看反馈列表

对应目录：

- `src/api/feedback/index.ts`

### 7.7 管理后台模块

能力：

- 使用记录查询

对应目录：

- `src/api/admin/usage.ts`

## 8. 请求封装与鉴权

统一请求实例位于 `src/utils/request.ts`。

主要机制：

- 基础路径为 `/api`
- 自动注入 `Authorization: Bearer <token>`
- POST/PUT/PATCH 默认 `application/json`
- 401 时自动尝试刷新 token
- 刷新失败后清空用户信息并跳转登录页

## 9. 本地缓存与前端数据流

当前前端大量使用本地持久化/缓存，保证流程连续性。

主要缓存点：

- 用户登录态：Pinia persist
- 职业模式：localStorage
- 报告按岗位缓存：Pinia persist
- JSON Resume 附加资料：Pinia persist
- 职业表单临时数据：`career-runtime`
- 岗位匹配结果：localStorage `jobMatchResult`
- AI 对话 conversationId：localStorage
- AI 助手窗口布局：localStorage
- 当前支付订单号：localStorage

这意味着：

- 页面刷新后，用户大多数中间状态可恢复
- 岗位匹配和报告存在较强的“前端本地工作台”特征

## 10. 当前页面级数据来源说明

### 10.1 主要依赖真实接口的模块

- 登录/注册/忘记密码/用户信息
- 职业表单提交
- 问卷接口
- 代码能力评估
- 职业报告生成、检查、润色
- 反馈
- 积分/会员/支付
- AI 助手

### 10.2 主要依赖本地 mock 或本地缓存的模块

- 首页雷达图与快捷入口配置
- 面试管理
- 部分知识图谱内容
- 岗位匹配页默认从本地缓存结果读取
- 简历模板页的模板预览图

## 11. 关键组件模块

### 布局类

- `Layout.vue`：登录后主框架
- `Sidebar.vue`：左侧导航
- `CHeader.vue`：顶部栏
- `MobileTabBar.vue`：移动端辅助导航

### 职业表单类

- `CareerForm_Upload.vue`：简历上传
- `ResumeMissingFieldsChat.vue`：补录聊天
- `CareerForm_Radar.vue`：能力雷达
- `Quenation.vue`：问卷组件

### 首页模式类

- `LearningModePanel.vue`
- `JobModePanel.vue`
- `LearningRecommendPanel.vue`
- `ModeSwitchCard.vue`

### 报告/图谱类

- `CReportEditor.vue`
- `CareerGraphCanvas.vue`
- `CareerGraphPanel.vue`
- `CareerGraphDetail.vue`

### 个人中心类

- `ProfileDashboard.vue`
- `ProfileInfoPanel.vue`
- `MemberPlanPanel.vue`
- `InviteFriendsPanel.vue`
- `FeedbackPanel.vue`
- `MoreSettingsPanel.vue`

## 12. 已知实现特点与维护建议

### 12.1 特点

- 业务页面较重，尤其是 `CareerForm.vue`、`CReport.vue`、`ChatBot.vue`
- 交互链路完整，但部分页面仍保留 mock 或展示占位内容
- 页面视觉较丰富，已明显偏“产品化页面”而非纯后台
- 文档、业务状态和本地缓存关系较强，适合继续完善流程闭环

### 12.2 当前值得关注的点

- 路由 `meta.requiresAuth` 使用不统一，认证策略更多依赖首页和用户状态判断
- 岗位匹配页强依赖本地 `jobMatchResult`，如果直接访问且无缓存会显示空态
- 知识图谱页部分路线只有列表卡片，详情树内容尚未补齐
- 面试管理页目前仍是 mock 数据驱动
- 文本中存在少量历史编码痕迹，但不影响主逻辑识别

## 13. 建议的测试重点

建议后续联调或回归时重点覆盖以下流程：

1. 注册 -> 登录 -> 首页 -> 职业表单 -> 岗位匹配 -> 报告生成完整链路
2. token 过期后的自动刷新与登出跳转
3. 简历上传解析、缺失字段补录、JSON Resume 导出
4. 岗位切换时报告缓存是否正确按岗位隔离
5. 支付成功后积分/会员状态刷新
6. AI 助手的文件上传、流式中断、重试、布局持久化
7. 移动端下个人中心、AI 助手、报告页、图谱页的布局稳定性

## 14. 文档对应代码范围

本文件基于当前仓库的以下范围整理：

- `src/views`
- `src/components`
- `src/stores`
- `src/api`
- `src/utils/request.ts`
- `src/router/index.ts`

更新时间：2026-04-16
