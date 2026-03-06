import os

from ai_service.utils.path_tool import get_abs_path


class PromptLoader:
    pdf_recognition: str

    def __init__(self, prompt_path: str):
        with open(os.path.join(prompt_path, "pdf_recognition.txt"), "r", encoding="utf-8") as f:
            self.pdf_recognition = f.read()


prompt_loader = PromptLoader(get_abs_path("prompts"))


if __name__ == "__main__":
    print(prompt_loader.pdf_recognition)
