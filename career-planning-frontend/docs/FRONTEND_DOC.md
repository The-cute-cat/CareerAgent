# AI 职业规划系统 - 前端功能文档

## 📖 项目简介

AI 职业规划系统是一个基于人工智能的职业规划辅助平台,帮助用户进行职业生涯规划、能力评估、岗位匹配等。前端采用现代化的技术栈,提供友好的用户交互体验。

## 🛠️ 技术栈

### 核心框架

- **Vue 3.5.29** - 采用 Composition API 开发模式
- **TypeScript 5.9.3** - 提供类型安全保障
- **Vite 7.3.1** - 快速的前端构建工具

### UI 组件库

- **Element Plus 2.13.5** - 企业级 Vue 3 组件库
- **@element-plus/icons-vue 2.3.2** - Element Plus 图标库
- **Bootstrap 5.3.8** - 辅助样式框架

### 状态管理与路由

- **Pinia 3.0.4** - Vue 官方推荐的状态管理库
- **pinia-plugin-persistedstate 4.7.1** - Pinia 持久化插件
- **Vue Router 4.6.4** - 官方路由管理器

### 数据可视化

- **ECharts 6.0.0** - 强大的数据可视化库
- **@antv/x6 3.1.6** - 图编辑引擎,用于绘制职业发展图谱
- **@antv/x6-vue-shape 3.0.2** - X6 的 Vue 形状组件

### 工具库

- **Axios 1.13.6** - HTTP 请求库
- **html2canvas 1.4.1** - 将 DOM 转换为 Canvas
- **jspdf 4.2.0** - 生成 PDF 文件

### 开发工具

- **ESLint 10.0.2** - 代码质量检查
- **Prettier 3.8.1** - 代码格式化
- **Vitest 4.0.18** - 单元测试框架

## 📁 项目结构

```
career-planning-frontend/
├── public/                 # 静态资源目录
├── src/
│   ├── api/               # API 接口层
│   │   ├── po/           # 数据对象定义
│   │   └── user/         # 用户相关 API
│   ├── assets/           # 静态资源(图片、样式等)
│   ├── components/       # 公共组件
│   │   ├── ChatBot.vue      # AI 助手悬浮窗
│   │   ├── CHeader.vue       # 顶部导航栏
│   │   ├── Layout.vue       # 整体布局组件
│   │   └── Sidebar.vue      # 侧边导航栏
│   ├── router/           # 路由配置
│   │   └── index.ts
│   ├── stores/           # Pinia 状态管理
│   │   ├── modules/      # Store 模块
│   │   │   └── user.ts   # 用户状态管理
│   │   └── index.ts
│   ├── types/            # TypeScript 类型定义
│   ├── utils/            # 工具函数
│   ├── views/            # 页面组件
│   │   ├── 404.vue                  # 404 错误页面
│   │   ├── CUserForgetPassword.vue  # 忘记密码页面
│   │   ├── CUserLogin.vue          # 登录页面
│   │   ├── CUserRegister.vue       # 注册页面
│   │   ├── DevelopmentMap.vue      # 职业发展地图
│   │   ├── HomePage.vue            # 首页/仪表盘
│   │   ├── CProfile.vue             # 个人中心
│   │   ├── CReport.vue              # 分析报告
│   │   └── Upload.vue              # 简历上传页面
│   ├── App.vue            # 根组件
│   ├── main.ts            # 应用入口
│   └── main.js            # JS 兼容入口
├── index.html
├── package.json
├── vite.config.ts
└── tsconfig.json
```

## 🎯 核心功能模块

### 1. 用户认证模块

#### 1.1 用户登录 (`/login`)

**功能描述**: 提供用户登录功能,支持"记住我"选项

**主要特性**:

- 用户名/邮箱 + 密码登录
- "记住我"功能,选择后可保持登录状态
- 登录状态持久化存储
- 自动重定向到目标页面或首页
- 已登录用户访问登录页自动重定向

**技术实现**:

- 使用 Pinia Store (`useUserStore`) 管理用户状态
- Token 存储在 Pinia 中,通过插件自动持久化
- 路由守卫检查登录状态

**关键代码位置**:

- 页面组件: `src/views/CUserLogin.vue`
- 状态管理: `src/stores/modules/user.ts`
- 路由守卫: `src/router/index.ts` (62-94行)

#### 1.2 用户注册 (`/register`)

**功能描述**: 新用户账号注册

**主要特性**:

- 用户名、邮箱、密码、确认密码输入
- 表单验证(邮箱格式、密码强度、密码一致性)
- 注册成功后自动跳转登录页

**关键代码位置**:

- 页面组件: `src/views/CUserRegister.vue`

#### 1.3 忘记密码 (`/forgot-password`)

**功能描述**: 帮助用户找回密码

**主要特性**:

- 通过邮箱验证找回密码
- 邮箱格式验证
- 发送重置密码链接

**关键代码位置**:

- 页面组件: `src/views/CUserForgetPassword.vue`

---

### 2. 首页仪表盘 (`/`)

**功能描述**: 用户登录后的首页,展示个人能力和快捷操作入口

**主要特性**:

#### 2.1 快捷功能卡片

提供四个主要功能的快速入口:

1. **上传简历**
   - 图标: `Upload`
   - 颜色: #409eff (蓝色)
   - 路由: `/upload`
   - 描述: 点击上传简历

2. **查看匹配**
   - 图标: `DocumentChecked`
   - 颜色: #67c23a (绿色)
   - 路由: `/report`
   - 描述: 岗位匹配

3. **生成报告**
   - 图标: `DataLine`
   - 颜色: #e6a23c (橙色)
   - 路由: `/report`
   - 描述: 生成我的生涯报告

4. **职业地图**
   - 图标: `MapLocation`
   - 颜色: #f56c6c (红色)
   - 路由: `/development-map`
   - 描述: 查看岗位晋升路线

#### 2.2 能力概览雷达图

- 使用 ECharts 绘制六维能力雷达图
- 能力维度: 沟通能力、专业技能、团队协作、学习能力、领导力、创新思维
- 基于简历分析生成的能力评估数据
- 响应式设计,自动适配屏幕大小

**技术实现**:

- ECharts 初始化在 `onMounted` 钩子中
- 数据动态渲染,可接入后端 API
- 窗口 resize 时自动调整图表尺寸

#### 2.3 系统公告

- 显示系统使用指南
- 引导用户完成主要功能流程:
  1. 上传简历
  2. 系统分析能力特点
  3. 查看匹配岗位和生涯报告
  4. 探索职业地图

**关键代码位置**:

- 页面组件: `src/views/HomePage.vue`

---

### 3. 简历上传模块 (`/upload`)

**功能描述**: 上传个人简历,系统将进行 AI 分析

**主要特性**:

- 支持 PDF、Word 等常见简历格式
- 拖拽上传功能
- 文件大小限制
- 上传进度显示
- 上传成功后自动分析简历内容

**技术实现**:

- 使用 Element Plus 的 `el-upload` 组件
- 通过 Axios 发送文件到后端 API
- 支持文件类型和大小验证

**关键代码位置**:

- 页面组件: `src/views/Upload.vue`

---

### 4. 分析报告模块 (`/report`)

**功能描述**: 展示基于简历分析生成的职业生涯报告

**主要特性**:

- 用户画像分析
- 能力评估详情
- 岗位匹配推荐
- 职业发展建议
- 报告导出功能(PDF 格式)

**技术实现**:

- 使用 ECharts 展示多维数据
- `html2canvas` + `jspdf` 生成 PDF
- Markdown 渲染展示文本内容

**关键代码位置**:

- 页面组件: `src/views/CReport.vue`

---

### 5. 职业发展地图 (`/development-map`)

**功能描述**: 可视化展示职业发展路径和晋升路线

**主要特性**:

- 使用 @antv/x6 绘制职业图谱
- 交互式节点和连线
- 支持节点拖拽
- 展示岗位层级关系
- 高亮当前所在岗位
- 显示能力要求和晋升条件

**技术实现**:

- X6 图编辑引擎
- Vue 自定义节点组件 (`@antv/x6-vue-shape`)
- 图谱数据动态渲染

**关键代码位置**:

- 页面组件: `src/views/DevelopmentMap.vue`

---

### 6. 个人中心 (`/profile`)

**功能描述**: 用户个人信息管理

**主要特性**:

- 个人资料编辑
- 头像上传
- 密码修改
- 账号设置
- 登录历史查看

**关键代码位置**:

- 页面组件: `src/views/CProfile.vue`

---

### 7. 公共组件

#### 7.1 布局组件 (`Layout.vue`)

**功能描述**: 整体页面布局框架

**主要特性**:

- 左侧固定宽度侧边栏 (220px)
- 顶部导航栏
- 中间主内容区
- 响应式设计
- 页面切换过渡动画
- 滚动条自定义样式

**布局结构**:

```vue
<el-container class="layout-container">
  <el-aside class="sidebar-wrapper">    <!-- 左侧侧边栏 -->
    <Sidebar />
  </el-aside>

  <el-container class="main-wrapper">   <!-- 右侧主内容区 -->
    <CHeader />                           <!-- 顶部 CHeader -->
    <el-main class="main-content">      <!-- 页面内容 -->
      <router-view />
    </el-main>
  </el-container>

  <ChatBot />                            <!-- AI 助手悬浮窗 -->
</el-container>
```

#### 7.2 侧边栏 (`Sidebar.vue`)

**功能描述**: 导航菜单,提供各功能模块的快速访问

**主要特性**:

- 深色渐变背景 (`#1a1f36` → `#243042`)
- 导航菜单:
  - 首页
  - 上传简历
  - 分析报告
  - 职业地图
  - 个人中心
- 当前路由高亮显示
- 图标 + 文字展示

#### 7.3 顶部导航栏 (`CHeader.vue`)

**功能描述**: 顶部工具栏,显示用户信息和操作入口

**主要特性**:

- 用户头像和昵称显示
- 消息通知
- 退出登录
- 响应式设计

#### 7.4 AI 助手 (`ChatBot.vue`)

**功能描述**: 悬浮窗形式的 AI 对话助手

**主要特性**:

- 固定在页面右下角
- 可展开/收起
- 实时对话功能
- 职业规划咨询
- 智能问答

---

### 8. 路由与状态管理

#### 8.1 路由配置

**路由结构**:

```
/login              - 登录页
/register           - 注册页
/forgot-password    - 忘记密码
/                   - 首页(需登录)
/upload             - 上传简历(需登录)
/report             - 分析报告(需登录)
/development-map    - 职业地图(需登录)
/profile            - 个人中心(需登录)
/:pathMatch(.*)*    - 404 页面
```

**路由守卫**:

- 自动检查用户登录状态
- 未登录访问需认证页面自动跳转登录页
- 已登录访问登录页自动跳转首页
- 支持重定向参数

**关键代码**: `src/router/index.ts`

#### 8.2 用户状态管理 (Pinia)

**Store 模块**: `useUserStore`

**State**:

- `accessToken`: 访问令牌
- `refreshToken`: 刷新令牌
- `userInfo`: 用户信息对象
- `isLoggedIn`: 是否已登录 (computed)

**Actions**:

- `setTokens(access, refresh)`: 设置 Token
- `clearTokens()`: 清除 Token
- `setUserALLInfo(access, refresh, user)`: 设置所有用户信息
- `clearUserALLInfo()`: 清除所有用户信息
- `clearUserInfo()`: 清除用户信息

**持久化配置**:

- 使用 `pinia-plugin-persistedstate` 插件
- 整个 store 自动持久化到 localStorage
- 刷新页面不丢失登录状态

**关键代码**: `src/stores/modules/user.ts`

---

## 🎨 UI/UX 特性

### 设计风格

- **主色调**: 蓝色系 (#409eff) - 体现专业、科技感
- **侧边栏**: 深色渐变背景,突出内容区
- **卡片式设计**: 内容模块化,层次分明
- **圆角设计**: 12px 统一圆角,现代感强
- **阴影效果**: hover 时提供视觉反馈

### 交互特性

- **过渡动画**: 页面切换淡入淡出效果
- **Hover 效果**: 卡片悬停上浮 + 阴影增强
- **响应式布局**: 支持桌面端、平板、手机
- **加载状态**: 操作时显示加载提示
- **消息提示**: Element Plus `el-message` 全局提示

### 响应式断点

- **桌面端**: > 1200px (快捷功能 4 列)
- **平板端**: 768px - 1200px (快捷功能 2 列)
- **移动端**: < 768px (快捷功能 1 列,侧边栏可能折叠)

---

## 🔐 安全特性

1. **Token 管理**
   - Access Token 和 Refresh Token 双 Token 机制
   - Token 存储在 Pinia 中,自动持久化
   - 支持自动刷新 Token

2. **路由守卫**
   - 所有需认证页面自动检查登录状态
   - 未登录用户自动跳转登录页
   - 防止越权访问

3. **数据验证**
   - 前端表单验证
   - 文件上传类型和大小限制
   - API 请求参数验证

---

## 📦 构建与部署

### 开发环境

```bash
# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 生产构建

```bash
# 类型检查
npm run type-check

# 构建生产版本
npm run build

# 预览生产构建
npm run preview
```

### 代码规范

```bash
# 运行 ESLint
npm run lint

# 代码格式化
npm run format
```

### 测试

```bash
# 运行单元测试
npm run test

# 测试 UI 界面
npm run test:ui

# 生成测试覆盖率报告
npm run test:coverage
```

---

## 🔧 配置文件说明

### vite.config.ts

- Vite 构建配置
- 路径别名配置 (@ 指向 src)
- 插件配置 (Vue、TypeScript、自动导入等)
- 开发服务器配置 (端口、代理等)

### tsconfig.json

- TypeScript 编译配置
- 模块解析策略
- 类型检查严格模式

### eslint.config.ts

- ESLint 规则配置
- Vue 3 最佳实践
- TypeScript 类型检查集成

---

## 📝 开发注意事项

### 1. 组件开发规范

- 使用 `<script setup>` 语法糖
- 使用 TypeScript 定义类型
- Props 必须定义类型
- 事件命名使用 kebab-case

### 2. 状态管理规范

- 使用 Pinia 进行状态管理
- 复杂逻辑拆分为多个 Store 模块
- 使用 computed 定义派生状态
- 使用 actions 处理异步操作

### 3. 路由规范

- 使用路由懒加载提升性能
- 路由命名使用 kebab-case
- 需认证的路由添加 `meta.requiresAuth`
- 合理使用路由守卫

### 4. API 调用规范

- API 统一放在 `src/api` 目录
- 使用 TypeScript 接口定义返回数据类型
- 统一错误处理
- 请求和响应拦截器配置

### 5. 样式规范

- 使用 scoped 样式避免污染
- 优先使用 Element Plus 组件样式
- 自定义样式使用语义化类名
- 响应式使用媒体查询

---

## 🚀 未来优化方向

1. **性能优化**
   - 路由懒加载全部实施
   - 组件按需引入
   - 图片懒加载和压缩
   - 代码分割优化

2. **用户体验**
   - PWA 支持,可离线访问
   - 骨架屏加载优化
   - 更多动画过渡效果
   - 暗色模式支持

3. **功能扩展**
   - 国际化 (i18n) 支持
   - 多语言切换
   - 数据可视化更多图表类型
   - 职业地图更丰富的交互

4. **测试覆盖**
   - 增加单元测试覆盖率
   - E2E 端到端测试
   - 性能测试

5. **监控与分析**
   - 埋点统计
   - 错误监控 (Sentry)
   - 性能分析

---

## 📞 联系与支持

如有问题或建议,请联系开发团队。

---

**文档版本**: v1.0  
**最后更新**: 2026-03-15  
**维护者**: CareerAgent 开发团队
