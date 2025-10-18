import yaml
from yaml.loader import SafeLoader
import logging
import csv

def save_users(config: dict) -> None:
    """
    Salva os usuários em um arquivo YAML.
    """
    yaml_path = "src/frontend/users/config.yaml"
    with open(yaml_path, "w") as file:
        yaml.dump(config, file, default_flow_style=False)
    logging.info("Usuários salvos com sucesso.")

def load_users() -> dict:
    """
    Carrega os usuários de um arquivo YAML.
    """
    yaml_path = "src/frontend/users/config.yaml"
    with open(yaml_path, "r") as file:
        config = yaml.load(file, Loader=SafeLoader)
    logging.info("Usuários carregados com sucesso.")

    return config

def save_messages(messages: list,file_name: str):
    """
    Salva as mensagens em um arquivo CSV.
    """
    data = {
        "user_question": [],
        "model_response": []
    }

    for message in messages[-2:]:
        if message["role"] == "user":
            data["user_question"].append(message["content"].replace("\n", " "))
        elif message["role"] == "assistant":
            data["model_response"].append(message["content"].replace("\n", " "))

    with open(file_name, 'a', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        rows = zip(*data.values())
        writer.writerows(rows)
    logging.info(f"Dados salvos em {file_name}")
