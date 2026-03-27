from pathlib import Path

from config import settings


class PromptLoader:
    """
    动态加载提示词文件。
    
    自动扫描指定目录下的所有 .txt 文件，通过属性访问：
        loader.pdf_recognition  # 访问 pdf_recognition.txt
        loader.my_prompt       # 访问 my_prompt.txt
    """

    def __init__(self, prompt_path: str):
        self._prompt_dir = Path(prompt_path)
        self._cache: dict[str, str] = {}
        self._available_prompts: set = set()
        self._scan_prompts()

    def _scan_prompts(self) -> None:
        """扫描目录下所有 .txt 文件"""
        if not self._prompt_dir.exists():
            raise FileNotFoundError(f"提示词目录不存在: {self._prompt_dir}")

        for file in self._prompt_dir.glob("*.txt"):
            self._available_prompts.add(file.stem)

    def _load_prompt(self, name: str) -> str:
        """加载单个提示词文件"""
        file_path = self._prompt_dir / f"{name}.txt"
        if not file_path.exists():
            raise AttributeError(f"提示词 '{name}' 不存在。")
        return file_path.read_text(encoding="utf-8")

    def __getattr__(self, name: str) -> str:
        """动态加载提示词（带缓存）"""
        if name.startswith("_"):
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

        if name not in self._cache:
            self._cache[name] = self._load_prompt(name)
        return self._cache[name]

    def list_prompts(self) -> list[str]:
        """列出所有可用的提示词名称"""
        return sorted(self._available_prompts)

    def reload(self, name: str = None) -> None:
        """
        重新加载提示词。
        
        Args:
            name: 指定提示词名称，为 None 时重载全部
        """
        if name:
            self._cache.pop(name, None)
        else:
            self._cache.clear()
            self._scan_prompts()


prompt_loader = PromptLoader(settings.path_config.prompt)
