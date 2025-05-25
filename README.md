# FinOps Demo

This project is a basic demonstration of Financial Operations (FinOps) using ServiceNow tables and MongoDB as the database. The application connects to ServiceNow to retrieve and manage financial data, while utilizing MongoDB for data storage and retrieval.

## Project Structure

```
finops-demo
├── src
│   ├── main.py               # Entry point of the application
│   ├── servicenow_client.py  # Client for interacting with ServiceNow
│   ├── mongodb_client.py     # Client for MongoDB operations
│   └── utils.py              # Utility functions for data processing
├── requirements.txt          # Project dependencies
├── README.md                 # Project documentation
└── .gitignore                # Files to ignore in version control
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd finops-demo
   ```

2. **Create a virtual environment:**
   ```
   python3 -m venv venv
   ```

3. **Activate the virtual environment:**
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. **Install the required dependencies:**
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the application, execute the following command:

```
python src/main.py
```

## Functionality

- **ServiceNow Integration:** The application can fetch data from ServiceNow tables and create new records using the ServiceNow API.
- **MongoDB Storage:** Financial data is stored and managed in MongoDB, allowing for efficient data retrieval and manipulation.
- **Utility Functions:** The project includes utility functions to assist with data formatting and validation.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.