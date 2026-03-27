import atexit
import os.path
import shutil
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import Dict, Any, List

import yaml
from pydantic import BaseModel, field_validator, SecretStr, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings.sources import InitSettingsSource

__all__ = ["settings", "LLMModelBase"]

from ai_service.utils.path_tool import abs_path, get_project_root, get_abs_path


class Database(BaseModel):
    """数据库配置嵌套类"""

    host: str = ""
    port: int = 0
    database: str = ""
    user: str = ""
    password: str = ""

    @field_validator("user")  # 这两个装饰器不能调换位置，否则验证逻辑失效!!!
    @classmethod
    def validate_user(cls, v):
        if v == "<USER>":
            raise ValueError("请在.env文件中配置数据库用户名")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if v == "<PASSWORD>":
            raise ValueError("请在.env文件中配置数据库密码")
        return v


class Communication(BaseModel):
    """通信配置嵌套类"""

    class Token(BaseModel):
        secret: str = ""
        expire: int = 1800

        @field_validator("secret")
        @classmethod
        def validate_secret(cls, v):
            if v == "<SECRET>":
                raise ValueError("请在.env文件中配置通信密钥")
            return v

    token: Token = Token()


class LLMModelBase(BaseModel):
    """模型配置基类"""
    name: str = "LLM"
    api_key: SecretStr = SecretStr("")  # 敏感信息，使用时调用 .get_secret_value() 方法获取
    base_url: str = ""
    model_name: str = ""
    timeout: float = 30.0
    max_retries: int = 3
    max_concurrent_requests: int = 3
    extra: Dict[str, Any] = {}

    def __repr__(self):
        return f"{self.__class__.__name__}(api_key={self.api_key}, base_url={self.base_url}, model_name={self.model_name}, timeout={self.timeout}, max_retries={self.max_retries}, extra={self.extra})"

    def __str__(self):
        return self.__repr__()

    @model_validator(mode="after")
    def validate_api_key(self) -> "LLMModelBase":
        if not self.api_key.get_secret_value() or self.api_key.get_secret_value() == "" or self.api_key.get_secret_value() == "<api_key>":
            raise ValueError(f"请在 .env 文件中配置正确的 {self.name} API Key")
        return self


class LiteLLM(LLMModelBase):
    """模型配置基类"""
    name: str = "LiteLLM"

    class Qwen(LLMModelBase):
        name: str = "LLM_Qwen"

    qwen: Qwen = Field(default_factory=Qwen)

    class Deepseek(LLMModelBase):
        name: str = "LLM_Deepseek"

    deepseek: Deepseek = Field(default_factory=Deepseek)

    class Image(LLMModelBase):
        name: str = "LLM_Image"

    image: Image = Field(default_factory=Image)


class LLM(LLMModelBase):
    """大模型通用配置"""


class PDF(BaseModel):
    model_name: str = ""
    extra: Dict[str, Any] = {}


class Image(BaseModel):
    model_name: str = ""
    suffix: List[str] = []
    max_size: int = 0  # 单位 MB
    max_dimension: int = 0  # 单位 px
    extra: Dict[str, Any] = {}


class TestQuestion(BaseModel):
    model_name: str = ""
    timeout: int = 30
    extra: Dict[str, Any] = {}


class PathConfig(BaseModel):
    temp: str = ""
    is_clean: bool = True
    log: str = ""
    prompt: str = ""
    data: str = ""

    @field_validator("temp")
    @classmethod
    def validate_temp(cls, v):
        if v == "<TEMP_PATH>" or not v or not Path(v).exists():
            v = tempfile.gettempdir()
        path = os.path.join(v, "career_agent", "ai_service", "temp")
        os.makedirs(path, exist_ok=True)
        return str(Path(path))

    @field_validator("log")
    @classmethod
    def validate_log(cls, v):
        if v == "<LOG_PATH>" or not v or not Path(v).exists():
            v = get_project_root()
        path = os.path.join(v, "logs")
        os.makedirs(path, exist_ok=True)
        return str(Path(path))

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, v):
        if v == "<PROMPT_PATH>" or not v or not Path(v).exists():
            v = get_abs_path("")
        path = os.path.join(v, "prompts")
        os.makedirs(path, exist_ok=True)
        return str(Path(path))

    @field_validator("data")
    @classmethod
    def validate_data(cls, v):
        if v == "<DATA_PATH>" or not v or not Path(v).exists():
            v = get_project_root()
        path = os.path.join(v, "data")
        os.makedirs(path, exist_ok=True)
        return str(Path(path))


class Vector(BaseModel):
    model_name: str = ""
    llm_model_name: str = ""


class Milvus(BaseModel):
    class Local(BaseModel):
        host: str = ""
        port: int = 19530

    class Cloud(BaseModel):
        url: str = ""
        token: SecretStr = SecretStr("")

    local: Local = Field(default_factory=Local)
    cloud: Cloud = Field(default_factory=Cloud)


class ChromaConfig(BaseModel):
    save_path: str = ""
    model_name: str = ""
    base_url: str = ""
    k: int = 5
    extra: Dict[str, Any] = {}

    def set_default_path(self, path: str):
        if self.save_path == "<SAVE_PATH>" or not self.save_path or not Path(self.save_path).exists():
            if path and path != "" and Path(path).exists():
                save_path = os.path.join(path, "chroma")
            else:
                save_path = os.path.join(get_project_root(), "data", "chroma")
            self.save_path = save_path
            os.makedirs(self.save_path, exist_ok=True)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=abs_path(".env"),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )
    database: Database = Field(default_factory=Database)
    communication: Communication = Field(default_factory=Communication)
    lite_llm: LiteLLM = Field(default_factory=LiteLLM)
    llm: LLM = Field(default_factory=LLM)
    pdf: PDF = Field(default_factory=PDF)
    image: Image = Field(default_factory=Image)
    test_question: TestQuestion = Field(default_factory=TestQuestion)
    path_config: PathConfig = Field(default_factory=PathConfig)
    vector: Vector = Field(default_factory=Vector)
    milvus: Milvus = Field(default_factory=Milvus)
    chroma_config: ChromaConfig = Field(default_factory=ChromaConfig)

    @model_validator(mode="after")
    def set_chroma_default_path(self) -> "Settings":
        """设置默认值"""
        self.chroma_config.set_default_path(self.path_config.data)
        return self

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
            with open(yaml_file, 'r', encoding='utf-8') as f:
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


def program_exit():
    """程序退出前执行的操作"""
    if settings.path_config.is_clean:  # 是否清理临时文件
        temp_path = os.path.join(settings.path_config.temp, "../../")
        if Path(temp_path).exists():
            shutil.rmtree(temp_path, ignore_errors=True)


settings = get_settings()
atexit.register(program_exit)

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
    print(settings.chroma_config.save_path)
    pass
