import os
from pathlib import Path

__all__ = [
    "get_project_root",
    "abs_path",
    "get_abs_path",
    "get_files_in_dir",
    "get_all_files_in_dir",
    "get_dir_in_dir",
]

from typing import List


def get_project_root() -> str:
    """
    返回项目根目录的绝对路径，例如：D:/../career-planning-ai/
    :return: 项目根目录的绝对路径
    """
    current_script_path = os.path.abspath(__file__)
    current_dir = os.path.dirname(current_script_path)
    return str(Path(os.path.join(current_dir, "../../../")).resolve())


def abs_path(relative_path: str) -> str:
    """
        根据相对路径返回绝对路径，相对于career-planning-ai文件夹
        :param relative_path: 相对路径，例如：/untils/path_tool
        :return: 绝对路径，例如：D:/../career-planning-ai/ + 相对路径
        """
    project_root = get_project_root()
    return str(Path(os.path.join(project_root, relative_path)).resolve())


def get_abs_path(relative_path: str) -> str:
    """
    根据相对路径返回绝对路径，相对于ai_service文件夹
    :param relative_path: 相对路径，例如：/untils/path_tool
    :return: 绝对路径，例如：D:/../career-planning-ai/src/ai_service/ + 相对路径
    """
    project_root = get_project_root()
    return str(Path(os.path.join(project_root, "src/ai_service/", relative_path)).resolve())


def get_files_in_dir(dir_abs_path: str) -> List[str]:
    """
    获取目录下所有文件的绝对路径（不包含子目录）
    :param dir_abs_path: 目录的绝对路径
    :return: 目录下所有文件的绝对路径列表
    """
    return [str(f.resolve()) for f in Path(dir_abs_path).iterdir() if f.is_file()]


def get_all_files_in_dir(dir_abs_path: str) -> List[str]:
    """
    获取目录下所有文件的绝对路径（包含子目录）
    :param dir_abs_path: 目录的绝对路径
    :return: 目录下所有文件的绝对路径列表
    """
    return [str(f.resolve()) for f in Path(dir_abs_path).rglob("*") if f.is_file()]


def get_dir_in_dir(dir_abs_path: str) -> list[str]:
    """
    获取目录下所有子目录的绝对路径
    :param dir_abs_path: 目录的绝对路径
    :return: 目录下所有子目录的绝对路径列表
    """
    return [str(f.resolve()) for f in Path(dir_abs_path).iterdir() if f.is_dir()]


if __name__ == '__main__':
    print("绝对路径：" + abs_path(""))
