from langchain_tavily import TavilySearch
import logging
from dotenv import load_dotenv

load_dotenv()

search_tool = TavilySearch(max_results=3, search_depth="advanced")

if __name__ == "__main__":
    # python -m src.app.domain.tools.search_tool

    result = search_tool.invoke({"query": "Quais são as últimas novidades da netflix?"})
    print(result)
    