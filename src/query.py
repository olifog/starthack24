
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


def query(text):
    query_embedding = openai_ef.encode_queries([text])[0]

    search_params = {
        "metric_type": "IP",
        "params": {},
    }

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

    return [{
        "path": x['path'],
        "text": x['text'],
    } for x in res]
