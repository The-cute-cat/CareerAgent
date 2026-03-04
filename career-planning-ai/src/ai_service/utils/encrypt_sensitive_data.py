import bcrypt

__all__ = ['hash_data', 'check_data']

BCRYPT_ROUNDS = 12


def hash_data(data: str) -> str:
    """使用 bcrypt 对敏感数据进行哈希处理。

    Args:
        data: 需要哈希的原始数据字符串。

    Returns:
        哈希后的字符串，包含 salt 和哈希结果。
    """
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    hashed_bytes = bcrypt.hashpw(data.encode('utf-8'), salt)
    return hashed_bytes.decode('utf-8')

def check_data(data: str, hashed_data: str) -> bool:
    """验证原始数据是否与哈希值匹配。

    Args:
        data: 待验证的原始数据字符串。
        hashed_data: 之前生成的哈希字符串。

    Returns:
        如果原始数据与哈希值匹配返回 True，否则返回 False。
    """
    return bcrypt.checkpw(data.encode('utf-8'), hashed_data.encode('utf-8'))