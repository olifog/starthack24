from pymilvus import MilvusClient, DataType
from pymilvus import model
from dotenv import load_dotenv
import os
from bs4 import BeautifulSoup
import pickle
import json

load_dotenv()

openai_ef = model.dense.OpenAIEmbeddingFunction(
    model_name='text-embedding-3-large',
    api_key=os.getenv('OPENAI_API_KEY'),
    dimensions=512
)

CLUSTER_ENDPOINT = "http://localhost:19530"
TOKEN = "default"

client = MilvusClient(
    uri=CLUSTER_ENDPOINT,
    token=TOKEN 
)


client.drop_collection(
    collection_name="kanton"
)

schema = MilvusClient.create_schema(
    auto_id=True,
    enable_dynamic_field=True,
)

schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=512)

index_params = client.prepare_index_params()

index_params.add_index(
    field_name="id"
)

index_params.add_index(
    field_name="vector", 
    index_type="AUTOINDEX",
    metric_type="IP"
)

client.create_collection(
    collection_name="kanton",
    schema=schema,
    index_params=index_params
)


replacement_dict = {
    'Ã¤': 'ä',  # lowercase ä
    'Ã¶': 'ö',  # lowercase ö
    'Ã¼': 'ü',  # lowercase ü
    'ÃŸ': 'ß',  # lowercase ß
    'Ã„': 'Ä',  # uppercase Ä
    'Ã–': 'Ö',  # uppercase Ö
    'Ãœ': 'Ü',  # uppercase Ü
}


def replace_malformed(text, replacements):
    for wrong, correct in replacements.items():
        text = text.replace(wrong, correct)
    return text


docs = []
docs_text = []

if not os.path.exists("final_docs.pkl"):
    for root, subdirs, files in os.walk("./data"):
        for file in files:
            filepath = os.path.join(root, file)
            if not filepath.endswith(".html"):
                continue
            with open(filepath, "r") as f:
                print(f"Processing file: {filepath}")
                data = f.read()
                corrected_data = replace_malformed(data, replacement_dict)
                
                soup = BeautifulSoup(corrected_data, 'html.parser')
                text_data = []
                for div in soup.find_all("div", class_="portalsg-p-container"):
                    text_data.append(div.get_text(separator=" ", strip=True))
                
                combined_text = " ".join(text_data)
                doc = {
                    "path": filepath
                }
                if len(combined_text) > 0:
                    docs_text.append(combined_text)
                    docs.append(doc)

    with open("docs_text.pkl", "wb") as f:
        pickle.dump(docs_text, f)
    
    with open("docs_initial.pkl", "wb") as f:
        pickle.dump(docs, f)
    
    # with open("docs_text.pkl", "rb") as f:
    #     docs_text = pickle.load(f)
    
    # with open("docs_initial.pkl", "rb") as f:
    #     docs = pickle.load(f)

    print(f"number of documents: {len(docs)}")
    
    
    batch_texts = []
    batch_start = 0
    letters = 0
    MAX_LETTERS = int(2.5*8192)

    final_docs = []

    for i in range(0, len(docs_text)):
        if letters + len(docs_text[i]) > MAX_LETTERS:
            print(f"batching up to {i} of {len(docs_text)}")
            try:
                batch_embeddings = openai_ef.encode_documents(batch_texts)
                for j, doc_text in enumerate(batch_texts):
                    final_docs.append({
                        "path": docs[batch_start+j]["path"],
                        "vector": batch_embeddings[j],
                        "text": doc_text
                    })
            except Exception as e:
                print(f"error: {e}")

            batch_texts = []
            letters = 0
            batch_start = i

        if len(docs_text[i]) > MAX_LETTERS:
            for z in range((len(docs_text[i]) // MAX_LETTERS)+1):
                try:
                    batch_embeddings = openai_ef.encode_documents(docs_text[i][z*MAX_LETTERS:(z+1)*MAX_LETTERS])

                    final_docs.append({
                        "path": docs[i]["path"],
                        "part": z,
                        "text": docs_text[i][z*MAX_LETTERS:(z+1)*MAX_LETTERS],
                        "vector": batch_embeddings[0]
                    })
                except Exception as e:
                    try:
                        batch_embeddings = openai_ef.encode_documents(docs_text[i][z*MAX_LETTERS:])

                        final_docs.append({
                            "path": docs[i]["path"],
                            "part": z,
                            "text": docs_text[i][z*MAX_LETTERS:(z+1)*MAX_LETTERS],
                            "vector": batch_embeddings[0]
                        })
                    except Exception as e:
                        print(f"error: {e}")
                        continue
                
        else:
            batch_texts.append(docs_text[i])
            letters += len(docs_text[i])
    
    with open("final_docs.pkl", "wb") as f:
        pickle.dump(final_docs, f)
    
else:
    with open("final_docs.pkl", "rb") as f:
        final_docs = pickle.load(f)

client.insert(collection_name="kanton", data=final_docs)
