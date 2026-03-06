from functools import lru_cache
from pathlib import Path
from typing import Dict, Any, List

import yaml
from pydantic import BaseModel, field_validator, SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic_settings.sources import InitSettingsSource

__all__ = ["settings"]

from ai_service.utils.path_tool import abs_path


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


class LLM(BaseModel):
    """大模型通用配置"""
    api_key: SecretStr = SecretStr("")  # 敏感信息，使用时调用 .get_secret_value() 方法获取
    base_url: str = ""  # 大模型服务器地址
    model_name: str = ""  # 大模型名称
    timeout: float = 30.0  # 超时时间
    max_retries: int = 3  # 最大重试次数
    extra: Dict[str, Any] = {}  # 额外参数

    def __repr__(self):
        return f"LLM(api_key={self.api_key}, base_url={self.base_url}, model_name={self.model_name}, timeout={self.timeout}, max_retries={self.max_retries}, extra={self.extra})"

    @field_validator("api_key", mode="after")
    @classmethod
    def validate_api_key(cls, v: SecretStr) -> SecretStr:
        if not v.get_secret_value() or v.get_secret_value() == "<api_key>":
            raise ValueError("请在 .env 文件中配置正确的 LLM API Key")
        return v


class PDF(BaseModel):
    model_name: str = ""
    extra: Dict[str, Any] = {}


class Image(BaseModel):
    model_name: str = ""
    suffix: List[str] = []
    max_size: int = 0  # 单位 MB
    max_dimension: int = 0  # 单位 px
    extra: Dict[str, Any] = {}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=abs_path(".env"),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )
    database: Database = Field(default_factory=Database)
    communication: Communication = Field(default_factory=Communication)
    llm: LLM = Field(default_factory=LLM)
    pdf: PDF = Field(default_factory=PDF)
    image: Image = Field(default_factory=Image)

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


settings = get_settings()

if __name__ == "__main__":
    print(f"\n数据库配置:")
    print(f"  主机: {settings.database.host}")
    print(f"  端口: {settings.database.port}")
    print(f"  数据库名: {settings.database.database}")
    print(f"  用户名: {settings.database.user}")
    print(f"  密码: {settings.database.password}")
    print(f"  API Key: {settings.llm.api_key.get_secret_value()}")
    pass
