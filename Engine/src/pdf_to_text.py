import os
os.environ["HF_HOME"] = "/cs/ep/110/HUJI-project/hf_cache"
os.environ["TRITON_CACHE_DIR"] = "/cs/ep/110/HUJI-project/hf_cache/triton_cache"
os.environ["TRANSFORMERS_CACHE"] = "/cs/ep/110/HUJI-project/hf_cache"
os.environ["HF_DATASETS_CACHE"] = "/cs/ep/110/HUJI-project/hf_cache"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"


import re
import logging
logging.getLogger("pdfminer").setLevel(logging.ERROR)
import pdfplumber
import json
from Engine.src.mistral_7b import invoke_model
from Engine.src.constants import PDFS_METADATA_FILE


def detect_toc_start_page(pdf, max_search_pages=10, min_item_count=3):
    toc_keywords = ["Table of Contents", "Index"]
    item_pattern = re.compile(r"\bItem\s+\d+[A-Z]?\.", re.IGNORECASE)

    for i in range(min(max_search_pages, len(pdf.pages))):
        text = pdf.pages[i].extract_text()
        if not text:
            continue

        lower_text = text.lower()
        item_count = len(item_pattern.findall(text))

        if any(kw.lower() in lower_text for kw in toc_keywords):
            if item_count >= min_item_count:
                print(f"TOC detected on page {i + 1} with {item_count} items (via keyword).")
                return i + 1

        elif item_count >= 10:  # threshold for "likely a TOC"
            print(f"TOC detected on page {i + 1} with {item_count} items (via item count only).")
            return i + 1

    return None


def extract_toc_entries_from_page(text):
    toc = {}

    # Step 1: Normalize space and split into raw lines
    raw_lines = text.replace("\xa0", " ").split("\n")

    # Step 2: Merge wrapped lines (e.g., Item 5 spanning two lines)
    lines = []
    for line in raw_lines:
        line = line.strip()
        if not line:
            continue
        if re.match(r"(?i)^item\s+\d+[A-Z]?\.?", line):
            lines.append(line)
        elif lines:
            lines[-1] += " " + line  # Merge into previous line
        else:
            lines.append(line)

    # Step 3: Define regex patterns
    standard_pattern = re.compile(r"(?i)^(Item\s+\d+[A-Z]?\.?)\s+(.*?)\s+(\d{1,3})\s*$")
    dot_pattern = re.compile(r"(?i)^(Item\s+\d+[A-Z]?\.?)\s+(.*?)\.{3,}\s*(\d{1,3})$")
    bare_item_pattern = re.compile(r"(?i)^(\d+[A-Z]?\.?)\s+(.*?)\s+(\d{1,3})\s*$")

    # Match counters
    standard_matches = 0
    dot_matches = 0
    bare_matches = 0

    # Step 4: Parse lines
    for original_line in lines:
        line = original_line.strip()
        if len(line) < 10 or "See" in line:
            continue

        match = standard_pattern.search(line)
        if match:
            item_num, title, page = match.groups()
            full_title = f"{item_num} {title}".strip()
            if full_title not in toc:
                toc[full_title] = int(page)
                standard_matches += 1
                print(f"[standard match] {original_line}")
            continue

        match = dot_pattern.search(line)
        if match:
            item_num, title, page = match.groups()
            full_title = f"{item_num} {title}".strip()
            if full_title not in toc:
                toc[full_title] = int(page)
                dot_matches += 1
                print(f"[dot match] {original_line}")
            continue

        match = bare_item_pattern.search(line)
        if match:
            item_num, title, page = match.groups()
            full_title = f"Item {item_num} {title}".strip()
            if full_title not in toc:
                toc[full_title] = int(page)
                bare_matches += 1
                print(f"[bare match] {original_line}")
            continue

        # Debug unmatched
        print(f"[UNMATCHED LINE] {original_line}")

    print(f"[DEBUG] TOC Entries: {len(toc)} total")
    print(f"         - Standard matches: {standard_matches}")
    print(f"         - Dot matches: {dot_matches}")
    print(f"         - Bare matches: {bare_matches}")

    return toc


def extract_toc_with_adjusted_pages(pdf_path):
    toc = {}
    with pdfplumber.open(pdf_path) as pdf:
        toc_start_index = detect_toc_start_page(pdf)
        if toc_start_index is None:
            print(f"[DEBUG] No TOC start page detected in {os.path.basename(pdf_path)}.")
            return {}

        toc_text = ""
        for i in range(toc_start_index - 1, min(toc_start_index + 9, len(pdf.pages))):
            text = pdf.pages[i].extract_text()
            if text:
                toc_text += "\n" + text

        raw_toc = extract_toc_entries_from_page(toc_text)

        if not raw_toc:
            print(f"[DEBUG] TOC page found but no entries parsed in {os.path.basename(pdf_path)}.")
            return {}

        logical_start = min(raw_toc.values())
        physical_start = toc_start_index + 1
        offset = physical_start - logical_start

        adjusted_toc = {title: page + offset for title, page in raw_toc.items()}
        return adjusted_toc


def extract_items_by_toc(pdf_path, toc):
    with pdfplumber.open(pdf_path) as pdf:
        sorted_items = sorted(toc.items(), key=lambda x: x[1])
        sections = []

        for i, (title, start_page) in enumerate(sorted_items):
            raw_end = sorted_items[i + 1][1] - 1 if i + 1 < len(sorted_items) else len(pdf.pages)
            end_page = max(start_page, raw_end)

            text = ""
            for p in range(start_page - 1, end_page):  # 0-indexed
                if 0 <= p < len(pdf.pages):
                    page_text = pdf.pages[p].extract_text()
                    if page_text:
                        text += page_text + "\n"

            sections.append({
                "title": title,
                "content": text.strip(),
                "page_start": start_page,
                "page_end": end_page
            })

        return sections


def save_items_to_files(items, output_dir, max_filename_length=100):
    os.makedirs(output_dir, exist_ok=True)
    for idx, item in enumerate(items):
        # Sanitize and truncate title
        safe_title = re.sub(r'[^a-zA-Z0-9_]', '_', item['title'])[:max_filename_length]
        filename = f"{idx+1:02d}_{safe_title}.txt"
        file_path = os.path.join(output_dir, filename)

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"{item['title']}\n\n{item['content']}")
        except OSError as e:
            print(f"[ERROR] Failed to write file {file_path}: {e}")


def process_10k_pdf(pdf_path, output_root):
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_dir = os.path.join(output_root, base_name)

    toc = extract_toc_with_adjusted_pages(pdf_path)
    if not toc:
        print(f"No TOC found for {os.path.basename(pdf_path)}. Skipping.")
        return

    sections = extract_items_by_toc(pdf_path, toc)

    print(f"\n{os.path.basename(pdf_path)}")
    print(f"Found {len(sections)} Items:\n")

    for item in sections:
        print(f"  - {item['title']} (pages {item['page_start']}–{item['page_end']})")

    save_items_to_files(sections, output_dir)


def split_pdf_to_items(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    for file_name in os.listdir(input_folder):
        if file_name.lower().endswith(".pdf"):
            pdf_path = os.path.join(input_folder, file_name)
            try:
                process_10k_pdf(pdf_path, output_folder)
            except Exception as e:
                print(f"Error processing {file_name}: {e}")


if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)

    input_folder = os.path.join(project_root, "data", "pdfs")
    output_folder = os.path.join(project_root, "data", "10k_items")

    print(f"Input folder: {input_folder}")
    print(f"Output folder: {output_folder}")

    split_pdf_to_items(input_folder, output_folder)
