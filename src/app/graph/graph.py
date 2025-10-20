from langgraph.graph import StateGraph, START, END
from src.app.graph.nodes import *
from src.app.graph.routers import *
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.base import BaseCheckpointSaver
import csv

def create_workflow(memory: BaseCheckpointSaver = MemorySaver()):
    # Criar o workflow
    workflow = StateGraph(AgentState)

    # Adicionar nós
    workflow.add_node("Supervisor_Agent", supervisor_agent_node)
    workflow.add_node("Search_Tables_and_Schemas", search_tables_and_schemas)
    workflow.add_node("Redis_With_Cache", redis_with_cache)
    workflow.add_node("Agent_SQL_Writer", agent_sql_writer_node)
    workflow.add_node("Agent_SQL_Validator", agent_sql_validator_node)
    workflow.add_node("Agent_BI", agent_bi_expert_node)
    workflow.add_node("Agent_Python_Generator", agent_python_code_data_visualization_generator_node)
    workflow.add_node("Agent_Python_Validator", agent_python_code_data_visualization_validator_node)

    # Adicionar edges simples
    workflow.add_edge(START, "Supervisor_Agent")

    workflow.add_conditional_edges(
        'Supervisor_Agent',
        route_supervisor,
        {
            'Search_Tables_and_Schemas': 'Search_Tables_and_Schemas',
            END: END
        }
    )

    workflow.add_conditional_edges(
        "Search_Tables_and_Schemas", route_search_tables_and_schemas,
        {
            "Redis_With_Cache": "Redis_With_Cache",
            END: END
        }
    )

    workflow.add_conditional_edges(
        "Redis_With_Cache", route_with_cache,
        {
            "Agent_SQL_Validator": "Agent_SQL_Validator",
            "Agent_SQL_Writer": "Agent_SQL_Writer",
        }
    )

    workflow.add_edge("Agent_SQL_Writer", "Agent_SQL_Validator")

    workflow.add_conditional_edges(
        'Agent_SQL_Validator',
        route_sql_validator,
        {
            'Agent_BI': 'Agent_BI',
            'Agent_SQL_Writer': 'Agent_SQL_Writer'
        }
    )

    workflow.add_conditional_edges(
        "Agent_BI",
        route_to_python_code,
        {"Agent_Python_Generator": "Agent_Python_Generator",
        "Supervisor_Agent": "Supervisor_Agent"}
    )

    workflow.add_edge("Agent_Python_Generator", "Agent_Python_Validator")

    workflow.add_conditional_edges(
        'Agent_Python_Validator',
        route_python_validator,
        {
            "Supervisor_Agent": "Supervisor_Agent",
            'Agent_Python_Generator': 'Agent_Python_Generator'
        }
    )

    # Compilar o workflow
    app = workflow.compile(checkpointer=memory)

    return app

if __name__ == "__main__":
    # python -m src.app.graph.graph
    # save_messages(data, "src/app/data/historic_data.csv")

    question = "Quais oas novidades da netflix?"
    # question = "Olá, como você está?"

    app = create_workflow()
    thread = {"configurable": {"thread_id": "abc345"}}
    # final_state = app.invoke({"question": question}, config=config)

    for state in app.stream({"question": question}, config=thread):
        for key,value in state.items():
            # print(key)
            print(value)
        # print(state)
        # agent = app.get_state(thread).metadata['writes']
        # print(agent)
        # agent_name = list(agent)[0]
        # print(agent_name)
        # print(app.get_state(thread))