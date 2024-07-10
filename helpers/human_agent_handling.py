import openai

def switch_to_human_agent(thread_id, client):
    summary = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="assistant",
        content="Unable to answer the question. Redirecting to a human agent..."
    )
    return summary
