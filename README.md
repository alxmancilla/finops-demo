# FinOps Demo

This project is a basic demonstration of Financial Operations (FinOps) using MongoDB as the database. The application generates applications, resources, resource costs and usage per hour, and stores/retrieves data from MongoDB. It also includes an interactive chatbot UI powered by Gradio for querying FinOps data.

## Dashboard
![Screenshot of a dashboard and chatbot for FinOps demo.](/img/finops_demo.png)


## Project Structure

```
finops-demo
├── README.md
├── requirements.txt
├── data/
│   └── finops_demo.gz
├── img/
│   └── finops_demo.png
└── src/
   ├── main.py                      # Entry point (run this to launch Gradio UI)
   ├── create_collections.py        # Script to create MongoDB collections
   ├── populate_collections_pos.py  # Populate POS-related collections and incidents/problems
   ├── populate_collection_ecommerce.py # Populate ecommerce-related collections
   ├── semantic_search.py           # Q&A and semantic search logic for chatbot
   ├── finops_agent.py              # Agent implementation (tools + data access)
   ├── demo_constants_dummy.py      # Example constants (copy/rename to override in env)
   └── tests/
      └── test_finops_agent.py
```

## Setup Instructions

1. **Clone the repository:**
   ```sh
   git clone <repository-url>
   cd finops-demo
   ```

2. **Create a virtual environment:**
   ```sh
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - On Windows:
     ```sh
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```sh
     source venv/bin/activate
     ```

4. **Install the required dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

5. **Setup configuration / environment variables:**
   This repo provides `src/demo_constants_dummy.py` with example values. Do NOT commit your real secrets. Copy or create a `src/demo_constants.py` (same keys) or set equivalent environment variables as needed. Minimal variables used across the repo:

   - `MONGO_URI` (MongoDB connection string)
   - `DATABASE_NAME` (e.g., `finops_demo`)
   - `OPENAI_API_KEY` (if you want agent LLM calls)
   - `VOYAGEAI_API_KEY` (if voyageai features are used)

   Example (create `src/demo_constants.py`):

   ```py
   MONGO_URI = "mongodb+srv://<user>:<pass>@cluster/..."
   DATABASE_NAME = "finops_demo"
   OPENAI_API_KEY = "sk-..."
   VOYAGEAI_API_KEY = "vai-..."
   OPENAI_LLM_MODEL = "gpt-4o"  # or other supported model
   AGENT_NAME = "FinOps Assistant"
   AGENT_DEBUG = False
   YEAR_TO_GENERATE = 2024
   LOCATIONS = ["Austin", "Dallas-Fort Worth", "Houston"]
   ```

6. **Prepare initial dataset for FinOps demo:**

   6.a ***Restore data from dump archive file***
   ```sh
   mongorestore --gzip --archive=data/finops_demo.gz --uri="PASTE_MONGO_URI"
   ```

   6.b ***Recreate data using scripts***
   ```sh
   python src/create_collections.py
   python src/populate_collections_pos.py
   python src/populate_collection_ecommerce.py
   ```

## Usage

To run the application and launch the interactive chatbot UI and dashboard (Gradio):

```sh
python src/main.py
```

This will start a Gradio web interface with a two-column layout:
- **Left (80%)**: Embedded dashboard (iframe, customizable URL)
- **Right (20%)**: Gradio-powered chatbot for natural language queries using the `q_and_a` method

Example questions:
- "What incidents impacted ecommerce platform in Dallas?"
- "Find recent incidents for this app ecommerceplatform-app-01"
- "Show the most recent incidents in Austin"

## Functionality

- **MongoDB Storage:** Store and manage financial and operational data in MongoDB.
- **POS & Ecommerce Data Generation:** Scripts to generate and populate realistic POS and ecommerce datasets, including incidents and problems.
- **Interactive Chatbot & Dashboard:** Gradio-powered UI for natural language queries and a customizable dashboard view.
- Notes & differences found

- The codebase places all runnable scripts inside `src/` — update commands in the README accordingly (changed from top-level `main.py` to `src/main.py`).
- There is a sample constants file at `src/demo_constants_dummy.py`; create `src/demo_constants.py` to override secrets/config.
- Tests live under `src/tests/` (not `tests/` at the repository root).
- The project uses an opinionated set of dependencies listed in `requirements.txt`; some packages reference `voyageai`, `pydantic-ai`, `gradio`, and `langchain` packages. Check versions in `requirements.txt` before installing.

If you want, I can:

- Add a minimal `src/demo_constants.py` template (without secrets) and a `.env` example.
- Add a short CONTRIBUTING or quick-start script to automate venv creation and dependency installation.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.