# Copilot 使用说明（面向 AI 编码代理）

目的：让 AI 代理快速上手并在此 repo 中安全、可预测地修改代码。

- **快速命令**: `npm install`, `npm run dev`, `npm run build`, `npm run type-check`, `npm run lint`, `npm run format`

- **大局架构**: 基于 Vite + Vue 3 + TypeScript。程序入口是 `src/main.ts`，顶层组件 `src/App.vue`。路由在 `src/router/index.ts` 管理，页面在 `src/views`，通用组件在 `src/components`，状态保存在 `src/stores`（Pinia）。

- **为什么这样组织**: 典型的 Vue SPA 布局，分离路由/视图/组件与 store 便于迭代和热重载（`vite` 支持）。类型检查通过 `vue-tsc --build` 运行（参见 `package.json` 的 `type-check` 脚本）。

- **关键文件/目录（编辑优先级）**
  - `src/main.ts`：插件、全局注册点。
  - `src/App.vue`：根 layout（包含 `<router-view/>`）。
  - `src/router/index.ts`：路由表（新增页面请在此注册）。
  - `src/stores/`：Pinia store，例如 `src/stores/counter.ts`。
  - `src/components/TheWelcome.vue`：包含一个开发时 helper：`fetch('/__open-in-editor?file=README.md')`，可触发在 dev 环境打开 README。
  - `src/assets/`：全局 CSS（`main.css`, `base.css`）。

- **项目约定 & 模式（实证）**
  - 所有全局状态使用 Pinia，放 `src/stores`，每个文件导出一个 store 函数。
  - 路由对象按页面拆分到 `src/views`，新增页面后在 `src/router/index.ts` 添加对应路由。示例：创建 `src/views/FooView.vue` 后在路由里 `import FooView from '@/views/FooView.vue'` 并添加路由项。
  - 使用 `vue-tsc --build` 做完整类型检查；CI/本地在发布前会运行此检查（见 `package.json`）。
  - Lint/format: 使用 `eslint` + `oxlint` + `prettier`。运行 `npm run lint` 和 `npm run format`。

- **集成点与外部依赖**
  - 依赖：`vue`, `pinia`, `vue-router`（参见 `package.json`）。
  - Vite dev server 提供 `/__open-in-editor` 风格的开发辅助端点（在 `TheWelcome.vue` 有示例使用）。
  - Node 版本要求参考 `package.json.engines`（Node 20/22+）。

- **修改示例（极简）**
  - 添加页面：创建 `src/views/NewView.vue` → 在 `src/router/index.ts` 添加路由 → 在导航或组件中引用。
  - 新 store：在 `src/stores/newStore.ts` 导出 `useNewStore` Pinia 函数并在组件内 `const store = useNewStore()` 使用。

- **安全修改与常见检查清单**
  - 先在本地运行 `npm run dev` 确认热更新无错误。
  - 运行 `npm run type-check` 确保无类型错误。
  - 运行 `npm run lint` 并修复自动修复建议。

- **如果不确定**: 指出要修改的具体文件（路径）、预期行为（render/route/store）与回归风险。优先请求澄清，而非猜测大型架构改动。

请审阅此草案并指出哪些部分需要补充或更精确的代码示例，我会根据反馈进行迭代。
