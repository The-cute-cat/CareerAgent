import os

from config import settings


class PromptLoader:
    pdf_recognition: str
    image_extract_text: str
    image_extract_visual_content: str
    test_question_generation_skill: str
    test_question_generation_tool: str
    test_question_censorship: str
    test_question_modification: str
    answer_evaluation: str

    def __init__(self, prompt_path: str):
        with open(os.path.join(prompt_path, "pdf_recognition.txt"), "r", encoding="utf-8") as f:
            self.pdf_recognition = f.read()
        with open(os.path.join(prompt_path, "image_extract_text.txt"), "r", encoding="utf-8") as f:
            self.image_extract_text = f.read()
        with open(os.path.join(prompt_path, "image_extract_visual_content.txt"), "r", encoding="utf-8") as f:
            self.image_extract_visual_content = f.read()
        with open(os.path.join(prompt_path, "test_question_generation_skill.txt"), "r", encoding="utf-8") as f:
            self.test_question_generation_skill = f.read()
        with open(os.path.join(prompt_path, "test_question_generation_tool.txt"), "r", encoding="utf-8") as f:
            self.test_question_generation_tool = f.read()
        with open(os.path.join(prompt_path, "answer_evaluation.txt"), "r", encoding="utf-8") as f:
            self.answer_evaluation = f.read()
        with open(os.path.join(prompt_path, "test_question_censorship.txt"), "r", encoding="utf-8") as f:
            self.test_question_censorship = f.read()
        with open(os.path.join(prompt_path, "test_question_modification.txt"), "r", encoding="utf-8") as f:
            self.test_question_modification = f.read()


prompt_loader = PromptLoader(settings.path_config.prompt)

if __name__ == "__main__":
    print(prompt_loader.pdf_recognition)
