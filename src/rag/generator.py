from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ResponseGenerator:
    """Gera respostas baseadas em contexto."""
    
    def generate(self, query: str, context: List[Dict[str, Any]]) -> str:
        """Gera resposta final."""
        if not context:
            return "Não encontrei informações relevantes para sua pergunta."
        
        # Construir contexto
        context_text = "\n".join([doc.get("text", doc.get("page_content", "")) for doc in context])
        
        # Resposta simples (você pode integrar com LLM depois)
        response = f"""Baseado no contexto encontrado:

        {context_text}

        Resposta: Esta é uma resposta gerada baseada no contexto fornecido. Para uma resposta mais elaborada, integre com um modelo de linguagem."""
        
        return response

if __name__ == "__main__":
    # python -m src.rag.generator
    
    generator = ResponseGenerator()
    context = [{"text": "A Netflix é uma empresa de streaming de vídeo que oferece uma ampla seleção de filmes, séries e programas de TV."}]
    response = generator.generate("Qual é a visão de longo prazo da Netflix?", context)
    print(response)
