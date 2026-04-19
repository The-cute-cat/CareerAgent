# CareerAgent - AI 职业规划系统前端

基于 Vue 3 + TypeScript + Vite 构建的 AI 驱动职业规划平台前端应用，提供智能简历分析、职业报告生成、岗位匹配、职业发展地图等核心功能。

## 项目预览

> 截图待补充

## 技术栈

| 类别 | 技术 | 版本 |
|------|------|------|
| 框架 | Vue 3 (Composition API) | 3.5.29 |
| 语言 | TypeScript | 5.9.3 |
| 构建工具 | Vite | 7.3.1 |
| UI 库 | Element Plus + Bootstrap 5 | - |
| 状态管理 | Pinia + 持久化插件 | 3.0.4 |
| 路由 | Vue Router | 4.6.4 |
| 可视化 | ECharts 6 + @antv/x6 3 | - |
| HTTP 客户端 | Axios | 1.13.6 |
| 测试 | Vitest | 4.0.18 |
| 代码规范 | ESLint + OxLint + Prettier | - |

## 核心功能

| # | 功能 | 说明 |
|---|------|------|
| 1 | **用户认证** | 登录/注册/忘记密码，双 Token（Access + Refresh）机制 |
| 2 | **职业表单** | 三种填写方式（上传简历 / 模板填写 / 语音输入），问卷式信息采集，雷达图能力评估 |
| 3 | **简历编辑与导出** | 富文本编辑器，JSON Resume 标准格式，PDF 导出 |
| 4 | **职业分析报告** | AI 生成职业生涯报告，支持查看与编辑，含用户画像/能力评估/岗位推荐/发展建议 |
| 5 | **职业发展地图** | 基于 @antv/x6 的交互式图谱，展示岗位层级关系、晋升路径、能力要求 |
| 6 | **岗位匹配** | 基于简历分析结果的智能岗位推荐 |
| 7 | **职位知识库** | 树形结构展示职位相关知识 |
| 8 | **面试管理** | 日历/列表/总览/回顾多种视图 |
| 9 | **AI 助手** | 悬浮窗式对话机器人，职业规划咨询与智能问答 |
| 10 | **积分与会员系统** | 积分管理、邀请好友、会员套餐 |
| 11 | **管理后台** | 使用记录查看、用户反馈管理 |

## 项目结构

```
src/
├── api/                         # API 接口层
│   ├── admin/                   # 管理后台 API
│   ├── career-form/             # 职业表单 API
│   ├── chatbot/                 # AI 聊天机器人 API
│   ├── feedback/                 # 用户反馈 API
│   ├── payment/                 # 支付 API
│   ├── points/                   # 积分系统 API
│   ├── report/                   # 报告 API
│   └── user/                     # 用户认证 API
├── assets/                      # 静态资源
├── components/                  # 组件
│   ├── AdminManager/            # 管理后台组件
│   ├── career-graph/            # 职业图谱组件
│   ├── CInterviews_Component/   # 面试组件
│   ├── CProfile_Component/       # 个人中心子面板
│   ├── CReport_Component/        # 报告编辑器组件
│   ├── JobKnowledge/            # 职位知识树组件
│   └── Person_Report/           # 富文本编辑器组件
├── mock/                        # Mock 数据
├── router/                      # 路由配置
├── stores/                      # Pinia 状态管理
│   └── modules/                 # app / careerReport / jsonResume / user
├── types/                       # TypeScript 类型定义
├── utils/                       # 工具函数
└── views/                       # 页面组件
```

## 页面路由

| 路由 | 页面 | 说明 |
|------|------|------|
| `/welcome` | LandingPage | 未登录欢迎页 |
| `/login` | CUserLogin | 用户登录 |
| `/register` | CUserRegister | 用户注册 |
| `/forgot-password` | CUserForgetPassword | 忘记密码 |
| `/` | CHomePage | 首页仪表盘 |
| `/career-form/resume` | CareerForm | 简历上传填写 |
| `/career-form/template` | CareerForm | 模板式简历填写 |
| `/career-form/voice` | CareerFormVoice | 语音输入式简历填写 |
| `/resume-editor` | ResumeEditor | 简历编辑器 |
| `/resume-template` | ResumeTemplate | 简历模板生成 |
| `/report` | CReport | 职业分析报告 |
| `/report/edit` | CReportEditor | 报告编辑器 |
| `/development-map` | DevelopmentMap | 职业发展地图 |
| `/job-matching` | JobMatching | 岗位匹配 |
| `/job-position` | JobMatching_Position | 岗位详情 |
| `/knowledge-base` | JobKnowledge | 职位知识库 |
| `/interviews/:type?` | CInterviews | 我的面试 |
| `/profile` | CProfile | 个人中心 |
| `/admin` | AdminPanel | 管理后台 |

## 快速开始

### 环境要求

- Node.js ^20.19.0 || >=22.12.0

### 安装依赖

```sh
npm install
```

### 开发模式运行

```sh
npm run dev
```

开发服务器启动在 `http://localhost:8081`，API 请求代理到 `http://127.0.0.1:8080`。

### 构建生产版本

```sh
npm run build
```

### 其他命令

```sh
npm run preview          # 预览生产构建
npm run type-check       # TypeScript 类型检查
npm run lint             # 代码检查（ESLint + OxLint）
npm run lint:fix         # 自动修复代码问题
npm run format           # 代码格式化（Prettier）
npm run test             # 运行测试
npm run test:coverage    # 测试覆盖率
```

## 开发配置

### 环境变量

创建 `.env` 或 `.env.local` 文件：

```env
VITE_API_BASE_URL=/api
VITE_APP_TITLE=CareerAgent
```

### API 请求代理

Vite 配置将 `/api/*` 请求代理到后端：

```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8080',
      changeOrigin: true
    }
  }
}
```

### IDE 推荐

[VS Code](https://code.visualstudio.com/) + [Vue - Official](https://marketplace.visualstudio.com/items?itemName=Vue.volar)

### 浏览器插件

- [Vue.js DevTools](https://chromewebstore.google.com/detail/vuejs-devtools/nhdogjmejiglipccpnnnanhbledajbpd)（Chrome/Edge）
- [Vue.js DevTools](https://addons.mozilla.org/en-US/firefox/addon/vue-js-devtools/)（Firefox）

### HTTPS 开发证书

项目使用 `vite-plugin-mkcert` 插件自动生成本地 SSL 证书。

## 代码规范

### ESLint 规则

- Vue 3 Composition API 风格
- TypeScript 严格模式
- Prettier 统一代码风格

### 提交规范

使用 commitlint 规范提交信息：

```
feat: 新功能
fix: 修复 bug
docs: 文档更新
style: 代码格式
refactor: 重构
test: 测试
chore: 构建/工具
```

## 相关文档

- [前端功能文档](docs/FRONTEND_DOC.md)
- [简历上传 API 文档](docs/RESUME_UPLOAD_API.md)
- [测试配置文档](docs/TEST_SETUP.md)
- [Vite 配置参考](https://vite.dev/config/)

## License

Private - All Rights Reserved
