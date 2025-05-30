# Contents of /finops-demo/finops-demo/src/main.py

import os
import gradio as gr
from demo_constants import (YEAR_TO_GENERATE, MONGO_URI, DATABASE_NAME, LOCATIONS)

# Import your collection creation and population scripts
from create_collections import create_collections
from populate_collections_pos import store_data_mongodb_hourly, generate_pos_data_for_year
from populate_collection_ecommerce import store_ecommerce_data_mongodb, generate_ecommerce_data_for_year
from semantic_search import q_and_a

def chatbot_interface(question):
    response = q_and_a(question)
    return response

def prepare_database():
    """
    Generate the dataset by creating collections and populating them with data.
    """
    # Step 1: Create MongoDB collections
    print("Creating MongoDB collections...")
    create_collections()
    print("Collections created.\n")

    # Step 2: Populate POS data
    print("Populating POS data...")
    daily_pos_data_2024 = generate_pos_data_for_year()
    store_data_mongodb_hourly(daily_pos_data_2024)
    print("POS data populated.\n")

    # Step 3: Populate Ecommerce data
    print("Populating Ecommerce data...")
    daily_ecommerce_data = generate_ecommerce_data_for_year()
    store_ecommerce_data_mongodb(daily_ecommerce_data)
    print("Ecommerce data populated.\n")
    
def main():
    # Gradio Chatbot UI
    gr.Interface(
        fn=chatbot_interface,
        inputs=gr.Textbox(lines=2, placeholder="Ask a question about incidents, costs, etc..."),
        outputs=gr.Textbox(label="Answer"),
        title="FinOps Demo Chatbot",
        description="Ask questions about your FinOps data. Example: 'What incidents impacted ecommerce platform in Dallas?'"
    ).launch()

if __name__ == "__main__":
    main()