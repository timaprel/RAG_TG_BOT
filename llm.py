from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os

class SaigaLLM:
    def __init__(self, model_name=None):
        if model_name is None:
            model_name = "C:/Users/user/.cache/huggingface/hub/models--IlyaGusev--saiga_llama3_8b/snapshots/5bb9917bdb85340549662ebb62c8e522037ff3f3"
        
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Используется устройство: {self.device}")
        print(f"Загрузка модели из: {model_name}")
        
        # Проверяем существование пути
        if not os.path.exists(model_name):
            print(f"Ошибка: Путь {model_name} не существует!")
            raise FileNotFoundError(f"Модель не найдена по пути: {model_name}")
        
        print("Загрузка токенизатора...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name, 
            local_files_only=True  
        )
        
        print("Загрузка модели...")
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto" if torch.cuda.is_available() else None,
            local_files_only=True  
        )
        
        if not torch.cuda.is_available():
            self.model = self.model.to(self.device)
        
        print("Модель успешно загружена!")

    def _build_prompt(self, user_text: str) -> str:
        return (
            "Ты полезный ассистент. Отвечай кратко и по делу.\n\n"
            f"Пользователь: {user_text}\n"
            "Ассистент:"
        )

    def generate(self, text: str, max_tokens: int = 250) -> str:
        prompt = self._build_prompt(text)
        
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        with torch.no_grad():
            output = self.model.generate(
                **inputs,
                max_new_tokens=max_tokens,
                temperature=0.7,
                top_p=0.9,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        generated = output[0][inputs.input_ids.shape[1]:]
        result = self.tokenizer.decode(generated, skip_special_tokens=True)
        
        return result.strip()
    
    def generate_text(self, text: str, max_tokens: int = 250) -> str:
        return self.generate(text, max_tokens)