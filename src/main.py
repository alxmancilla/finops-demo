# Contents of /finops-demo/finops-demo/src/main.py

import os
from demo_constants import (YEAR_TO_GENERATE, MONGO_URI, DATABASE_NAME, LOCATIONS)

# Import your collection creation and population scripts
from create_collections import create_collections
from populate_collections_pos import store_data_mongodb_hourly, generate_pos_data_for_year
from populate_collection_ecommerce import store_ecommerce_data_mongodb, generate_ecommerce_data_for_year
from gen_embeddings import semantic_search

def main():
    # Step 1: Create MongoDB collections
    print("Creating MongoDB collections...")
    # create_collections()
    print("Collections created.\n")

    # Step 2: Populate POS data
    print("Populating POS data...")
    # daily_pos_data_2024 = generate_pos_data_for_year()
    # store_data_mongodb_hourly()
    print("POS data populated.\n")

    # Step 3: Populate Ecommerce data
    print("Populating Ecommerce data...")
    # daily_ecommerce_data = generate_ecommerce_data_for_year()
    # store_ecommerce_data_mongodb(daily_ecommerce_data)
    print("Ecommerce data populated.\n")

    results = semantic_search("What incidents impacted ecommerce platform in Dallas?")
    for doc in results.results:
        print(doc)
        
if __name__ == "__main__":
    main()