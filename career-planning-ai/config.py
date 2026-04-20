import atexit
import json
import os.path
import shutil
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import Any

import certifi
import yaml
from pydantic import (
    BaseModel,
    field_validator,
    SecretStr,
    Field,
    model_validator,
    PrivateAttr,
)
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings.sources import InitSettingsSource

__all__ = ["settings", "_LLMModelBase"]

from ai_service.utils.path_tool import abs_path, get_project_root, get_abs_path


class _Database(BaseModel):
    """数据库配置嵌套类"""

    host: str = ""
    port: int = 0
    database: str = ""
    user: str = ""
    password: SecretStr = SecretStr("")
    pool_size: int = 10
    max_overflow: int = 20
    pool_pre_ping: bool = True
    pool_recycle: int = 3600

    @field_validator("user")  # 这两个装饰器不能调换位置，否则验证逻辑失效!!!
    @classmethod
    def _validate_user(cls, v):
        if v == "<USER>":
            raise ValueError("请在.env文件中配置数据库用户名")
        return v

    @field_validator("password")
    @classmethod
    def _validate_password(cls, v):
        if v == "<PASSWORD>":
            raise ValueError("请在.env文件中配置数据库密码")
        return v


class _Communication(BaseModel):
    """通信配置嵌套类"""

    class _Token(BaseModel):
        secret: str = ""
        expire: int = 1800

        @field_validator("secret")
        @classmethod
        def _validate_secret(cls, v):
            if v == "<SECRET>" or v == "<secret>" or not v:
                raise ValueError("请在.env文件中配置通信密钥")
            return v

    token: _Token = _Token()


class _LLMModelBase(BaseModel):
    """模型配置基类"""

    _skip_verify: bool = PrivateAttr(default=False)
    _name: str = ""
    api_key: SecretStr = SecretStr("")  # 敏感信息，使用时调用 .get_secret_value() 方法获取
    base_url: str = ""
    model_name: str = ""
    timeout: float = -1
    max_retries: int = -1
    max_concurrent_requests: int = -1
    extra: dict[str, Any] = {}

    def __repr__(self):
        return f"{self.__class__.__name__}(_name={self._name}, api_key={self.api_key}, base_url={self.base_url}, model_name={self.model_name}, timeout={self.timeout}, max_retries={self.max_retries},max_concurrent_requests={self.max_concurrent_requests}, extra={self.extra})"

    def __str__(self):
        return self.__repr__()

    def _set_skip_verify(self, skip_verify: bool):
        self._skip_verify = skip_verify
        return self

    @model_validator(mode="after")
    def _validate_default_value(self) -> "_LLMModelBase":
        if self._skip_verify:
            return self
        if not self.base_url:
            raise ValueError(
                f"请在 .env 文件中配置正确的 {self._name if self._name else self.__class__.__name__} Base URL"
            )
        if self.api_key.get_secret_value() in ("<API_KEY>", "<api_key>", "", None):
            raise ValueError(
                f"请在 .env 文件中配置正确的 {self._name if self._name else self.__class__.__name__} API Key"
            )
        if not self.model_name:
            raise ValueError(
                f"请在 .env 文件中配置正确的 {self._name if self._name else self.__class__.__name__} Model Name"
            )
        if self.timeout <= 0:
            raise ValueError(
                f"请在 .env 文件中配置正确的 {self._name if self._name else self.__class__.__name__} Timeout"
            )
        if self.max_retries <= 0:
            raise ValueError(
                f"请在 .env 文件中配置正确的 {self._name if self._name else self.__class__.__name__} Max Retries"
            )
        if self.max_concurrent_requests <= 0:
            raise ValueError(
                f"请在 .env 文件中配置正确的 {self._name if self._name else self.__class__.__name__} Max Concurrent Requests"
            )
        return self


class _LLM(_LLMModelBase):
    """大模型通用配置"""

    _skip_verify: bool = PrivateAttr(default=True)

    def _set_default_value(self, llm: _LLMModelBase):
        if self.api_key.get_secret_value() == "<api_key>":
            raise ValueError(
                f"{self.__class__.__name__} api_key 应该是需要配置的但现在未配置"
            )
        if not self.base_url:
            self.base_url = llm.base_url
        else:
            if self.base_url != llm.base_url and self.api_key.get_secret_value() in (
                    "<API_KEY>",
                    "<api_key>",
                    "",
                    None,
            ):
                raise ValueError(
                    f"❌️错误：{self.__class__.__name__} base_url 和 llm.base_url 不一致且 api_key 未配置，不能继承api_key！"
                )
        if not self.api_key.get_secret_value():
            self.api_key = llm.api_key
        if not self.model_name:
            self.model_name = llm.model_name
        if self.timeout == -1:
            self.timeout = llm.timeout
        if self.max_retries == -1:
            self.max_retries = llm.max_retries
        if self.max_concurrent_requests == -1:
            self.max_concurrent_requests = llm.max_concurrent_requests
        if not self.extra:
            self.extra = llm.extra


class _LiteLLM(_LLM):
    _name: str = "LiteLLM"

    class _Qwen(_LLM):
        _name: str = "LLM_Qwen"

    qwen: _Qwen = Field(default_factory=_Qwen)

    class _Deepseek(_LLM):
        _name: str = "LLM_Deepseek"

    deepseek: _Deepseek = Field(default_factory=_Deepseek)

    class _Image(_LLM):
        _name: str = "LLM_Image"

    image: _Image = Field(default_factory=_Image)

    def _set_default_value(self, llm: _LLMModelBase):
        super()._set_default_value(llm)
        for key, value in self.__dict__.items():
            if isinstance(value, _LLM):
                value._set_default_value(llm)


class _PDF(_LLM):
    suffix: list[str] = ["PDF"]


class _Image(_LLM):
    suffix: list[str] = []
    max_size: int = 0  # 单位 MB
    max_dimension: int = 0  # 单位 px


class _TestQuestion(_LLM):
    ...


class _GrowthPlanAgent(_LLM):
    ...


class _PathConfig(BaseModel):
    class _Temp(BaseModel):
        path: str = ""
        exit_is_clean: bool = True
        run_is_clean: bool = True
        expire: int = 900
        cleanup_interval: int = 60

        @field_validator("path")
        @classmethod
        def _validate_temp(cls, v):
            if v == "<TEMP_PATH>" or not v or not Path(v).exists():
                v = tempfile.gettempdir()
            path = os.path.join(v, "career_agent", "ai_service", "temp")
            os.makedirs(path, exist_ok=True)
            return str(Path(path))

    temp: _Temp = _Temp()
    log: str = ""
    prompt: str = ""
    data: str = ""

    @field_validator("log")
    @classmethod
    def _validate_log(cls, v):
        if v == "<LOG_PATH>" or not v or not Path(v).exists():
            v = get_project_root()
        path = os.path.join(v, "logs")
        os.makedirs(path, exist_ok=True)
        return str(Path(path))

    @field_validator("prompt")
    @classmethod
    def _validate_prompt(cls, v):
        if v == "<PROMPT_PATH>" or not v or not Path(v).exists():
            v = get_abs_path("")
        path = os.path.join(v, "prompts")
        os.makedirs(path, exist_ok=True)
        return str(Path(path))

    @field_validator("data")
    @classmethod
    def _validate_data(cls, v):
        if v == "<DATA_PATH>" or not v or not Path(v).exists():
            v = get_project_root()
        path = os.path.join(v, "data")
        os.makedirs(path, exist_ok=True)
        return str(Path(path))


class _Vector(BaseModel):
    model_name: str = ""
    llm_model_name: str = ""
    llm_long_model_name: str = ""


class _Milvus(BaseModel):
    force_local: bool = True  # true=强制本地模式，false=自动故障转移

    class _Local(BaseModel):
        host: str = ""
        port: int = 19530

    class _Cloud(BaseModel):
        url: str = ""
        token: SecretStr = SecretStr("")

    local: _Local = Field(default_factory=_Local)
    cloud: _Cloud = Field(default_factory=_Cloud)


class _ChromaConfig(_LLM):
    _name: str = "Chroma"
    save_path: str = ""
    k: int = 5

    class _Collection(BaseModel):
        default: str = "default_collection"
        project_collection: str = "open_source_projects"
        book_collection: str = "books"
        intern_collection: str = "internships"
        video_collection: str = "videos"

    collection_name: _Collection = Field(default_factory=_Collection)

    def _set_default_path(self, path: str):
        if (
                self.save_path == "<SAVE_PATH>"
                or not self.save_path
                or not Path(self.save_path).exists()
        ):
            if path and path != "" and Path(path).exists():
                save_path = os.path.join(path, "chroma")
            else:
                save_path = os.path.join(get_project_root(), "data", "chroma")
            self.save_path = save_path
            os.makedirs(self.save_path, exist_ok=True)


class _CodeAbility(_LLM):
    _name: str = "CodeAbility"
    github_token: SecretStr = SecretStr("")
    gitee_token: SecretStr = SecretStr("")

    @field_validator("github_token")
    @classmethod
    def _validate_secret(cls, v):
        if v.get_secret_value() in ("<GITHUB_TOKEN>", "<token>", "", None):
            print(
                "⚠️警告：请在.env文件中配置github个人访问令牌，否则可能因github访问速率限制，导致无法获取github仓库信息。"
            )
            return SecretStr("")
        return v

    @field_validator("gitee_token")
    @classmethod
    def _validate_gitee_token(cls, v):
        if v.get_secret_value() in ("<GITEE_TOKEN>", "<token>", "", None):
            print(
                "⚠️警告：请在.env文件中配置gitee个人访问令牌，否则可能因gitee访问速率限制，导致无法获取gitee仓库信息。"
            )
            return SecretStr("")
        return v


class _MatchAnalyzer(_LLM):
    ...


class _RedisConfig(BaseModel):
    is_can_use: bool = True  # redis缓存是否能用
    host: str = ""
    port: int = 6379
    username: str = ""
    password: SecretStr = SecretStr("")
    connect_timeout: int = 2000

    class _CacheTimeout(BaseModel):
        default: int = 3600
        file_parse: int = 3600
        code_ability: int = 3600
        report: int = 3600
        question: int = 3600

    cache_timeout: _CacheTimeout = Field(default_factory=_CacheTimeout)

    @model_validator(mode="after")
    def _validate_availability(self):
        if self.host in ("<HOST>", "<host>", "", None) or self.port <= 0:
            self.is_can_use = False
            print("⚠️警告：请在.env文件中配置redis相关配置，否则导致无法使用redis缓存。")
        return self


class _Neo4jConfig(BaseModel):
    url: str = ""
    username: str = ""
    password: SecretStr = SecretStr("")

    @field_validator("password")
    @classmethod
    def _validate_password(cls, v):
        if v.get_secret_value() in ("<PASSWORD>", "<password>", "", None):
            print("⚠️警告：请在.env文件中配置neo4j密码，否则无法使用图数据库功能。")
            return SecretStr("")
        return v


class _Other(BaseModel):
    ssl_verify: bool | str = True
    text_file_suffix: list[str] = ["txt", "md"]
    word_file_suffix: list[str] = ["doc", "docx"]

    @model_validator(mode="after")
    def set_default_value(self):
        if self.ssl_verify:
            self.ssl_verify = certifi.where()
        return self


class _Conversation(BaseModel):
    class _Memory(BaseModel):
        class _Short(_LLM):
            max_messages: int = 20
            max_tokens: int = 5000
            compression_trigger_raito: float = 0.8
            keep_recent_messages: int = 8

        class _Long(_LLM):
            max_memory_count: int = 50
            min_score: float = 0.6
            collection_name: str = "user_memories"

        class _Extraction(_LLM):
            ...

        class _Compression(_LLM):
            ...

        short: _Short = Field(default_factory=_Short)
        long: _Long = Field(default_factory=_Long)
        extraction: _Extraction = Field(default_factory=_Extraction)
        compression: _Compression = Field(default_factory=_Compression)

    class _Agent(_LLM):
        ...

    save_path: str = ""
    memory: _Memory = Field(default_factory=_Memory)
    agent: _Agent = Field(default_factory=_Agent)

    @model_validator(mode="after")
    def _set_default_values(self):
        if (
                self.save_path == "<SAVE_PATH>"
                or not self.save_path
                or not Path(self.save_path).exists()
        ):
            self.save_path = os.path.join(get_project_root(), "data", "conversation")
            os.makedirs(self.save_path, exist_ok=True)
        return self


class _KnowledgeGraph(BaseModel):
    class _Analysis(_LLM): ...

    class _Explain(_LLM): ...

    analysis: _Analysis = Field(default_factory=_Analysis)
    explain: _Explain = Field(default_factory=_Explain)


class _ReportAssistant(_LLM): ...


class _GraphBuild(BaseModel):
    """离线建图超参（权重/阈值/惩罚项等）。

    说明：该配置仅影响离线建图结果（Neo4j 图结构与边权），在线查询逻辑保持兼容。
    """

    class _Tf(BaseModel):
        # 以“Competency.category”（中文）为 key 的 TF 等效权重
        category_weights: dict[str, float] = Field(
            default_factory=lambda: {
                "核心专业技能": 1.0,
                "工具与平台能力": 0.7,
                "语言能力": 0.5,
                "证书要求": 0.6,
            }
        )
        default_weight: float = 0.7

    class _CosLow(BaseModel):
        text_weight: float = 0.7
        attr_weight: float = 0.3

    class _Jaccard(BaseModel):
        threshold: float = 0.1
        blocking_min_jobs: int = 3000
        blocking_top_m: int = 20

    class _Clustering(BaseModel):
        coarse_resolution: float = 0.1
        coarse_isolation_threshold: float = 0.1
        fine_resolution: float = 1.0
        fine_isolation_threshold: float = 0.05
        fine_weight_transform_offset: float = 0.1
        fine_weight_transform_power: float = 2.0

    class _Pareto(BaseModel):
        keep_fronts: int = 2
        cross_community_penalty: float = 0.5

    class _Routing(BaseModel):
        attraction_weights: dict[str, float] = Field(
            default_factory=lambda: {
                "jaccard_high": 0.5,
                "cos_low": 0.3,
                "salary_gain": 0.2,
            }
        )
        rank_penalty_per_rank: float = 0.15
        cross_penalty: float = 0.5

    class _DegreeZeroFallback(BaseModel):
        top_k: int = 3

    tf: _Tf = Field(default_factory=_Tf)
    cos_low: _CosLow = Field(default_factory=_CosLow)
    jaccard: _Jaccard = Field(default_factory=_Jaccard)
    clustering: _Clustering = Field(default_factory=_Clustering)
    pareto: _Pareto = Field(default_factory=_Pareto)
    routing: _Routing = Field(default_factory=_Routing)
    degree_zero_fallback: _DegreeZeroFallback = Field(
        default_factory=_DegreeZeroFallback
    )


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=abs_path(".env"),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )
    debug: bool = False
    database: _Database = Field(default_factory=_Database)
    communication: _Communication = Field(default_factory=_Communication)
    lite_llm: _LiteLLM = Field(default_factory=_LiteLLM)
    llm: _LLMModelBase = Field(default_factory=_LLMModelBase)
    pdf: _PDF = Field(default_factory=_PDF)
    image: _Image = Field(default_factory=_Image)
    test_question: _TestQuestion = Field(default_factory=_TestQuestion)
    growth_plan_agent: _GrowthPlanAgent = Field(default_factory=_GrowthPlanAgent)
    path_config: _PathConfig = Field(default_factory=_PathConfig)
    vector: _Vector = Field(default_factory=_Vector)
    milvus: _Milvus = Field(default_factory=_Milvus)
    chroma_config: _ChromaConfig = Field(default_factory=_ChromaConfig)
    match_analyzer: _MatchAnalyzer = Field(default_factory=_MatchAnalyzer)
    code_ability: _CodeAbility = Field(default_factory=_CodeAbility)
    redis: _RedisConfig = Field(default_factory=_RedisConfig)
    neo4j: _Neo4jConfig = Field(default_factory=_Neo4jConfig)
    other: _Other = Field(default_factory=_Other)
    conversation: _Conversation = Field(default_factory=_Conversation)
    knowledge_graph: _KnowledgeGraph = Field(default_factory=_KnowledgeGraph)
    report_assistant: _ReportAssistant = Field(default_factory=_ReportAssistant)
    graph_build: _GraphBuild = Field(default_factory=_GraphBuild)

    # noinspection PyProtectedMember
    @model_validator(mode="after")
    def _set_default_values(self) -> "Settings":
        """设置默认值"""
        self.chroma_config._set_default_path(self.path_config.data)
        self._set_llm_default_values(self)
        return self

    # noinspection PyProtectedMember
    def _set_llm_default_values(self, obj):
        """递归设置所有_LLM类型字段的默认值"""
        if hasattr(obj, "__dict__"):
            for key, value in obj.__dict__.items():
                if isinstance(value, _LLM):
                    value._set_default_value(self.llm)
                elif hasattr(value, "__dict__"):
                    self._set_llm_default_values(value)

    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls,
            init_settings,  # 显式传递给 Settings() 的值
            env_settings,  # 环境变量（不包括 dotenv）
            dotenv_settings,  # 从 .env 文件加载的数据
            file_secret_settings,  # 从文件加载的密钥（如有）
    ):
        yaml_file = Path(abs_path("config.yaml"))
        if yaml_file.exists():
            with open(yaml_file, "r", encoding="utf-8") as f:
                yaml_data = yaml.safe_load(f) or {}
            yaml_source = InitSettingsSource(settings_cls, yaml_data)
        else:
            yaml_source = InitSettingsSource(settings_cls, {})
        return (  # 从上到下优先级从高到低
            init_settings,  # 显式传递给 Settings() 的值
            env_settings,  # 环境变量（不包括 dotenv）
            dotenv_settings,  # 从 .env 文件加载的数据
            file_secret_settings,  # 从文件加载的密钥（如有）
            yaml_source,  # 从 yaml 文件加载的数据
        )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


def _program_exit():
    """程序退出前执行的操作"""
    if settings.path_config.temp.exit_is_clean:  # 是否清理临时文件
        temp_path = os.path.join(settings.path_config.temp.path, "../../")
        if Path(temp_path).exists():
            shutil.rmtree(temp_path, ignore_errors=True)


settings = get_settings()
atexit.register(_program_exit)

if __name__ == "__main__":
    # print(f"\n数据库配置:")
    # print(f"  主机: {settings.database.host}")
    # print(f"  端口: {settings.database.port}")
    # print(f"  数据库名: {settings.database.database}")
    # print(f"  用户名: {settings.database.user}")
    # print(f"  密码: {settings.database.password}")
    # print(f"  API Key: {settings.llm.api_key.get_secret_value()}")
    # print(settings.lite_llm.qwen)
    # print(settings.milvus.cloud.token.get_secret_value())
    # print(settings.chroma_config.save_path)
    # print(settings.conversation.memory.long.model_name)
    # print(settings.lite_llm.qwen)
    os.makedirs("./temp", exist_ok=True)
    with open("./temp/settings.json", "w", encoding="utf-8") as file:  # 导出配置到文件
        json.dump(settings.model_dump(mode="json"), file, indent=2, ensure_ascii=False)
    pass
