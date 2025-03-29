import os
import yaml
from garminetl.ocr import extract_markdown_from_pdf

# Project base directory (one level above src/)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Load the config.yaml file
config_path = os.path.join(BASE_DIR, "config.yaml")
with open(config_path, "r", encoding="utf-8") as file:
    config = yaml.safe_load(file)

# Build paths for raw and processed data
raw_dir = os.path.join(BASE_DIR, config["paths"]["raw_data"])
processed_dir = os.path.join(BASE_DIR, config["paths"]["processed_data"])
os.makedirs(processed_dir, exist_ok=True)

# Iterate over PDFs in the raw directory and convert them to Markdown
for filename in os.listdir(raw_dir):
    if filename.lower().endswith(".pdf"):
        pdf_path = os.path.join(raw_dir, filename)
        print(f"Processing: {filename}")
        markdown_text = extract_markdown_from_pdf(pdf_path)

        # Save output as Markdown file
        output_filename = os.path.splitext(filename)[0] + ".md"
        output_path = os.path.join(processed_dir, output_filename)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown_text)
        print(f"Markdown saved to: {output_path}")
