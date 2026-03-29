"""
平台URL解析器
解析用户输入的代码托管平台URL，识别平台和用户名
"""
import re


class PlatformURLParser:
    """解析用户输入的代码托管平台URL，识别平台和用户名"""

    PLATFORM_PATTERNS = {
        "github": {
            "patterns": [
                r"https?://(?:www\.)?github\.com/([a-zA-Z0-9\-]+)/?(?:$|tab)",
                r"https?://(?:www\.)?github\.com/([a-zA-Z0-9\-]+)/?$"
            ],
            "api_base": "https://api.github.com/users/{username}",
            "repos_api": "https://api.github.com/users/{username}/repos",
        },
        "gitee": {
            "patterns": [
                r"https?://(?:www\.)?gitee\.com/([a-zA-Z0-9\-_]+)/?(?:$|tab)",
                r"https?://(?:www\.)?gitee\.com/([a-zA-Z0-9\-_]+)/?$"
            ],
            "api_base": "https://gitee.com/api/v5/users/{username}",
            "repos_api": "https://gitee.com/api/v5/users/{username}/repos"
        }
    }

    def __init__(self):
        self.platform = None
        self.username = None

    def parse(self, url: str) -> dict:
        """
        解析URL，返回平台和用户名

        Args:
            url: 用户输入的URL

        Returns:
            {"platform": "github/gitee", "username": "xxx", "valid": bool, "api_base": str, "repos_api": str}
        """
        url = url.strip().rstrip("/")

        for platform, config in self.PLATFORM_PATTERNS.items():
            for pattern in config["patterns"]:
                match = re.match(pattern, url)
                if match:
                    return {
                        "platform": platform,
                        "username": match.group(1),
                        "valid": True,
                        "api_base": config["api_base"].format(username=match.group(1)),
                        "repos_api": config["repos_api"].format(username=match.group(1))
                    }

        return {"platform": None, "username": None, "valid": False}


platform_url_parser = PlatformURLParser()
