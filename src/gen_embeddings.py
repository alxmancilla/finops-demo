
import demo_constants 
import pymongo
import voyageai

client = pymongo.MongoClient(demo_constants.MONGO_URI)
db = client[demo_constants.DATABASE_NAME]
vo = voyageai.Client(api_key=demo_constants.VOYAGEAI_API_KEY)

def gen_embeddings():
    """
    Generate embeddings for the specified MongoDB collection.
    """
    coll = db["incidents"]

    # Fetch documents from the collection
    results = coll.find().skip(0).limit(10)
    docs = list(results)
    print(len(docs))

    # Extract text from documents and generate embeddings
    texts = [doc["description"] for doc in docs]

    result = vo.embed(texts, model=demo_constants.VOYAGEAI_MODEL, input_type="document") 
    print(result)
    embeddings = result.embeddings
    print(len(embeddings))
    
    # Store embeddings back to MongoDB
    for doc, embedding in zip(docs, embeddings):
        coll.update_one({"_id": doc["_id"]}, {"$set": {"embedding": embedding}})

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
    
    documents = list(results)
    print(documents)
    descriptions = [doc["description"] for doc in documents]
    documents_reranked = vo.rerank(query, descriptions, model="rerank-2", top_k=3)
    print(documents_reranked)

    return documents_reranked
      
if __name__ == "__main__":
    # Connect to MongoDB
    #gen_embeddings()
    results = semantic_search("What were the most recent incident with POS in Texas?")
    for doc in results.results:
        print(doc)
    
    
    
    
    
    