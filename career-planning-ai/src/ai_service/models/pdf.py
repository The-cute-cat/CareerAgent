from enum import Enum


class PDFType(str, Enum):
    TEXT_BASED = "text_based"   # 可直接提取文本
    SCANNED = "scanned"         # 扫描件，需要 OCR
    MIXED = "mixed"             # 部分页面有文本，部分没有
    ENCRYPTED = "encrypted"     # 加密文件
    UNKNOWN = "unknown"        # 未知类型