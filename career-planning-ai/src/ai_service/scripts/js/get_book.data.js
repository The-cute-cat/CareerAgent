// @ts-check
// noinspection SpellCheckingInspection

/**
 * 豆瓣图书搜索数据爬取脚本
 * 用于从豆瓣图书搜索页面爬取高评分书籍信息
 */

import fs from 'fs';
import path from 'path';
import readline from 'readline';
import {fileURLToPath} from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 文件路径配置
const RESULT_DIR = path.join(__dirname, 'books_data');
const PROGRESS_FILE = path.join(__dirname, '.get_book_crawl_progress.json');
const ALL_BOOKS_FILE = path.join(RESULT_DIR, 'all_books.json');
const COOKIE_FILE = path.join(__dirname, '.douban_cookies.json');

// 代理配置
const PROXY_URL = "https://cors-proxy-worker.hopecat.dpdns.org/?url=";

// 爬取配置
const CONFIG = {
  baseUrl: 'https://search.douban.com/book/subject_search',
  maxPages: 50,              // 同一个搜索词最多爬50个页面
  maxBooks: 100,             // 最多爬100本评分大于7.5的书
  minRating: 7.5,            // 最低评分阈值
  requestDelay: [4000, 5000], // 请求延迟 4-5秒
  keywordDelay: [6000, 12000], // 关键词之间延迟 6-12秒
  retryDelay: 15000,         // 重试延迟 15秒
  maxRetries: 3,             // 最大重试次数
  cooldownAfterBlock: 30000, // 被拦截后冷却时间 30秒
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

// User-Agent 列表（随机选择，模拟不同浏览器）
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
  // 检查是否有验证码页面
  if (html.includes('验证') && html.includes('code')) return true;
  if (html.includes('captcha')) return true;
  if (html.includes('访问过于频繁')) return true;
  if (html.includes('暂时无法访问')) return true;
  // 检查是否有 __DATA__
  return !html.includes('window.__DATA__');

}

/**
 * 从HTML中提取 window.__DATA__ 数据
 * @param {string} html - HTML内容
 * @returns {object|null} 解析后的数据对象
 */
function extractBookData(html) {
  try {
    const dataMatch = html.match(/window\.__DATA__\s*=\s*(\{[^]*?});\s*window\.__USER__/);
    
    if (!dataMatch || !dataMatch[1]) {
      return null;
    }

  return JSON.parse(dataMatch[1]);
  } catch (error) {
    console.error('解析数据失败:', error.message);
    return null;
  }
}

/**
 * 解析 abstract 字段中的信息
 * @param {string} abstract - abstract字符串
 * @returns {object} 解析后的信息
 */
function parseAbstract(abstract) {
  const result = {
    author: '',
    translator: '',
    publisher: '',
    publish_date: '',
    price: ''
  };
  
  if (!abstract) return result;
  
  const parts = abstract.split(' / ').map(p => p.trim());
  result.author = parts[0] || '';
  
  let publisherIndex = -1;
  
  for (let i = parts.length - 1; i >= 1; i--) {
    const part = parts[i];
    
    if (!result.price && (part.includes('元') || /^\$/.test(part) || /EUR/.test(part) || /^USD/.test(part))) {
      result.price = part;
      continue;
    }
    
    if (!result.publish_date && /^\d{4}/.test(part)) {
      result.publish_date = part;
      continue;
    }
    
    if (publisherIndex === -1 && part.length > 1 && !/^\d{4}/.test(part)) {
      result.publisher = part;
      publisherIndex = i;
      continue;
    }
  }
  
  if (publisherIndex > 1) {
    const translators = parts.slice(1, publisherIndex);
    result.translator = translators.join(' / ');
  }
  
  return result;
}

/**
 * 格式化书籍信息
 */
function formatBookItem(item, keyword, category) {
  if (item.tpl_name !== 'search_subject') {
    return null;
  }
  
  const book = {
    id: item.id,
    title: item.title,
    url: item.url,
    cover_url: item.cover_url,
    abstract: item.abstract || '',
    rating: item.rating ? {
      score: item.rating.value || 0,
      count: item.rating.count || 0
    } : null,
    keyword: keyword,
    category: category,
    crawl_time: new Date().toISOString()
  };
  
  const abstractInfo = parseAbstract(item.abstract);
  Object.assign(book, abstractInfo);
  
  return book;
}

/**
 * 处理搜索结果数据
 */
function processSearchResult(data, keyword, category) {
  if (!data) return null;
  
  const result = {
    query: data.text,
    total: data.total,
    count: data.count,
    start: data.start,
    books: []
  };
  
  if (data.items && Array.isArray(data.items)) {
    data.items.forEach(item => {
      const book = formatBookItem(item, keyword, category);
      if (book) result.books.push(book);
    });
  }
  
  return result;
}

/**
 * 保存爬取进度
 */
function saveProgress(progress) {
  try {
    fs.writeFileSync(PROGRESS_FILE, JSON.stringify(progress, null, 2), 'utf-8');
    console.log(`[Progress] Saved: category=${progress.currentCategoryIndex}, keyword=${progress.currentKeywordIndex}`);
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
 * 加载已爬取的书籍数据
 */
function loadExistingBooks() {
  try {
    if (fs.existsSync(ALL_BOOKS_FILE)) {
      const data = fs.readFileSync(ALL_BOOKS_FILE, 'utf-8');
      return JSON.parse(data);
    }
  } catch (err) {
    console.log('[Books] No existing books found');
  }
  return [];
}

/**
 * 保存书籍数据到JSON
 */
function saveBooksToJson(books) {
  try {
    if (!fs.existsSync(RESULT_DIR)) {
      fs.mkdirSync(RESULT_DIR, { recursive: true });
    }
    fs.writeFileSync(ALL_BOOKS_FILE, JSON.stringify(books, null, 2), 'utf-8');
    console.log(`[Books] Saved ${books.length} books`);
  } catch (err) {
    console.error('[Books] Failed to save:', err);
  }
}

/**
 * 转换为CSV格式
 */
function convertToCSV(books) {
  if (books.length === 0) return '';
  
  const columns = [
    'id', 'title', 'author', 'translator', 'publisher', 
    'publish_date', 'price', 'rating_score', 'rating_count',
    'keyword', 'category', 'url', 'cover_url', 'crawl_time'
  ];
  
  const header = columns.join(',');
  const escapeField = (field) => {
    if (field === null || field === undefined) return '""';
    let str = String(field);
    if (str.includes(',') || str.includes('"') || str.includes('\n')) {
      str = '"' + str.replace(/"/g, '""') + '"';
    }
    return str;
  };
  
  const rows = books.map(book => {
    return columns.map(col => {
      let value;
      if (col === 'rating_score') {
        value = book.rating ? book.rating.score : 0;
      } else if (col === 'rating_count') {
        value = book.rating ? book.rating.count : 0;
      } else {
        value = book[col];
      }
      return escapeField(value);
    }).join(',');
  });
  
  return header + '\n' + rows.join('\n');
}

/**
 * 保存书籍数据到CSV
 */
function saveBooksToCSV(books, category) {
  try {
    if (!fs.existsSync(RESULT_DIR)) {
      fs.mkdirSync(RESULT_DIR, { recursive: true });
    }
    const safeCategory = category.replace(/[\/\\:*?"<>|]/g, '-');
    const filename = `${safeCategory}-${new Date().getTime()}.csv`;
    const filepath = path.join(RESULT_DIR, filename);
    const csv = convertToCSV(books);
    fs.writeFileSync(filepath, '\ufeff' + csv, 'utf-8');
    console.log(`[CSV] Saved ${books.length} books to ${filename}`);
  } catch (err) {
    console.error('[CSV] Failed to save:', err);
  }
}

// 连续无数据计数器
let consecutiveEmptyCount = 0;

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
    
    // 添加Cookie
    if (cookieJar.size > 0) {
      requestHeaders['Cookie'] = getCookieString();
    }
    
    // 使用代理
    const proxyUrl = PROXY_URL + encodeURIComponent(url);
    
    const response = await fetch(proxyUrl, {
      headers: requestHeaders,
      redirect: 'follow'
    });
    
    // 更新Cookie
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
    
    // 检查是否被反爬
    if (isBlocked(html)) {
      console.log('[Block] Detected anti-crawl mechanism');
      consecutiveEmptyCount++;
      
      if (consecutiveEmptyCount >= 3) {
        await promptNewCookie();
        consecutiveEmptyCount = 0;
      }
      
      await delay(CONFIG.cooldownAfterBlock);
      if (retryCount < CONFIG.maxRetries) {
        return fetchPageWithRetry(url, retryCount + 1);
      }
      return null;
    }
    
    consecutiveEmptyCount = 0;
    return html;
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
 * 爬取单个关键词的书籍
 */
async function crawlKeyword(keyword, category, collectedBooks) {
  const newBooks = [];
  const collectedIds = new Set(collectedBooks.map(b => b.id));
  let highRatedCount = 0;
  
  console.log(`\n[Crawl] Starting: "${keyword}" (${category})`);
  
  for (let page = 0; page < CONFIG.maxPages; page++) {
    if (highRatedCount >= CONFIG.maxBooks) {
      console.log(`[Done] Reached max books (${CONFIG.maxBooks})`);
      break;
    }
    
    const start = page * 15;
    const url = `${CONFIG.baseUrl}?search_text=${encodeURIComponent(keyword)}&cat=1001&start=${start}`;
    console.log(`[Fetch] Page ${page + 1}: ${url}`);
    
    const html = await fetchPageWithRetry(url);
    if (!html) {
      console.log(`[Skip] Failed to fetch page ${page + 1}`);
      await delay(CONFIG.requestDelay[0], CONFIG.requestDelay[1]);
      continue;
    }
    
    const rawData = extractBookData(html);
    if (!rawData) {
      console.log(`[Skip] No data extracted`);
      await delay(CONFIG.requestDelay[0], CONFIG.requestDelay[1]);
      continue;
    }
    
    const result = processSearchResult(rawData, keyword, category);
    if (!result || result.books.length === 0) {
      console.log(`[Done] No more books`);
      break;
    }
    
    for (const book of result.books) {
      if (collectedIds.has(book.id)) continue;
      
      const score = book.rating ? book.rating.score : 0;
      if (score >= CONFIG.minRating) {
        newBooks.push(book);
        collectedIds.add(book.id);
        highRatedCount++;
        console.log(`[Found] ${book.title} - ${score}分`);
      }
    }
    
    console.log(`[Page ${page + 1}] ${result.books.length} books, high-rated: ${highRatedCount}`);
    await delay(CONFIG.requestDelay[0], CONFIG.requestDelay[1]);
  }
  
  console.log(`[Complete] "${keyword}": ${highRatedCount} books`);
  return newBooks;
}

// 搜索关键词配置
const dbSearchKeywords = [
  {
    category: "后端开发",
    keywords: [
      "Java入门", "Java核心技术", "Java并发编程", "Java虚拟机", "JVM底层原理",
      "Spring Boot实战", "Spring Cloud微服务", "Spring源码解析",
      "Go语言编程", "Go并发编程", "Go Web实战",
      "Python基础教程", "Python高级编程", "Flask Web开发", "Django实战",
      "Node.js开发指南", "Node.js实战"
    ]
  },
  {
    category: "前端开发",
    keywords: [
      "HTML与CSS入门", "JavaScript高级程序设计", "ES6标准入门",
      "Vue.js实战", "Vue3源码解析", "Vue组件设计",
      "React设计原理", "React Hooks实战", "Next.js全栈开发",
      "前端性能优化", "前端工程化", "Webpack深入浅出", "TypeScript实战"
    ]
  },
  {
    category: "数据库与缓存",
    keywords: [
      "MySQL必知必会", "MySQL性能调优", "MySQL底层原理", "高性能MySQL",
      "Redis设计与实现", "Redis实战", "Redis源码剖析",
      "MongoDB权威指南", "Elasticsearch实战", "图数据库入门"
    ]
  },
  {
    category: "人工智能与数据科学",
    keywords: [
      "机器学习入门", "机器学习实战", "统计学习方法",
      "深度学习入门", "PyTorch深度学习", "TensorFlow实战",
      "大语言模型应用开发", "LLM微调", "Prompt工程指南",
      "自然语言处理", "计算机视觉", "推荐系统实战",
      "Python数据分析", "Pandas数据处理", "数据挖掘"
    ]
  },
  {
    category: "架构与系统设计",
    keywords: [
      "大型网站技术架构", "高并发系统设计", "分布式系统原理",
      "微服务架构设计", "领域驱动设计", "微服务治理",
      "设计模式", "代码整洁之道", "重构改善既有代码设计",
      "系统架构师教程", "云原生架构"
    ]
  },
  {
    category: "运维云计算与中间件",
    keywords: [
      "Linux命令行大全", "鸟哥的Linux私房菜", "Linux底层原理",
      "Docker技术入门与实战", "Kubernetes权威指南", "K8s生产级实践",
      "Nginx高性能Web服务器", "RabbitMQ实战", "Kafka权威指南"
    ]
  },
  {
    category: "计算机基础",
    keywords: [
      "数据结构与算法分析", "算法导论", "剑指Offer", "LeetCode刷题",
      "计算机网络自顶向下", "TCP/IP详解", "图解HTTP",
      "深入理解计算机系统", "操作系统导论", "Linux内核设计与实现"
    ]
  }
];

/**
 * 主爬取函数
 */
async function main() {
  console.log('=== 豆瓣图书爬虫 ===');
  console.log(`代理: ${PROXY_URL ? '已启用' : '未使用'}`);
  console.log(`配置: 最低评分=${CONFIG.minRating}, 每关键词最多${CONFIG.maxBooks}本`);
  console.log(`延迟: 请求${CONFIG.requestDelay[0]}-${CONFIG.requestDelay[1]}ms, 关键词${CONFIG.keywordDelay[0]}-${CONFIG.keywordDelay[1]}ms`);
  console.log('');
  
  // 尝试加载Cookie
  if (!loadCookiesFromFile()) {
    console.log('[Cookie] 未找到Cookie文件，将使用无Cookie模式');
    console.log('[Cookie] 建议首次运行时输入Cookie以获得更好的效果\n');
    await promptNewCookie();
  }
  
  // 加载已有数据
  const allBooks = loadExistingBooks();
  console.log(`[Load] Found ${allBooks.length} existing books`);
  
  // 加载进度
  const savedProgress = loadProgress();
  let startCategoryIndex = 0;
  let startKeywordIndex = 0;
  
  if (savedProgress) {
    startCategoryIndex = savedProgress.currentCategoryIndex || 0;
    startKeywordIndex = savedProgress.currentKeywordIndex || 0;
    console.log(`[Resume] Starting from category ${startCategoryIndex}, keyword ${startKeywordIndex}`);
  }
  
  // 按分类爬取
  for (let catIdx = startCategoryIndex; catIdx < dbSearchKeywords.length; catIdx++) {
    const categoryData = dbSearchKeywords[catIdx];
    const category = categoryData.category;
    const categoryBooks = [];
    
    console.log(`\n${'='.repeat(50)}`);
    console.log(`[Category ${catIdx + 1}/${dbSearchKeywords.length}] ${category}`);
    console.log('='.repeat(50));
    
    const keywordStart = (catIdx === startCategoryIndex) ? startKeywordIndex : 0;
    
    for (let kwIdx = keywordStart; kwIdx < categoryData.keywords.length; kwIdx++) {
      const keyword = categoryData.keywords[kwIdx];
      
      saveProgress({
        currentCategoryIndex: catIdx,
        currentKeywordIndex: kwIdx,
        totalBooks: allBooks.length,
        timestamp: new Date().toISOString()
      });
      
      const newBooks = await crawlKeyword(keyword, category, allBooks);
      
      if (newBooks.length > 0) {
        allBooks.push(...newBooks);
        categoryBooks.push(...newBooks);
        
        if (allBooks.length % 20 === 0) {
          saveBooksToJson(allBooks);
          saveCookiesToFile();
        }
      }
      
      // 关键词之间的延迟
      if (kwIdx < categoryData.keywords.length - 1) {
        await delay(CONFIG.keywordDelay[0], CONFIG.keywordDelay[1]);
      }
    }
    
    if (categoryBooks.length > 0) {
      saveBooksToCSV(categoryBooks, category);
    }
  }
  
  saveBooksToJson(allBooks);
  saveCookiesToFile();
  rl.close();
  
  console.log('\n=== 爬取完成 ===');
  console.log(`总共收集: ${allBooks.length} 本书籍`);
  console.log(`数据保存在: ${RESULT_DIR}`);
}

// 运行主函数
main().catch(err => {
  console.error('\n=== 爬取出错 ===');
  console.error(err);
  rl.close();
});

export {
  extractBookData,
  parseAbstract,
  formatBookItem,
  processSearchResult,
  crawlKeyword,
  main
};
