# starthack24
## Design Brief
An ultra-low latency, real-time chatbot assistant serves as a telephone operator for the [Government of St Gallen website](www.sg.ch). It efficiently handles incoming calls, providing answers to queries, or redirecting calls to specific government departments as needed. This solution facilitates time-management for officials in the call center, enabling them to focus on more critical tasks.

## Tech Stack
- GPT-4 model with engineered prompts
- Vector database
- Whisper API speech to text
- Elevenlabs API text to speech
- Twilio API for making phone calls
- Flask backend, hosted using ngrok
  
## setup

1. `python3 -m venv .venv`
2. `source .venv/bin/activate`
3. `pip install -r requirements.txt`

## setup for local vector db

1. do all of above
2. install docker - <https://docs.docker.com/get-docker/>
3. run `bash standalone_embed.sh start` from the root of the repo
4. run `python3 src/process_data.py`

## querying the vector db

sample query example is in src/sample_query.py, can run from root by doing `python src/sample_query.py`
