import demo_constants 
import voyageai
import time
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_voyageai import VoyageAIEmbeddings
from langchain_openai import ChatOpenAI
from langchain_mongodb.retrievers.hybrid_search import MongoDBAtlasHybridSearchRetriever
from langchain_mongodb.chat_message_histories import MongoDBChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import MessagesPlaceholder

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


embedding_model = VoyageAIEmbeddings(model=demo_constants.VOYAGEAI_EMBEDDINDG_MODEL,   
                                      api_key=demo_constants.VOYAGEAI_API_KEY)
vo = voyageai.Client(api_key=demo_constants.VOYAGEAI_API_KEY)
llm = ChatOpenAI(openai_api_key=demo_constants.OPENAI_API_KEY, temperature=0.5, model=demo_constants.OPENAI_LLM_MODEL)

vector_store = MongoDBAtlasVectorSearch.from_connection_string(
                    connection_string = demo_constants.MONGO_URI,
                    embedding = embedding_model,
                    text_key = "description",
                    embedding_key = "embedding",
                    relevance_score_fn = "cosine_similarity",
                    index_name = "vector_index",
                    namespace = demo_constants.DATABASE_NAME+"."+demo_constants.INCIDENTS_COLLECTION_NAME
                )

# Initialize the retriever
retriever = MongoDBAtlasHybridSearchRetriever(
    vectorstore = vector_store,
    search_index_name = "search_index",
    top_k = 10,
    fulltext_penalty = 50,
    vector_penalty = 50
)

def hybrid_search(query):
    """
    Hybrid search for the specified query.
    Args:
        query (str): Query string
    """
    # Print results
    documents = retriever.invoke(query)
    return list(documents)                 

def rerank_documents(query, documents):
    """
    Rerank the documents based on the query.
    Args:
        query (str): Query string
        documents (list): List of documents to rerank
    """
    #for doc in documents:
    #    print("Document before reranking: ", doc)
        
    descriptions = [doc.page_content for doc in documents]
    #print("Descriptions for reranking: ", descriptions)
    reranked_docs = vo.rerank(query, descriptions, model=demo_constants.VOYAGEAI_RERANKER_MODEL, top_k=5)
    #print("Reranked documents: ", reranked_docs)
    return reranked_docs

# Define a function that gets the chat message history 
def get_session_history(session_id: str) -> MongoDBChatMessageHistory:
    return MongoDBChatMessageHistory(
        connection_string=demo_constants.MONGO_URI,
        session_id=session_id,
        database_name=demo_constants.DATABASE_NAME,
        collection_name= demo_constants.HISTORY_COLLECTION_NAME
    )
    
    
def get_response(query, documents):

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
    #retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={ "k": 5 })
    #documents = retriever.invoke(query)
    #documents = hybrid_search("What were the main causes of system malfunctions in 2024?")

    # Create a retriever chain that processes the question with history and retrieves documents
    retriever_chain = RunnablePassthrough.assign(context=question_chain | retriever | (lambda docs: "\n\n".join([d.document for d in documents.results])))

    # Create a prompt template that includes the retrieved context and chat history
    rag_system_prompt = """You are a helpful assistant. Act as a Site Reliability Engineer expert. 
    Answer the question based only on the following context:
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
    return rag_with_memory.invoke(
                   {"question": query},
                    {"configurable": {"session_id": "user_1"}}
                )
    

def q_and_a(query):
    """
    Perform question and answer based on the query.
    Args:
        query (str): Query string
    """
    documents = hybrid_search(query)
    reranked_docs = rerank_documents(query, documents)
    response = get_response(query, reranked_docs)
    return response

if __name__ == "__main__":
    question = "Where and when were incidents reported with complete system malfunction recently?"
    print(question)
    response = q_and_a(question)
    print(response)
    time.sleep(30)
  
    question = "What did I asked before?"
    print(question)
    response = q_and_a(question)
    print(response)