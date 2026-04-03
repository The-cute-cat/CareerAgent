// @ts-check
// noinspection SpellCheckingInspection

import * as cheerio from 'cheerio';
import * as fs from 'fs';
import * as path from 'path';
import {fileURLToPath} from 'url';

/** @typedef {import('cheerio').CheerioAPI} CheerioAPI */

// 获取当前脚本目录
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 文件路径
const RESULT_FILE = path.join(__dirname, 'internships_url.txt');
const PROGRESS_FILE = path.join(__dirname, '.internships_crawl_progress.json');

// 配置
const CONFIG = {
    requestDelay: [2000, 5000],      // 每次请求延迟 2-5 秒
    batchSize: 10,                    // 每批请求数量
    batchPause: 30000,                // 每批后暂停 30 秒
    retryDelay: 60000,                // 错误重试等待 60 秒
    maxRetries: 3,                    // 最大重试次数
    maxPagesPerKeyword: 10,           // 每个关键词最多爬取页数
};

// 核心城市列表（用于笛卡尔积组合）
const CORE_CITIES = ['北京', '上海', '广州', '深圳', '杭州', '成都'];

// 搜索关键词配置
const shixisengSearchKeywords = [
    {
        category: "后端开发",
        keywords: [
            "Java实习生", "Java研发实习生", "Java后端实习生",
            "Go实习生", "Go开发实习生",
            "C++实习生", "C++开发实习生",
            "Python实习生", "Python后端实习生",
            "PHP实习生", "后端开发实习生", "后台开发实习生"
        ]
    },
    {
        category: "前端开发",
        keywords: [
            "前端实习生", "前端开发实习生", "Web前端实习生",
            "Vue实习生", "React实习生",
            "小程序实习生", "全栈实习生", "前端研发实习生"
        ]
    },
    {
        category: "人工智能与算法",
        keywords: [
            "算法实习生", "AI实习生", "人工智能实习生",
            "机器学习实习生", "深度学习实习生",
            "NLP实习生", "自然语言处理实习生",
            "CV实习生", "计算机视觉实习生",
            "推荐算法实习生", "大模型实习生", "LLM实习生", "AIGC实习生"
        ]
    },
    {
        category: "数据开发与分析",
        keywords: [
            "数据分析实习生", "数据开发实习生", "数据挖掘实习生",
            "数据仓库实习生", "数仓实习生", "ETL实习生",
            "BI实习生", "商业分析实习生", "大数据实习生"
        ]
    },
    {
        category: "测试与质量保障",
        keywords: [
            "测试实习生", "软件测试实习生", "自动化测试实习生",
            "测试开发实习生", "测开实习生", "QA实习生"
        ]
    },
    {
        category: "运维、云计算与安全",
        keywords: [
            "运维实习生", "SRE实习生", "DevOps实习生",
            "云计算实习生", "网络工程师实习生",
            "安全实习生", "网络安全实习生", "渗透测试实习生"
        ]
    },
    {
        category: "移动端开发",
        keywords: [
            "Android实习生", "安卓开发实习生",
            "iOS实习生", "苹果开发实习生",
            "鸿蒙实习生", "HarmonyOS实习生", "移动端开发实习生"
        ]
    },
    {
        category: "嵌入式与硬件",
        keywords: [
            "嵌入式实习生", "嵌入式软件开发实习生",
            "单片机实习生", "RTOS实习生", "物联网实习生"
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
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36',
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
 * 构建搜索URL
 * @param {string} keyword
 * @param {string} city
 * @param {number} page
 */
function buildSearchUrl(keyword, city, page = 1) {
    const baseUrl = 'https://www.shixiseng.com/interns';
    const params = new URLSearchParams({
        page: page.toString(),
        type: 'intern',
        keyword: keyword,
        area: '',
        months: '',
        days: '',
        degree: '',
        official: '',
        enterprise: '',
        salary: '-0',
        publishTime: '',
        sortType: '',
        city: city,
        internExtend: ''
    });
    return `${baseUrl}?${params.toString()}`;
}

/**
 * 保存结果到文件
 * @param {Object[]} results
 */
function saveResults(results) {
    try {
        const lines = results.map(r => 
            `${r.url}|${r.keyword}|${r.city}|${r.internId}|${r.priority}|${r.title}`
        );
        fs.writeFileSync(RESULT_FILE, lines.join('\n'));
        console.log(`[Result] Saved ${results.length} URLs to ${RESULT_FILE}`);
    } catch (err) {
        console.error('[Result] Failed to save:', err);
    }
}

/**
 * 保存爬取进度
 * @param {string} currentKeyword
 * @param {string} currentCity
 * @param {number} currentPage
 * @param {number} totalUrls
 */
function saveProgress(currentKeyword, currentCity, currentPage, totalUrls) {
    try {
        const progress = {
            currentKeyword,
            currentCity,
            currentPage,
            totalUrls,
            timestamp: new Date().toISOString()
        };
        fs.writeFileSync(PROGRESS_FILE, JSON.stringify(progress, null, 2));
    } catch (err) {
        console.error('[Progress] Failed to save:', err);
    }
}

/**
 * 加载爬取进度
 * @returns {{currentKeyword: string, currentCity: string, currentPage: number} | null}
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
 * 加载已收集的URL
 * @returns {Set<string>}
 */
function loadExistingResults() {
    const urlSet = new Set();
    try {
        if (fs.existsSync(RESULT_FILE)) {
            const data = fs.readFileSync(RESULT_FILE, 'utf-8');
            data.split('\n').filter(line => line.trim()).forEach(line => {
                const parts = line.split('|');
                if (parts[0]) {
                    urlSet.add(parts[0]);
                }
            });
        }
    } catch (err) {
        console.log('[Result] No previous results found');
    }
    return urlSet;
}

/**
 * 分析岗位名称，判断优先级
 * @param {string} title
 * @returns {{priority: number, tags: string[]}}
 */
function analyzeTitle(title) {
    const tags = [];
    let priority = 2; // 默认中等优先级
    
    // 高优先级关键词
    if (title.includes('暑期') || title.includes('转正') || title.includes('校招')) {
        priority = 3;
        tags.push('高优');
        if (title.includes('转正')) tags.push('可转正');
        if (title.includes('暑期')) tags.push('暑期实习');
    }
    
    // 低优先级关键词
    if (title.includes('日常') && !title.includes('转正')) {
        priority = 1;
        tags.push('日常实习');
    }
    
    return { priority, tags };
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
                'Referer': 'https://www.shixiseng.com/',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
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

        const html = await response.text();
        return cheerio.load(html);
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
 * 解码HTML实体
 * @param {string} str
 */
function decodeHtmlEntities(str) {
    // 处理 &#x 格式的实体
    str = str.replace(/&#x([0-9a-fA-F]+);?/g, (_, hex) => 
        String.fromCharCode(parseInt(hex, 16))
    );
    // 处理 &# 格式的实体
    str = str.replace(/&#(\d+);?/g, (_, dec) => 
        String.fromCharCode(parseInt(dec, 10))
    );
    return str;
}

/**
 * 从页面提取实习信息
 * @param {CheerioAPI} $
 * @param {string} keyword
 * @param {string} city
 */
function extractFromPage($, keyword, city) {
    const results = [];
    
    $('div[data-intern-id]').each((_, element) => {
        const internId = $(element).attr('data-intern-id');
        if (!internId || !internId.startsWith('inn_')) return;
        
        // 提取标题
        const titleLink = $(element).find('a.title').first();
        let title = titleLink.attr('title') || '';
        // 解码HTML实体
        title = decodeHtmlEntities(title);
        
        // 分析优先级
        const { priority, tags } = analyzeTitle(title);
        
        results.push({
            url: `https://www.shixiseng.com/intern/${internId}`,
            internId,
            keyword,
            city,
            title,
            priority,
            tags
        });
    });
    
    return results;
}

// 主程序
console.log('=== 实习僧 URL 爬虫 ===');
console.log(`配置: 延迟=${CONFIG.requestDelay[0]}-${CONFIG.requestDelay[1]}ms, 每批=${CONFIG.batchSize}, 批次暂停=${CONFIG.batchPause / 1000}s`);
console.log(`核心城市: ${CORE_CITIES.join(', ')}`);
console.log('');

// 决定运行模式
const args = process.argv.slice(2);
const mode = args[0] || 'crawl';

if (mode === 'generate-urls') {
    // 生成所有待爬取的URL列表（笛卡尔积）
    console.log('[Mode] Generate URLs mode');
    
    const allSearchUrls = [];
    for (const category of shixisengSearchKeywords) {
        for (const keyword of category.keywords) {
            for (const city of CORE_CITIES) {
                for (let page = 1; page <= CONFIG.maxPagesPerKeyword; page++) {
                    allSearchUrls.push({
                        url: buildSearchUrl(keyword, city, page),
                        keyword,
                        city,
                        page,
                        category: category.category
                    });
                }
            }
        }
    }
    
    console.log(`[Generate] Total search URLs: ${allSearchUrls.length}`);
    
    // 保存到文件
    const searchUrlsFile = path.join(__dirname, 'internships_search_urls.json');
    fs.writeFileSync(searchUrlsFile, JSON.stringify(allSearchUrls, null, 2));
    console.log(`[Saved] Search URLs saved to ${searchUrlsFile}`);
    
    // 统计
    const keywordCount = shixisengSearchKeywords.reduce((sum, cat) => sum + cat.keywords.length, 0);
    console.log(`\n[Stats]`);
    console.log(`  - 分类数: ${shixisengSearchKeywords.length}`);
    console.log(`  - 关键词数: ${keywordCount}`);
    console.log(`  - 城市数: ${CORE_CITIES.length}`);
    console.log(`  - 每关键词最大页数: ${CONFIG.maxPagesPerKeyword}`);
    console.log(`  - 总搜索URL数: ${keywordCount} × ${CORE_CITIES.length} × ${CONFIG.maxPagesPerKeyword} = ${allSearchUrls.length}`);
    
} else {
    // 实际爬取模式
    console.log('[Mode] Crawl mode - starting actual crawling...');
    console.log('提示: 使用 "node get_internships_url_list.js generate-urls" 可生成待爬取URL列表\n');
    
    // 加载已有结果和进度
    const existingUrls = loadExistingResults();
    const savedProgress = loadProgress();
    const allResults = [];
    
    // 重建已有结果
    if (fs.existsSync(RESULT_FILE)) {
        const data = fs.readFileSync(RESULT_FILE, 'utf-8');
        data.split('\n').filter(line => line.trim()).forEach(line => {
            const parts = line.split('|');
            if (parts.length >= 6) {
                allResults.push({
                    url: parts[0],
                    keyword: parts[1],
                    city: parts[2],
                    internId: parts[3],
                    priority: parseInt(parts[4]),
                    title: parts[5]
                });
            }
        });
    }
    
    if (allResults.length > 0) {
        console.log(`[Resume] Found ${allResults.length} existing URLs`);
    }
    
    let requestCount = 0;
    let foundNewUrls = 0;
    
    // 主爬取循环
    (async () => {
        try {
            for (const category of shixisengSearchKeywords) {
                console.log(`\n[Category] ${category.category}`);
                
                for (const keyword of category.keywords) {
                    console.log(`\n[Keyword] ${keyword}`);
                    
                    for (const city of CORE_CITIES) {
                        // 检查断点
                        let startPage = 1;
                        if (savedProgress && 
                            savedProgress.currentKeyword === keyword && 
                            savedProgress.currentCity === city) {
                            startPage = savedProgress.currentPage;
                            console.log(`[Resume] Continuing from page ${startPage}`);
                        }
                        
                        for (let page = startPage; page <= CONFIG.maxPagesPerKeyword; page++) {
                            const searchUrl = buildSearchUrl(keyword, city, page);
                            console.log(`[Fetch] City: ${city}, Page: ${page}`);
                            console.log(`  URL: ${searchUrl}`);
                            
                            try {
                                const $ = await fetchPageWithRetry(searchUrl);
                                const pageResults = extractFromPage($, keyword, city);
                                
                                if (pageResults.length === 0) {
                                    console.log(`[Done] No more results on page ${page}`);
                                    break;
                                }
                                
                                // 过滤已存在的URL
                                const newResults = pageResults.filter(r => !existingUrls.has(r.url));
                                
                                if (newResults.length > 0) {
                                    allResults.push(...newResults);
                                    newResults.forEach(r => existingUrls.add(r.url));
                                    foundNewUrls += newResults.length;
                                    console.log(`[Found] ${newResults.length} new URLs (total: ${allResults.length})`);
                                } else {
                                    console.log(`[Skip] All URLs already exists`);
                                }
                                
                                requestCount++;
                                
                                // 每批请求后暂停
                                if (requestCount % CONFIG.batchSize === 0) {
                                    console.log(`\n[Batch] ${requestCount} requests, pausing for ${CONFIG.batchPause / 1000}s...\n`);
                                    saveResults(allResults);
                                    saveProgress(keyword, city, page + 1, allResults.length);
                                    await delay(CONFIG.batchPause);
                                } else {
                                    // 请求间延迟
                                    await delay(CONFIG.requestDelay[0], CONFIG.requestDelay[1]);
                                }
                                
                            } catch (err) {
                                console.error(`[Error] ${err.message}`);
                                saveResults(allResults);
                                saveProgress(keyword, city, page, allResults.length);
                                throw err;
                            }
                        }
                    }
                }
            }
            
            console.log('\n=== 爬取完成 ===');
            console.log(`总共收集: ${allResults.length} 个URL`);
            console.log(`新增: ${foundNewUrls} 个URL`);
            
        } catch (err) {
            console.error('\n=== 爬取中断 ===');
            console.error(`原因: ${err.message}`);
        } finally {
            saveResults(allResults);
            console.log(`\n结果已保存: ${RESULT_FILE}`);
        }
    })();
}
