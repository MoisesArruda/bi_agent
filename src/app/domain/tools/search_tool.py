from langchain.tools import TavilySearchResults, tool
import logging

logger = logging.getLogger(__name__)

tavily_tool = TavilySearchResults(max_results=3, search_depth="advanced")

@tool("web_search_tavily", return_direct=True)
def web_search_tavily(query: str) -> str:
    """Busca informações atualizadas na web usando Tavily."""
    search_results = tavily_tool.invoke({"query": query})
    output = []
    for r in search_results:
        output.append(f"🔗 {r['url']}\nResumo: {r['content'][:250]}...")
    return "\n\n".join(output)


if __name__ == "__main__":
    pergunta = "Quais são as novidades da netflix?"
    print(web_search_tavily(pergunta))