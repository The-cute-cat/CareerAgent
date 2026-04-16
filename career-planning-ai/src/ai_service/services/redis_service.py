"""
Redis 缓存服务模块

提供 Redis 缓存的增删改查功能，支持单例模式管理连接。
"""
import json
from typing import Any

from redis import Redis
from redis.exceptions import RedisError

from ai_service.services import log as logger
from config import settings

_instances: dict[str, "RedisService"] = {}


class RedisService:
    # noinspection SpellCheckingInspection
    """
        Redis 缓存服务类

        功能:
            - 字符串缓存存储与检索
            - 支持过期时间设置
            - 支持原子操作（incr, decr, setnx）
            - 单例模式管理多个连接实例

        Example:
            >>> # 获取单例实例
            >>> redis = RedisService.get_instance()
            >>> # 设置缓存
            >>> redis.set("user:1", {"name": "张三", "age": 25}, ttl=3600)
            >>> # 获取缓存
            >>> data = redis.get("user:1")
            >>> # 判断键是否存在
            >>> if redis.exists("user:1"):
            ...     print("用户存在")
            >>> # 原子计数器
            >>> redis.incr("page_views")
        """

    def __init__(self, prefix: str = "career"):
        """
        初始化 Redis 服务

        Args:
            prefix: 缓存键前缀，用于区分不同业务场景
        """
        self._prefix = prefix
        self._is_available = settings.redis.is_can_use
        self._client: Redis | None = None

        if not self._is_available:
            logger.warning("⚠️警告：Redis 服务不可用，请检查配置")
            return

        try:
            self._client = Redis(
                host=settings.redis.host,
                port=settings.redis.port,
                username=settings.redis.username or None,
                password=settings.redis.password.get_secret_value() or None,
                decode_responses=True,
                socket_timeout=settings.redis.connect_timeout / 1000,
                socket_connect_timeout=settings.redis.connect_timeout / 1000,
            )
            self._client.ping()
            logger.info(
                f"✅ Redis 服务连接成功: host={settings.redis.host}, port={settings.redis.port}, prefix={self._prefix}"
            )
        except RedisError as e:
            self._is_available = False
            self._client = None
            logger.error(f"❌️ Redis 服务连接失败: {e}")

    @classmethod
    def get_instance(cls, prefix: str = "career") -> "RedisService":
        """
        获取单例实例

        Args:
            prefix: 缓存键前缀

        Returns:
            RedisService 实例
        """
        if prefix not in _instances:
            _instances[prefix] = cls(prefix=prefix)
        return _instances[prefix]

    @classmethod
    def clear_instance(cls, prefix: str = "career") -> None:
        """清除缓存的实例"""
        if prefix in _instances:
            instance = _instances[prefix]
            if instance._client:
                instance._client.close()
            del _instances[prefix]
            logger.info(f"已清除 Redis 实例缓存: {prefix}")

    def _build_key(self, key: str) -> str:
        """构建带前缀的键名"""
        return f"{self._prefix}:{key}" if self._prefix else key

    @property
    def is_available(self) -> bool:
        """检查 Redis 服务是否可用"""
        return self._is_available and self._client is not None

    @property
    def client(self) -> Redis | None:
        """获取底层 Redis 客户端实例"""
        return self._client

    def get(self, key: str, default: Any = None, ttl: int | None = 0) -> Any:
        """
        获取缓存值

        Args:
            key: 缓存键
            default: 默认值（键不存在时返回）
            ttl: 过期时间（秒），None 表示永不过期，0 表示不更新过期时间

        Returns:
            缓存值，如果不存在则返回默认值
        """
        if not self.is_available:
            return default

        try:
            full_key = self._build_key(key)
            value = self._client.get(full_key)
            if ttl is None:
                self._client.persist(full_key)
            elif ttl > 0:
                self._client.expire(full_key, ttl)
            if value is None:
                return default
            # 尝试 JSON 反序列化
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except RedisError as e:
            logger.error(f"Redis 获取缓存失败: key={key}, error={e}")
            return default

    def set(self, key: str, value: Any, ttl: int | None = settings.redis.cache_timeout.default) -> bool:
        """
        设置缓存值

        Args:
            key: 缓存键
            value: 缓存值（自动 JSON 序列化）
            ttl: 过期时间（秒），None 表示永不过期

        Returns:
            是否设置成功
        """
        if not self.is_available:
            return False

        try:
            full_key = self._build_key(key)
            if not isinstance(value, str):
                value = json.dumps(value, ensure_ascii=False)

            if ttl:
                self._client.setex(full_key, ttl, value)
            else:
                self._client.set(full_key, value)
            return True
        except RedisError as e:
            logger.error(f"Redis 设置缓存失败: key={key}, error={e}")
            return False

    def delete(self, key: str) -> bool:
        """
        删除缓存

        Args:
            key: 缓存键

        Returns:
            是否删除成功
        """
        if not self.is_available:
            return False

        try:
            full_key = self._build_key(key)
            self._client.delete(full_key)
            return True
        except RedisError as e:
            logger.error(f"Redis 删除缓存失败: key={key}, error={e}")
            return False

    def exists(self, key: str) -> bool:
        """
        检查键是否存在

        Args:
            key: 缓存键

        Returns:
            键是否存在
        """
        if not self.is_available:
            return False

        try:
            full_key = self._build_key(key)
            return bool(self._client.exists(full_key))
        except RedisError as e:
            logger.error(f"Redis 检查键存在失败: key={key}, error={e}")
            return False

    def expire(self, key: str, ttl: int) -> bool:
        """
        设置键的过期时间

        Args:
            key: 缓存键
            ttl: 过期时间（秒）

        Returns:
            是否设置成功
        """
        if not self.is_available:
            return False

        try:
            full_key = self._build_key(key)
            return bool(self._client.expire(full_key, ttl))
        except RedisError as e:
            logger.error(f"Redis 设置过期时间失败: key={key}, error={e}")
            return False

    def ttl(self, key: str) -> int:
        """
        获取键的剩余过期时间

        Args:
            key: 缓存键

        Returns:
            剩余秒数，-1 表示永不过期，-2 表示键不存在
        """
        if not self.is_available:
            return -2

        try:
            full_key = self._build_key(key)
            return self._client.ttl(full_key)
        except RedisError as e:
            logger.error(f"Redis 获取过期时间失败: key={key}, error={e}")
            return -2

    def incr(self, key: str, amount: int = 1) -> int:
        """
        原子递增

        Args:
            key: 缓存键
            amount: 递增量

        Returns:
            递增后的值
        """
        if not self.is_available:
            return 0

        try:
            full_key = self._build_key(key)
            return self._client.incrby(full_key, amount)
        except RedisError as e:
            logger.error(f"Redis 递增失败: key={key}, error={e}")
            return 0

    def decr(self, key: str, amount: int = 1) -> int:
        """
        原子递减

        Args:
            key: 缓存键
            amount: 递减量

        Returns:
            递减后的值
        """
        if not self.is_available:
            return 0

        try:
            full_key = self._build_key(key)
            return self._client.decrby(full_key, amount)
        except RedisError as e:
            logger.error(f"Redis 递减失败: key={key}, error={e}")
            return 0

    def set_if_not_exists(self, key: str, value: Any, ttl: int | None = settings.redis.cache_timeout.default) -> bool:
        # noinspection SpellCheckingInspection
        """
                设置值（仅在键不存在时）= setnx
                仅当键不存在时设置值（分布式锁常用）

                Args:
                    key: 缓存键
                    value: 缓存值
                    ttl: 过期时间（秒）

                Returns:
                    是否设置成功（键已存在返回 False）
                """
        if not self.is_available:
            return False

        try:
            full_key = self._build_key(key)
            if not isinstance(value, str):
                value = json.dumps(value, ensure_ascii=False)

            if ttl:
                return bool(self._client.set(full_key, value, nx=True, ex=ttl))
            else:
                return bool(self._client.setnx(full_key, value))
        except RedisError as e:
            # noinspection SpellCheckingInspection
            logger.error(f"Redis setnx 失败: key={key}, error={e}")
            return False

    def get_set(self, key: str, value: Any) -> Any:
        """
        设置新值并返回旧值

        Args:
            key: 缓存键
            value: 新值

        Returns:
            旧值，键不存在返回 None
        """
        if not self.is_available:
            return None

        try:
            full_key = self._build_key(key)
            if not isinstance(value, str):
                value = json.dumps(value, ensure_ascii=False)

            old_value = self._client.getset(full_key, value)
            if old_value is None:
                return None
            try:
                return json.loads(old_value)
            except (json.JSONDecodeError, TypeError):
                return old_value
        except RedisError as e:
            logger.error(f"Redis getset 失败: key={key}, error={e}")
            return None

    def mget(self, keys: list[str]) -> dict[str, Any]:
        """
        批量获取缓存值

        Args:
            keys: 缓存键列表

        Returns:
            键值对字典
        """
        if not self.is_available or not keys:
            return {}

        try:
            full_keys = [self._build_key(k) for k in keys]
            values = self._client.mget(full_keys)

            result = {}
            for key, value in zip(keys, values):
                if value is not None:
                    try:
                        result[key] = json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        result[key] = value
            return result
        except RedisError as e:
            logger.error(f"Redis 批量获取失败: keys={keys}, error={e}")
            return {}

    def mset(self, mapping: dict[str, Any], ttl: int | None = settings.redis.cache_timeout.default) -> bool:
        """
        批量设置缓存值

        Args:
            mapping: 键值对字典
            ttl: 过期时间（秒），注意：批量操作不支持单独设置每个键的 TTL

        Returns:
            是否设置成功
        """
        if not self.is_available or not mapping:
            return False

        try:
            # 构建带前缀的键值对
            full_mapping = {}
            for key, value in mapping.items():
                full_key = self._build_key(key)
                if not isinstance(value, str):
                    value = json.dumps(value, ensure_ascii=False)
                full_mapping[full_key] = value

            self._client.mset(full_mapping)

            # 如果需要设置过期时间，需要单独处理每个键
            if ttl:
                pipe = self._client.pipeline()
                for full_key in full_mapping.keys():
                    pipe.expire(full_key, ttl)
                pipe.execute()

            return True
        except RedisError as e:
            logger.error(f"Redis 批量设置失败: error={e}")
            return False

    def keys(self, pattern: str = "*") -> list[str]:
        """
        获取匹配模式的所有键

        Args:
            pattern: 匹配模式（如 "user:*"）

        Returns:
            匹配的键列表（不包含前缀）
        """
        if not self.is_available:
            return []

        try:
            full_pattern = self._build_key(pattern)
            full_keys = self._client.keys(full_pattern)

            # 移除前缀
            prefix_len = len(self._prefix) + 1 if self._prefix else 0
            return [k[prefix_len:] if prefix_len else k for k in full_keys]
        except RedisError as e:
            logger.error(f"Redis 获取键列表失败: pattern={pattern}, error={e}")
            return []

    def flush_db(self) -> bool:
        """
        清空当前数据库（危险操作，慎用！）

        Returns:
            是否清空成功
        """
        if not self.is_available:
            return False

        try:
            self._client.flushdb()
            logger.warning(f"已清空 Redis 数据库: prefix={self._prefix}")
            return True
        except RedisError as e:
            logger.error(f"Redis 清空数据库失败: error={e}")
            return False

    def close(self) -> None:
        """关闭连接"""
        if self._client:
            self._client.close()
            logger.info(f"Redis 连接已关闭: prefix={self._prefix}")

    def ping(self) -> bool:
        """
        测试连接是否正常

        Returns:
            连接是否正常
        """
        if not self.is_available:
            return False

        try:
            return self._client.ping()
        except RedisError:
            return False

    def __enter__(self) -> "RedisService":
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """上下文管理器出口"""
        self.close()

    def __repr__(self) -> str:
        status = "available" if self.is_available else "unavailable"
        return f"RedisService(prefix={self._prefix}, status={status})"
