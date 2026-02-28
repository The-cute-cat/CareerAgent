from functools import lru_cache

from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings, YamlConfigSettingsSource, SettingsConfigDict

__all__ = ["settings"]


class Database(BaseModel):
    """数据库配置嵌套类"""

    host: str
    port: int
    database: str
    user: str
    password: str

    @field_validator("user") # 这两个装饰器不能调换位置，否则验证逻辑失效!!!
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


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )
    database: Database = Database(host="", port=0, database="", user="", password="")

    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls,
            init_settings,  # 显式传递给 Settings() 的值
            env_settings,  # 环境变量（不包括 dotenv）
            dotenv_settings,  # 从 .env 文件加载的数据
            file_secret_settings,  # 从文件加载的密钥（如有）
    ):
        return (  # 从上到下优先级从高到低
            init_settings,  # 显式传递给 Settings() 的值
            env_settings,  # 环境变量（不包括 dotenv）
            dotenv_settings,  # 从 .env 文件加载的数据
            file_secret_settings,  # 从文件加载的密钥（如有）
            YamlConfigSettingsSource(  # 从 yaml 文件加载的数据
                settings_cls, yaml_file="config.yaml"
            ),
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
    pass
