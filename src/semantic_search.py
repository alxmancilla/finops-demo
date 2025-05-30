
import demo_constants 
import pymongo
import voyageai
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

client = pymongo.MongoClient(demo_constants.MONGO_URI)
db = client[demo_constants.DATABASE_NAME]
vo = voyageai.Client(api_key=demo_constants.VOYAGEAI_API_KEY)


def semantic_search(query):
    """
    Generate embeddings for the specified MongoDB collection.
    Args:
        collection (str): Collection name
        query (str): Query string
    """
    coll = db["incidents"]

    query_embedding = vo.embed([query], model="voyage-3.5", input_type="query").embeddings[0]

    pipeline = [
        {
            "$vectorSearch": {
                "index": "vector_index",
                "queryVector": query_embedding,
                "path": "embedding",
                "limit": 5,  # number of nearest neighbors to return
                "numCandidates": 50,  # number of HNSW entry points to explore
            }
        },
        {
            "$project": {
                "_id": 0,
                "title": 1,
                "description": 1,
                "resource_id": 1,
                "estimated_cost": 1,
                "metrics": "metrics",
                "score": { '$meta': "vectorSearchScore" }            }
        },
    ]

    results = coll.aggregate(pipeline)
    
    return list(results)


def rerank_documents(query, documents):
    """
    Rerank the documents based on the query.
    Args:
        query (str): Query string
        documents (list): List of documents to rerank
    """
    descriptions = [doc["description"] for doc in documents]
    reranked_docs = vo.rerank(query, descriptions, model="rerank-2", top_k=3)
    return reranked_docs

def get_response(query, documents):
    """
    Get the response for the query based on the documents.
    Args:
        query (str): Query string
        documents (list): List of documents to get response from
    """
    template = """
    You are a helpful assistant. Act as a Site Reliability Engineer expert. 
    Use the following pieces of context to answer the question at the end.
    Provide a detailed and accurate answer based on the context.
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    Do not answer the question if there is no given context.
    Do not answer the question if it is not related to the context."
            
    Context:
    {context}
    
    Question: {question}
    """
    custom_rag_prompt = PromptTemplate.from_template(template)

    retrieve = {
        "context": (lambda docs: "\n\n".join([d.document for d in documents.results])), 
        "question": RunnablePassthrough()
        }

    llm = ChatOpenAI(openai_api_key=demo_constants.OPENAI_API_KEY, temperature=0.5, model="gpt-3.5-turbo")

    response_parser = StrOutputParser()

    rag_chain = (
        retrieve
        | custom_rag_prompt
        | llm
        | response_parser
    )

    answer = rag_chain.invoke(query)
    
    return answer

def q_and_a(query):
    """
    Perform question and answer based on the query.
    Args:
        query (str): Query string
    """
    documents = semantic_search(query)
    reranked_docs = rerank_documents(query, documents)
    response = get_response(query, reranked_docs)
    
    return response
      
if __name__ == "__main__":
    # Connect to MongoDB
    question = "Where and when were incidents reported with complete system malfunction recently?" 
    response = q_and_a(question)
    print(response)
    
    
    
    
    
    