from functools import lru_cache

from pydantic import Field, BaseModel
from pydantic_settings import BaseSettings, YamlConfigSettingsSource, SettingsConfigDict

__all__ = ["settings"]


class DatabaseConfig(BaseModel):
    """数据库配置嵌套类"""
    host: str
    port: int
    database: str
    user: str | None = None
    password: str | None = None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_nested_delimiter="__",
        extra='ignore'
    )
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)

    @classmethod
    def settings_customise_sources(cls, settings_cls, *args, **kwargs):
        return (
            YamlConfigSettingsSource(settings_cls, yaml_file="config.yaml"),
            *args,
        )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

if __name__ == '__main__':
    print(f"\n数据库配置:")
    print(f"  主机: {settings.database.host}")
    print(f"  端口: {settings.database.port}")
    print(f"  数据库名: {settings.database.database}")
    print(f"  用户名: {settings.database.user}")
    print(f"  密码: {settings.database.password}")
    pass
