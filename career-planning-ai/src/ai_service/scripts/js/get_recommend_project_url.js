// @ts-check
// noinspection SpellCheckingInspection

import * as cheerio from 'cheerio';
import * as fs from 'fs';
import * as path from 'path';
import * as readline from 'readline';
import {fileURLToPath} from 'url';

/** @typedef {import('cheerio').CheerioAPI} CheerioAPI */
/** @typedef {import('cheerio').Cheerio} Cheerio */

// 获取当前脚本目录
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 文件路径
const COOKIE_FILE = path.join(__dirname, '.gitee_cookies.json');
const RESULT_FILE = path.join(__dirname, 'recommend_project_url.txt');
const PROGRESS_FILE = path.join(__dirname, '.crawl_progress.json');

// 配置
const CONFIG = {
    requestDelay: [2000, 3000],      // 每次请求延迟 2-4 秒（增加避免触发反爬）
    batchSize: 30,                    // 每批请求数量（减少）
    batchPause: 60000,                // 每批后暂停 60 秒（增加）
    retryDelay: 120000,               // 错误重试等待 120 秒
    maxRetries: 3,                    // 最大重试次数
    cooldownAfter405: 300000,         // 405 后冷却 5 分钟
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
                cookieJar.set(name, /** @type {string} */ (value));
            }
            console.log(`[Cookie] Loaded from file: ${cookieJar.size} cookies`);
            return true;
        }
    } catch (err) {
        console.log('[Cookie] Failed to load from file:', err);
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
        console.log('[Cookie] Failed to save to file:', err);
    }
}

/**
 * 从响应头更新 Cookie
 * @param {Headers} headers
 */
function updateCookies(headers) {
    const setCookie = headers.get('set-cookie');
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

// User-Agent 列表（随机选择，模拟不同浏览器）
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
 * 获取随机请求头
 */
function getRandomHeaders() {
    return {
        'User-Agent': getRandomUserAgent(),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Referer': 'https://gitee.com/',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'Cache-Control': 'max-age=0',
    };
}

const baseHeaders = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Referer': 'https://gitee.com/',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
};

// 默认 Cookie（首次运行使用）
const DEFAULT_COOKIE = "BEC=8ddb6c1710618f9098bae11a2ceedd43; user_locale=zh-CN; oschina_new_user=false; abymg_id=1_B92937BE9D305339066EDE91E9C1C7AE6AE6648BF82C769DC9EC260AC783EA08; tz=Asia%2FShanghai; gitee-session-n=SVRsYVRGMG1KU1dIUlUxcDBiQjhuRHlpYjJGeFN1Q2s2NjNCM2dtWWdtWEVLanlqTGgxdTExWmJQbTQ0KzhDR29jdlgrRXNuT0FCMUJjazNFTTU4TFRyQk9ibHNUM3VYMVVZdlNaMlhrMlYxZk9zenhWMHBIRG9jTnFYVlBVM3dVQWNEN2o3Ym84UGx3M0ZsRzZXUVo0dzJ0M0gzVUdQWE5WcDRMS1BscDNtdUx5dDc5eHhPL0pYZzRrTTAwZGh6LS1LaTg4eFZjWlVOVXZ4N2FnSXdqQWF3PT0%3D--a3546fff29727f5b78bd758fc0c385f1bc24abe1; nox_jst_v1=2.0_a214_znfm5PImWAUd05c1lQdceuZBmQJ2jwDtjADN3aRaWA7vDgoB3Ib5CfPdwovIsH4ZNAL5rVEGvowsguEoyUihaWa345OP89Th60k12COXaS4o7uljsrl4qYqCybyCM+qDPU57Ho4YH5/E205qzveQZu5xMIZV3Nj+rbQcf5dWWw2xZSZyG3p3oigmTuNlrWAV91FV4uAd3rc3yc8d/J59WkPZXILlwpCsrRa8zi/lsn4TOxedSIXjvxo0O0f33Fop3jEd+MZFiWYi9TdBcb/YiA=="

// 尝试从文件加载 Cookie
if (!loadCookiesFromFile()) {
    console.log('[Cookie] Using default cookies');
    initCookies(DEFAULT_COOKIE);
}

const proxy_url = "";

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
 * 保存已收集的项目URL到文件
 * @param {string[]} urls
 */
function saveResults(urls) {
    try {
        fs.writeFileSync(RESULT_FILE, urls.join('\n'));
        console.log(`[Result] Saved ${urls.length} URLs to ${RESULT_FILE}`);
    } catch (err) {
        console.error('[Result] Failed to save:', err);
    }
}

/**
 * 保存爬取进度
 * @param {string} currentCategory
 * @param {number} currentPage
 * @param {string[]} urls
 */
function saveProgress(currentCategory, currentPage, urls) {
    try {
        const progress = {
            currentCategory,
            currentPage,
            totalUrls: urls.length,
            timestamp: new Date().toISOString()
        };
        fs.writeFileSync(PROGRESS_FILE, JSON.stringify(progress, null, 2));
    } catch (err) {
        console.error('[Progress] Failed to save:', err);
    }
}

/**
 * 加载爬取进度
 * @returns {{currentCategory: string, currentPage: number} | null}
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
 * @returns {string[]}
 */
function loadExistingResults() {
    try {
        if (fs.existsSync(RESULT_FILE)) {
            const data = fs.readFileSync(RESULT_FILE, 'utf-8');
            return data.split('\n').filter(url => url.trim());
        }
    } catch (err) {
        console.log('[Result] No previous results found');
    }
    return [];
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
 * @param {number} [errorCode]
 * @returns {Promise<boolean>}
 */
async function promptNewCookie(errorCode = 429) {
    console.log('\n' + '='.repeat(50));
    if (errorCode === 405) {
        console.log('[405] Access Denied! Anti-crawler detected.');
        console.log('Possible reasons: Cookie expired, IP flagged, or too many requests.');
    } else {
        console.log('[429] Rate limited! Cookie may be expired.');
    }
    console.log('='.repeat(50));
    console.log('Please login to Gitee in browser and copy new cookies.');
    console.log('Press Enter after you have copied the cookies...');

    await readLine('');

    const newCookie = await readLine('Paste new cookies here: ');

    if (newCookie && newCookie.length > 10) {
        cookieJar.clear();
        initCookies(newCookie);
        saveCookiesToFile();
        console.log('[Cookie] Updated successfully!\n');
        return true;
    } else {
        console.log('[Cookie] Invalid input, please try again.\n');
        return false;
    }
}

/**
 * 带重试的请求
 * @param {string} url
 * @param {number} [retryCount]
 */
async function fetchPageWithRetry(url, retryCount = 0) {
    while (true) {
        try {
            // 使用随机请求头，模拟不同浏览器
            const response = await fetch(proxy_url + url, {
                headers: {
                    ...getRandomHeaders(),
                    'Cookie': getCookieString(),
                },
                redirect: 'follow',
            });

            updateCookies(response.headers);

            // 处理 405 错误（反爬触发）
            if (response.status === 405) {
                console.log(`\n[405] Anti-crawl triggered at ${url}`);
                console.log(`[Cooldown] Waiting ${CONFIG.cooldownAfter405 / 1000}s before retry...`);
                await delay(CONFIG.cooldownAfter405);
                
                const updated = await promptNewCookie(405);
                if (updated) {
                    continue; // 用新 Cookie 重试
                }
                throw new Error('ACCESS_DENIED - Failed to update cookie after 405');
            }

            // 处理 429 错误（速率限制）
            if (response.status === 429) {
                const updated = await promptNewCookie(429);
                if (updated) {
                    continue; // 用新 Cookie 重试
                }
                throw new Error('RATE_LIMITED - Failed to update cookie');
            }

            // 处理 403 错误
            if (response.status === 403) {
                console.log(`\n[403] Forbidden - possible cookie issue`);
                const updated = await promptNewCookie(403);
                if (updated) {
                    continue;
                }
                throw new Error('FORBIDDEN - Failed to update cookie');
            }

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const html = await response.text();
            return cheerio.load(html);
        } catch (err) {
            if (err.message.includes('RATE_LIMITED') || err.message.includes('ACCESS_DENIED') || err.message.includes('FORBIDDEN')) {
                throw err;
            }
            if (retryCount < CONFIG.maxRetries) {
                console.log(`[Retry] ${err.message}, retrying... (${retryCount + 1}/${CONFIG.maxRetries})`);
                await delay(CONFIG.retryDelay);
                retryCount++;
                continue;
            }
            throw err;
        }
    }
}

// 主程序
console.log('=== Gitee Project URL Crawler ===');
console.log(`Config: delay=${CONFIG.requestDelay[0]}-${CONFIG.requestDelay[1]}ms, batch=${CONFIG.batchSize}, batchPause=${CONFIG.batchPause / 1000}s`);
console.log('');

// 加载已有结果和进度
const recommend_project_url = loadExistingResults();
const savedProgress = loadProgress();

if (recommend_project_url.length > 0) {
    console.log(`[Resume] Found ${recommend_project_url.length} existing URLs`);
}

// 获取分类列表
const base_url = "https://gitee.com/explore/all?order=starred";
console.log(`[Fetch] Getting categories from ${base_url}...`);
const $doc = await fetchPageWithRetry(base_url);

const recommend_url = [];
$doc(".explore-categories__item a").each((_, element) => {
    const href = $doc(element).attr('href');
    if (href && !href.includes("explore/all")) {
        recommend_url.push(href);
    }
});
console.log(`[Found] ${recommend_url.length} categories\n`);

// 请求计数器
let requestCount = 0;

try {
    for (let catIndex = 0; catIndex < recommend_url.length; catIndex++) {
        const url = recommend_url[catIndex];

        // 从上次进度继续
        let startPage = 1;
        if (savedProgress && savedProgress.currentCategory === url) {
            startPage = savedProgress.currentPage;
            console.log(`[Resume] Continuing from page ${startPage}`);
        }

        let i = startPage;
        while (true) {
            const l = "https://gitee.com" + url + "&page=" + i;
            console.log(`[${catIndex + 1}/${recommend_url.length}] Fetching: ${l}`);

            try {
                const $$doc = await fetchPageWithRetry(l);
                const temp = [];
                $$doc(".project-title h3 a").each((_, element) => {
                    const href = $$doc(element).attr('href');
                    if (href && !recommend_project_url.includes(href)) {
                        temp.push(href);
                    }
                });

                if (temp.length === 0) {
                    console.log(`[Done] No more projects on page ${i}, moving to next category\n`);
                    break;
                }

                recommend_project_url.push(...temp);
                requestCount++;

                // 每批请求后暂停
                if (requestCount % CONFIG.batchSize === 0) {
                    console.log(`\n[Batch] ${requestCount} requests completed, pausing for ${CONFIG.batchPause / 1000}s...\n`);
                    await delay(CONFIG.batchPause);
                }

                // 保存进度
                saveProgress(url, i + 1, recommend_project_url);

                // 定期保存结果
                if (recommend_project_url.length % 50 === 0) {
                    saveResults(recommend_project_url);
                }

                console.log(`[Count] Total URLs: ${recommend_project_url.length}\n`);
                i++;

                // 请求间延迟
                await delay(CONFIG.requestDelay[0], CONFIG.requestDelay[1]);

            } catch (err) {
                console.error(`\n[Error] ${err.message}`);
                throw err;
            }
        }
    }

    console.log('\n=== Crawling Completed ===');
    console.log(`Total URLs collected: ${recommend_project_url.length}`);

} catch (err) {
    console.error(`\n=== Crawling Stopped ===`);
    console.error(`Reason: ${err.message}`);
} finally {
    saveResults(recommend_project_url);
    saveCookiesToFile();
    rl.close();
    console.log(`\nTotal URLs saved: ${recommend_project_url.length}`);
}
