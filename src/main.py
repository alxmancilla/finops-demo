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
    print("Creating MongoDB collections...")
    create_collections()
    print("Collections created.\n")

    print("Populating POS data...")
    daily_pos_data_2024 = generate_pos_data_for_year()
    store_data_mongodb_hourly(daily_pos_data_2024)
    print("POS data populated.\n")

    print("Populating Ecommerce data...")
    daily_ecommerce_data = generate_ecommerce_data_for_year()
    store_ecommerce_data_mongodb(daily_ecommerce_data)
    print("Ecommerce data populated.\n")

def main():
    # Left: Dashboard iframe (replace src with your dashboard URL or local file if needed)
    dashboard = gr.HTML(
        '<iframe style="background: #F1F5F4;border: none;border-radius: 2px;box-shadow: 0 2px 10px 0 rgba(70, 76, 79, .2);width: 100vw;height: 100vh;"  src="https://charts.mongodb.com/charts-alejandromr-rhflbxf/embed/dashboards?id=604434bb-49dc-4fe0-85a6-4c708d3eeee6&theme=light&autoRefresh=true&maxDataAge=300&showTitleAndDesc=false&scalingWidth=fixed&scalingHeight=fixed"></iframe>'
    )

    # Right: Gradio chatbot interface
    chatbot = gr.Interface(
        fn=chatbot_interface,
        inputs=gr.Textbox(lines=2, placeholder="Ask a question about incidents, costs, etc..."),
        outputs=gr.Textbox(label="Answer"),
        title="FinOps Demo Chatbot",
        description="Ask questions about your FinOps data. Example: 'What incidents impacted ecommerce platform in Dallas?'"
    )

    # Layout: 2 columns, left 80%, right 20%
    with gr.Blocks() as demo:
        with gr.Row():
            with gr.Column(scale=8):
                dashboard.render()
            with gr.Column(scale=2):
                chatbot.render()

    demo.launch()

if __name__ == "__main__":
    main()