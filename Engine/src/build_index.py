import json
import os
import sys
import faiss
import numpy as np
import torch
import ctypes
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import platform

sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from constants import HUGGINGFACE_TOKEN


def get_short_path(long_path):
    """
    On Windows, converts a long path to 8.3 short path format.
    On non-Windows systems, returns the original path.
    """
    if platform.system() == "Windows":
        buffer = ctypes.create_unicode_buffer(260)
        result = ctypes.windll.kernel32.GetShortPathNameW(long_path, buffer, 260)
        if result:
            return buffer.value
    return long_path


def encode_and_save_per_item(folder_path, model, index_base_path, metadata_base_path):
    """
    Recursively goes through each DOCUMENT folder, then each ITEM subfolder,
    and creates one FAISS index + metadata file for each ITEM.
    """
    # List all document folders
    document_folders = [
        d for d in os.listdir(folder_path)
        if os.path.isdir(os.path.join(folder_path, d))
    ]

    for doc_folder in tqdm(document_folders, desc="Processing documents"):
        doc_folder_path = os.path.join(folder_path, doc_folder)

        # For each document folder, find all ITEM subfolders
        item_folders = [
            i for i in os.listdir(doc_folder_path)
            if os.path.isdir(os.path.join(doc_folder_path, i))
        ]

        for item_folder in tqdm(item_folders, desc=f"Processing items in {doc_folder}", leave=False):
            item_folder_path = os.path.join(doc_folder_path, item_folder)

            embeddings = []
            metadata = []

            # Gather all .txt files inside this item folder
            text_files = [
                file_name for file_name in os.listdir(item_folder_path)
                if file_name.endswith(".txt")
            ]

            for file_name in text_files:
                file_path = os.path.join(item_folder_path, file_name)
                with open(file_path, "r", encoding="utf-8") as file:
                    passage_text = file.read()

                # Encode passage text using SentenceTransformer
                embedding = model.encode(passage_text, show_progress_bar=False)

                embeddings.append(embedding)
                metadata.append({
                    "document": doc_folder,
                    "item": item_folder,
                    "file": file_name,
                    "text": passage_text
                })


            if embeddings:
                embeddings = np.vstack(embeddings)
                index = faiss.IndexFlatL2(embeddings.shape[1])
                index.add(embeddings)

                # Prepare output subfolders
                index_doc_path = os.path.join(index_base_path, doc_folder)
                metadata_doc_path = os.path.join(metadata_base_path, doc_folder)
                os.makedirs(index_doc_path, exist_ok=True)
                os.makedirs(metadata_doc_path, exist_ok=True)

                # Convert to short path if needed
                index_doc_path_short = get_short_path(index_doc_path)
                metadata_doc_path_short = get_short_path(metadata_doc_path)
                index_path_short = os.path.join(index_doc_path_short, f"{item_folder}.faiss")
                metadata_path_short = os.path.join(metadata_doc_path_short, f"{item_folder}.npy")

                # Save index and metadata
                faiss.write_index(index, index_path_short)
                np.save(metadata_path_short, metadata)

                print(f"Index saved to {index_path_short}")
                print(f"Metadata saved to {metadata_path_short}")


def create_indexes(input_folder, index_base_folder, metadata_base_folder):
    """
    Convenience function to load the DPR model, create subfolders,
    and call the main encode-and-save routine.
    """
    os.makedirs(index_base_folder, exist_ok=True)
    os.makedirs(metadata_base_folder, exist_ok=True)

    model = SentenceTransformer("sentence-transformers/all-mpnet-base-v2")

    encode_and_save_per_item(input_folder, model, index_base_folder, metadata_base_folder)


if __name__ == "__main__":
    # Current script's directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Project root
    project_root = os.path.dirname(current_dir)

    # Paths
    input_folder = os.path.join(project_root, "data", "split_10k_items")
    index_base_path = os.path.join(project_root, "embeddings", "index_per_pdf_items_v2")
    metadata_base_path = os.path.join(project_root, "embeddings", "metadata_per_pdf_items_v2")

    os.makedirs(index_base_path, exist_ok=True)
    os.makedirs(metadata_base_path, exist_ok=True)

    create_indexes(input_folder, index_base_path, metadata_base_path)