from dataclasses import dataclass
from typing import List, Dict

__all__ = [
    "FileSignature",
    "FILE_SIGNATURES",
    "DANGEROUS_EXTENSIONS",
    "SAFE_EXTENSIONS",
    "OLE2_SIGNATURES",
    "ZIP_SIGNATURES",
]


@dataclass
class FileSignature:
    """文件签名定义"""
    extension: str
    mime_type: str
    description: str
    magic_bytes: List[bytes]  # 支持多个特征码
    max_offset: int = 0  # 最大偏移量


@dataclass
class DeepCheckSignature:
    """深度检测签名定义"""
    extension: str
    mime_type: str
    description: str
    markers: List[bytes]  # 文件内部特征标记


# noinspection SpellCheckingInspection
FILE_SIGNATURES: Dict[str, FileSignature] = {
    # PDF
    "pdf": FileSignature(
        extension="pdf",
        mime_type="application/pdf",
        description="Portable Document Format",
        magic_bytes=[b"%PDF-"]
    ),

    # 图片
    "png": FileSignature(
        extension="png",
        mime_type="image/png",
        description="Portable Network Graphics",
        magic_bytes=[b"\x89PNG\r\n\x1a\n"]
    ),
    "jpg": FileSignature(
        extension="jpg",
        mime_type="image/jpeg",
        description="JPEG Image",
        magic_bytes=[b"\xff\xd8\xff"]
    ),
    "gif": FileSignature(
        extension="gif",
        mime_type="image/gif",
        description="Graphics Interchange Format",
        magic_bytes=[b"GIF87a", b"GIF89a"]
    ),
    "bmp": FileSignature(
        extension="bmp",
        mime_type="image/bmp",
        description="Bitmap Image",
        magic_bytes=[b"BM"]
    ),
    "webp": FileSignature(
        extension="webp",
        mime_type="image/webp",
        description="WebP Image",
        magic_bytes=[b"RIFF\x00\x00\x00\x00WEBP"]  # RIFF + 4字节大小 + WEBP
    ),
    "ico": FileSignature(
        extension="ico",
        mime_type="image/x-icon",
        description="Icon Image",
        magic_bytes=[b"\x00\x00\x01\x00"]
    ),
    "tiff": FileSignature(
        extension="tiff",
        mime_type="image/tiff",
        description="TIFF Image",
        magic_bytes=[b"II*\x00", b"MM\x00*"]  # 小端/大端
    ),

    # 文档
    "docx": FileSignature(
        extension="docx",
        mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        description="Microsoft Word Document",
        magic_bytes=[b"PK\x03\x04"]  # ZIP 格式
    ),
    "xlsx": FileSignature(
        extension="xlsx",
        mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        description="Microsoft Excel Spreadsheet",
        magic_bytes=[b"PK\x03\x04"]
    ),
    "pptx": FileSignature(
        extension="pptx",
        mime_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        description="Microsoft PowerPoint Presentation",
        magic_bytes=[b"PK\x03\x04"]
    ),
    "doc": FileSignature(
        extension="doc",
        mime_type="application/msword",
        description="Microsoft Word 97-2003",
        magic_bytes=[b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"]
    ),
    "xls": FileSignature(
        extension="xls",
        mime_type="application/vnd.ms-excel",
        description="Microsoft Excel 97-2003",
        magic_bytes=[b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1"]
    ),

    # 压缩文件
    "zip": FileSignature(
        extension="zip",
        mime_type="application/zip",
        description="ZIP Archive",
        magic_bytes=[b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"]
    ),
    "rar": FileSignature(
        extension="rar",
        mime_type="application/vnd.rar",
        description="RAR Archive",
        magic_bytes=[b"Rar!\x1a\x07\x00", b"Rar!\x1a\x07\x01\x00"]
    ),
    "7z": FileSignature(
        extension="7z",
        mime_type="application/x-7z-compressed",
        description="7-Zip Archive",
        magic_bytes=[b"7z\xbc\xaf\x27\x1c"]
    ),
    "gz": FileSignature(
        extension="gz",
        mime_type="application/gzip",
        description="GZIP Compressed",
        magic_bytes=[b"\x1f\x8b\x08"]
    ),

    # 可执行文件 (危险)
    "exe": FileSignature(
        extension="exe",
        mime_type="application/x-msdownload",
        description="Windows Executable",
        magic_bytes=[b"MZ"]
    ),
    "dll": FileSignature(
        extension="dll",
        mime_type="application/x-msdownload",
        description="Windows Dynamic Link Library",
        magic_bytes=[b"MZ"]
    ),

    # 其他
    "txt": FileSignature(
        extension="txt",
        mime_type="text/plain",
        description="Plain Text",
        magic_bytes=[]  # 文本文件无特征码
    ),
    "csv": FileSignature(
        extension="csv",
        mime_type="text/csv",
        description="Comma-Separated Values",
        magic_bytes=[]
    ),
    "rtf": FileSignature(
        extension="rtf",
        mime_type="application/rtf",
        description="Rich Text Format",
        magic_bytes=[b"{\\rtf"]
    ),
    "json": FileSignature(
        extension="json",
        mime_type="application/json",
        description="JSON Data",
        magic_bytes=[]  # JSON 无固定魔数，由后续检测
    ),
    "xml": FileSignature(
        extension="xml",
        mime_type="application/xml",
        description="XML Document",
        magic_bytes=[b"<?xml"]
    ),
    "html": FileSignature(
        extension="html",
        mime_type="text/html",
        description="HTML Document",
        magic_bytes=[b"<!DOCTYPE", b"<html", b"<HTML"]
    ),
}

# 危险文件类型
DANGEROUS_EXTENSIONS = {
    "exe", "dll", "bat", "cmd", "sh", "bash", "ps1",
    "vbs", "js", "jar", "app", "msi", "scr", "pif"
}

# 安全文件类型 (允许上传)
SAFE_EXTENSIONS = {
    "pdf", "png", "jpg", "jpeg", "gif", "bmp", "webp", "ico", "tiff",
    "doc", "docx", "xls", "xlsx", "ppt", "pptx", "rtf",
    "txt", "csv", "json", "xml", "html",
    "zip", "rar", "7z", "gz"
}

OLE2_SIGNATURES: Dict[str, DeepCheckSignature] = {
    "xls": DeepCheckSignature(
        extension="xls",
        mime_type="application/vnd.ms-excel",
        description="Microsoft Excel 97-2003",
        markers=[b"Workbook", b"\x00W\x00o\x00r\x00k\x00b\x00o\x00o\x00k", b"Book"]
    ),
    "doc": DeepCheckSignature(
        extension="doc",
        mime_type="application/msword",
        description="Microsoft Word 97-2003",
        markers=[b"WordDocument", b"\x00W\x00o\x00r\x00d\x00D\x00o\x00c\x00u\x00m\x00e\x00n\x00t"]
    ),
    "ppt": DeepCheckSignature(
        extension="ppt",
        mime_type="application/vnd.ms-powerpoint",
        description="Microsoft PowerPoint 97-2003",
        markers=[
            b"PowerPoint Document",
            b"Current User",
            b"\x00P\x00o\x00w\x00e\x00r\x00P\x00o\x00i\x00n\x00t\x00 \x00D\x00o\x00c\x00u\x00m\x00e\x00n\x00t",
        ]
    ),
}

# noinspection SpellCheckingInspection
ZIP_SIGNATURES: Dict[str, DeepCheckSignature] = {
    "xlsx": DeepCheckSignature(
        extension="xlsx",
        mime_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        description="Microsoft Excel Spreadsheet",
        markers=[b"xl/workbook.xml"]
    ),
    "docx": DeepCheckSignature(
        extension="docx",
        mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        description="Microsoft Word Document",
        markers=[b"word/document.xml"]
    ),
    "pptx": DeepCheckSignature(
        extension="pptx",
        mime_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        description="Microsoft PowerPoint Presentation",
        markers=[b"ppt/presentation.xml"]
    ),
}
