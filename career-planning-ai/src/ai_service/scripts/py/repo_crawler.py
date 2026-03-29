import asyncio

import requests
import base64
import re
import time
import json
from urllib.parse import urlparse

from ai_service.agents.common_agent import common_agent
from ai_service.services.prompt_loader import prompt_loader

# noinspection SpellCheckingInspection
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/vnd.github.v3+json"  # GitHub API 要求
}


# 如果有 GitHub Token，可以取消注释下面这行，能大幅提高访问速率限制（从60次/小时提升到5000次/小时）
# HEADERS["Authorization"] = "token YOUR_GITHUB_TOKEN_HERE"

def clean_markdown(text):
    """
    清洗 Markdown 文本，去掉特殊符号、链接、图片标签，
    保留纯文本语义，适合向量化
    """
    if not text:
        return ""
    text = re.sub(r'!\[.*?]\(.*?\)', '', text)
    text = re.sub(r'\[([^]]+)]\([^)]+\)', r'\1', text)
    text = re.sub(r'[#*`>\-]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def parse_repo_url(url):
    """从 URL 中提取 owner 和 repo 名"""
    path = urlparse(url).path.strip('/').split('/')
    if len(path) >= 2:
        return path[0], path[1]
    return None, None


def parse_ai_response(ai_response: str) -> dict:
    """解析 AI 返回的 JSON 数据，提取结构化字段"""
    default_result = {
        "summary": "",
        "tech_tags": [],
        "use_cases": [],
        "difficulty": "进阶",
        "business_domains": []
    }

    if not ai_response:
        return default_result

    try:
        # 尝试提取 JSON 块（可能被 ```json 包裹）
        json_str = ai_response
        if "```json" in ai_response:
            json_str = ai_response.split("```json")[1].split("```")[0].strip()
        elif "```" in ai_response:
            json_str = ai_response.split("```")[1].split("```")[0].strip()

        result = json.loads(json_str)
        return {
            "summary": result.get("summary", ""),
            "tech_tags": result.get("tech_tags", []),
            "use_cases": result.get("use_cases", []),
            "difficulty": result.get("difficulty", "进阶"),
            "business_domains": result.get("business_domains", [])
        }
    except Exception as e:
        print(f"  [警告] 解析 AI 响应失败: {e}，使用原始文本作为 summary")
        return {**default_result, "summary": ai_response}


async def fetch_readme_content(api_url, owner, repo):
    """通过 API 获取 README 的纯文本内容并 AI 分析提取结构化信息"""
    readme_api_url = f"{api_url}/repos/{owner}/{repo}/readme"
    try:
        resp = requests.get(readme_api_url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            content_base64 = resp.json().get('content', '')
            content = base64.b64decode(content_base64).decode('utf-8', errors='ignore')
            clean_text = clean_markdown(content)
            prompt_text = prompt_loader.readme_summary.format(content=clean_text)
            ai_response = await common_agent.get_answer(prompt_text)
            return parse_ai_response(ai_response)
    except Exception as e:
        print(f"  [警告] 获取 README 失败: {e}")
    return parse_ai_response("")


async def crawl_github(url):
    """爬取 GitHub 仓库"""
    owner, repo = parse_repo_url(url)
    if not owner or not repo:
        return None

    api_url = "https://api.github.com"
    repo_url = f"{api_url}/repos/{owner}/{repo}"

    try:
        resp = requests.get(repo_url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            print(f"  ✓ 成功获取 GitHub: {data.get('full_name')}")

            # 获取 README AI 分析结果
            ai_result = await fetch_readme_content(api_url, owner, repo)

            # 统一 license 字段处理
            license_info = None
            if data.get('license') and isinstance(data.get('license'), dict):
                license_info = data['license'].get('spdx_id')

            # 组装用于向量数据库的数据结构
            vector_db_record = {
                "id": f"github_{owner}_{repo}",
                "url": url,
                "content": f"项目名称：{data.get('name')}。\n项目简介：{data.get('description') or '无'}。\n详细说明：{ai_result['summary']}",
                "metadata": {
                    # 基础信息
                    "source": "github",
                    "name": data.get('name'),
                    "full_name": data.get('full_name'),
                    "description": data.get('description'),
                    "language": data.get('language'),
                    "license": license_info,
                    # 分类标签
                    "topics": data.get('topics', []),
                    "tech_tags": ai_result['tech_tags'],
                    "use_cases": ai_result['use_cases'],
                    "business_domains": ai_result['business_domains'],
                    "difficulty": ai_result['difficulty'],
                    # 热度指标
                    "stars": data.get('stargazers_count', 0),
                    "forks": data.get('forks_count', 0),
                    # 活跃度指标
                    "open_issues": data.get('open_issues_count', 0),
                    "last_updated": data.get('updated_at'),
                    "created_at": data.get('created_at')
                }
            }
            return vector_db_record
        else:
            print(f"  ✗ GitHub API 返回错误: {resp.status_code} - {url}")
    except Exception as e:
        print(f"  ✗ 请求 GitHub 异常: {e}")
    return None


async def crawl_gitee(url):
    """爬取 Gitee 仓库"""
    owner, repo = parse_repo_url(url)
    if not owner or not repo:
        return None

    api_url = "https://gitee.com/api/v5"
    repo_url = f"{api_url}/repos/{owner}/{repo}"

    try:
        resp = requests.get(repo_url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            print(f"  ✓ 成功获取 Gitee: {data.get('full_name')}")

            # 获取 README AI 分析结果
            ai_result = await fetch_readme_content(api_url, owner, repo)

            # Gitee license 处理
            license_info = None
            if data.get('license'):
                if isinstance(data.get('license'), dict):
                    license_info = data['license'].get('name')
                else:
                    license_info = data.get('license')

            # 组装用于向量数据库的数据结构
            vector_db_record = {
                "id": f"gitee_{owner}_{repo}",
                "url": url,
                "content": f"项目名称：{data.get('name')}。\n项目简介：{data.get('description') or '无'}。\n详细说明：{ai_result['summary']}",
                "metadata": {
                    # 基础信息
                    "source": "gitee",
                    "name": data.get('name'),
                    "full_name": data.get('full_name'),
                    "description": data.get('description'),
                    "language": data.get('language'),
                    "license": license_info,
                    # 分类标签
                    "topics": data.get('topics', []),
                    "tech_tags": ai_result['tech_tags'],
                    "use_cases": ai_result['use_cases'],
                    "business_domains": ai_result['business_domains'],
                    "difficulty": ai_result['difficulty'],
                    # 热度指标
                    "stars": data.get('stargazers_count', 0),
                    "forks": data.get('forks_count', 0),
                    # 活跃度指标
                    "open_issues": data.get('open_issues_count', 0),
                    "last_updated": data.get('updated_at'),
                    "created_at": data.get('created_at')
                }
            }
            return vector_db_record
        else:
            print(f"  ✗ Gitee API 返回错误: {resp.status_code} - {url}")
    except Exception as e:
        print(f"  ✗ 请求 Gitee 异常: {e}")
    return None


async def main():
    # 待爬取的 URL 列表
    url_list = [
        "https://github.com/Snailclimb/interview-guide",
        "https://github.com/itwanger/PaiAgent",
        "https://gitee.com/xiaonuobase/snowy",
        "https://gitee.com/y_project/RuoYi",
        "https://github.com/elunez/eladmin",
        "https://github.com/macrozheng/mall",
        "https://gitee.com/kekingcn/file-online-preview"
    ]

    results = []

    print(f"开始爬取，共 {len(url_list)} 个仓库...\n")
    for url in url_list:
        if "github.com" in url:
            result = await crawl_github(url)
        elif "gitee.com" in url:
            result = await crawl_gitee(url)
        else:
            print(f"  ✗ 不支持的域名: {url}")
            continue

        if result:
            results.append(result)

        # 礼貌性延时，防止触发 IP 限制 (尤其是 GitHub，没 Token 的话限制 60次/小时)
        time.sleep(1.5)

        # 保存为 JSON 文件，后续可直接读取插入向量库
    output_file = "./../temp/repo_data_for_vector_db.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 爬取完成！成功 {len(results)} 个，数据已保存至 {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
