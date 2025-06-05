
import demo_constants 
import pymongo
import voyageai

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

from langchain_mongodb.retrievers.hybrid_search import MongoDBAtlasHybridSearchRetriever

from langchain_mongodb import MongoDBAtlasVectorSearch

client = pymongo.MongoClient(demo_constants.MONGO_URI)
db = client[demo_constants.DATABASE_NAME]
vo = voyageai.Client(api_key=demo_constants.VOYAGEAI_API_KEY)
llm = ChatOpenAI(openai_api_key=demo_constants.OPENAI_API_KEY, temperature=0.5, model=demo_constants.OPENAI_LLM_MODEL)


# Create the vector store
#vector_store = MongoDBAtlasVectorSearch.from_connection_string(
#   connection_string = demo_constants.MONGO_URI,
#   embedding = vo,
#   namespace = demo_constants.DATABASE_NAME+"."+demo_constants.INCIDENTS_COLLECTION_NAME,
#   text_key = "description",
#  embedding_key = "embedding",
#   relevance_score_fn = "cosine_similarity",
#   index_name = "vector_index",
#)


def hybrid_search(query):
    """
    Hybrid search for the specified query.
    Args:
        query (str): Query string
    """

    # Initialize the retriever
    #retriever = MongoDBAtlasHybridSearchRetriever(
    #    vectorstore = vector_store,
    #    search_index_name = "search_index",
    #    top_k = 5,
    #    fulltext_penalty = 50,
    #    vector_penalty = 50
    #)

    # Print results
    #documents = retriever.invoke(query)
    
    query_embedding = vo.embed([query], model=demo_constants.VOYAGEAI_EMBEDDINDG_MODEL, input_type="query").embeddings[0]
    
    vectorWeight = 0.8
    fullTextWeight = 0.2
    
    documents = db.incidents.aggregate([
            {
                '$vectorSearch': {
                    'index': 'vector_index', 
                    'path': 'embedding', 
                    'queryVector': query_embedding, 
                    'numCandidates': 50, 
                    'limit': 10
                }
            }, {
                '$group': {
                    '_id': None, 
                    'docs': {
                        '$push': '$$ROOT'
                    }
                }
            }, {
                '$unwind': {
                    'path': '$docs', 
                    'includeArrayIndex': 'rank'
                }
            }, {
                '$addFields': {
                    'vs_score': {
                        '$multiply': [
                            vectorWeight, {
                                '$divide': [
                                    1.0, {
                                        '$add': [
                                            '$rank', 60
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                }
            }, {
                '$project': {
                    'vs_score': 1, 
                    '_id': '$docs._id', 
                    'description': '$docs.description',
                }
            }, {
                '$unionWith': {
                    'coll': 'incidents', 
                    'pipeline': [
                        {
                            '$search': {
                                'index': 'search_index', 
                                'phrase': {
                                    'query': query, 
                                    'path': 'description'
                                }
                            }
                        }, {
                            '$limit': 10
                        }, {
                            '$group': {
                                '_id': None, 
                                'docs': {
                                    '$push': '$$ROOT'
                                }
                            }
                        }, {
                            '$unwind': {
                                'path': '$docs', 
                                'includeArrayIndex': 'rank'
                            }
                        }, {
                            '$addFields': {
                                'fts_score': {
                                    '$multiply': [
                                        fullTextWeight, {
                                            '$divide': [
                                                1.0, {
                                                    '$add': [
                                                        '$rank', 60
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                }
                            }
                        }, {
                            '$project': {
                                'fts_score': 1, 
                                '_id': '$docs._id', 
                                'description': '$docs.description',
                            }
                        }
                    ]
                }
            }, {
                '$group': {
                    '_id': '$_id', 
                    'description': {
                        '$first': '$description'
                    }, 
                    'vs_score': {
                        '$max': '$vs_score'
                    }, 
                    'fts_score': {
                        '$max': '$fts_score'
                    }
                }
            }, {
                '$project': {
                    '_id': 1, 
                    'description': 1, 
                    'vs_score': {
                        '$ifNull': [
                            '$vs_score', 0
                        ]
                    }, 
                    'fts_score': {
                        '$ifNull': [
                            '$fts_score', 0
                        ]
                    }
                }
            }, {
                '$project': {
                    'score': {
                        '$add': [
                            '$fts_score', '$vs_score'
                        ]
                    }, 
                    '_id': 1, 
                    'description': 1, 
                    'vs_score': 1, 
                    'fts_score': 1
                }
            }, {
                '$sort': {
                    'score': -1
                }
            }, {
                '$limit': 10
            }
        ])
    
    
    #for doc in documents:
        #print("Incident ID: " + doc["incident_id"])
        #print("Application ID: " + doc["app_id"])
        #print("Description: " + doc["description"])
        #print("Search score: {}".format(doc["fts_score"]))
        #print("Vector Search score: {}".format(doc["vs_score"]))
        #print("Total score: {}\n".format(doc["fts_score"] + doc["vs_score"]))
    
    return list(documents)


def rerank_documents(query, documents):
    """
    Rerank the documents based on the query.
    Args:
        query (str): Query string
        documents (list): List of documents to rerank
    """
    descriptions = [doc["description"] for doc in documents]
    #print("Descriptions for reranking: ", descriptions)
    reranked_docs = vo.rerank(query, descriptions, model=demo_constants.VOYAGEAI_RERANKER_MODEL, top_k=5)
    #print("Reranked documents: ", reranked_docs)
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
    documents = hybrid_search(query)
    reranked_docs = rerank_documents(query, documents)
    response = get_response(query, reranked_docs)
    
    return response
      
if __name__ == "__main__":
    # Connect to MongoDB
    question = "What incidents occurred in Houston?" 
    print(question)
    response = q_and_a(question)
    print(response)
    
    
    
    
    
    