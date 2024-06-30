# Book Embedding and Search System

This repository contains the code and scripts for generating embeddings for books, storing them in a Supabase database, and providing search and graph functionalities using Supabase Edge Functions.

## Project Structure

.
├── supabase
│ ├── functions
│ │ ├── search
│ │ │ └── index.ts
│ │ └── graph
│ │ └── index.ts
├── scripts
│ ├── data
│ │ └── pg_catalog.csv
│ └── populate_database.ipynb
|  |
├── README.md


### Supabase Edge Functions

The Supabase Edge Functions are located in the `supabase/functions` directory.

- **search/index.ts**: Handles the search functionality by accepting embeddings and returning the top 10 books.
- **graph/index.ts**: Handles the graph functionality by accepting a book ID and building a similarity graph.

### Scripts

The script for generating embeddings and populating the Supabase database is located in the `scripts` directory.

- **populate_database.ipynb**: A Jupyter notebook that contains the code to process the books, generate embeddings, and populate the Supabase database. This notebook is intended to run on Google Colab.

### Data

The `pg_catalog.csv` file, located in the `scripts/data` directory, contains the list of books and their metadata used for book processing.

## Getting Started

### Prerequisites

- [Supabase CLI](https://supabase.com/docs/guides/cli)
- Python 3.7 or higher
- Jupyter Notebook (for running `populate_database.ipynb`)
- Google Colab account

### Setting Up Supabase

1. Sign up for Supabase and create a new project.
2. Note your Supabase `URL` and `API Key`.
3. Set up your database schema to store the documents and embeddings. You can use the following schema as a starting point:

    ```sql
    CREATE TABLE documents (
        id uuid PRIMARY KEY,
        content text,
        embeddings float8[],
        metadata jsonb
    );
    ```

4. Install the Supabase CLI:

    ```sh
    npm install -g supabase
    ```

5. Log in to Supabase:

    ```sh
    supabase login
    ```

6. Initialize the Supabase project:

    ```sh
    supabase init
    ```

### Deploying Supabase Edge Functions

1. Navigate to the root directory of your project.
2. Deploy the search function:

    ```sh
    supabase functions deploy search
    ```

3. Deploy the graph function:

    ```sh
    supabase functions deploy graph
    ```

### Running on Google Colab

1. Upload the `pg_catalog.csv` file located in `scripts/data` to your Google Drive.
2. Open `populate_database.ipynb` in Google Colab.
3. Follow the instructions in the notebook to process the books, generate embeddings, and populate your Supabase database.

## Usage

### Search Function

To search for the top 10 books based on a question, make a POST request to the search function endpoint with the embeddings:

```sh
curl -X POST https://rgjkrflnxopeixwpsjae.supabase.co/functions/v1/search -d '{"embeddings": [[0.1, 0.2, ...]], "topN": 10}'
```

### Graph Function

To get a graph of similar books based on a book ID, make a GET request to the graph function endpoint:

```sh
curl https://rgjkrflnxopeixwpsjae.supabase.co/functions/v1/graph?book_id=1234
```

### License
This project is licensed under the GNU General Public License