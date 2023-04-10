# webscrapers
Home for all the webscrapers we use for various eVision projects


## Local setup:

### Installation:
- Create venv
  ```shell
  python3 -m venv .venv
  source .venv/bin/activate
  ```
- Add python path to the vnev. Create a new file called `python-path.pth` in `.venv/lib/python3.10/site-packages/python-path.pth`
- Paste your project path in this file eg: `/home/k2/Work/SCU/eVision/webscrapers`.
- Restart your venv
  ```shell
  deactivate # shut down venv
  source .venv/bin/activate
  ```
- Create a copy of `.env.example`. Rename the copy to `.env` and change the values accordingly.

### Running:

- Start the db container with the follwoing command: 
  ```shell
  sudo docker build -t evision-db .
  sudo docker run -p 5432:5432 evision-db
  ```

- Run the migration with the following command
  ```shell
  cd app
  alembic revision --autogenerate -m 'some message'
  alembic upgrade head
  ```
- This should create all the db (if not created already)
- To run the influenza scraper simply `python influenza/scraper.py` 
  - This should scrape the data from CDC and google trends and dump the data into the db


## Extending the work:

### Adding new tables
- Simply create a new class in the models.py. Run the alembic migrations. This will create the required tables.
- Now in the web scraper script, add the logic to dump the scraped data into the tbles. Refer to the `influenza/scraper.py` .
