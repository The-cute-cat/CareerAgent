import os

from ai_service.utils.path_tool import get_abs_path


class PromptLoader:
    pdf_recognition: str

    def __init__(self, prompt_path: str):
        self.pdf_recognition = open(os.path.join(prompt_path, "pdf_recognition.txt"), "r", encoding="utf-8").read()


prompt_loader = PromptLoader(get_abs_path("prompts"))
