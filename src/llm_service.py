import os 
from src.prompt_templates import build_prompt
from google import genai


class LLMService:
    def __init__(self):
        api_key=os.getenv("GEMINI_API_KEY")
        if not os.getenv("GEMINI_API_KEY"):
            raise ValueError("GEMINI_API_KEY environment variable is missing!")
        
        # 2. Correct initialization: The client automatically looks for GEMINI_API_KEY
        self.client = genai.Client()
        
        # 3. Prefer a broadly available model, with fallbacks for quota or availability issues.
        self.models = [
            os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
            "gemini-2.0-flash",
            "gemini-2.5-flash-lite",
            "gemini-2.5-pro",
        ]

    def _is_retryable_model_error(self, error: Exception) -> bool:
        message = str(error).lower()
        return any(
            token in message
            for token in (
                "404",
                "not_found",
                "429",
                "resource_exhausted",
                "quota",
                "rate limit",
            )
        )

    def generate_answer(self, question: str, context: str) -> str:
        

        prompt = build_prompt(question, context)

        try:
            last_error = None
            for model_name in self.models:
                try:
                    response = self.client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                    )

                    return response.text.strip()
                except Exception as e:
                    last_error = e
                    if not self._is_retryable_model_error(e):
                        raise

            return (
                "Error generating response: Gemini quota or model availability prevented "
                f"all configured models from answering. Last error: {last_error}"
            )

        except Exception as e:
            return f"Error generating response: {e}"


LLM_Service = LLMService