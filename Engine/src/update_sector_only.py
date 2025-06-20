import os
import pandas as pd
from tqdm import tqdm

from Engine.src.extract_fields import extract_sector, clean_sector_output, get_short_path


def main():
    # -------- Paths --------
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    csv_path = os.path.join(project_root, "output", "final_metadata_table.csv")
    query_results_dir = get_short_path(os.path.join(project_root, "output", "query_results_v2"))

    # -------- Load CSV --------
    df = pd.read_csv(csv_path)

    # -------- Update Sector --------
    for i, row in tqdm(df.iterrows(), total=len(df), desc="Updating sector column"):
        folder_name = row["folder_name"]

        try:
            sector = extract_sector(folder_name)
            sector = clean_sector_output(sector)
            df.at[i, "sector"] = sector
            print(f"[OK] {folder_name}: sector → {sector}")
        except Exception as e:
            print(f"[ERROR] {folder_name}: {e}")
            df.at[i, "sector"] = None

    # -------- Save Back --------
    df.to_csv(csv_path, index=False)
    print(f"[✅ Done] Sector column updated in: {csv_path}")


if __name__ == "__main__":
    main()
