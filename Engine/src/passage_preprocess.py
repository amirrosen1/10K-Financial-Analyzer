import json
import os

def split_text_into_passages(text, passage_size=300):
    """
    Splits text into passages of approximately 'passage_size' words.
    """
    words = text.split()
    passages = [
        " ".join(words[i:i + passage_size])
        for i in range(0, len(words), passage_size)
    ]
    return passages

def process_text_file(input_path, output_folder, passage_size=300):
    """
    Processes a single .txt file, splits it into passages,
    and saves them in a subfolder named after the file (minus .txt).
    """
    with open(input_path, "r", encoding="utf-8") as file:
        text = file.read()

    # Split text into passages
    passages = split_text_into_passages(text, passage_size)

    # Create a subfolder for the passages, named after the file
    file_name = os.path.basename(input_path).replace(".txt", "")
    subfolder_path = os.path.join(output_folder, file_name)
    os.makedirs(subfolder_path, exist_ok=True)

    # Save each passage as a separate file
    for idx, passage in enumerate(passages):
        passage_path = os.path.join(subfolder_path, f"passage_{idx+1}.txt")
        with open(passage_path, "w", encoding="utf-8") as passage_file:
            passage_file.write(passage)

    print(f"Processed {file_name} into {len(passages)} passages.")

def process_document_folder(document_folder_path, output_folder, passage_size=300):
    """
    Given a folder for a single document (e.g. AAPL_00026289-17-000070),
    process all .txt files (Items) in that folder.
    """
    # e.g., document_folder_path = ".../data/10k_items/AAPL_00026289-17-000070"
    document_name = os.path.basename(document_folder_path)
    # Create a matching subfolder in the output folder
    document_output_path = os.path.join(output_folder, document_name)
    os.makedirs(document_output_path, exist_ok=True)

    # Iterate over each text file in this document folder
    for file_name in os.listdir(document_folder_path):
        if file_name.endswith(".txt"):
            input_path = os.path.join(document_folder_path, file_name)
            # Use our existing function to split into passages
            process_text_file(input_path, document_output_path, passage_size)

def split_items_to_passages(input_folder, output_folder, passage_size=300):
    """
    Iterates over all subfolders in 'input_folder'.
    Each subfolder is treated as one "document" folder containing item files.
    """
    os.makedirs(output_folder, exist_ok=True)
    # Go through each subfolder in input_folder
    for folder_name in os.listdir(input_folder):
        folder_path = os.path.join(input_folder, folder_name)
        if os.path.isdir(folder_path):
            # This is a document folder (like AAPL_00026289-17-000070)
            process_document_folder(folder_path, output_folder, passage_size)


if __name__ == "__main__":
    # Example usage:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)

    # Suppose your documents are in:   Engine/data/10k_items
    # And you want output in:          Engine/data/split_10k_items
    input_folder = os.path.join(project_root, "data", "10k_items")
    output_folder = os.path.join(project_root, "data", "split_10k_items")

    split_items_to_passages(input_folder, output_folder, passage_size=100)
