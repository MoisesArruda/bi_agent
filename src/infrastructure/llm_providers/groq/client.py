import os
from dotenv import load_dotenv
from groq import Groq
from langchain_groq.chat_models import ChatGroq

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

class GroqChatHandler:
    """Classe para gerenciar interações com modelos Groq."""

    def __init__(self):
        self.client = Groq()

    def list_models(self):
        list_models = self.client.models.list().data
        models = [model.id for model in list_models]
        return models

    def get_model(self, model_name: str, temperature: float = 0.0):
        invoke_model = ChatGroq(model_name=model_name, temperature=temperature)
        return invoke_model

    def send_message(self, message: str, temperature: float = 0.0):
        response = self.get_model.invoke(message, temperature=temperature)
        return response

if __name__ == "__main__":

    groq_client = GroqChatHandler()

    models = groq_client.list_models()
    print(models)

    invoke_model = groq_client.get_model(models[0])
    print(invoke_model)

    response = groq_client.send_message("Olá. Com qual modelo estou conversando?")
    print(response)