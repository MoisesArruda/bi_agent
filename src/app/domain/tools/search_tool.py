from langchain_tavily import TavilySearch
from langchain.agents import tool
from dotenv import load_dotenv

load_dotenv()

tool = TavilySearch(max_results=3, search_depth="advanced")

search_query = "O que é BENFORD LAW?"
search_results = tool(search_query)

print(search_results)

# if __name__ == "__main__":
    # python -m src.app.domain.tools.search_tool

    # results = search_tool("Quais são as últimas novidades da netflix?")
    # for result in results:
    #     print(result["results"][0].url)
    