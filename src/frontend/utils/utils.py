import csv


def save_messages(messages: list,file_name: str):

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
    print(f"Dados salvos em {file_name}")