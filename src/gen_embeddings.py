
import demo_constants 
import pymongo
import voyageai

client = pymongo.MongoClient(demo_constants.MONGO_URI)
db = client[demo_constants.DATABASE_NAME]
vo = voyageai.Client(api_key=demo_constants.VOYAGEAI_API_KEY)
llm = ChatOpenAI(openai_api_key=demo_constants.OPENAI_API_KEY, temperature=0.5, model=demo_constants.OPENAI_LLM_MODEL)


def gen_contextual_embeddings(documents):
    """
    Get the response for the query based on the documents.
    Args:
        query (str): Query string
        documents (list): List of documents to get response from
    """
    
    template = """
    You are a helpful assistant. Act as a Site Reliability Engineer expert. 
    Use the following information to generate a brief description of an incident.
    <document> 
{{WHOLE_DOCUMENT}} 
</document> 
Here is the chunk we want to situate within the whole document 
<chunk> 
{{CHUNK_CONTENT}} 
</chunk> 
Please give a short succinct context to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk. Answer only with the succinct context and nothing else. 

            
    Context:
    {context}
    
    Question: {question}
    """

    texts = [doc["description"] for doc in documents]

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
    
    
    
    
    
    