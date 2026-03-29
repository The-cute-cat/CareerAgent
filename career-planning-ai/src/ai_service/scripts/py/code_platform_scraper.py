"""
代码平台数据采集器
支持 GitHub API 和 Gitee API
"""
import time
import requests


class CodePlatformScraper:
    """
    代码平台数据采集器
    支持 GitHub API 和 Gitee API
    """

    def __init__(self, github_token: str | None = None, gitee_token: str | None = None):
        self.github_headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "CareerGuide-Bot/1.0"
        }
        if github_token:
            self.github_headers["Authorization"] = f"token {github_token}"

        self.gitee_params = {}
        if gitee_token:
            self.gitee_params["access_token"] = gitee_token

    # ==================== GitHub 数据采集 ====================

    def fetch_github_profile(self, username: str) -> dict:
        """获取GitHub用户基本信息"""
        url = f"https://api.github.com/users/{username}"
        resp = requests.get(url, headers=self.github_headers, timeout=10)
        if resp.status_code != 200:
            raise Exception(f"GitHub API 请求失败: {resp.status_code} - {resp.text}")
        data = resp.json()
        return {
            "username": data.get("login"),
            "avatar_url": data.get("avatar_url"),
            "name": data.get("name"),
            "bio": data.get("bio"),
            "location": data.get("location"),
            "company": data.get("company"),
            "blog": data.get("blog"),
            "public_repos": data.get("public_repos", 0),
            "followers": data.get("followers", 0),
            "following": data.get("following", 0),
            "created_at": data.get("created_at"),
            "total_private_repos": data.get("total_private_repos", 0),
            "account_years": self._calc_years(data.get("created_at"))
        }

    def fetch_github_repos(self, username: str, sort: str = "updated", per_page: int = 30) -> list:
        """
        获取GitHub用户仓库列表

        Args:
            username: 用户名
            sort: updated/stars/created
            per_page: 每页数量（最多100）
        """
        url = f"https://api.github.com/users/{username}/repos"
        params = {
            "sort": sort,
            "direction": "desc",
            "per_page": per_page,
            "type": "owner"
        }
        resp = requests.get(url, headers=self.github_headers, params=params, timeout=15)
        if resp.status_code != 200:
            raise Exception(f"GitHub Repos API 请求失败: {resp.status_code}")

        repos = []
        for repo in resp.json():
            repos.append({
                "repo_name": repo.get("name"),
                "full_name": repo.get("full_name"),
                "description": repo.get("description"),
                "language": repo.get("language"),
                "languages_url": repo.get("languages_url"),
                "stargazers_count": repo.get("stargazers_count", 0),
                "forks_count": repo.get("forks_count", 0),
                "open_issues_count": repo.get("open_issues_count", 0),
                "watchers_count": repo.get("watchers_count", 0),
                "size": repo.get("size", 0),
                "created_at": repo.get("created_at"),
                "updated_at": repo.get("updated_at"),
                "pushed_at": repo.get("pushed_at"),
                "fork": repo.get("fork", False),
                "has_readme": None,
                "has_wiki": repo.get("has_wiki", False),
                "has_pages": repo.get("has_pages", False),
                "topics": repo.get("topics", []),
                "license": repo.get("license", {}).get("spdx_id") if repo.get("license") else None
            })
        return repos

    def fetch_github_repo_languages(self, username: str, repo_name: str) -> dict:
        """获取单个仓库的语言构成"""
        url = f"https://api.github.com/repos/{username}/{repo_name}/languages"
        resp = requests.get(url, headers=self.github_headers, timeout=10)
        if resp.status_code == 200:
            return resp.json()
        return {}

    # ==================== Gitee 数据采集 ====================

    def fetch_gitee_profile(self, username: str) -> dict:
        """获取Gitee用户基本信息"""
        url = f"https://gitee.com/api/v5/users/{username}"
        params = self.gitee_params.copy()
        resp = requests.get(url, params=params, timeout=10)
        if resp.status_code != 200:
            raise Exception(f"Gitee API 请求失败: {resp.status_code}")
        data = resp.json()
        return {
            "username": data.get("login"),
            "avatar_url": data.get("avatar_url"),
            "name": data.get("name"),
            "bio": data.get("bio"),
            "location": data.get("location"),
            "company": data.get("company"),
            "blog": data.get("blog"),
            "public_repos": data.get("public_repos", 0),
            "followers": data.get("followers", 0),
            "following": data.get("following", 0),
            "created_at": data.get("created_at"),
            "account_years": self._calc_years(data.get("created_at"))
        }

    def fetch_gitee_repos(self, username: str, page: int = 1, per_page: int = 30) -> list:
        """获取Gitee用户仓库列表"""
        url = f"https://gitee.com/api/v5/users/{username}/repos"
        params = {
            **self.gitee_params,
            "sort": "updated",
            "direction": "desc",
            "page": page,
            "per_page": per_page,
            "type": "owner"
        }
        resp = requests.get(url, params=params, timeout=15)
        if resp.status_code != 200:
            raise Exception(f"Gitee Repos API 请求失败: {resp.status_code}")

        repos = []
        for repo in resp.json():
            repos.append({
                "repo_name": repo.get("name"),
                "full_name": repo.get("full_name"),
                "description": repo.get("description"),
                "language": repo.get("language"),
                "stargazers_count": repo.get("stargazers_count", 0),
                "forks_count": repo.get("forks_count", 0),
                "open_issues_count": repo.get("open_issues_count", 0),
                "size": repo.get("size", 0),
                "created_at": repo.get("created_at"),
                "updated_at": repo.get("updated_at"),
                "pushed_at": repo.get("pushed_at"),
                "fork": repo.get("fork", False),
                "homepage": repo.get("homepage"),
                "license": repo.get("license", {}).get("spdx_id") if repo.get("license") else None
            })
        return repos

    # ==================== 工具方法 ====================

    @staticmethod
    def _calc_years(created_at: str | None) -> float:
        """计算账号注册年限"""
        if not created_at:
            return 0
        try:
            created = time.strptime(created_at[:10], "%Y-%m-%d")
            now = time.localtime()
            years = (time.mktime(now) - time.mktime(created)) / (365.25 * 24 * 3600)
            return round(years, 1)
        except Exception as e:
            print(f"计算账号注册年限失败: {e}")
            return 0

code_platform_scraper = CodePlatformScraper()
