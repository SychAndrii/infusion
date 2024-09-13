import json
import threading
from concurrent.futures import ThreadPoolExecutor

THREAD_POOL_SIZE = 4


# Function to process JSON data
def process_data(data):
    return [item for item in data if item.get("value") > 100]


# Function to read and parse the JSON file
def read_json_file(file_path):
    with open(file_path, "r") as json_file:
        return json.load(json_file)


def main():
    # Use thread pool executor for parallel processing
    with ThreadPoolExecutor(max_workers=THREAD_POOL_SIZE) as executor:
        try:
            # Read JSON file
            data = read_json_file("data.json")

            # Submit tasks for parallel processing
            future = executor.submit(process_data, data)
            processed_data = future.result()

            print("Processed Data:", processed_data)

        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
