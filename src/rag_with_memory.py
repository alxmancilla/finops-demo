import demo_constants 
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_voyageai import VoyageAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import MessagesPlaceholder

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


embedding_model = VoyageAIEmbeddings(model=demo_constants.VOYAGEAI_EMBEDDINDG_MODEL)
llm = ChatOpenAI(model = demo_constants.OPENAI_LLM_MODEL)

vector_store = MongoDBAtlasVectorSearch.from_connection_string(
                    connection_string = demo_constants.MONGO_URI,
                    embedding = embedding_model,
                    namespace = demo_constants.DATABASE_NAME+"."+demo_constants.INCIDENTS_COLLECTION_NAME"
                )
                    

# Define a function that gets the chat message history 
def get_session_history(session_id: str) -> MongoDBChatMessageHistory:
    return MongoDBChatMessageHistory(
        connection_string=MONGODB_URI,
        session_id=session_id,
        database_name=demo_constants.DATABASE_NAME,
        collection_name="rag_with_memory"
    )
    
    

# Create a prompt to generate standalone questions from follow-up questions
standalone_system_prompt = """
  Given a chat history and a follow-up question, rephrase the follow-up question to be a standalone question.
  Do NOT answer the question, just reformulate it if needed, otherwise return it as is.
  Only return the final standalone question.
"""

standalone_question_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", standalone_system_prompt),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)
# Parse output as a string
parse_output = StrOutputParser()

question_chain = standalone_question_prompt | llm | parse_output


# Create a retriever
retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={ "k": 5 })

# Create a retriever chain that processes the question with history and retrieves documents
retriever_chain = RunnablePassthrough.assign(context=question_chain | retriever | (lambda docs: "\n\n".join([d.page_content for d in docs])))

# Create a prompt template that includes the retrieved context and chat history
rag_system_prompt = """Answer the question based only on the following context:
{context}
"""

rag_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", rag_system_prompt),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{question}"),
    ]
)

# Build the RAG chain
rag_chain = (
    retriever_chain
    | rag_prompt
    | llm
    | parse_output
)

# Wrap the chain with message history
rag_with_memory = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="question",
    history_messages_key="history",
)


if __name__ == "__main__":
    response_1 = rag_with_memory.invoke(
        {"question": "What was MongoDB's latest acquisition?"},
        {"configurable": {"session_id": "user_1"}}
    )
    print(response_1)