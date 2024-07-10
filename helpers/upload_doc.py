import openai
import os

def upload_documents(assistant_id):
    docs_path = "docs"
    file_ids = []

    for doc in os.listdir(docs_path):
        if doc.endswith(".pdf"):
            with open(os.path.join(docs_path, doc), "rb") as file:
                response = openai.File.create(
                    file=file,
                    purpose='answers'
                )
                file_id = response["id"]
                file_ids.append(file_id)
                
                # Associate each file id with the current assistant
                assistant_file = openai.Assistant.create_file(
                    assistant_id=assistant_id, file_id=file_id
                )
    
    return file_ids

