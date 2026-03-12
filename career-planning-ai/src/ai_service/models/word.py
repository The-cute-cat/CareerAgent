from enum import StrEnum


class WordType(StrEnum):  # 3.11+用strEnum更优(可不使用vaile)，低版本用str, Enum
    """
    Word文档类型枚举（核心维度：格式+可处理性+加密/权限+内容特征+兼容场景）
    设计逻辑：
    1. 基础格式：区分普通/模板/兼容格式（.doc/.docx/.dot/.rtf/WPS）
    2. 可处理性：文本提取/OCR/混合/嵌入式对象/修订/批注
    3. 加密/权限：细分打开密码/编辑密码/权限限制
    4. 异常状态：细分部分损坏/完全损坏，保留兜底UNKNOWN
    """
    # ========== 基础格式 - 可直接提取文本（兼容原设计） ==========
    DOC_TEXT_BASED = "doc_text_based"               # .doc（老版），纯文本可提取
    DOCX_TEXT_BASED = "docx_text_based"             # .docx（新版），纯文本可提取
    DOT_TEXT_BASED = "dot_text_based"               # .dot/.dotx（Word模板），纯文本可提取
    RTF_COMPATIBLE = "rtf_compatible"               # .rtf（兼容格式，Word可打开）
    WPS_TEXT_BASED = "wps_text_based"               # .wps/.wpt（WPS生成，兼容Word）
    # ========== 基础格式 - 需OCR/特殊处理（兼容原设计） ==========
    DOCX_SCANNED = "docx_scanned"                   # .docx，纯扫描图片（需OCR）
    DOCX_MIXED = "docx_mixed"                       # .docx，文本+扫描图片（混合）
    DOCX_EMBEDDED_OBJECT = "docx_embedded_object"   # .docx，含嵌入式Excel/PPT/OLE对象
    # ========== 内容特征 - 专业处理场景 ==========
    DOCX_TRACK_CHANGES = "docx_track_changes"       # .docx，含修订标记（需区分原始/修订文本）
    DOCX_ANNOTATION_DENSE = "docx_annotation_dense" # .docx，批注密集型（需提取批注文本）
    DOCX_LARGE_SCALE = "docx_large_scale"           # .docx，超大文档（1000+页，需分片解析）
    # ========== 加密/权限 - 细分场景（补充原ENCRYPTED） ==========
    ENCRYPTED_OPEN = "encrypted_open"               # 仅需打开密码（解密后可正常处理）
    ENCRYPTED_EDIT = "encrypted_edit"               # 需编辑密码（打开后只读，无法修改）
    PERMISSION_RESTRICTED = "permission_restricted" # 无加密但限制复制/编辑（Word权限设置）
    # ========== 异常状态 - 细分场景（补充原CORRUPTED） ==========
    CORRUPTED_PARTIAL = "corrupted_partial"         # 部分损坏（仍可提取部分文本）
    CORRUPTED_COMPLETE = "corrupted_complete"       # 完全损坏（无法解析任何内容）
    # ========== 特殊状态（兼容原设计） ==========
    MACRO_ENABLED = "macro_enabled"                 # .docm/.dotm，含宏（安全风险）
    # ========== 兜底类型（兼容原设计） ==========
    UNKNOWN = "unknown"                             # 未知类型（非标准Word/无法识别）
