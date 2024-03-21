# starthack24

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
