# Web Sémantique - Extract Data

## Build the project (once)

1. Create Python venv in the project root directory `python -m venv ./.venv`  

2. Activate the venv :
- Windows `.\.venv\Scripts\activate`
- Unix `source .venv/bin/activate`

3. Once in the venv, install the requirements `pip install -r requirements.txt`.

4. Download the dataset [on Kaggle](https://www.kaggle.com/code/alaasedeeq/european-soccer-database-with-sqlite3/input) and put the database.sqlite3 file at the project root.

5. Generate the HTML pages : 
- `python ./build/generate_html_pages.py`
- `python ./build/generate_enriched_html_pages.py` (chose 3 : generate both)

## Run the project

(This assumes the project has been built as per the instructions above)

1. Activate the venv (if not already activated) : 
 - Windows `.\.venv\Scripts\activate`
 - Unix `source .venv/bin/activate`

2. Run the API `fastapi dev main.py` 

3. Go to http://127.0.0.1:8000/