import json
import os
from tqdm import tqdm
from transformers import AutoTokenizer, AutoModelForCausalLM


def load_single_result(file_path):
    """
    Load a single query result saved as a JSON file.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def process_passages_in_batches(passages, prompt_template, model, tokenizer, batch_size=4, max_length=512, max_new_tokens=20):
    """
    Process passages in batches using a language model.
    """
    results = []

    for i in tqdm(range(0, len(passages), batch_size), desc="Processing Batches"):
        batch = passages[i:i + batch_size]

        # Prepare prompts for the batch
        input_texts = [prompt_template.format(text=p["text"]) for p in batch]

        # Tokenize and move inputs to GPU
        inputs = tokenizer(input_texts, return_tensors="pt", padding=True, truncation=True, max_length=max_length)

        # Generate outputs with max_new_tokens=20
        outputs = model.generate(**inputs, max_new_tokens=max_new_tokens)

        # Decode outputs
        decoded_outputs = [tokenizer.decode(o, skip_special_tokens=True) for o in outputs]

        # Save the results
        for passage, output in zip(batch, decoded_outputs):
            results.append({
                "passage": passage["text"],
                "output": output
            })

    return results


if __name__ == "__main__":
    # Path to the single JSON file
    json_file_path = "output/query_results_MSFT.json"  # Replace with your file path

    # Hugging Face API token
    hf_token = "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"  # Replace with your actual token

    # Load language model
    model_name = "google/gemma-2-2b-it"
    tokenizer = AutoTokenizer.from_pretrained(model_name, token=hf_token)
    model = AutoModelForCausalLM.from_pretrained(model_name, token=hf_token)

    # Load the single JSON result
    print(f"Loading results from: {json_file_path}")
    passages = load_single_result(json_file_path)

    # Prompt template for processing
    prompt_template = (
        "Here is a passage extracted from a document:\n\n"
        "{text}\n\n"
        "Please extract the 'Net Income' and associated year from the text."
    )

    # Process passages in batches
    batch_size = 4  # Adjust based on your hardware capabilities
    print("Processing passages...")
    processed_results = process_passages_in_batches(passages, prompt_template, model, tokenizer, batch_size=batch_size)

    # Display and save results
    output_file = "output/processed_results_MSFT.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(processed_results, f, indent=4)
    print(f"Processed results saved to {output_file}")

    # Display the first few results
    for result in processed_results[:5]:  # Show the first 5 results
        print(f"\nPassage:\n{result['passage'][:200]}...")
        print(f"Model Output:\n{result['output']}\n")
