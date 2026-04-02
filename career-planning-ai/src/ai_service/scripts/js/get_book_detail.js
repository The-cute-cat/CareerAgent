// @ts-check
// noinspection SpellCheckingInspection

/**
 * 豆瓣图书详情爬取脚本
 * 从已爬取的书籍URL获取详细页面信息
 */

import * as cheerio from 'cheerio';
import fs from 'fs';
import path from 'path';
import readline from 'readline';
import {fileURLToPath} from 'url';

/** @typedef {import('cheerio').CheerioAPI} CheerioAPI */

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 文件路径配置
const SOURCE_FILE = path.join(__dirname, 'books_data', 'all_books.json');
const RESULT_DIR = path.join(__dirname, 'books_data');
const RESULT_FILE = path.join(RESULT_DIR, 'books_detail.json');
const FAILED_FILE = path.join(RESULT_DIR, 'failed_books.json');
const PROGRESS_FILE = path.join(__dirname, '.book_detail_progress.json');
const COOKIE_FILE = path.join(__dirname, '.douban_cookies.json');

// 代理配置
const PROXY_URL = "https://cors-proxy-worker.hopecat.dpdns.org/?url=";

// 爬取配置
const CONFIG = {
    requestDelay: [3000, 5000],   // 请求延迟 3-5秒
    batchSize: 20,                 // 每批请求数量
    batchPause: 60000,             // 每批后暂停 60秒
    retryDelay: 15000,             // 重试延迟 15秒
    maxRetries: 3,                 // 最大重试次数
    cooldownAfterBlock: 30000,     // 被拦截后冷却时间
};

// Cookie 管理器
const cookieJar = new Map();

/**
 * 初始化 Cookie
 * @param {string} cookieString
 */
function initCookies(cookieString) {
    cookieString.split(';').forEach(cookie => {
        const [name, ...valueParts] = cookie.trim().split('=');
        if (name && valueParts.length > 0) {
            cookieJar.set(name, valueParts.join('='));
        }
    });
}

/**
 * 从文件加载 Cookie
 */
function loadCookiesFromFile() {
    try {
        if (fs.existsSync(COOKIE_FILE)) {
            const data = fs.readFileSync(COOKIE_FILE, 'utf-8');
            const cookies = JSON.parse(data);
            for (const [name, value] of Object.entries(cookies)) {
                cookieJar.set(name, value);
            }
            console.log(`[Cookie] Loaded from file: ${cookieJar.size} cookies`);
            return true;
        }
    } catch (err) {
        console.log('[Cookie] Failed to load from file:', err.message);
    }
    return false;
}

/**
 * 保存 Cookie 到文件
 */
function saveCookiesToFile() {
    try {
        const cookies = Object.fromEntries(cookieJar);
        fs.writeFileSync(COOKIE_FILE, JSON.stringify(cookies, null, 2));
        console.log(`[Cookie] Saved to file: ${cookieJar.size} cookies`);
    } catch (err) {
        console.log('[Cookie] Failed to save to file:', err.message);
    }
}

/**
 * 从响应头更新 Cookie
 * @param {Headers} responseHeaders
 */
function updateCookies(responseHeaders) {
    const setCookie = responseHeaders.get('set-cookie');
    if (setCookie) {
        const cookieParts = setCookie.split(',');
        cookieParts.forEach(part => {
            const cookiePair = part.split(';')[0].trim();
            const [name, ...valueParts] = cookiePair.split('=');
            if (name && valueParts.length > 0) {
                cookieJar.set(name, valueParts.join('='));
            }
        });
    }
}

/**
 * 获取当前 Cookie 字符串
 * @returns {string}
 */
function getCookieString() {
    return Array.from(cookieJar.entries())
        .map(([name, value]) => `${name}=${value}`)
        .join('; ');
}

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

// 创建 readline 接口
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
});

/**
 * 从控制台读取用户输入
 * @param {string} prompt
 * @returns {Promise<string>}
 */
function readLine(prompt) {
    return new Promise(resolve => {
        rl.question(prompt, answer => {
            resolve(answer.trim());
        });
    });
}

/**
 * 让用户输入新 Cookie
 * @returns {Promise<boolean>}
 */
async function promptNewCookie() {
    console.log('\n' + '='.repeat(50));
    console.log('[Warning] 可能被反爬机制拦截或Cookie过期');
    console.log('请在浏览器中登录豆瓣，然后复制Cookie');
    console.log('获取方法: F12打开开发者工具 -> Network -> 刷新页面 -> 点击任意请求 -> Headers -> Cookie');
    console.log('='.repeat(50));

    const newCookie = await readLine('请粘贴Cookie (直接回车跳过): ');

    if (newCookie && newCookie.length > 10) {
        cookieJar.clear();
        initCookies(newCookie);
        saveCookiesToFile();
        console.log('[Cookie] Updated successfully!\n');
        return true;
    }
    console.log('[Cookie] Skipped\n');
    return false;
}

/**
 * 检查HTML是否被反爬
 * @param {string} html
 * @returns {boolean} true表示被拦截
 */
function isBlocked(html) {
    // 优先检查是否是正常的书籍页面
    // 正常页面有 #info 区域或评分区域，这是最强有力的正面证据
    if (html.includes('id="info"') || html.includes('class="rating_num"')) {
        return false;
    }

    // 没有正常页面元素时，检查是否是反爬验证页面
    if (html.includes('name="captcha-solution"')) return true;
    if (html.includes('id="captcha_img"')) return true;

    // 检查是否是频率限制页面
    if (html.includes('访问过于频繁')) return true;
    if (html.includes('暂时无法访问')) return true;
    if (html.includes('检测到有异常请求')) return true;

    return false;
}

/**
 * 清理字符串中的多余空白字符
 * @param {string} str
 * @returns {string}
 */
function cleanWhitespace(str) {
    if (!str) return '';
    return str.replace(/\s+/g, ' ').trim();
}

/**
 * 从详情页 #info 区域提取字段值
 * @param {CheerioAPI} $
 * @param {string} fieldName - 字段名称（如 "作者", "出版社", "译者" 等）
 * @returns {string} 提取的值
 */
function extractInfoField($, fieldName) {
    let result = '';

    // 查找包含字段名的 span.pl
    $('#info span.pl').each((_, el) => {
        const text = $(el).text().trim();

        // 匹配字段名（处理可能的空格和冒号）
        if (text.includes(fieldName)) {
            // 获取该 span 之后的内容
            let $next = $(el).next();

            // 如果下一个元素是链接（如作者、出版社）
            if ($next.is('a')) {
                result = $next.text().trim();
            } else if ($next.is('br')) {
                // 如果是 br，说明值在同一行但不是链接
                // 尝试获取 span 之后的文本节点
                let node = el.nextSibling;
                let textParts = [];
                while (node && node.type !== 'tag' && !(node.type === 'tag' && node.name === 'br')) {
                    if (node.type === 'text') {
                        textParts.push(node.data);
                    }
                    node = node.nextSibling;
                }
                if (textParts.length > 0) {
                    result = textParts.join('').replace(/^[:：]\s*/, '').trim();
                }
            } else {
                // 尝试获取文本节点
                let node = el.nextSibling;
                let textParts = [];
                while (node && node.type !== 'tag') {
                    if (node.type === 'text') {
                        textParts.push(node.data);
                    }
                    node = node.nextSibling;
                }
                if (textParts.length > 0) {
                    result = textParts.join('').replace(/^[:：]\s*/, '').trim();
                }
            }

            return false; // 找到后退出循环
        }
    });

    return cleanWhitespace(result);
}

/**
 * 从详情页HTML提取书籍详细信息
 * @param {CheerioAPI} $
 * @param {object} basicInfo - 基础信息（从搜索页获取），只保留 id, title, url, cover_url, keyword, category
 * @returns {object} 详细信息对象
 */
function extractBookDetail($, basicInfo) {
    // 只保留基础字段，其他字段从详情页重新获取
    const detail = {
        id: basicInfo.id,
        title: basicInfo.title,
        url: basicInfo.url,
        cover_url: basicInfo.cover_url,
        keyword: basicInfo.keyword,
        category: basicInfo.category,

        // 从详情页获取的字段
        subtitle: '',
        author: '',
        translator: '',
        publisher: '',
        publish_date: '',
        price: '',
        isbn: '',
        pages: '',
        binding: '',
        summary: '',
        author_intro: '',
        catalog: '',
        rating: null,
        rating_detail: null,

        crawl_time: basicInfo.crawl_time,
        detail_crawl_time: new Date().toISOString()
    };

    try {
        // 提取副标题
        const subtitle = $('h2.subtitle span').first().text().trim();
        if (subtitle) {
            detail.subtitle = subtitle;
        }

        // 从 #info 区域精确提取各字段
        detail.author = extractInfoField($, '作者');
        detail.translator = extractInfoField($, '译者');
        detail.publisher = extractInfoField($, '出版社');

        // 出版年
        detail.publish_date = extractInfoField($, '出版年');

        // 定价
        detail.price = extractInfoField($, '定价');

        // ISBN
        detail.isbn = extractInfoField($, 'ISBN');

        // 页数
        detail.pages = extractInfoField($, '页数');

        // 装帧
        detail.binding = extractInfoField($, '装帧');

        // 提取评分详情
        const ratingScore = $('strong.rating_num').text().trim();
        const ratingCount = $('span.rating_people span').text().trim();
        if (ratingScore) {
            const score = parseFloat(ratingScore) || 0;
            const count = parseInt(ratingCount) || 0;

            detail.rating = {
                score: score,
                count: count
            };

            detail.rating_detail = {
                score: score,
                count: count,
                distribution: {}
            };

            // 提取评分分布
            $('.rating_wrap .stars5, .rating_wrap .stars4, .rating_wrap .stars3, .rating_wrap .stars2, .rating_wrap .stars1').each((_, el) => {
                const starText = $(el).text().trim();
                const percent = $(el).nextAll('.rating_per').first().text().trim();
                if (starText && percent) {
                    detail.rating_detail.distribution[starText] = percent;
                }
            });
        }

        // 提取内容简介
        const summarySection = $('#link-report .intro').first();
        if (summarySection.length) {
            // 优先获取完整内容（展开后的）
            const fullSummary = $('#link-report .all .intro p').map((_, el) => $(el).text().trim()).get().join('\n');
            if (fullSummary) {
                detail.summary = fullSummary.replace(/\n{3,}/g, '\n\n').trim();
            } else {
                // 否则获取简短内容
                detail.summary = summarySection.find('p').map((_, el) => $(el).text().trim()).get().join('\n').replace(/\n{3,}/g, '\n\n').trim();
            }
        }

        // 提取作者简介
        const authorIntroSection = $('h2:contains("作者简介")').next('.indent').find('.intro');
        if (authorIntroSection.length) {
            detail.author_intro = authorIntroSection.find('p').map((_, el) => $(el).text().trim()).get().join('\n').replace(/\n{3,}/g, '\n\n').trim();
        }

        // 提取目录
        const catalogSection = $('#dir_' + basicInfo.id + '_short');
        if (catalogSection.length) {
            detail.catalog = catalogSection.text().replace(/\s+/g, ' ').trim();
        }

    } catch (err) {
        console.error(`[Parse Error] ${err.message}`);
    }

    return detail;
}

/**
 * 加载源数据
 */
function loadSourceBooks() {
    try {
        if (fs.existsSync(SOURCE_FILE)) {
            const data = fs.readFileSync(SOURCE_FILE, 'utf-8');
            return JSON.parse(data);
        }
    } catch (err) {
        console.error('[Source] Failed to load:', err.message);
    }
    return [];
}

/**
 * 加载已爬取的详情数据
 */
function loadExistingDetails() {
    try {
        if (fs.existsSync(RESULT_FILE)) {
            const data = fs.readFileSync(RESULT_FILE, 'utf-8');
            return JSON.parse(data);
        }
    } catch (err) {
        console.log('[Detail] No existing details found');
    }
    return [];
}

/**
 * 加载失败记录
 */
function loadFailedBooks() {
    try {
        if (fs.existsSync(FAILED_FILE)) {
            const data = fs.readFileSync(FAILED_FILE, 'utf-8');
            return JSON.parse(data);
        }
    } catch (err) {
        // ignore
    }
    return [];
}

/**
 * 保存失败记录
 * @param {object[]} failedBooks
 */
function saveFailedBooks(failedBooks) {
    try {
        fs.writeFileSync(FAILED_FILE, JSON.stringify(failedBooks, null, 2), 'utf-8');
    } catch (err) {
        console.error('[Failed] Failed to save failed records:', err.message);
    }
}

/**
 * 保存详情数据
 * @param {object[]} details
 */
function saveDetails(details) {
    try {
        if (!fs.existsSync(RESULT_DIR)) {
            fs.mkdirSync(RESULT_DIR, {recursive: true});
        }
        fs.writeFileSync(RESULT_FILE, JSON.stringify(details, null, 2), 'utf-8');
        console.log(`[Save] Saved ${details.length} book details`);
    } catch (err) {
        console.error('[Save] Failed to save:', err.message);
    }
}

/**
 * 保存爬取进度
 */
function saveProgress(progress) {
    try {
        fs.writeFileSync(PROGRESS_FILE, JSON.stringify(progress, null, 2), 'utf-8');
        console.log(`[Progress] Fetched: ${progress.fetched}, Remaining: ${progress.remaining}`);
    } catch (err) {
        console.error('[Progress] Failed to save:', err.message);
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
 * 带重试的页面请求
 */
async function fetchPageWithRetry(url, retryCount = 0) {
    try {
        const requestHeaders = {
            'User-Agent': getRandomUserAgent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
        };

        if (cookieJar.size > 0) {
            requestHeaders['Cookie'] = getCookieString();
        }

        const proxyUrl = PROXY_URL + encodeURIComponent(url);

        const response = await fetch(proxyUrl, {
            headers: requestHeaders,
            redirect: 'follow'
        });

        updateCookies(response.headers);

        if (response.status === 403 || response.status === 405) {
            console.log(`[${response.status}] Access denied`);
            await promptNewCookie();
            if (retryCount < CONFIG.maxRetries) {
                await delay(CONFIG.cooldownAfterBlock);
                return fetchPageWithRetry(url, retryCount + 1);
            }
            return null;
        }

        if (response.status === 429) {
            console.log('[429] Rate limited');
            await delay(CONFIG.cooldownAfterBlock);
            if (retryCount < CONFIG.maxRetries) {
                return fetchPageWithRetry(url, retryCount + 1);
            }
            return null;
        }

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const html = await response.text();

        if (isBlocked(html)) {
            console.log('[Block] Detected anti-crawl mechanism');
            await promptNewCookie();
            await delay(CONFIG.cooldownAfterBlock);
            if (retryCount < CONFIG.maxRetries) {
                return fetchPageWithRetry(url, retryCount + 1);
            }
            return null;
        }

        return cheerio.load(html);
    } catch (err) {
        if (retryCount < CONFIG.maxRetries) {
            console.log(`[Retry] ${err.message} (${retryCount + 1}/${CONFIG.maxRetries})`);
            await delay(CONFIG.retryDelay);
            return fetchPageWithRetry(url, retryCount + 1);
        }
        console.error(`[Error] Failed to fetch:`, err.message);
        return null;
    }
}

/**
 * 加载缺失书籍列表
 */
function loadMissingBooks() {
    const MISSING_FILE = path.join(RESULT_DIR, 'missing_books.json');
    try {
        if (fs.existsSync(MISSING_FILE)) {
            const data = fs.readFileSync(MISSING_FILE, 'utf-8');
            return JSON.parse(data);
        }
    } catch (err) {
        // ignore
    }
    return [];
}

/**
 * 主爬取函数
 */
async function main() {
    console.log('=== 豆瓣图书详情爬虫 ===');
    console.log(`代理: ${PROXY_URL ? '已启用' : '未使用'}`);
    console.log(`配置: 请求延迟=${CONFIG.requestDelay[0]}-${CONFIG.requestDelay[1]}ms, 每批=${CONFIG.batchSize}`);
    console.log('');

    // 检查命令行参数
    const args = process.argv.slice(2);
    const retryMissing = args.includes('--retry-missing');

    // 加载Cookie
    if (!loadCookiesFromFile()) {
        console.log('[Cookie] 未找到Cookie文件');
        await promptNewCookie();
    }

    // 加载源数据
    let sourceBooks;
    if (retryMissing) {
        sourceBooks = loadMissingBooks();
        console.log(`[Source] Loaded ${sourceBooks.length} missing books from missing_books.json`);
    } else {
        sourceBooks = loadSourceBooks();
        console.log(`[Source] Loaded ${sourceBooks.length} books from source`);
    }

    if (sourceBooks.length === 0) {
        console.log('[Error] No source books found. Please run get_book.data.js first.');
        rl.close();
        return;
    }

    // 加载已有详情
    const existingDetails = loadExistingDetails();
    const existingIds = new Set(existingDetails.map(b => b.id));
    console.log(`[Detail] Found ${existingDetails.length} existing details`);

    // 过滤出需要爬取的书籍
    const booksToFetch = sourceBooks.filter(book => !existingIds.has(book.id));
    console.log(`[Task] ${booksToFetch.length} books need detail fetching`);

    if (booksToFetch.length === 0) {
        console.log('[Done] All books already have details');
        rl.close();
        return;
    }

    // 加载进度
    const savedProgress = loadProgress();
    let startIndex = 0;

    if (savedProgress?.fetched) {
        startIndex = savedProgress.fetched;
        console.log(`[Resume] Resuming from ${startIndex} fetched, ${savedProgress.remaining || '?'} remaining`);
        console.log(`         Previous: ${savedProgress.success} success, ${savedProgress.fail} fail`);
    }

    let requestCount = 0;
    let successCount = 0;
    let failCount = 0;
    let fetchedCount = 0; // 本次已爬取数量
    let failedBooks = loadFailedBooks(); // 加载已有失败记录

    // 开始爬取
    for (let i = startIndex; i < booksToFetch.length; i++) {
        const book = booksToFetch[i];
        fetchedCount++;

        console.log(`\n[${fetchedCount}/${booksToFetch.length - startIndex}] Fetching: ${book.title}`);
        console.log(`  URL: ${book.url}`);

        const $ = await fetchPageWithRetry(book.url);

        if (!$) {
            console.log(`[Fail] Could not fetch page`);
            failCount++;

            // 记录失败
            failedBooks.push({
                id: book.id,
                title: book.title,
                url: book.url,
                failTime: new Date().toISOString(),
                reason: 'fetch_failed'
            });

            // 每10个失败保存一次
            if (failCount % 10 === 0) {
                saveFailedBooks(failedBooks);
            }

            // 保存进度
            saveProgress({
                fetched: fetchedCount,
                remaining: booksToFetch.length - startIndex - fetchedCount,
                success: successCount,
                fail: failCount,
                timestamp: new Date().toISOString()
            });

            await delay(CONFIG.requestDelay[0], CONFIG.requestDelay[1]);
            continue;
        }

        // 提取详情
        const detail = extractBookDetail($, book);
        existingDetails.push(detail);
        existingIds.add(detail.id);
        successCount++;

        console.log(`[Success] ISBN: ${detail.isbn}, Pages: ${detail.pages}`);
        console.log(`  Summary: ${detail.summary.substring(0, 50)}...`);

        requestCount++;

        // 每10个保存一次结果
        if (successCount % 10 === 0) {
            saveDetails(existingDetails);
            saveCookiesToFile();
            console.log(`[AutoSave] Saved ${existingDetails.length} details`);
        }

        // 保存进度
        if (fetchedCount % 10 === 0) {
            saveProgress({
                fetched: fetchedCount,
                remaining: booksToFetch.length - startIndex - fetchedCount,
                success: successCount,
                fail: failCount,
                timestamp: new Date().toISOString()
            });
        }

        // 每批后暂停
        if (requestCount % CONFIG.batchSize === 0) {
            console.log(`\n[Batch] ${requestCount} requests, pausing for ${CONFIG.batchPause / 1000}s...`);
            await delay(CONFIG.batchPause);
        }

        // 请求间延迟
        await delay(CONFIG.requestDelay[0], CONFIG.requestDelay[1]);
    }

    // 保存最终结果
    saveDetails(existingDetails);
    saveCookiesToFile();
    saveFailedBooks(failedBooks);

    // 删除进度文件
    if (fs.existsSync(PROGRESS_FILE)) {
        fs.unlinkSync(PROGRESS_FILE);
    }

    rl.close();

    console.log('\n=== 爬取完成 ===');
    console.log(`成功: ${successCount}`);
    console.log(`失败: ${failCount}`);
    console.log(`总计: ${existingDetails.length} 本书详情`);
    console.log(`保存位置: ${RESULT_FILE}`);
    if (failCount > 0) {
        console.log(`失败记录: ${FAILED_FILE}`);
    }
}

// 运行
main().catch(err => {
    console.error('\n=== 爬取出错 ===');
    console.error(err);
    rl.close();
});

export {
    extractBookDetail,
    fetchPageWithRetry,
    main
};
