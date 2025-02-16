from db_utils import query_documents
from groq import Groq
from dotenv import load_dotenv
import os

# Load API key
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise ValueError("Missing GROQ_API_KEY in .env file!")

# Initialize Groq client
groq_client = Groq(api_key=api_key)

def query_and_generate_response(user_query):
    """Query ChromaDB and generate a response using the model."""
    # Query ChromaDB for relevant context
    relevant_docs = query_documents(user_query)

    # Prepare the context
    context = "\n".join(relevant_docs) if relevant_docs else "No relevant context found."

    # Construct the LLM prompt
    prompt = f"""
    You are a helpful assistant. Use the context below to answer the question.
    If the context doesn't provide enough information, respond with "I don't know."

    Context:
    {context}

    Question: {user_query}
    Answer:
    """

    # Query the LLaMA model
    response = groq_client.chat.completions.create(
        model="llama-3.3-70b-specdec",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    # Return the generated response
    return response.choices[0].message.content

# Accept user input and generate response
user_input = input("Enter your question: ")
response = query_and_generate_response(user_input)
print(f"🤖 Model Response:\n{response}")