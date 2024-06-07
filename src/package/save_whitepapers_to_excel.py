import pandas as pd
from datetime import datetime
import uuid
import os

def save_whitepapers_to_excel(whitepapers):
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    file_name = f"whitepapers_{current_time}_{unique_id}.xlsx"
    directory = os.path.join("static", "Whitepapers")

    # Ensure the directory exists
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist. Creating it...")
        os.makedirs(directory)
        print(f"Directory {directory} created.")
    else:
        print(f"Directory {directory} already exists.")

    file_path = os.path.join(directory, file_name)
    print(f"Saving Excel file to {file_path}")
    df = pd.DataFrame(whitepapers)
    df.to_excel(file_path, index=False)
    return file_path
