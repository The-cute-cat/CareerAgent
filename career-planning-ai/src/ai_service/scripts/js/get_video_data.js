// @ts-check
// noinspection SpellCheckingInspection

/**
 * B站视频课程爬取脚本
 * 从B站搜索结果获取视频课程数据，用于推荐系统
 */

import * as fs from 'fs';
import * as path from 'path';
import {fileURLToPath} from 'url';

/** @typedef {import('cheerio').CheerioAPI} CheerioAPI */

// 获取当前脚本目录
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 文件路径配置
const RESULT_DIR = path.join(__dirname, 'video_data');
const RESULT_FILE = path.join(RESULT_DIR, 'bilibili_courses.json');
const PROGRESS_FILE = path.join(__dirname, '.video_crawl_progress.json');

// 爬取配置
const CONFIG = {
    requestDelay: [3000, 6000],      // 每次请求延迟 3-6 秒
    batchSize: 10,                     // 每批请求数量
    batchPause: 30000,                // 每批后暂停 30 秒
    retryDelay: 10000,                // 错误重试等待 10 秒
    maxRetries: 3,                    // 最大重试次数
    maxPagesPerKeyword: 20,           // 每个关键词最多爬取页数
    orderType: 'click',               // 排序方式: click(播放量), pubdate(发布日期), dm(弹幕数), stow(收藏数)
};

// IT技术搜索关键词配置
const itSearchKeywords = [
    {
        category: "前端开发",
        tags: ["前端", "Web"],
        keywords: [
            "HTML5 CSS3 零基础入门全套教程",
            "JavaScript ES6 核心语法与进阶",
            "TypeScript 从入门到实战教程",
            "Vue3 组合式API 企业级项目实战",
            "React18 最新Hooks原理与实战",
            "Next.js 服务端渲染SSR全栈开发",
            "Node.js Koa/Express 后端接口开发",
            "前端Webpack5 Vite 工程化配置",
            "前端性能优化与首屏加载提速"
        ]
    },
    {
        category: "后端开发",
        tags: ["后端", "服务端"],
        keywords: [
            "Java 零基础入门到精通 尚硅谷",
            "Java并发编程 JUC底层原理",
            "Spring Boot3 微服务架构实战",
            "Spring Cloud Alibaba 组件源码解析",
            "MyBatis Plus 高级查询与插件",
            "Go语言 Gin框架 微服务实战",
            "Go语言 并发编程 goroutine通道",
            "Python Django/Flask Web全栈开发",
            "Python FastAPI 高性能接口开发",
            "Rust 语言从入门到实战教程",
            "C++ 内存管理与现代特性"
        ]
    },
    {
        category: "AI与数据科学",
        tags: ["AI", "大模型", "算法"],
        keywords: [
            "机器学习 吴恩达 算法详解",
            "PyTorch 深度学习框架实战",
            "TensorFlow2 入门到项目实战",
            "大模型 LLM 微调部署实战",
            "LangChain 应用开发全套教程",
            "RAG 检索增强生成 从原理到实战",
            "Transformer 架构 源码逐行解析",
            "YOLOv8 目标检测 训练与部署",
            "OpenCV 计算机视觉图像处理"
        ]
    },
    {
        category: "数据库与中间件",
        tags: ["数据库", "中间件", "架构"],
        keywords: [
            "MySQL 高级性能调优与慢查询分析",
            "PostgreSQL 从入门到高可用架构",
            "Redis 底层数据结构与缓存穿透击穿",
            "MongoDB 文档数据库企业级实战",
            "ElasticSearch 全文检索与日志分析",
            "RocketMQ 底层原理与分布式事务",
            "Kafka 高吞吐量消息队列实战",
            "RabbitMQ 消息可靠性投递机制"
        ]
    },
    {
        category: "云原生与DevOps",
        tags: ["运维", "云原生", "Linux"],
        keywords: [
            "Linux 鸟哥私房菜 零基础",
            "Linux Shell脚本编程自动化运维",
            "Docker 容器化部署从入门到实践",
            "Kubernetes K8s 集群搭建与排错",
            "Prometheus Grafana 监控告警体系",
            "Jenkins GitLab CI/CD 自动化流水线",
            "Istio 服务网格微服务治理"
        ]
    },
    {
        category: "移动端开发",
        tags: ["移动端", "App", "跨平台"],
        keywords: [
            "Android Jetpack Compose 现代UI开发",
            "Android 高级性能优化与内存泄漏",
            "iOS Swift UI 底层原理与实战",
            "Flutter 3.0 跨平台应用开发实战",
            "鸿蒙HarmonyOS ArkTS 原生应用开发",
            "React Native 跨平台从原理到实战"
        ]
    },
    {
        category: "底层基础与面试",
        tags: ["基础", "面试", "八股文"],
        keywords: [
            "数据结构与算法 LeetCode 刷题指南",
            "计算机网络 TCP/IP 协议栈详解",
            "操作系统 进程线程 内存管理",
            "Java 面试八股文 深度剖析",
            "程序员简历指导与大厂面试技巧"
        ]
    }
];

// User-Agent 列表
const USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
];

/**
 * 获取随机 User-Agent
 */
function getRandomUserAgent() {
    return USER_AGENTS[Math.floor(Math.random() * USER_AGENTS.length)];
}

/**
 * 延迟函数
 * @param {number} minMs
 * @param {number} [maxMs]
 */
function delay(minMs, maxMs = null) {
    const ms = maxMs ? Math.floor(Math.random() * (maxMs - minMs + 1)) + minMs : minMs;
    console.log(`[Delay] Waiting ${Math.floor(ms / 1000)}s...`);
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * 构建B站搜索URL
 * @param {string} keyword - 搜索关键词
 * @param {number} page - 页码
 * @param {string} order - 排序方式
 */
function buildSearchUrl(keyword, page = 1, order = 'click') {
    const baseUrl = 'https://search.bilibili.com/all';
    const params = new URLSearchParams({
        keyword: keyword,
        from_source: 'webtop_search',
        spm_id_from: '333.1007',
        search_source: '5',
        page: page.toString(),
        order: order
    });
    return `${baseUrl}?${params.toString()}`;
}

/**
 * 从HTML内容中提取 window.__pinia 数据
 * @param {string} htmlContent - HTML文件内容
 * @returns {object|null} - 解析出的数据对象
 */
function extractPiniaData(htmlContent) {
    try {
        // 查找 window.__pinia 开始的位置（支持有无空格两种格式）
        let piniaStart = htmlContent.indexOf('window.__pinia=');
        if (piniaStart === -1) {
            piniaStart = htmlContent.indexOf('window.__pinia = ');
        }
        if (piniaStart === -1) {
            console.error('未找到 window.__pinia 数据');
            return null;
        }

        // 提取脚本标签内容
        const startTag = '<script type="text/javascript">';
        const scriptStart = htmlContent.lastIndexOf(startTag, piniaStart);
        const scriptEnd = htmlContent.indexOf('</script>', piniaStart);
        
        if (scriptStart === -1 || scriptEnd === -1) {
            console.error('无法定位脚本标签');
            return null;
        }

        // 提取完整的脚本内容（不包含script标签）
        const scriptContent = htmlContent.substring(scriptStart + startTag.length, scriptEnd);
        
        // 使用正则提取 IIFE，支持有无空格
        const piniaAssignMatch = scriptContent.match(/window\.__pinia\s*=\s*(\([\s\S]+)$/);
        if (!piniaAssignMatch) {
            console.error('无法提取 pinia IIFE');
            return null;
        }

        const iifeCode = piniaAssignMatch[1].trim();
        
        // 直接执行 IIFE 获取返回值
        try {
            // eslint-disable-next-line no-eval
            return eval(iifeCode);
        } catch (evalError) {
            // 如果直接 eval 失败，尝试用 Function 构造器
            try {
                const getPinia = new Function('return ' + iifeCode);
                return getPinia();
            } catch (funcError) {
                console.error('执行 pinia 代码失败:', funcError.message);
                return null;
            }
        }
    } catch (error) {
        console.error('解析 pinia 数据失败:', error.message);
        return null;
    }
}

/**
 * 从 pinia 数据中提取视频课程列表
 * @param {object} piniaData - pinia 数据对象
 * @param {string} keyword - 搜索关键词
 * @param {string} category - 分类
 * @param {string[]} tags - 标签
 * @returns {array} - 课程列表
 */
function extractVideoCourses(piniaData, keyword, category, tags) {
    const courses = [];
    
    try {
        const searchResponse = piniaData?.searchResponse?.searchAllResponse;
        if (!searchResponse || !searchResponse.result) {
            console.error('无法找到搜索结果数据');
            return courses;
        }

        // 遍历 result 数组，找到视频类型的数据
        for (const resultItem of searchResponse.result) {
            if (resultItem.data && Array.isArray(resultItem.data) && resultItem.data.length > 0) {
                // 检查是否有视频数据（通过检查第一个元素是否有 bvid）
                if (resultItem.data[0].bvid) {
                    for (const video of resultItem.data) {
                        const course = extractCourseInfo(video, keyword, category, tags);
                        if (course) {
                            courses.push(course);
                        }
                    }
                }
            }
        }
    } catch (error) {
        console.error('提取视频课程失败:', error.message);
    }
    
    return courses;
}

/**
 * 提取单个课程信息
 * @param {object} video - 原始视频数据
 * @param {string} keyword - 搜索关键词
 * @param {string} category - 分类
 * @param {string[]} tags - 标签
 * @returns {object|null} - 处理后的课程信息
 */
function extractCourseInfo(video, keyword, category, tags) {
    if (!video || !video.bvid) {
        return null;
    }

    // 清理标题中的 HTML 标签
    const cleanTitle = video.title
        ? video.title.replace(/<em class="keyword">/g, '').replace(/<\/em>/g, '')
        : '';

    // 构建完整的图片URL
    const picUrl = video.pic
        ? (video.pic.startsWith('//') ? `https:${video.pic}` : video.pic)
        : '';

    // 构建完整的UP主头像URL
    const authorAvatar = video.upic
        ? (video.upic.startsWith('//') ? video.upic : `https:${video.upic}`)
        : '';

    // 格式化发布日期
    const pubDate = video.pubdate
        ? new Date(video.pubdate * 1000).toISOString().split('T')[0]
        : (video.pubstr || '');

    return {
        // 基础信息
        id: video.bvid,
        bvid: video.bvid,
        aid: video.aid,
        title: cleanTitle,
        description: video.description || '',
        url: `https://www.bilibili.com/video/${video.bvid}`,
        coverImage: picUrl,
        
        // 作者信息
        author: video.author || '',
        authorId: video.mid,
        authorAvatar: authorAvatar,
        
        // 分类信息
        categoryId: video.typeid,
        categoryName: video.typename || '',
        tags: video.tag ? video.tag.split(',').map(t => t.trim()).filter(t => t) : [],
        
        // 搜索元数据
        searchKeyword: keyword,
        category: category,
        categoryTags: tags,
        
        // 统计数据
        playCount: video.play || 0,
        danmakuCount: video.danmaku || video.video_review || 0,
        favoriteCount: video.favorites || 0,
        likeCount: video.like || 0,
        commentCount: video.review || 0,
        
        // 时间信息
        duration: video.duration || '',
        publishDate: pubDate,
        publishTimestamp: video.pubdate,
        
        // 用于向量化的文本
        searchableText: buildSearchableText(cleanTitle, video.description, video.tag),
        
        // 元数据
        crawledAt: new Date().toISOString(),
        source: 'bilibili',
        type: 'video_course'
    };
}

/**
 * 构建用于向量搜索的文本
 * @param {string} title - 标题
 * @param {string} description - 描述
 * @param {string} tags - 标签
 * @returns {string} - 合并后的文本
 */
function buildSearchableText(title, description, tags) {
    const parts = [];
    
    if (title) {
        parts.push(`标题：${title}`);
    }
    
    if (description) {
        parts.push(`描述：${description}`);
    }
    
    if (tags) {
        parts.push(`标签：${tags}`);
    }
    
    return parts.join('\n');
}

/**
 * 带重试的请求
 * @param {string} url
 * @param {number} [retryCount]
 */
async function fetchPageWithRetry(url, retryCount = 0) {
    try {
        const response = await fetch(url, {
            headers: {
                'User-Agent': getRandomUserAgent(),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Referer': 'https://www.bilibili.com/',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-site',
                'sec-fetch-user': '?1',
            },
        });

        // 检查反爬
        if (response.status === 403 || response.status === 429) {
            console.log(`[${response.status}] Possible anti-crawl detected, waiting longer...`);
            await delay(CONFIG.retryDelay * 2);
            if (retryCount < CONFIG.maxRetries) {
                return fetchPageWithRetry(url, retryCount + 1);
            }
        }

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.text();
    } catch (err) {
        if (retryCount < CONFIG.maxRetries) {
            console.log(`[Retry] ${err.message}, retrying... (${retryCount + 1}/${CONFIG.maxRetries})`);
            await delay(CONFIG.retryDelay);
            return fetchPageWithRetry(url, retryCount + 1);
        }
        throw err;
    }
}

/**
 * 保存结果到文件
 * @param {Object[]} results
 */
function saveResults(results) {
    try {
        if (!fs.existsSync(RESULT_DIR)) {
            fs.mkdirSync(RESULT_DIR, {recursive: true});
        }
        fs.writeFileSync(RESULT_FILE, JSON.stringify(results, null, 2), 'utf-8');
        console.log(`[Result] Saved ${results.length} courses to ${RESULT_FILE}`);
    } catch (err) {
        console.error('[Result] Failed to save:', err);
    }
}

/**
 * 保存爬取进度
 */
function saveProgress(progress) {
    try {
        fs.writeFileSync(PROGRESS_FILE, JSON.stringify(progress, null, 2), 'utf-8');
    } catch (err) {
        console.error('[Progress] Failed to save:', err);
    }
}

/**
 * 加载爬取进度
 */
function loadProgress() {
    try {
        if (fs.existsSync(PROGRESS_FILE)) {
            const data = fs.readFileSync(PROGRESS_FILE, 'utf-8');
            return JSON.parse(data);
        }
    } catch (err) {
        console.log('[Progress] No previous progress found');
    }
    return null;
}

/**
 * 加载已收集的课程
 */
function loadExistingResults() {
    try {
        if (fs.existsSync(RESULT_FILE)) {
            const data = fs.readFileSync(RESULT_FILE, 'utf-8');
            return JSON.parse(data);
        }
    } catch (err) {
        console.log('[Result] No previous results found');
    }
    return [];
}

// 主程序
console.log('=== B站视频课程爬虫 ===');
console.log(`配置: 延迟=${CONFIG.requestDelay[0]}-${CONFIG.requestDelay[1]}ms, 每批=${CONFIG.batchSize}, 排序=${CONFIG.orderType}`);
console.log('');

// 决定运行模式
const args = process.argv.slice(2);
const mode = args[0] || 'crawl';

if (mode === 'crawl') {
    // 实际爬取模式
    console.log('[Mode] Crawl mode - starting actual crawling...\n');
    
    // 加载已有结果和进度
    const existingCourses = loadExistingResults();
    const existingBvids = new Set(existingCourses.map(c => c.bvid));
    const savedProgress = loadProgress();
    
    console.log(`[Resume] Found ${existingCourses.length} existing courses`);
    
    let requestCount = 0;
    let foundNewCourses = 0;
    
    // 确定起始位置
    let startCategoryIndex = 0;
    let startKeywordIndex = 0;
    let startPage = 1;
    
    if (savedProgress) {
        // 找到上次中断的位置
        for (let i = 0; i < itSearchKeywords.length; i++) {
            if (itSearchKeywords[i].category === savedProgress.category) {
                startCategoryIndex = i;
                for (let j = 0; j < itSearchKeywords[i].keywords.length; j++) {
                    if (itSearchKeywords[i].keywords[j] === savedProgress.keyword) {
                        startKeywordIndex = j;
                        startPage = savedProgress.page || 1;
                        break;
                    }
                }
                break;
            }
        }
        console.log(`[Resume] Continuing from category "${savedProgress.category}", keyword "${savedProgress.keyword}", page ${startPage}`);
    }
    
    // 主爬取循环
    (async () => {
        try {
            for (let ci = startCategoryIndex; ci < itSearchKeywords.length; ci++) {
                const categoryData = itSearchKeywords[ci];
                console.log(`\n[Category] ${categoryData.category}`);
                
                for (let ki = (ci === startCategoryIndex ? startKeywordIndex : 0); ki < categoryData.keywords.length; ki++) {
                    const keyword = categoryData.keywords[ki];
                    console.log(`\n[Keyword] ${keyword}`);
                    
                    for (let page = (ci === startCategoryIndex && ki === startKeywordIndex ? startPage : 1); page <= CONFIG.maxPagesPerKeyword; page++) {
                        const searchUrl = buildSearchUrl(keyword, page, CONFIG.orderType);
                        console.log(`[Fetch] Page: ${page}`);
                        console.log(`  URL: ${searchUrl}`);
                        
                        try {
                            const htmlContent = await fetchPageWithRetry(searchUrl);
                            const piniaData = extractPiniaData(htmlContent);
                            
                            requestCount++;
                            
                            if (!piniaData) {
                                console.log(`[Skip] Failed to extract data from page ${page}`);
                                // 即使失败也要延迟
                                if (requestCount % CONFIG.batchSize === 0) {
                                    console.log(`\n[Batch] ${requestCount} requests, pausing for ${CONFIG.batchPause / 1000}s...\n`);
                                    await delay(CONFIG.batchPause);
                                } else {
                                    await delay(CONFIG.requestDelay[0], CONFIG.requestDelay[1]);
                                }
                                continue;
                            }
                            
                            const pageCourses = extractVideoCourses(
                                piniaData, 
                                keyword, 
                                categoryData.category, 
                                categoryData.tags
                            );
                            
                            if (pageCourses.length === 0) {
                                console.log(`[Done] No results on page ${page}`);
                                // 延迟后再跳出
                                if (requestCount % CONFIG.batchSize === 0) {
                                    console.log(`\n[Batch] ${requestCount} requests, pausing for ${CONFIG.batchPause / 1000}s...\n`);
                                    await delay(CONFIG.batchPause);
                                } else {
                                    await delay(CONFIG.requestDelay[0], CONFIG.requestDelay[1]);
                                }
                                break;
                            }
                            
                            // 过滤已存在的课程
                            const newCourses = pageCourses.filter(c => !existingBvids.has(c.bvid));
                            
                            if (newCourses.length > 0) {
                                existingCourses.push(...newCourses);
                                newCourses.forEach(c => existingBvids.add(c.bvid));
                                foundNewCourses += newCourses.length;
                                console.log(`[Found] ${newCourses.length} new courses (total: ${existingCourses.length})`);
                            } else {
                                console.log(`[Skip] All courses already exist`);
                            }
                            
                            // 每10个结果保存一次
                            if (foundNewCourses % 10 === 0 && foundNewCourses > 0) {
                                saveResults(existingCourses);
                            }
                            
                            // 每批请求后暂停
                            if (requestCount % CONFIG.batchSize === 0) {
                                console.log(`\n[Batch] ${requestCount} requests, pausing for ${CONFIG.batchPause / 1000}s...\n`);
                                saveResults(existingCourses);
                                saveProgress({
                                    category: categoryData.category,
                                    keyword: keyword,
                                    page: page + 1,
                                    total: existingCourses.length,
                                    timestamp: new Date().toISOString()
                                });
                                await delay(CONFIG.batchPause);
                            } else {
                                await delay(CONFIG.requestDelay[0], CONFIG.requestDelay[1]);
                            }
                            
                        } catch (err) {
                            console.error(`[Error] ${err.message}`);
                            saveResults(existingCourses);
                            saveProgress({
                                category: categoryData.category,
                                keyword: keyword,
                                page: page,
                                total: existingCourses.length,
                                timestamp: new Date().toISOString()
                            });
                            throw err;
                        }
                    }
                }
            }
            
            console.log('\n=== 爬取完成 ===');
            console.log(`总共收集: ${existingCourses.length} 个课程`);
            console.log(`新增: ${foundNewCourses} 个课程`);
            
            // 清理进度文件
            if (fs.existsSync(PROGRESS_FILE)) {
                fs.unlinkSync(PROGRESS_FILE);
            }
            
        } catch (err) {
            console.error('\n=== 爬取中断 ===');
            console.error(`原因: ${err.message}`);
        } finally {
            saveResults(existingCourses);
            console.log(`\n结果已保存: ${RESULT_FILE}`);
        }
    })();
    
} else {
    console.error(`[Error] 未知模式: ${mode}`);
    console.log('用法: node get_video_data.js [crawl]');
    process.exit(1);
}

export {
    extractPiniaData,
    extractVideoCourses,
    extractCourseInfo,
    buildSearchUrl,
    itSearchKeywords
};
