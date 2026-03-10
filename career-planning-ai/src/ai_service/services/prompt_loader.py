import os

from config import settings


class PromptLoader:
    pdf_recognition: str
    image_extract_text: str
    image_extract_visual_content: str

    def __init__(self, prompt_path: str):
        with open(os.path.join(prompt_path, "pdf_recognition.txt"), "r", encoding="utf-8") as f:
            self.pdf_recognition = f.read()
        with open(os.path.join(prompt_path, "image_extract_text.txt"), "r", encoding="utf-8") as f:
            self.image_extract_text = f.read()
        with open(os.path.join(prompt_path, "image_extract_visual_content.txt"), "r", encoding="utf-8") as f:
            self.image_extract_visual_content = f.read()


prompt_loader = PromptLoader(settings.path_config.prompt)

if __name__ == "__main__":
    print(prompt_loader.pdf_recognition)
