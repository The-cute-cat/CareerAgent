import sys
import asyncio
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.ai_service.services.word_extractor import WordExtractor  # noqa: E402
from src.ai_service.utils.logger_handler import log  # noqa: E402


TEST_DOC_PATH = Path(__file__).parent / "关于向量数据库的选择.docx"


def test_detect_word_to_enhance_text():
    """
    测试detect_word_to_enhance_text完整流程（直接调用主方法）
    测试用例：tests目录下的"关于向量数据库的选择.docx"
    """
    test_file_path = TEST_DOC_PATH

    print(f"\n测试文件路径: {test_file_path}")
    print(f"文件是否存在: {test_file_path.exists()}")

    if not test_file_path.exists():
        print("❌ 错误：测试文件不存在！")
        return False

    print("\n" + "=" * 60)
    print("调用 detect_word_to_enhance_text 完整流程")
    print("=" * 60)

    try:
        # 直接调用完整的文档处理方法
        extractor = WordExtractor()
        result = asyncio.run(extractor.detect_word_to_enhance_text(str(test_file_path)))

        if result is None:
            print("❌ 错误：提取结果为None！")
            return False

        print(f"✅ 文档处理成功")
        print(f"✅ 提取内容长度: {len(result)} 字符")

        print("\n" + "=" * 60)
        print("提取内容预览（前500字符）")
        print("=" * 60)
        print(result[:500])
        print("=" * 60)

        # 保存完整结果到文件
        output_path = Path(__file__).parent / "test_output.txt"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"\n✅ 完整提取内容已保存到: {output_path}")

        return True

    except Exception as e:
        print(f"❌ 文档处理失败: {e}")
        log.error(f"文档处理异常: {e}", exc_info=True)
        return False


def test_word_type_detection():
    """
    测试Word文档类型检测功能
    """
    test_file_path = TEST_DOC_PATH

    if not test_file_path.exists():
        print("❌ 错误：测试文件不存在！")
        return False

    print("\n检测Word文档类型...")
    word_type = WordExtractor.detect_word_type(str(test_file_path))

    print(f"✅ 文档类型: {word_type}")
    return True


def test_has_images():
    """
    测试文档是否包含图片
    """
    test_file_path = TEST_DOC_PATH

    if not test_file_path.exists():
        print("❌ 错误：测试文件不存在！")
        return False

    print("\n检测文档是否包含图片...")
    has_images = WordExtractor._has_images(test_file_path)

    print(f"✅ 包含图片: {has_images}")
    return True


def test_extract_text():
    """
    测试文本提取功能（已弃用方法 - 仅用于向后兼容测试）
    注意：_extract_text 已弃用，推荐使用 detect_word_to_enhance_text
    """
    test_file_path = TEST_DOC_PATH

    if not test_file_path.exists():
        print("❌ 错误：测试文件不存在！")
        return False

    print("\n⚠️  测试已弃用的 _extract_text 方法...")
    word_type = WordExtractor.detect_word_type(str(test_file_path))
    texts = WordExtractor._extract_text(str(test_file_path), word_type)

    print(f"✅ 提取到 {len(texts)} 个段落")
    if texts:
        print(f"第一个段落预览: {texts[0][:100]}...")
    print("ℹ️  提示：此方法已弃用，请使用 detect_word_to_enhance_text")
    return True


def test_extract_images():
    """
    测试图片提取功能（并将图片保存到tests/extracted_images目录）
    """
    test_file_path = TEST_DOC_PATH

    if not test_file_path.exists():
        print("❌ 错误：测试文件不存在！")
        return False

    print("\n提取文档图片...")
    word_type = WordExtractor.detect_word_type(str(test_file_path))
    images = WordExtractor._extract_images_bytes(str(test_file_path), word_type)

    print(f"✅ 提取到 {len(images)} 张图片")

    if len(images) > 0:
        # 创建保存图片的目录
        output_dir = Path(__file__).parent / "extracted_images"
        output_dir.mkdir(exist_ok=True)
        print(f"\n保存图片到: {output_dir}")

        # 保存每张图片
        for i, (img_bytes, suffix) in enumerate(images):
            output_path = output_dir / f"image_{i+1}.{suffix}"
            with open(output_path, "wb") as f:
                f.write(img_bytes)
            print(
                f"  图片 {i+1}: {len(img_bytes)} 字节, "
                f"格式={suffix} -> {output_path.name}"
            )

        print(f"\n✅ 所有图片已保存到: {output_dir}")
    else:
        print("ℹ️  文档中没有图片")

    return True


def test_magic_number():
    """
    测试魔数获取功能
    """
    test_file_path = TEST_DOC_PATH

    if not test_file_path.exists():
        print("❌ 错误：测试文件不存在！")
        return False

    print("\n获取文件魔数...")
    magic_number = WordExtractor.get_magic_number(str(test_file_path))

    print(f"✅ 文件魔数: {magic_number}")
    return True


def test_list_to_string():
    """
    测试列表转字符串功能
    """
    print("\n测试列表转字符串...")
    test_list = ["第一行", "第二行", "第三行"]
    result = WordExtractor.list_to_string(test_list)

    expected = "第一行\n第二行\n第三行"
    if result == expected:
        print(f"✅ 转换成功: {repr(result)}")
        return True
    else:
        print(f"❌ 转换失败: 期望 {repr(expected)}, 得到 {repr(result)}")
        return False


def test_detect_images_api():
    """
    专门测试阿里云API图片识别功能（含详细调试信息）
    """
    test_file_path = TEST_DOC_PATH

    if not test_file_path.exists():
        print("❌ 错误：测试文件不存在！")
        return False

    print("\n" + "=" * 60)
    print("阿里云API图片识别测试")
    print("=" * 60)

    # 提取图片
    print("\n1. 提取图片...")
    try:
        word_type = WordExtractor.detect_word_type(str(test_file_path))
        images = WordExtractor._extract_images_bytes(str(test_file_path), word_type)
        print(f"✅ 提取到 {len(images)} 张图片")

        if len(images) == 0:
            print("ℹ️  文档中没有图片，无法测试API调用")
            return True

        # 保存提取的图片
        output_dir = Path(__file__).parent / "extracted_images"
        output_dir.mkdir(exist_ok=True)
        print(f"   保存图片到: {output_dir}")
        for i, (img_bytes, suffix) in enumerate(images):
            output_path = output_dir / f"image_{i+1}.{suffix}"
            with open(output_path, "wb") as f:
                f.write(img_bytes)
            print(f"   - image_{i+1}.{suffix} ({len(img_bytes)} 字节)")

    except Exception as e:
        print(f"❌ 图片提取失败: {e}")
        log.error(f"图片提取异常: {e}", exc_info=True)
        return False
    
    from config import settings
    # 初始化WordExtractor
    print("\n2. 初始化WordExtractor和AI服务...")
    try:
        extractor = WordExtractor()
        print("✅ 初始化成功")
        print(f"   模型名称: {settings.llm.model_name}")
        print(f"   API URL: {settings.llm.base_url}")
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        log.error(f"初始化异常: {e}", exc_info=True)
        return False

    # 逐张测试图片识别
    print(f"\n3. 开始识别 {len(images)} 张图片...")
    descriptions = []
    for i, (img_bytes, suffix) in enumerate(images):
        print(f"\n  处理图片 {i+1}/{len(images)}:")
        print(f"    - 大小: {len(img_bytes)} 字节")
        print(f"    - 格式: {suffix}")

        try:
            result = asyncio.run(extractor._detect_images(img_bytes, suffix))

            if result:
                print("    ✅ 识别成功")
                print(f"    - 识别结果长度: {len(result)} 字符")
                print(f"    - 结果预览: {result[:100]}...")
                descriptions.append(result)
            else:
                print("    ⚠️  API返回空结果")
        except Exception as e:
            print(f"    ❌ 识别失败: {e}")
            log.error(f"图片{i+1}识别异常: {e}", exc_info=True)
            print("    详细错误:")
            print(f"      类型: {type(e).__name__}")
            print(f"      消息: {str(e)}")

    # 总结
    print("\n" + "=" * 60)
    print(f"识别总结: 成功识别 {len(descriptions)}/{len(images)} 张图片")
    print("=" * 60)

    return len(descriptions) > 0 or len(images) == 0


def run_all_tests():
    """
    运行所有测试
    """
    print("\n" + "=" * 60)
    print("开始运行Word文档提取测试")
    print("=" * 60)

    tests = [
        ("魔数获取测试", test_magic_number),
        ("Word类型检测测试", test_word_type_detection),
        ("图片检测测试", test_has_images),
        ("图片提取测试", test_extract_images),
        ("列表转字符串测试", test_list_to_string),
        ("阿里云API图片识别测试", test_detect_images_api),
        ("完整文档提取测试（主方法）", test_detect_word_to_enhance_text),
        ("文本提取测试（已弃用）", test_extract_text),
    ]

    results = []
    for test_name, test_func in tests:
        print("\n" + "=" * 60)
        print(f"运行测试: {test_name}")
        print("=" * 60)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            log.error(f"测试 {test_name} 失败: {e}")
            results.append((test_name, False))

    # 输出测试总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_all_tests()
