"""
代码能力评估器
整合特征提取、AI分析、综合评估完整流程
"""
import asyncio
import json
from collections import Counter
from datetime import datetime

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

from ai_service.services.prompt_loader import prompt_loader
from config import settings
from ai_service.scripts.py.platform_url_parser import platform_url_parser
from ai_service.scripts.py.code_platform_scraper import code_platform_scraper


class FeatureExtractor:
    """
    特征提取器
    将原始API数据转化为结构化特征
    """

    def __init__(self, profile: dict, repos: list, platform: str = "github"):
        self.profile = profile
        self.repos = repos
        self.platform = platform
        self.features = {}

    def extract_all(self) -> dict:
        """提取全部特征"""
        self._extract_basic_features()
        self._extract_repo_features()
        self._extract_language_features()
        self._extract_activity_features()
        self._extract_quality_features()
        self._calculate_composite_score()
        return self.features

    def _extract_basic_features(self):
        """提取账号基础信息"""
        self.features["basic"] = {
            "platform": self.platform,
            "username": self.profile.get("username"),
            "account_years": self.profile.get("account_years", 0),
            "total_public_repos": self.profile.get("public_repos", 0),
            "followers": self.profile.get("followers", 0),
            "following": self.profile.get("following", 0),
            "has_bio": bool(self.profile.get("bio")),
            "has_company": bool(self.profile.get("company")),
            "has_location": bool(self.profile.get("location")),
        }

    def _extract_repo_features(self):
        """提取仓库统计特征"""
        original_repos = [r for r in self.repos if not r.get("fork", False)]

        total_stars = sum(r.get("stargazers_count", 0) for r in original_repos)
        total_forks = sum(r.get("forks_count", 0) for r in original_repos)
        avg_stars = round(total_stars / max(len(original_repos), 1), 1)

        small_repos = [r for r in original_repos if r.get("size", 0) < 100]
        medium_repos = [r for r in original_repos if 100 <= r.get("size", 0) < 1000]
        large_repos = [r for r in original_repos if r.get("size", 0) >= 1000]

        repos_with_desc = [r for r in original_repos if r.get("description")]
        desc_ratio = round(len(repos_with_desc) / max(len(original_repos), 1) * 100, 1)

        repos_with_license = [r for r in original_repos if r.get("license")]
        license_ratio = round(len(repos_with_license) / max(len(original_repos), 1) * 100, 1)

        starred_repos = [r for r in original_repos if r.get("stargazers_count", 0) > 0]
        popular_repos = [r for r in original_repos if r.get("stargazers_count", 0) >= 50]

        self.features["repo"] = {
            "original_repo_count": len(original_repos),
            "forked_repo_count": len(self.repos) - len(original_repos),
            "total_stars": total_stars,
            "total_forks": total_forks,
            "avg_stars_per_repo": avg_stars,
            "max_star_repo": max((r.get("stargazers_count", 0) for r in original_repos), default=0),
            "repos_starred": len(starred_repos),
            "repos_popular": len(popular_repos),
            "small_repos": len(small_repos),
            "medium_repos": len(medium_repos),
            "large_repos": len(large_repos),
            "description_ratio": desc_ratio,
            "license_ratio": license_ratio,
            "top_repos": sorted(original_repos, key=lambda x: x.get("stargazers_count", 0), reverse=True)[:5]
        }

    def _extract_language_features(self):
        """提取编程语言使用特征"""
        languages = [r.get("language") for r in self.repos if r.get("language")]
        lang_counter = Counter(languages)
        total = sum(lang_counter.values())

        main_languages = [
            {"language": lang, "count": count, "ratio": round(count / max(total, 1) * 100, 1)}
            for lang, count in lang_counter.most_common()
            if count / max(total, 1) > 0.05
        ]

        unique_langs = len(lang_counter)

        lang_categories = {
            "前端": ["JavaScript", "TypeScript", "HTML", "CSS", "Vue", "React", "Svelte"],
            "后端": ["Java", "Python", "Go", "Rust", "C#", "PHP", "Ruby", "Node"],
            "移动端": ["Swift", "Kotlin", "Dart", "Objective-C"],
            "系统/底层": ["C", "C++", "Assembly", "Rust"],
            "数据/AI": ["Python", "R", "Julia", "MATLAB"],
            "DevOps": ["Shell", "Dockerfile", "Makefile", "HCL"],
        }

        category_match = {}
        for category, langs in lang_categories.items():
            matched = [l for l in languages if any(kw in str(l) for kw in langs)]
            if matched:
                category_match[category] = len(matched)

        self.features["language"] = {
            "total_language_count": unique_langs,
            "primary_language": lang_counter.most_common(1)[0][0] if lang_counter else None,
            "language_distribution": main_languages,
            "language_categories": category_match,
            "language_diversity": "高" if unique_langs >= 5 else "中" if unique_langs >= 3 else "低",
            "full_stack_potential": len(category_match) >= 2
        }

    def _extract_activity_features(self):
        """提取代码活跃度特征"""
        original_repos = [r for r in self.repos if not r.get("fork", False)]

        if not original_repos:
            self.features["activity"] = {
                "recently_active": False,
                "active_repo_count": 0,
                "activity_level": "无数据"
            }
            return

        now = datetime.now()
        recent_3m, recent_6m, recent_1y = 0, 0, 0

        for repo in original_repos:
            pushed = repo.get("pushed_at", "")
            if pushed:
                try:
                    push_time = datetime.strptime(pushed[:19], "%Y-%m-%dT%H:%M:%S")
                    days_ago = (now - push_time).days
                    if days_ago <= 90:
                        recent_3m += 1
                    if days_ago <= 180:
                        recent_6m += 1
                    if days_ago <= 365:
                        recent_1y += 1
                except Exception as e:
                    print(f"Error parsing pushed_at: {pushed},error: {e}")

        active_ratio_3m = round(recent_3m / max(len(original_repos), 1) * 100, 1)

        if active_ratio_3m >= 60:
            activity_level = "非常活跃"
        elif active_ratio_3m >= 30:
            activity_level = "较活跃"
        elif active_ratio_3m >= 10:
            activity_level = "一般"
        else:
            activity_level = "不活跃"

        self.features["activity"] = {
            "active_repos_3m": recent_3m,
            "active_repos_6m": recent_6m,
            "active_repos_1y": recent_1y,
            "active_ratio_3m": active_ratio_3m,
            "activity_level": activity_level,
            "recently_active": recent_3m > 0
        }

    def _extract_quality_features(self):
        """提取代码质量相关特征"""
        repo_features = self.features.get("repo", {})

        engineering_score = 0
        engineering_details = []

        if repo_features.get("description_ratio", 0) >= 80:
            engineering_score += 20
            engineering_details.append("仓库描述完善")
        elif repo_features.get("description_ratio", 0) >= 50:
            engineering_score += 10
            engineering_details.append("仓库描述部分完善")
        else:
            engineering_details.append("多数仓库缺少描述")

        # 开源协议
        if repo_features.get("license_ratio", 0) >= 80:
            engineering_score += 20
            engineering_details.append("开源协议覆盖率高")
        elif repo_features.get("license_ratio", 0) >= 50:
            engineering_score += 10
            engineering_details.append("部分仓库有开源协议")
        else:
            engineering_details.append("多数仓库缺少开源协议")

        # 项目规模
        if repo_features.get("medium_repos", 0) > 0 or repo_features.get("large_repos", 0) > 0:
            engineering_score += 20
            engineering_details.append("有一定规模的项目")
        else:
            engineering_score += 5
            engineering_details.append("项目规模偏小")

        # 社区认可
        if repo_features.get("repos_starred", 0) >= 3:
            engineering_score += 20
            engineering_details.append("多个项目获得社区认可")
        elif repo_features.get("repos_starred", 0) >= 1:
            engineering_score += 10
            engineering_details.append("少量项目获得认可")
        else:
            engineering_details.append("暂无社区认可")

        # 账号年限
        if self.profile.get("account_years", 0) >= 3:
            engineering_score += 20
            engineering_details.append("开发经验丰富")
        elif self.profile.get("account_years", 0) >= 1:
            engineering_score += 10
            engineering_details.append("有一定开发经验")
        else:
            engineering_score += 5
            engineering_details.append("开发经验较短")

        self.features["quality"] = {
            "engineering_score": engineering_score,
            "engineering_level": self._score_to_level(engineering_score),
            "engineering_details": engineering_details,
        }

    def _calculate_composite_score(self):
        """计算代码能力综合评分（0-100）"""
        repo = self.features.get("repo", {})
        lang = self.features.get("language", {})
        activity = self.features.get("activity", {})
        quality = self.features.get("quality", {})

        weights = {
            "project_scale": 25,
            "tech_breadth": 15,
            "activity": 25,
            "engineering": 20,
            "community": 15
        }

        scores = {}

        # 项目规模
        original_count = repo.get("original_repo_count", 0)
        if original_count >= 20:
            scores["project_scale"] = 25
        elif original_count >= 10:
            scores["project_scale"] = 20
        elif original_count >= 5:
            scores["project_scale"] = 15
        elif original_count >= 2:
            scores["project_scale"] = 10
        else:
            scores["project_scale"] = original_count * 5

        # 技术广度
        lang_count = lang.get("total_language_count", 0)
        full_stack = lang.get("full_stack_potential", False)
        if lang_count >= 5 and full_stack:
            scores["tech_breadth"] = 15
        elif lang_count >= 3:
            scores["tech_breadth"] = 12
        elif lang_count >= 2:
            scores["tech_breadth"] = 8
        elif lang_count >= 1:
            scores["tech_breadth"] = 5
        else:
            scores["tech_breadth"] = 0

        # 活跃度
        activity_level = activity.get("activity_level", "不活跃")
        activity_map = {"非常活跃": 25, "较活跃": 20, "一般": 12, "不活跃": 5, "无数据": 0}
        scores["activity"] = activity_map.get(activity_level, 0)

        # 工程化
        scores["engineering"] = quality.get("engineering_score", 0)

        # 社区影响力
        total_stars = repo.get("total_stars", 0)
        followers = self.profile.get("followers", 0)
        if total_stars >= 500 or followers >= 100:
            scores["community"] = 15
        elif total_stars >= 100 or followers >= 50:
            scores["community"] = 12
        elif total_stars >= 20 or followers >= 10:
            scores["community"] = 8
        elif total_stars >= 1 or followers >= 1:
            scores["community"] = 4
        else:
            scores["community"] = 0

        total_score = sum(scores.get(k, 0) * v for k, v in weights.items())
        max_score = sum(weights.values())
        final_score = round(total_score / max_score * 100, 1)

        self.features["composite"] = {
            "total_score": final_score,
            "level": self._score_to_level(final_score),
            "dimension_scores": scores,
            "weights": weights,
            "max_score": max_score
        }

    @staticmethod
    def _score_to_level(score: float) -> str:
        if score >= 90:
            return "S（卓越）"
        elif score >= 80:
            return "A（优秀）"
        elif score >= 65:
            return "B（良好）"
        elif score >= 50:
            return "C（中等）"
        elif score >= 30:
            return "D（初学）"
        else:
            return "E（待评估）"


class AIAnalyzer:
    """
    AI分析器
    基于LangChain进行深度分析
    """

    def __init__(self, llm=None):
        if llm:
            self.llm = llm
        else:
            self.llm = ChatOpenAI(
                model=settings.code_ability.model_name,
                base_url=settings.code_ability.base_url,
                api_key=settings.code_ability.api_key,
                temperature=settings.code_ability.extra.get("temperature", 0.3),
                timeout=settings.code_ability.timeout,
            )

    def analyze(self, features: dict) -> dict:
        """综合分析生成代码能力评估报告"""

        prompt = ChatPromptTemplate.from_messages([
            ("system", prompt_loader.small_prompts.get("code_ability")),
            ("human", prompt_loader.code_ability)
        ])

        basic = features.get("basic", {})
        repo = features.get("repo", {})
        lang = features.get("language", {})
        activity = features.get("activity", {})
        quality = features.get("quality", {})

        top_repos = repo.get("top_repos", [])
        top_repos_detail = "\n".join([
            f"  - {r.get('repo_name', 'N/A')} (⭐{r.get('stargazers_count', 0)}, "
            f"{r.get('language', 'N/A')}, {'有' if r.get('description') else '无'}描述)"
            for r in top_repos
        ]) or "无仓库数据"

        lang_dist = lang.get("language_distribution", [])
        lang_dist_str = ", ".join([f"{l['language']}({l['ratio']}%)" for l in lang_dist[:5]]) or "N/A"

        lang_cats = lang.get("language_categories", {})
        lang_cats_str = ", ".join([f"{k}:{v}个项目" for k, v in lang_cats.items()]) or "N/A"

        chain = prompt | self.llm | StrOutputParser()

        result = chain.invoke({
            "platform": basic.get("platform", "unknown"),
            "account_years": basic.get("account_years", 0),
            "public_repos": basic.get("total_public_repos", 0),
            "followers": basic.get("followers", 0),
            "original_count": repo.get("original_repo_count", 0),
            "total_stars": repo.get("total_stars", 0),
            "total_forks": repo.get("total_forks", 0),
            "max_star": repo.get("max_star_repo", 0),
            "top_repos_detail": top_repos_detail,
            "lang_count": lang.get("total_language_count", 0),
            "primary_language": lang.get("primary_language", "N/A"),
            "lang_distribution": lang_dist_str,
            "lang_categories": lang_cats_str,
            "full_stack": "是" if lang.get("full_stack_potential") else "否",
            "active_3m": activity.get("active_repos_3m", 0),
            "activity_level": activity.get("activity_level", "N/A"),
            "engineering_score": quality.get("engineering_score", 0),
            "engineering_details": "; ".join(quality.get("engineering_details", [])) or "N/A"
        })

        try:
            clean_result = result.strip()
            if clean_result.startswith("```"):
                clean_result = clean_result.split("\n", 1)[-1]
            if clean_result.endswith("```"):
                clean_result = clean_result[:-3]
            clean_result = clean_result.strip()
            if clean_result.startswith("json"):
                clean_result = clean_result[4:].strip()
            return json.loads(clean_result)
        except json.JSONDecodeError:
            return {"raw_response": result, "parse_error": True}


class CodeAbilityEvaluator:
    """
    代码能力评估器
    整合 URL解析 → 数据采集 → 特征提取 → AI分析 完整流程
    """

    def __init__(self, llm=None):
        self.ai_analyzer = AIAnalyzer(llm) if llm else AIAnalyzer()

    async def evaluate(self, url: str, use_ai: bool = True) -> dict:
        """
        代码能力评估核心流程

        Args:
            url: GitHub或Gitee主页链接
            use_ai: 是否使用AI深度分析

        Returns:
            包含评分、特征、AI报告的字典

        Raises:
            ValueError: URL无效或用户不存在
        """
        parse_result = platform_url_parser.parse(url)
        if not parse_result["valid"]:
            raise ValueError("URL格式无效，请输入正确的GitHub或Gitee主页链接")

        platform = parse_result["platform"]
        username = parse_result["username"]

        try:
            if platform == "github":
                profile = await asyncio.to_thread(code_platform_scraper.fetch_github_profile, username)
                repos = await asyncio.to_thread(code_platform_scraper.fetch_github_repos, username, per_page=30)
            else:
                profile = await asyncio.to_thread(code_platform_scraper.fetch_gitee_profile, username)
                repos = await asyncio.to_thread(code_platform_scraper.fetch_gitee_repos, username, per_page=30)
        except Exception as e:
            raise ValueError(f"用户 {username} 不存在或请求失败: {str(e)}")

        if not repos:
            raise ValueError(f"用户 {username} 没有任何公开仓库，无法评估")

        # Step 3: 特征提取
        extractor = FeatureExtractor(profile, repos, platform)
        features = extractor.extract_all()

        # Step 4: AI分析
        ai_analysis = None
        if use_ai:
            try:
                ai_analysis = self.ai_analyzer.analyze(features)
            except Exception as e:
                ai_analysis = {"error": f"AI分析失败: {str(e)}"}

        return {
            "platform": platform,
            "username": username,
            "composite_score": features["composite"]["total_score"],
            "level": features["composite"]["level"],
            "features": features,
            "ai_analysis": ai_analysis
        }


# 单例
code_ability_evaluator = CodeAbilityEvaluator()
