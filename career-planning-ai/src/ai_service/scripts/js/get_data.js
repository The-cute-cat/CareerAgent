// @ts-check
// noinspection SpellCheckingInspection

import * as cheerio from 'cheerio';
import * as fs from 'fs';

const proxy_url = "";//https://cors-proxy-worker.hopecat.dpdns.org/?url=";

// 延迟函数，支持随机延迟
function delay(minMs, maxMs = null) {
    const ms = maxMs ? Math.floor(Math.random() * (maxMs - minMs + 1)) + minMs : minMs;
    return new Promise(resolve => setTimeout(resolve, ms));
}

// 请求配置
const headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
};

/**
 * @param {string} url
 * @returns {Promise<CheerioAPI>}
 */
async function fetchPage(url) {
    const response = await fetch(proxy_url + url, {
        headers,
        redirect: 'follow',
    });
    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }
    const html = await response.text();
    return cheerio.load(html);
}

const html_url = fs.existsSync('./temp/csv/url.txt') ? fs.readFileSync('./temp/csv/url.txt', 'utf8').split('\n') : [];
const fail_url = [];

async function get_data(url) {
    const allData = [];
    let job_id = ""
    let $doc;
    try {
        $doc = await fetchPage(url);
    } catch (e) {
        console.error(e, "url:" + url);
        fail_url.push(url);
        return {
            data: [],
            job_id: ""
        };
    }
    const t = $doc("head title").text().trim();
    job_id = t.slice(0, t.indexOf("招聘")).replace("「", "");
    const urls = [];
    $doc(".pagination__pages .soupager .soupager__index").each((index, item) => {
        const url = $doc(item).attr('href');
        if (url) {
            urls.push(url);
        }
    });
    for (const url of urls) {
        await delay(600, 1000);
        let $$doc;
        try {
            $$doc = await fetchPage(url);
        } catch (e) {
            console.error(e, "url:" + url);
            fail_url.push(url);
            continue;
        }
        const links = [];
        $$doc(".jobinfo__top a").each((index, item) => {
            const link = $$doc(item).attr('href');
            if (link) {
                links.push(link);
            }
        });
        for (const link of links) {
            if (html_url.includes(link)) {
                continue;
            }
            html_url.push(link);
            await delay(800, 1200);
            let $$$doc;
            try {
                $$$doc = await fetchPage(link);
            } catch (e) {
                console.error(e, "url:" + link);
                fail_url.push(link);
                continue;
            }
            const itemData = parse_content($$$doc);
            itemData["url"] = link;
            allData.push(itemData);
            console.log(itemData);
        }
    }
    return {
        data: allData,
        job_id: job_id
    };
}

function convertToCSV(data) {
    if (data.length === 0) return '';

    const columns = ['url', 'job', 'salary', 'city', 'district', 'experience', 'education',
        'job_type', 'headcount', 'employer_tag', 'skills_item',
        'describtion', 'address', 'update_time'];

    const header = columns.join(',');
    const escapeField = (field) => {
        if (field === null || field === undefined) return '""';
        let str = String(field);
        if (str.includes(',') || str.includes('"') || str.includes('\n')) {
            str = '"' + str.replace(/"/g, '""') + '"';
        }
        return str;
    };

    const rows = data.map(item => {
        const row = columns.map(col => {
            let value = item[col];
            if (Array.isArray(value)) {
                value = value.join(';');
            }
            return escapeField(value);
        });
        return row.join(',');
    });

    return header + '\n' + rows.join('\n');
}

/**
 * @param {CheerioAPI} $doc
 * @returns {Record<string, string | string[]>}
 */
function parse_content($doc) {
    const result = {};
    result["update_time"] = $doc(".summary-plane__time").text().replace("更新于 ", "");
    if (result["update_time"].includes("今天")) {
        result["update_time"] = result["update_time"].replace("今天", new Date().toLocaleDateString())
    }
    result["employer_tag"] = [];
    $doc(".best-employer-tag__tag-text").each((index, item) => {
        result["employer_tag"].push($doc(item).text().trim());
    });
    result["job"] = $doc(".summary-plane__title").text();
    result["salary"] = $doc(".summary-plane__salary").text();
    const infoItems = $doc(".summary-plane__info li");
    infoItems.each((index, item) => {
        const $item = $doc(item);
        const link = $item.find("a");
        const span = $item.find("span");

        if (link.length > 0) {
            // 城市
            result["city"] = link.text().trim();
            if (span.length > 0) {
                result["district"] = span.text().trim();
            }
        } else {
            const text = $item.text().trim();
            if (text.includes("年") || text.includes("经验")) {
                result["experience"] = text;
            } else if (text.includes("本科") || text.includes("硕士") || text.includes("博士") || text.includes("大专") || text.includes("学历") || text.includes("高中") || text.includes("中专")) {
                result["education"] = text;
            } else if (text.includes("全职") || text.includes("兼职") || text.includes("实习")) {
                result["job_type"] = text;
            } else if (text.includes("招")) {
                result["headcount"] = text;
            }
        }
    });
    result["skills_item"] = [];
    $doc(".describtion__skills-content span").each((index, item) => {
        const skill = $doc(item).text().trim();
        if (skill) {
            result["skills_item"].push(skill);
        }
    });
    result["describtion"] = $doc(".describtion__detail-content").text();
    result["address"] = $doc(".job-address__content-text").text();
    return result;
}

function saveToCSV(data, filepath = 'temp/csv') {
    const csv = convertToCSV(data["data"]);
    const safeJobId = data["job_id"].replace(/[\/\\:*?"<>|]/g, '-');
    const filename = `${safeJobId}-${new Date().getTime()}.csv`;
    if (!fs.existsSync(filepath)) {
        fs.mkdirSync(filepath);
    }
    fs.writeFileSync(filepath + '/' + filename, '\ufeff' + csv, 'utf-8'); // \ufeff 添加BOM以支持Excel正确显示中文
    console.log(`数据已保存到 ${filepath + '/' + filename}，共 ${data["data"].length} 条记录`);
}

const list = ["kw01500O80EO062", "kw00N00JG08K058", "kw011G08O",
    "kw011G0BO08C02M01B", "kw01800I00A0", "kw01800U80EG06G03F01N0", "kw013G0I80AC",
    "kw013G0RO0DG06203E01JG", "kw01200P80DG07003801KG", "kw01700RO0CG06A01E01L00SO",
    "kw01B00GG", "kw012G0SG0DG06203E01JG", "kw01900T80C807I", "kw01800P80E806O", "kwA5K6G22TSLT0MNG8",
    "kwBL652PAV1U7MUJNMBS057K8", "kwG4D6EB2V019T2", "kwIS06OGII0PJP0NF5F85LS20", "kwI56NURJRK5Q0C",
    "kwFJTNTNSMOPH10", "kw9Q8ON8BRIS", "kwHFMPFSO05U4SD64H00NLDVIVC9FG0KUH", "kw012G0KG0A1H80PPF00NLT53L50",
    "kw01400L009K04O01L"
    /*]
    const list1 = [*/
    , "kw01500O80EO06202J01HG0SG0D407003K", "kwA96NLRQV019T2", "kw010G0RG0CG07403F01KG0P0",
    "kw01KG0JO0AC", "kw01AG0CO08G", "kw01AG0H806G", "kw011G0JO08C04U02J00P00H00B0", "kwBG7MSE321TFG0KUH",
    "kwBUN4VOAV019T2", "kwBG7NK2QUHTFG0KUH", "kwF7TL5A2V019T2", "kwJOVO96AV019T2NF5F85LS20",
    "kwCLO66RJ32PHPG", "kwCLO66RIV019T2", "kwCLO66RKHOUBCC", "kwCLO66RIEQDF96", "kwCLO66RIUIDFG0KUH",
    "kwCLO66RJ7MPJO8NG8", "kw012G0L009HEUAUGBBO40", "kw01100I8", "kwE8M8CQO", "kwCLO66RII0PJP0NG8",
    "kwI78OF3B5E1HMSKG6CU80", "kw9OQ5T2J5E1HMSKG6CU80"
    /*]
    const list2 = [*/
    , "kwCST5CQ49OQ4SI", "kwARV51JSBOP92M", "kwG7L72DKBTM500M84EG30", "kwHFMPFSSBOP92M", "kwCST5CQ2EN9TPER6L",
    "kwBFU84AJRITMDA", "kwCST5CQ2RCP760", "kwDNOLT9IRCP760", "kwCEK86K3RITMDA", "kwCGE7Q8JRITMDA",
    "kwAF6MMEKBP002V66ECEJNN5RCQK", "kwFEBMPLATSLT0MNG8", "kwCPT81VCQFQD7CV7RFRFLRPBQ1DF0G",
    "kwCUR6F12U10", "kwF0A57KBUPTQ0C", "kw014G0L32G1JIU01FF0A57KB07DRD2", "kw011G0L009S", "kw011G0I809S",
    "kwHTNKTTJD9E5TA", "kwAAFO1VBD9E5TA", "kwG7L55A2J2PMKN2UL", "kwDL5ONLAV019T2", "kwC0JO1VBD9E5TA", "kwF7TL5A3QTTMKN2UL"
    /*]
    const list3 = [*/
    , "kwDOBP03RD9E5TA", "kwDOS643RD9E5TA", "kwF1M4TTJD9E5TA", "kwI0D4VOBD9E5TA", "kwCNG4TEJ779VC9265DL5ONL8",
    "kwDL5ONLATSLT0MNG8", "kwDL5ONLBUPTQ0C", "kwHV87TT2TSLT0MNG8", "kwHV87TT2V019T2NF5F85LS20", "kwHV87TT307DRD2",
    "kwFJTNTNQTSLT0MNG8", "kwFT8NTN2TSLT0MNG8", "kwFT8NTN4FQ1VF8", "kwFT8NTN2FS5G6UMS9A5K5RPBQ1DF0G", "kwFJTNTNQRH58MG",
    "kwFJTNTNRRK5Q0CL2O", "kwFT8KU62TSLT0MNG8", "kw01200GG084", "kw01400P80DG07003401IG0SO0DC", "kw012G0KG0A1DPSPDTJ1V9BRG",
    "kw014G0L32G1JIUP9FCC0G", "kw014G0L4D528SUUT1EG30", "kw9VGM0RR2G1JIUJGJAHC0", "kw9VGM0RR2G1JIUVMFEG300BQE7DTQ2"
    /*]
    const list4 = [*/
    , "kwD03L3HIJ2PEUAUGBBO40", "kwEEO5EEIUIHQIGNF5F85LS27V1004C021012VU28", "kwHEV5I1RUUHHA8NF5F85LS20",
    "kwHEGNN5R779S6OJNMFRQ6592TSLT0MNG8", "kwAKN583J2G1JIUP9FCC0G", "kwAKN54JB2G1JIUP9FCC0G", "kwH7HL3CR5N5K4GNF5F85LS20",
    "kwCA06EBR55THG2NF5F85LS20", "kwBEF6BFCOFQAUS", "kwBEF6BFATSLT0MNG8"
]
for (const item of list) {
    const data = await get_data(`https://www.zhaopin.com/sou/jl489/${item}`);
    try {
        saveToCSV(data)
    } catch (e) {
        fs.writeFileSync(`temp/csv/${item}.json`, JSON.stringify(data, null, 2), 'utf-8');
        console.error(e, "保存失败");
    }
}
if (!fs.existsSync("temp/csv")) {
    fs.mkdirSync("temp/csv");
}
fs.writeFileSync(`temp/csv/fail_url.txt`, fail_url.join("\n"), 'utf-8');
fs.writeFileSync(`temp/csv/url.txt`, html_url.join("\n"), 'utf-8');

