
from pymilvus import MilvusClient, model
import os
from dotenv import load_dotenv

# Load the environment variables
load_dotenv()

# Initialize OpenAI Embedding Function with your API key
openai_ef = model.dense.OpenAIEmbeddingFunction(
    model_name='text-embedding-3-large',
    api_key=os.getenv('OPENAI_API_KEY'),
    dimensions=512
)

# Milvus client connection parameters
CLUSTER_ENDPOINT = "http://localhost:19530"
TOKEN = "default"

# Connect to Milvus client
client = MilvusClient(
    uri=CLUSTER_ENDPOINT,
    token=TOKEN
)

# Define your queries
queries = ["Informationen zum Ersatz von Reisepässen"]

# Encode the queries into embeddings
query_embeddings = openai_ef.encode_queries(queries)

# Now you can use these embeddings to search in Milvus
# Note: This part is assuming your collection and vector field setup
search_params = {
    "metric_type": "IP",
    "params": {},
}

for query_embedding in query_embeddings:
    search_results = client.search(
        collection_name="kanton",
        data=[query_embedding],
        limit=5,
        search_params=search_params
    )

    res = client.get(
        collection_name="kanton",
        ids=[x['id'] for x in search_results[0]],
    )
    
    # Handle the search results
    print(f"Search results for query: \"{queries[0]}\"")
    print('\n'.join([f"\n----------------------------------------------\nID: {x['id']}, Closeness: {search_results[0][i]['distance']} Path: {x['path']}\nText: {x['text'][:600]}..." for i, x in enumerate(res)]))

