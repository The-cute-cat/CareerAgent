from enum import Enum


class PDFType(str, Enum):
    TEXT_BASED = "text_based"   # 可直接提取文本
    SCANNED = "scanned"         # 扫描件，需要 OCR
    MIXED = "mixed"             # 部分页面有文本，部分没有
    ENCRYPTED = "encrypted"     # 加密文件
    UNKNOWN = "unknown"        # 未知类型

class PDFInfo:
    def __init__(self):
        self.total_pages = 0 # 总页数
        self.text_count = 0 # 文本页数
        self.scanned_count = 0 # 扫描页数
        self.encrypted = False # 是否加密
        self.has_images = False # 是否有图片
        self.total_chars = 0 # 总字符数
        self.text_page_list = [] # 文本页列表
        self.scanned_page_list = [] # 扫描页列表

    def __str__(self):
        return f"PDFInfo(total_pages={self.total_pages}, text_count={self.text_count}, scanned_count={self.scanned_count}, encrypted={self.encrypted}, has_images={self.has_images}, total_chars={self.total_chars}, text_page_list={self.text_page_list}, scanned_page_list={self.scanned_page_list})"

    def __repr__(self):
        return self.__str__()