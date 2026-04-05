// @ts-check
// noinspection SpellCheckingInspection

import * as cheerio from 'cheerio';
import * as fs from 'fs';
import * as path from 'path';
import {fileURLToPath} from 'url';

// 获取当前脚本目录
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 文件路径
const URL_FILE = path.join(__dirname, 'internships_url.txt');
const RESULT_FILE = path.join(__dirname, 'internships_detail.json');
const PROGRESS_FILE = path.join(__dirname, '.internships_detail_progress.json');

// 配置
const CONFIG = {
    requestDelay: [2000, 5000],      // 每次请求延迟 2-5 秒
    saveInterval: 10,                // 每爬取10条保存一次
    batchPause: 30000,               // 每批后暂停 30 秒
    retryDelay: 60000,               // 错误重试等待 60 秒
    maxRetries: 3,                   // 最大重试次数
};

// User-Agent 列表
const USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15',
];

function getRandomUserAgent() {
    return USER_AGENTS[Math.floor(Math.random() * USER_AGENTS.length)];
}

function delay(minMs, maxMs = null) {
    const ms = maxMs ? Math.floor(Math.random() * (maxMs - minMs + 1)) + minMs : minMs;
    console.log(`[Delay] Waiting ${Math.floor(ms / 1000)}s...`);
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * 从HTML中解析 NUXT 数据
 * @param {string} html
 * @returns {Object|null}
 */
function parseNuxtData(html) {
    try {
        // 匹配 window.__NUXT__ = (function(...) { ... }(...));
        const nuxtMatch = html.match(/window\.__NUXT__\s*=\s*\(function[\s\S]*?\}\((.*?)\);<\/script>/);
        if (!nuxtMatch) {
            // 尝试另一种格式
            const simpleMatch = html.match(/window\.__NUXT__\s*=\s*(\{[\s\S]*?\});/);
            if (simpleMatch) {
                return JSON.parse(simpleMatch[1]);
            }
            return null;
        }
        
        // 这种格式需要执行JS来解析，我们改用正则直接提取关键字段
        return extractFieldsFromHtml(html);
    } catch (err) {
        console.error('[Parse] Failed to parse NUXT data:', err.message);
        return extractFieldsFromHtml(html);
    }
}

/**
 * 从HTML中直接提取关键字段
 * @param {string} html
 * @returns {Object}
 */
function extractFieldsFromHtml(html) {
    const $ = cheerio.load(html);
    const result = {};
    
    // 岗位名称
    result.jobTitle = $('.new_job_name span').first().text().trim() || 
                      $('div.job_detail').prev().text().trim();
    
    // 公司信息
    result.company = {
        name: $('.com-name').text().trim(),
        logo: $('.com_intro .logo img').attr('src') || '',
        industry: '',
        scale: ''
    };
    
    // 薪资
    const salaryText = $('.job_money').text().trim();
    result.salary = salaryText;
    
    // 解析薪资范围
    const salaryMatch = salaryText.match(/(\d+)-(\d+)\/天/);
    if (salaryMatch) {
        result.minSalary = parseInt(salaryMatch[1]);
        result.maxSalary = parseInt(salaryMatch[2]);
    }
    
    // 地点
    result.city = $('.job_position').attr('title') || $('.job_position').text().trim();
    result.address = $('.com_position').text().trim();
    
    // 学历要求
    result.degree = $('.job_academic').text().trim();
    
    // 每周天数
    const weekText = $('.job_week').text().trim();
    result.daysPerWeek = parseInt(weekText) || 0;
    
    // 实习时长
    const timeText = $('.job_time').text().trim();
    const monthMatch = timeText.match(/(\d+)/);
    result.months = monthMatch ? parseInt(monthMatch[1]) : 0;
    
    // 职位描述（核心：技术栈提取）
    result.jobDescription = $('.job_detail').text().trim();
    
    // 福利标签
    result.tags = [];
    $('.job_good_list span').each((_, el) => {
        result.tags.push($(el).text().trim());
    });
    
    // 刷新时间
    result.refreshTime = $('.job_date .cutom_font').text().trim();
    
    // 截止日期
    const deadlineText = html.match(/截止日期[：:]\s*(\d{4}-\d{2}-\d{2})/);
    result.deadline = deadlineText ? deadlineText[1] : '';
    
    // 从script中提取更多信息
    extractFromScript(html, result);
    
    return result;
}

/**
 * 从script标签中提取额外信息
 * @param {string} html
 * @param {Object} result
 */
function extractFromScript(html, result) {
    // 提取行业
    const industryMatch = html.match(/g\.industry\s*=\s*"([^"]+)"/);
    if (industryMatch) {
        result.company.industry = industryMatch[1].replace(/\\u002F/g, '/');
    }
    
    // 提取公司规模
    const scaleMatch = html.match(/g\.scale\s*=\s*"([^"]+)"/);
    if (scaleMatch) {
        result.company.scale = scaleMatch[1];
    }
    
    // 提取岗位UUID
    const uuidMatch = html.match(/inn_([a-z0-9]+)/);
    if (uuidMatch) {
        result.internId = 'inn_' + uuidMatch[1];
    }
    
    // 提取投递人数
    const deliverMatch = html.match(/g\.delivered_num\s*=\s*(\d+)/);
    if (deliverMatch) {
        result.deliveredCount = parseInt(deliverMatch[1]);
    }
}

/**
 * 从职位描述中提取技术栈
 * @param {string} description
 * @returns {string[]}
 */
function extractTechStack(description) {
    const techStack = [];
    
    // 常见技术栈关键词
    const techKeywords = [
        // 后端
        'Java', 'Spring', 'Spring Boot', 'Spring MVC', 'MyBatis', 'MyBatis-Plus',
        'Hibernate', 'JPA', 'Struts', 'Dubbo', 'Netty',
        'Go', 'Gin', 'Beego', 'Echo',
        'Python', 'Django', 'Flask', 'FastAPI', 'Tornado',
        'C\\+\\+', 'C#', '.NET', 'ASP.NET',
        'Node\\.js', 'Express', 'Koa', 'NestJS',
        'PHP', 'Laravel', 'ThinkPHP',
        'Ruby', 'Rails',
        
        // 前端
        'JavaScript', 'TypeScript', 'Vue', 'React', 'Angular', 'Svelte',
        'HTML', 'CSS', 'Sass', 'Less', 'Tailwind', 'Bootstrap',
        'Webpack', 'Vite', 'Rollup',
        '小程序', '微信小程序', 'uni-app', 'Taro',
        
        // 数据库
        'MySQL', 'PostgreSQL', 'Oracle', 'SQL Server', 'MariaDB',
        'MongoDB', 'Redis', 'Elasticsearch', 'Solr',
        'ClickHouse', 'HBase', 'Cassandra',
        
        // 大数据
        'Hadoop', 'Spark', 'Flink', 'Kafka', 'Hive', 'Presto',
        '数据仓库', 'ETL', '数据湖',
        
        // AI/ML
        '机器学习', '深度学习', 'TensorFlow', 'PyTorch', 'Keras',
        'NLP', '计算机视觉', 'CV', 'LLM', '大模型', 'AIGC',
        '推荐算法', '强化学习',
        
        // 云原生/运维
        'Docker', 'Kubernetes', 'K8s', 'Jenkins', 'GitLab CI',
        'AWS', 'Azure', 'GCP', '阿里云', '腾讯云',
        'Linux', 'Nginx', 'Tomcat',
        'DevOps', 'SRE', 'Prometheus', 'Grafana',
        
        // 移动端
        'Android', 'iOS', 'Swift', 'Objective-C', 'Kotlin',
        'Flutter', 'React Native', '鸿蒙', 'HarmonyOS',
        
        // 其他
        'Git', 'Maven', 'Gradle', 'npm', 'yarn',
        'RESTful', 'GraphQL', 'gRPC', 'WebSocket',
        '微服务', '分布式', '高并发', '消息队列',
        'JVM', 'GC', '多线程', '并发',
    ];
    
    for (const keyword of techKeywords) {
        const regex = new RegExp(keyword, 'i');
        if (regex.test(description)) {
            // 清理特殊字符
            const cleanKeyword = keyword.replace(/\\/g, '');
            if (!techStack.includes(cleanKeyword)) {
                techStack.push(cleanKeyword);
            }
        }
    }
    
    return techStack;
}

/**
 * 分析岗位类型和优先级
 * @param {Object} detail
 * @returns {Object}
 */
function analyzeJobDetail(detail) {
    const analysis = {
        priority: 2,
        jobType: '日常实习',
        techStack: [],
        keySkills: []
    };
    
    // 从标题和标签判断优先级
    const titleAndTags = (detail.jobTitle || '') + ' ' + (detail.tags || []).join(' ');
    
    if (titleAndTags.includes('暑期') || titleAndTags.includes('转正')) {
        analysis.priority = 3;
        analysis.jobType = detail.tags.includes('可转正实习') ? '可转正实习' : '暑期实习';
    } else if (titleAndTags.includes('日常')) {
        analysis.priority = 1;
        analysis.jobType = '日常实习';
    }
    
    // 提取技术栈
    if (detail.jobDescription) {
        analysis.techStack = extractTechStack(detail.jobDescription);
    }
    
    return analysis;
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
            },
        });

        if (response.status === 403 || response.status === 429) {
            console.log(`[${response.status}] Anti-crawl detected, waiting...`);
            await delay(CONFIG.retryDelay * 2);
            if (retryCount < CONFIG.maxRetries) {
                return fetchPageWithRetry(url, retryCount + 1);
            }
        }

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        return await response.text();
    } catch (err) {
        if (retryCount < CONFIG.maxRetries) {
            console.log(`[Retry] ${err.message} (${retryCount + 1}/${CONFIG.maxRetries})`);
            await delay(CONFIG.retryDelay);
            return fetchPageWithRetry(url, retryCount + 1);
        }
        throw err;
    }
}

/**
 * 保存结果
 * @param {Object[]} results
 */
function saveResults(results) {
    fs.writeFileSync(RESULT_FILE, JSON.stringify(results, null, 2));
    console.log(`[Save] ${results.length} records saved`);
}

/**
 * 保存进度
 * @param {number} index
 * @param {number} total
 */
function saveProgress(index, total) {
    fs.writeFileSync(PROGRESS_FILE, JSON.stringify({ currentIndex: index, total }));
}

/**
 * 加载进度
 */
function loadProgress() {
    try {
        if (fs.existsSync(PROGRESS_FILE)) {
            return JSON.parse(fs.readFileSync(PROGRESS_FILE, 'utf-8'));
        }
    } catch {}
    return null;
}

/**
 * 加载已收集的URL
 */
function loadUrls() {
    const urls = [];
    try {
        if (fs.existsSync(URL_FILE)) {
            const data = fs.readFileSync(URL_FILE, 'utf-8');
            data.split('\n').filter(line => line.trim()).forEach(line => {
                const parts = line.split('|');
                urls.push({
                    url: parts[0],
                    keyword: parts[1] || '',
                    city: parts[2] || '',
                    internId: parts[3] || '',
                    priority: parseInt(parts[4]) || 2,
                });
            });
        }
    } catch {}
    return urls;
}

/**
 * 加载已有详情
 */
function loadExistingDetails() {
    try {
        if (fs.existsSync(RESULT_FILE)) {
            return JSON.parse(fs.readFileSync(RESULT_FILE, 'utf-8'));
        }
    } catch {}
    return [];
}

// 主程序
console.log('=== 实习岗位详情爬虫 ===\n');

const args = process.argv.slice(2);
const mode = args[0] || 'crawl';

if (mode === 'parse-file') {
    // 解析本地HTML文件
    const filePath = args[1] || path.join(__dirname, '../temp/8.html');
    console.log(`[Parse] Parsing file: ${filePath}`);
    
    if (fs.existsSync(filePath)) {
        const html = fs.readFileSync(filePath, 'utf-8');
        const detail = extractFieldsFromHtml(html);
        const analysis = analyzeJobDetail(detail);
        
        console.log('\n=== 解析结果 ===');
        console.log(`岗位名称: ${detail.jobTitle}`);
        console.log(`公司: ${detail.company?.name}`);
        console.log(`行业: ${detail.company?.industry}`);
        console.log(`规模: ${detail.company?.scale}`);
        console.log(`薪资: ${detail.salary}`);
        console.log(`城市: ${detail.city}`);
        console.log(`地址: ${detail.address}`);
        console.log(`学历: ${detail.degree}`);
        console.log(`每周天数: ${detail.daysPerWeek}`);
        console.log(`实习月数: ${detail.months}`);
        console.log(`标签: ${detail.tags?.join(', ')}`);
        console.log(`优先级: ${analysis.priority}`);
        console.log(`岗位类型: ${analysis.jobType}`);
        console.log(`\n技术栈 (${analysis.techStack.length}个):`);
        console.log(analysis.techStack.join(', '));
        console.log(`\n职位描述:\n${detail.jobDescription?.substring(0, 200)}...`);
    } else {
        console.log(`[Error] File not found: ${filePath}`);
    }
    
} else {
    // 爬取模式
    console.log('[Mode] Crawl mode\n');
    
    const urls = loadUrls();
    if (urls.length === 0) {
        console.log('[Error] No URLs found. Run get_internships_url_list.js first.');
        process.exit(1);
    }
    
    console.log(`[Load] ${urls.length} URLs to process`);
    
    const existingDetails = loadExistingDetails();
    const existingIds = new Set(existingDetails.map(d => d.internId));
    const progress = loadProgress();
    
    const startIndex = progress?.currentIndex || 0;
    const results = [...existingDetails];
    
    let count = 0;
    
    (async () => {
        try {
            for (let i = startIndex; i < urls.length; i++) {
                const urlInfo = urls[i];
                
                // 跳过已爬取的
                if (existingIds.has(urlInfo.internId)) {
                    console.log(`[${i + 1}/${urls.length}] Skip ${urlInfo.internId} (exists)`);
                    continue;
                }
                
                console.log(`[${i + 1}/${urls.length}] Fetch ${urlInfo.url}`);
                
                try {
                    const html = await fetchPageWithRetry(urlInfo.url);
                    const detail = extractFieldsFromHtml(html);
                    const analysis = analyzeJobDetail(detail);
                    
                    results.push({
                        ...detail,
                        ...urlInfo,
                        priority: analysis.priority,
                        jobType: analysis.jobType,
                        techStack: analysis.techStack,
                        crawlTime: new Date().toISOString()
                    });
                    
                    count++;
                    console.log(`  -> ${detail.jobTitle} @ ${detail.company?.name}`);
                    console.log(`  -> Tech: ${analysis.techStack.slice(0, 5).join(', ')}${analysis.techStack.length > 5 ? '...' : ''}`);
                    
                    // 每saveInterval条保存一次
                    if (count % CONFIG.saveInterval === 0) {
                        console.log(`\n[Save] ${count} records fetched, saving to file...`);
                        saveResults(results);
                        saveProgress(i + 1, urls.length);
                        console.log(`[Pause] Waiting ${CONFIG.batchPause / 1000}s...\n`);
                        await delay(CONFIG.batchPause);
                    } else {
                        await delay(CONFIG.requestDelay[0], CONFIG.requestDelay[1]);
                    }
                    
                } catch (err) {
                    console.error(`  -> Error: ${err.message}`);
                    saveResults(results);
                    saveProgress(i, urls.length);
                }
            }
            
            console.log('\n=== 完成 ===');
            console.log(`新增: ${count} 条`);
            console.log(`总计: ${results.length} 条`);
            
        } catch (err) {
            console.error(`\n[Error] ${err.message}`);
        } finally {
            saveResults(results);
            console.log(`\n结果: ${RESULT_FILE}`);
        }
    })();
}
