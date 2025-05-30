# FinOps Demo

This project is a basic demonstration of Financial Operations (FinOps) using MongoDB as the database. The application generates applications, resources, as well as resource cost and resource usage per hour, while utilizing MongoDB for data storage and retrieval. It also features an interactive chatbot UI powered by Gradio for querying FinOps data.

## Project Structure

```
finops-demo
├── src
│   ├── main.py                       # Entry point of the application and Gradio chatbot UI
│   ├── create_collections.py         # Script to create MongoDB collections
│   ├── populate_collections_pos.py   # Populate POS-related collections and incidents/problems
│   ├── populate_collection_ecommerce.py # Populate ecommerce-related collections
│   ├── semantic_search.py            # Q&A and semantic search logic for chatbot
├── requirements.txt                  # Project dependencies
├── README.md                         # Project documentation
└── .gitignore                        # Files to ignore in version control
```

## Setup Instructions

1. **Clone the repository:**
   ```sh
   git clone <repository-url>
   cd finops-demo
   ```

2. **Create a virtual environment:**
   ```sh
   python3 -m venv venv
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

## Usage

To run the application and launch the interactive chatbot UI:

```sh
python src/main.py
```

This will start a Gradio web interface where you can ask questions about incidents, costs, and other FinOps data. Example questions:
- "What incidents impacted ecommerce platform in Dallas?"
- "Find recent incidents for this app ecommerceplatform-app-01"
- "Show the most recent incidents in Austin"

## Functionality

- **MongoDB Storage:** Store and manage financial and operational data in MongoDB.
- **POS & Ecommerce Data Generation:** Scripts to generate and populate realistic POS and ecommerce datasets, including incidents and problems.
- **Interactive Chatbot:** Gradio-powered UI for natural language queries using the `q_and_a` method and semantic search.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.