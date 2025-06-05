
import demo_constants 
import pymongo
import voyageai

client = pymongo.MongoClient(demo_constants.MONGO_URI)
db = client[demo_constants.DATABASE_NAME]
vo = voyageai.Client(api_key=demo_constants.VOYAGEAI_API_KEY)

def gen_embeddings(document):
    """
    Generate embeddings for a single document.
    
    Args:
        document (dict): The document to generate embeddings for.
    
    Returns:
        dict: The document with the generated embedding.
    """
    texts = [document["description"]]
    result = vo.embed(texts, model=demo_constants.VOYAGEAI_EMBEDDINDG_MODEL, input_type="document")
    embedding = result.embeddings[0]
    
    return {"_id": document["_id"], "embedding": embedding}    

def gen_embeddings():
    """
    Generate embeddings for the specified MongoDB collection.
    """
    coll = db[demo_constants.INCIDENTS_COLLECTION_NAME]

    # Fetch documents from the collection
    results = coll.find().skip(0).limit(10)
    docs = list(results)
    print(len(docs))

    # Extract text from documents and generate embeddings
    texts = [doc["description"] for doc in docs]

    result = vo.embed(texts, model=demo_constants.VOYAGEAI_EMBEDDINDG_MODEL, input_type="document") 
    #print(result)
    embeddings = result.embeddings
    #print(len(embeddings))
    
    # Store embeddings back to MongoDB
    for doc, embedding in zip(docs, embeddings):
        coll.update_one({"_id": doc["_id"]}, {"$set": {"embedding": embedding}})

      
if __name__ == "__main__":
    # Connect to MongoDB
    #gen_embeddings()
    for doc in results:
        print(doc)
    
    
    
    
    
    