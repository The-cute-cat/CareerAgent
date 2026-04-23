/**
 * 知识库岗位影响与知识精讲模拟数据
 */

export interface KnowledgeMockData {
  analyze: string
  explain: string
}

export type JobKnowledgeMockMap = Record<string, KnowledgeMockData>

// Java 研发工程师学习路径
const javaLearningPathData: JobKnowledgeMockMap = {
  'java-learning-path_java-core-domain': {
    analyze: `## Java 核心知识领域对岗位的影响

### 岗位匹配度：核心必备（95%）

作为 Java 研发工程师，核心知识领域是立足之本：

**1. 面试通过率**
- 大厂 Java 岗面试中，基础语法、集合、并发占比 40%+
- Spring 体系考察频率达 90% 以上

**2. 日常开发效率**
- 扎实的基础能减少 30% 的 Bug 产生
- 熟悉集合与并发，能写出高性能代码

**3. 职业发展**
- 基础薄弱者通常停留在 CRUD 工程师层面
- 核心基础扎实才能进阶架构师

### 学习建议
建议投入 3-4 周系统学习，完成至少 2 个实战项目。`,

    explain: `## Java 核心知识领域精讲

### 一、Java 语言基础

**1. 面向对象编程（OOP）**
四大特性：封装、继承、多态、抽象

**2. 集合框架**
- List: ArrayList（查询快）、LinkedList（增删快）
- Set: HashSet（去重）、TreeSet（排序）
- Map: HashMap（O1查询）、ConcurrentHashMap（线程安全）

**3. 并发编程**
- 线程池：核心线程数、最大线程数、队列策略
- 锁机制：synchronized、ReentrantLock
- 原子类：AtomicInteger、AtomicReference

### 二、Spring 体系

**1. Spring Core**
- IoC 容器：控制反转、依赖注入
- Bean 生命周期：实例化→属性填充→初始化→销毁
- 作用域：singleton、prototype、request、session

**2. Spring Boot**
- 自动配置原理：@Conditional 条件注解
- Starter 机制：开箱即用
- 配置文件：application.yml/properties

**3. 事务管理**
- 传播行为：REQUIRED、REQUIRES_NEW、NESTED
- 隔离级别：读未提交、读已提交、可重复读、串行化
- 失效场景：非public、同类调用、异常被吞`,
  },

  'java-learning-path_java-language': {
    analyze: `## Java 语言基础对岗位的影响

### 岗位匹配度：核心必备（100%）

**面试必考：**
- 集合源码（HashMap、ConcurrentHashMap）出镜率 95%
- 并发编程（线程池、锁机制）必问
- JVM 内存模型高级岗位必考

**实际工作：**
- 集合选择不当会导致性能问题
- 并发处理不当会引发线程安全问题
- 基础薄弱排查 Bug 效率低下

### 薪资影响
| 掌握程度 | 面试表现 | 薪资定位 |
|---------|---------|---------|
| 扎实（源码+实践） | 优秀 | 25-40w |
| 会用（API 层面） | 良好 | 15-25w |
| 薄弱（只能 CURD） | 一般 | 10-18w |`,

    explain: `## Java 语言基础精讲

### HashMap 源码深度解析

**核心数据结构：**
- table: 桶数组（Node数组）
- size: 元素个数
- threshold: 扩容阈值 = 容量 × 加载因子（默认0.75）

**put() 方法流程：**
1. 计算哈希：hash = (h = key.hashCode()) ^ (h >>> 16)
2. 定位桶位：(n - 1) & hash
3. 无冲突直接插入；冲突则链表/红黑树处理
4. 超过阈值（8）转红黑树；低于（6）退链表
5. 达到扩容阈值，触发 resize()

**线程安全问题：**
- JDK 1.7：头插法导致死循环（并发扩容）
- JDK 1.8：尾插法避免死循环，但仍会丢数据
- 解决方案：ConcurrentHashMap（分段锁/CAS）

### 线程池核心参数

| 参数 | 含义 | 建议值 |
|-----|------|-------|
| corePoolSize | 核心线程数 | CPU密集型=CPU核数+1 |
| maximumPoolSize | 最大线程数 | IO密集型=CPU核数×2 |
| keepAliveTime | 空闲存活时间 | 60秒 |
| workQueue | 任务队列 | LinkedBlockingQueue |
| handler | 拒绝策略 | CallerRunsPolicy |

**拒绝策略：**
- AbortPolicy：抛出异常（默认）
- CallerRunsPolicy：调用者执行
- DiscardPolicy：静默丢弃
- DiscardOldestPolicy：丢弃最老任务

### 锁机制对比

| 特性 | synchronized | ReentrantLock |
|-----|-------------|---------------|
| 实现 | JVM层面 | API层面（AQS） |
| 可中断 | 不支持 | 支持 |
| 超时获取 | 不支持 | 支持 |
| 公平锁 | 非公平 | 支持 |
| 条件变量 | 一个 | 多个 |`,
  },

  'java-learning-path_java-framework': {
    analyze: `## Spring 体系对岗位的影响

### 岗位匹配度：核心框架（90%）

**企业现状：**
- 95% 以上的 Java 企业使用 Spring/Spring Boot
- 不会 Spring = 找不到 Java 后端工作
- Spring 掌握深度直接决定开发效率

**面试权重：**
- Spring IoC/AOP 原理必问
- Spring Boot 自动配置机制高频考点
- 事务传播、循环依赖、Bean 生命周期是分水岭

**工作影响：**
| 能力层级 | 工作表现 | 职业定位 |
|---------|---------|---------|
| 源码级理解 | 快速定位问题、优化性能 | 高级工程师 |
| 熟练使用 | 正常完成开发任务 | 初中级工程师 |
| 仅会配置 | 遇到问题无法解决 | 初级工程师 |`,

    explain: `## Spring 体系精讲

### Spring 循环依赖解决机制

**什么是循环依赖：**
AService 依赖 BService，BService 又依赖 AService

**三级缓存解决方案：**
- 一级缓存（singletonObjects）：完整单例 Bean
- 二级缓存（earlySingletonObjects）：早期引用（未填充属性）
- 三级缓存（singletonFactories）：单例工厂（生成早期引用）

**解决流程：**
1. A 实例化后，放入三级缓存
2. A 填充属性时发现需要 B
3. B 实例化，填充属性时发现需要 A
4. 从三级缓存获取 A 的早期引用，注入 B
5. B 创建完成，注入 A
6. A 创建完成

**无法解决的情况：**
- 构造器注入循环依赖
- 原型 Bean 循环依赖

### Spring 事务机制

**@Transactional 失效场景：**
1. 非 public 方法
2. 同类内部调用（this.method() 不走代理）
3. 异常被捕获未抛出
4. 非 RuntimeException（默认只回滚 RuntimeException）
5. 异步方法（@Async 在另一个线程执行）

**事务传播行为：**
- REQUIRED（默认）：加入当前事务，无则新建
- REQUIRES_NEW：挂起当前事务，新建独立事务
- NESTED：在当前事务中创建嵌套事务

### Spring Boot 自动配置原理

**@SpringBootApplication 拆解：**
- @SpringBootConfiguration：@Configuration
- @EnableAutoConfiguration：开启自动配置
- @ComponentScan：组件扫描

**自动配置流程：**
1. 启动时扫描 META-INF/spring.factories
2. 加载所有 EnableAutoConfiguration 类
3. @Conditional 条件判断
4. 条件满足则执行配置类，注册 Bean`,
  },

  'java-learning-path_cloud-stack': {
    analyze: `## 云原生技术栈对岗位的影响

### 岗位匹配度：高级必备（75%）

**行业趋势：**
- 云原生已成为后端高级工程师标配技能
- 不掌握 Docker/K8s，难以进入一线互联网公司
- 传统运维模式正在被 DevOps/云原生取代

**岗位需求分析：**
| 公司类型 | 云原生要求 | 薪资影响 |
|---------|-----------|---------|
| 大厂（阿里/字节） | 必备，深度使用 | +30-50% |
| 中厂（B轮以上） | 熟悉，能独立部署 | +15-30% |
| 传统企业 | 加分项 | +10% |`,

    explain: `## 云原生技术栈精讲

### Docker 核心原理

**容器 vs 虚拟机：**
| 特性 | 容器 | 虚拟机 |
|-----|------|-------|
| 启动速度 | 秒级 | 分钟级 |
| 资源占用 | 共享内核，轻量 | 完整 OS，笨重 |
| 隔离级别 | 进程级 | 硬件级 |
| 镜像大小 | MB 级 | GB 级 |

**镜像分层：**
- FROM：基础层（只读）
- COPY/ADD：应用层（只读）
- RUN：构建层（只读）
- CMD/ENTRYPOINT：启动层

**容器隔离机制：**
- Namespace：进程、网络、文件系统隔离
- Cgroups：CPU、内存、IO 资源限制
- UnionFS：文件系统分层

### Kubernetes 核心资源

**Pod（最小调度单元）：**
- 包含一个或多个容器
- 共享网络命名空间
- 有独立 IP 地址

**Deployment（无状态应用）：**
- replicas：副本数
- strategy：更新策略（RollingUpdate/Recreate）
- selector：标签选择器

**Service（服务发现）：**
- ClusterIP：集群内部访问（默认）
- NodePort：节点端口暴露
- LoadBalancer：云厂商负载均衡

### CI/CD 流程设计

**GitLab CI 核心概念：**
- stages：阶段（build/test/deploy）
- jobs：任务
- runner：执行器

**部署策略：**
- 蓝绿部署：两套环境切换，零停机
- 金丝雀发布：小流量验证，渐进式发布
- 滚动部署：逐个替换，资源占用少`,
  },

  'java-learning-path_java-ai': {
    analyze: `## AI 与 Java 融合对岗位的影响

### 岗位匹配度：未来趋势（60%→90%）

**行业变革：**
- AI 正在重塑后端开发，传统 Java 工程师面临转型
- 会 AI 的 Java 工程师薪资普遍高 20-40%
- "Java + AI" 复合人才成为招聘热点

**岗位需求变化：**
| 时间节点 | 技能要求 | 市场热度 |
|---------|---------|---------|
| 2023 | AI 了解即可 | 3星 |
| 2024 | 能接入 LLM | 4星 |
| 2025+ | 能设计 AI 应用架构 | 5星 |

**学习紧迫性：**
建议所有 Java 工程师在 2024 年内掌握 LLM 接入能力。`,

    explain: `## AI 与 Java 融合精讲

### LLM 接入架构

**典型 RAG 架构：**
用户提问 → Query理解 → 向量检索 → 提示组装 → LLM生成 → 结果返回

**Java 接入方式：**
1. 直接调用 OpenAI API（WebClient/RestTemplate）
2. 使用 Spring AI 框架（推荐）
3. 接入国产大模型（文心一言、通义千问）

### Spring AI 框架

**核心功能：**
- ChatClient：对话客户端
- EmbeddingClient：向量化客户端
- VectorStore：向量存储
- PromptTemplate：提示模板

**RAG 实现步骤：**
1. 文档加载（DocumentReader）
2. 文本分块（TokenTextSplitter）
3. 向量化（EmbeddingClient）
4. 存储到向量数据库（VectorStore）
5. 检索相似文档（SimilaritySearch）
6. 组装 Prompt 调用 LLM

### 向量数据库

**常用选择：**
- Milvus：分布式向量数据库
- Pinecone：托管向量数据库
- Redis：RediSearch 模块
- PostgreSQL：pgvector 插件

**核心概念：**
- Embedding：文本向量化
- Similarity Search：相似度搜索（余弦相似度）
- Index：索引（HNSW、IVF）`,
  },
}

// 前端工程师学习路径
const frontendLearningPathData: JobKnowledgeMockMap = {
  'frontend-learning-path_frontend-core': {
    analyze: `## 前端核心知识对岗位的影响

### 岗位匹配度：核心必备（100%）

**必备技能栈：**
- HTML/CSS/JavaScript 是前端工程师的立身之本
- Vue/React/Angular 掌握程度决定就业竞争力
- 前端工程化（Webpack/Vite）是高级工程师标配

**市场需求分析：**
| 技能组合 | 岗位数量 | 薪资区间 |
|---------|---------|---------|
| Vue + 小程序 | 最多 | 15-25w |
| React + TS | 多 | 20-35w |
| 全栈（Node.js）| 较少 | 25-45w |

**面试重点：**
- JavaScript 原型链、闭包、异步（必考）
- Vue/React 原理（虚拟 DOM、Diff 算法）
- 性能优化（首屏加载、运行时性能）

### 职业分水岭
- 初级：能还原页面，懂基础框架使用
- 中级：懂原理，能优化性能，有工程化意识
- 高级：架构设计、跨端、Node 全栈`,

    explain: `## 前端核心知识精讲

### JavaScript 深入

**原型与原型链：**
- 每个对象都有 __proto__ 属性指向原型
- 原型链终点是 Object.prototype
- 用于实现继承和属性查找

**闭包及应用：**
- 定义：函数 + 函数内部可访问的外部变量
- 应用：模块化、柯里化、防抖节流
- 注意：可能导致内存泄漏

**异步编程：**
- Callback → Promise → Async/Await
- 事件循环：宏任务、微任务
- Promise 原理：状态机、then 链式调用

### Vue 3 原理

**响应式系统：**
- Vue2：Object.defineProperty（无法监听新增/删除）
- Vue3：Proxy（完美监听，性能更好）

**虚拟 DOM：**
- 用 JS 对象描述真实 DOM
- Diff 算法：同级比较，key 优化
- Patch：对比差异，最小化更新

**Composition API：**
- setup：组件入口
- ref/reactive：响应式数据
- computed/watch：计算属性和侦听器
- 生命周期钩子：onMounted、onUnmounted

### 性能优化

**首屏加载优化：**
- 路由懒加载
- 组件异步加载
- 图片懒加载/WebP
- Tree Shaking
- Gzip/Brotli 压缩
- HTTP 缓存

**运行时优化：**
- v-once：只渲染一次
- v-memo：缓存条件渲染
- 虚拟列表：长列表优化
- 防抖/节流：事件控制`,
  },
}

// 数据分析师学习路径
const dataAnalystPathData: JobKnowledgeMockMap = {
  'data-analyst-path_data-foundation': {
    analyze: `## 数据分析基础对岗位的影响

### 岗位匹配度：核心必备（100%）

**行业需求爆发：**
- 数据分析已成为企业数字化转型的核心岗位
- 互联网/金融/零售行业数据分析师需求年增 30%+
- "业务 + 数据"复合型人才最抢手

**技能与薪资关系：**
| 技能水平 | 工具掌握 | 薪资区间 |
|---------|---------|---------|
| 初级（Excel+SQL） | Excel、基础 SQL | 10-15w |
| 中级（+Python/BI） | Python、Tableau | 15-25w |
| 高级（+建模+业务） | 机器学习、业务洞察 | 25-40w |

**面试高频考点：**
- SQL 窗口函数、复杂 Join
- 统计学基础（假设检验、回归分析）
- 业务指标体系设计（AARRR、漏斗分析）

### 关键提示
数据分析不是纯技术岗，业务理解 + 数据能力才是核心竞争力。`,

    explain: `## 数据分析基础精讲

### SQL 进阶技巧

**窗口函数：**
- ROW_NUMBER()：唯一排名（1,2,3,4）
- RANK()：跳跃排名（1,2,2,4）
- LAG/LEAD()：前后行数据访问
- 应用：累计求和、分组排名、同比环比

**复杂业务查询：**
- 留存率计算（次日留存、7日留存）
- 漏斗分析（各阶段转化率）
- RFM 用户分层

### Python 数据分析

**Pandas 核心操作：**
- 数据读取：read_csv、read_sql
- 数据清洗：dropna、fillna、drop_duplicates
- 数据转换：map、apply、groupby
- 透视表：pivot_table

**可视化：**
- Matplotlib：基础图表
- Seaborn：统计图表
- Pyecharts：交互式图表

### 业务指标体系

**AARRR 模型：**
- Acquisition（获客）：新增用户、CAC
- Activation（激活）：首次使用、激活率
- Retention（留存）：次日/7日/30日留存
- Revenue（收入）：ARPU、LTV、付费率
- Referral（推荐）：NPS、分享率

**RFM 用户分层：**
- R（Recency）：最近消费时间
- F（Frequency）：消费频率
- M（Monetary）：消费金额
- 应用：精准营销、用户运营`,
  },
}

// 合并所有数据
export const jobKnowledgeMockData: JobKnowledgeMockMap = {
  ...javaLearningPathData,
  ...frontendLearningPathData,
  ...dataAnalystPathData,
}

/**
 * 获取知识点的模拟数据
 */
export function getKnowledgeMockData(
  roleId: string,
  nodeId: string
): KnowledgeMockData | null {
  const key = `${roleId}_${nodeId}`
  return jobKnowledgeMockData[key] || null
}

/**
 * 检查是否存在模拟数据
 */
export function hasKnowledgeMockData(
  roleId: string,
  nodeId: string
): boolean {
  const key = `${roleId}_${nodeId}`
  return key in jobKnowledgeMockData
}

export default jobKnowledgeMockData
