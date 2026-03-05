from dataclasses import dataclass
from typing import List, Dict

__all__ = ["FileSignature", "FILE_SIGNATURES", "DANGEROUS_EXTENSIONS", "SAFE_EXTENSIONS"]


@dataclass
class FileSignature:
    """文件签名定义"""
    extension: str
    mime_type: str
    description: str
    magic_bytes: List[bytes]  # 支持多个特征码
    max_offset: int = 0  # 最大偏移量


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
        magic_bytes=[b"RIFF", b"WEBP"]
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
    "json": FileSignature(
        extension="json",
        mime_type="application/json",
        description="JSON Data",
        magic_bytes=[b"{", b"["]
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
    "pdf", "png", "jpg", "jpeg", "gif", "bmp", "webp",
    "doc", "docx", "xls", "xlsx", "ppt", "pptx",
    "txt", "csv", "json", "xml", "html",
    "zip", "rar", "7z", "gz"
}
