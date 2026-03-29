__all__ = ['fix_json_file']
# -*- coding: utf-8 -*-
"""
JSON 格式自动修复工具
支持任意文件，修复后保存到原位置
"""

import json
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import Tuple, List, Dict, Any, Optional, Union
from ai_service.utils.logger_handler import log


class JSONFixer:
    """JSON 格式修复器"""

    # 常见 JSON 问题及修复方法
    FIX_METHODS = [
        'remove_bom',
        'remove_comments',
        'fix_trailing_commas',
        'fix_single_quotes',
        'fix_unquoted_keys',
        'fix_control_characters',
        'merge_multiple_arrays',
        'extract_first_array',
        'extract_json_objects',
    ]

    @staticmethod
    def remove_bom(content: str) -> str:
        """移除 BOM 头"""
        if content.startswith('\ufeff'):
            return content[1:]
        return content

    @staticmethod
    def remove_comments(content: str) -> str:
        """移除 JSON 注释（// 和 /* */）"""
        # 移除单行注释（注意不要移除字符串内的 //）
        lines = []
        in_string = False
        escape_next = False

        for line in content.split('\n'):
            new_line = []
            i = 0
            while i < len(line):
                char = line[i]

                if escape_next:
                    new_line.append(char)
                    escape_next = False
                    i += 1
                    continue

                if char == '\\':
                    new_line.append(char)
                    escape_next = True
                    i += 1
                    continue

                if char == '"' and not escape_next:
                    in_string = not in_string
                    new_line.append(char)
                    i += 1
                    continue

                if not in_string and i + 1 < len(line):
                    # 检查 // 注释
                    if line[i:i + 2] == '//':
                        break  # 忽略该行剩余部分
                    # 检查 /* 注释
                    if line[i:i + 2] == '/*':
                        # 查找 */
                        end_idx = line.find('*/', i)
                        if end_idx != -1:
                            i = end_idx + 2
                            continue

                new_line.append(char)
                i += 1

            lines.append(''.join(new_line))

        content = '\n'.join(lines)

        # 移除多行注释 /* */
        content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)

        return content

    @staticmethod
    def fix_trailing_commas(content: str) -> str:
        """修复尾部逗号（,] 或 ,}）"""
        # 移除 ] 或 } 前的逗号（包括中间的空白和注释）
        content = re.sub(r',(\s*[}\]])', r'\1', content)
        return content

    @staticmethod
    def fix_single_quotes(content: str) -> str:
        """修复单引号（将单引号转换为双引号）"""
        # 注意：这个修复可能有风险，只在字符串上下文中替换
        # 简单实现：替换所有单引号为双引号
        # 更安全的实现需要解析字符串上下文

        # 匹配键名的单引号
        content = re.sub(r"'([^']+)'(\s*:)", r'"\1"\2', content)

        # 匹配字符串值的单引号（不在键名位置）
        # 这个比较复杂，简单处理：替换所有独立的单引号字符串
        content = re.sub(r":\s*'([^']*)'", r': "\1"', content)

        return content

    @staticmethod
    def fix_unquoted_keys(content: str) -> str:
        """修复未加引号的键名"""
        # 匹配未加引号的键名：word:
        content = re.sub(r'([{,]\s*)([a-zA-Z_][a-zA-Z0-9_]*)\s*:', r'\1"\2":', content)
        return content

    @staticmethod
    def fix_control_characters(content: str) -> str:
        """修复控制字符（如 \n, \t, \r 在字符串外）"""
        # 这个比较复杂，通常 JSON 解析器会处理
        # 这里只做简单的清理
        content = content.replace('\r\n', '\n')
        content = content.replace('\r', '\n')
        return content

    @staticmethod
    def extract_json_arrays(content: str) -> List[str]:
        """提取所有完整的 JSON 数组"""
        arrays = []
        depth = 0
        start = -1
        in_string = False
        escape_next = False

        for i, char in enumerate(content):
            if escape_next:
                escape_next = False
                continue

            if char == '\\' and in_string:
                escape_next = True
                continue

            if char == '"' and not escape_next:
                in_string = not in_string
                continue

            if not in_string:
                if char == '[':
                    if depth == 0:
                        start = i
                    depth += 1
                elif char == ']':
                    depth -= 1
                    if depth == 0 and start != -1:
                        arrays.append(content[start:i + 1])
                        start = -1

        return arrays

    @staticmethod
    def extract_json_objects(content: str) -> List[str]:
        """提取所有完整的 JSON 对象（当没有数组时）"""
        objects = []
        depth = 0
        start = -1
        in_string = False
        escape_next = False

        for i, char in enumerate(content):
            if escape_next:
                escape_next = False
                continue

            if char == '\\' and in_string:
                escape_next = True
                continue

            if char == '"' and not escape_next:
                in_string = not in_string
                continue

            if not in_string:
                if char == '{':
                    if depth == 0:
                        start = i
                    depth += 1
                elif char == '}':
                    depth -= 1
                    if depth == 0 and start != -1:
                        objects.append(content[start:i + 1])
                        start = -1

        return objects

    @staticmethod
    def merge_json_items(items: List[str]) -> List[Dict[str, Any]]:
        """合并多个 JSON 项（数组或对象）"""
        all_items = []
        for item_str in items:
            try:
                item = json.loads(item_str)
                if isinstance(item, list):
                    all_items.extend(item)
                elif isinstance(item, dict):
                    all_items.append(item)
            except json.JSONDecodeError:
                continue
        return all_items

    @staticmethod
    def try_parse(content: str) -> Tuple[bool, Any, str]:
        """
        尝试解析 JSON

        返回:
            (success, data, error_message)
        """
        try:
            data = json.loads(content)
            return True, data, ""
        except json.JSONDecodeError as e:
            return False, None, f"{e.msg} (第 {e.lineno} 行，第 {e.colno} 列)"

    @staticmethod
    def fix(file_path: Union[str, Path],
            encoding: str = 'utf-8',
            create_backup: bool = False,
            verbose: bool = True) -> Tuple[bool, str, Dict[str, Any]]:
        """
        修复 JSON 文件

        参数:
            file_path: 文件路径
            encoding: 文件编码
            create_backup: 是否创建备份
            verbose: 是否输出详细日志

        返回:
            (success, message, report)
            report 包含：
                - original_size: 原始文件大小
                - fixed_size: 修复后文件大小
                - fixes_applied: 应用的修复方法列表
                - backup_path: 备份文件路径
                - data_count: 数据条数
        """
        path = Path(file_path)

        report = {
            'success': False,
            'original_size': 0,
            'fixed_size': 0,
            'fixes_applied': [],
            'backup_path': None,
            'data_count': 0,
            'errors': []
        }

        if verbose:
            log.info(f"\n🔧 正在修复：{path.absolute()}")

        # 检查文件
        if not path.exists():
            msg = f"文件不存在：{path.absolute()}"
            report['errors'].append(msg)
            return False, msg, report

        if not path.is_file():
            msg = f"路径不是文件：{path.absolute()}"
            report['errors'].append(msg)
            return False, msg, report

        # 读取文件
        try:
            with open(path, 'r', encoding=encoding) as f:
                original_content = f.read()
            report['original_size'] = len(original_content.encode('utf-8'))
        except Exception as e:
            msg = f"读取文件失败：{e}"
            report['errors'].append(msg)
            return False, msg, report

        # 如果已经是有效 JSON，无需修复
        success, data, error = JSONFixer.try_parse(original_content)
        if success:
            if verbose:
                log.info("✓ 文件格式正确，无需修复")
            report['success'] = True
            report['data_count'] = len(data) if isinstance(data, list) else 1
            return True, "✓ 文件格式正确，无需修复", report

        if verbose:
            log.error(f"⚠ 检测到格式问题：{error}")
            log.info("🔍 开始尝试修复...")

        # 创建备份
        backup_path = None
        if create_backup:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = path.parent / f"{path.stem}.backup_{timestamp}{path.suffix}"
            try:
                shutil.copy2(path, backup_path)
                report['backup_path'] = str(backup_path.absolute())
                if verbose:
                    log.info(f"✓ 已创建备份：{backup_path.name}")
            except Exception as e:
                if verbose:
                    log.info(f"⚠ 创建备份失败：{e}")

        # 逐步应用修复方法
        content = original_content
        fixes_applied = []

        for method_name in JSONFixer.FIX_METHODS:
            method = getattr(JSONFixer, method_name, None)
            if not method:
                continue

            # 特殊处理：extract 和 merge 方法
            if method_name.startswith('extract_') or method_name == 'merge_json_items':
                continue

            try:
                new_content = method(content)
                if new_content != content:
                    fixes_applied.append(method_name)
                    content = new_content

                    # 尝试解析
                    success, data, error = JSONFixer.try_parse(content)
                    if success:
                        if verbose:
                            log.info(f"✓ 应用修复：{method_name}")
                        break
            except Exception as e:
                if verbose:
                    log.error(f"⚠ 修复方法 {method_name} 失败：{e}")
                continue

        # 如果还没成功，尝试提取并合并数组/对象
        if not success:
            # 尝试提取数组
            arrays = JSONFixer.extract_json_arrays(content)
            if len(arrays) > 0:
                if verbose:
                    log.info(f"📊 发现 {len(arrays)} 个 JSON 数组")
                data_list = JSONFixer.merge_json_items(arrays)
                if data_list:
                    success = True
                    data = data_list
                    fixes_applied.append('merge_multiple_arrays')
                    if verbose:
                        log.info(f"✓ 合并 {len(arrays)} 个数组，共 {len(data_list)} 条数据")

            # 尝试提取对象
            if not success:
                objects = JSONFixer.extract_json_objects(content)
                if len(objects) > 0:
                    if verbose:
                        log.info(f"📊 发现 {len(objects)} 个 JSON 对象")
                    data_list = JSONFixer.merge_json_items(objects)
                    if data_list:
                        success = True
                        data = data_list
                        fixes_applied.append('extract_json_objects')
                        if verbose:
                            log.info(f"✓ 提取 {len(objects)} 个对象，共 {len(data_list)} 条数据")

        # 如果修复成功，保存文件
        if success:
            try:
                # 确保数据是列表
                if not isinstance(data, list):
                    data = [data]

                # 保存修复后的内容
                fixed_content = json.dumps(data, ensure_ascii=False, indent=2)

                with open(path, 'w', encoding=encoding) as f:
                    f.write(fixed_content)

                report['success'] = True
                report['fixed_size'] = len(fixed_content.encode('utf-8'))
                report['fixes_applied'] = fixes_applied
                report['data_count'] = len(data)

                msg = f"✓ 修复成功！应用了 {len(fixes_applied)} 个修复方法，共 {len(data)} 条数据"

                if verbose:
                    log.info(f"\n{msg}")
                    if fixes_applied:
                        log.info("📝 应用的修复方法:")
                        for fix in fixes_applied:
                            log.info(f"  - {fix}")

                return True, msg, report

            except Exception as e:
                msg = f"保存文件失败：{e}"
                report['errors'].append(msg)

                # 恢复备份
                if backup_path and create_backup:
                    try:
                        shutil.copy2(backup_path, path)
                        if verbose:
                            log.info("⚠ 已恢复原始文件")
                    except:
                        pass

                return False, msg, report
        else:
            msg = "✗ 无法自动修复，请手动检查文件格式"
            report['errors'].append(msg)

            if verbose:
                log.info(f"\n{msg}")
                log.info("\n💡 建议:")
                log.info("  1. 检查第 91 行或第 404 行附近的格式")
                log.info("  2. 确保只有一个最外层数组 [...]")
                log.info("  3. 移除所有注释（// 和 /* */）")
                log.info("  4. 检查括号是否匹配")

            # 恢复备份
            if backup_path and create_backup:
                try:
                    shutil.copy2(backup_path, path)
                    if verbose:
                        log.info("⚠ 已恢复原始文件")
                except:
                    pass

            return False, msg, report


# ==========================================
# 便捷函数
# ==========================================

def fix_json_file(file_path: Union[str, Path],
                  encoding: str = 'utf-8',
                  create_backup: bool = False,
                  verbose: bool = True) -> Tuple[bool, str]:
    """
    修复 JSON 文件的便捷函数

    参数:
        file_path: 文件路径
        encoding: 文件编码
        create_backup: 是否创建备份
        verbose: 是否输出详细日志

    返回:
        (success, message)
    """
    success, message, report = JSONFixer.fix(
        file_path,
        encoding=encoding,
        create_backup=create_backup,
        verbose=verbose
    )
    return success, message




# ==========================================
# 使用示例
# ==========================================

if __name__ == "__main__":
    # 示例 1: 修复单个文件
    print("=" * 70)
    print("示例 1: 修复单个文件")
    print("=" * 70)

    # file_path = r"E:\软件工程相关资料\项目比赛\服创2026\岗位.json"
    file_path = r"E:\软件工程相关资料\项目比赛\服创2026\3.txt"

    success, message = fix_json_file(file_path, verbose=True)

    if success:
        print(f"\n✅ {message}")
    else:
        print(f"\n❌ {message}")

    print("\n" + "="*70)
    print("示例 2: 批量修复目录")
    print("="*70)


