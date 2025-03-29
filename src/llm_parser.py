# src/llm_parse.py

import os
import re
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()
token = os.getenv("GITHUB_TOKEN")

# Set up OpenAI client (Azure-hosted GitHub Model)
client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=token
)

# Base path and markdown file
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
markdown_path = os.path.join(BASE_DIR, "data", "processed", "Workout1.md")

# Read markdown content
with open(markdown_path, "r", encoding="utf-8") as f:
    markdown_text = f.read()

# Extract only weeks 3 and 4 (optional filtering)
match = re.search(r"(## SEMANA 3.*?)(## SEMANA 5|$)", markdown_text, re.DOTALL | re.IGNORECASE)
selected_text = match.group(1).strip() if match else markdown_text

# Prompt is in Portuguese (pt-BR) because the training plans are in that language, and I'm a Brazilian developer :)
# English summary below:
# ---
# You are a virtual assistant specializing in sports training plans.
# Please extract the running workouts from weeks 3 and 4 and organize them in the JSON format below,
# grouping training days and blocks (warm-up, main set, cooldown).
# ---
prompt = f"""
Você é um assistente especializado em planilhas de treino de corrida.
Extraia os treinos das semanas 3 e 4 e organize no seguinte formato JSON:

[
  {{
    "semana": 3,
    "dias": [
      {{
        "dia": "segunda-feira",
        "tipo": "corrida",
        "blocos": [
          {{ "tipo": "aquecimento", "tempo": "10 min", "descricao": "caminhada" }},
          ...
        ]
      }}
    ]
  }},
  ...
]

Aqui está o conteúdo da planilha:

{selected_text}
"""

# Call the LLM with the prompt
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "Você é um assistente especializado em planos de corrida."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.7,
    max_tokens=3000
)

# Extract and clean response content
result = response.choices[0].message.content.strip()

# Ensure output directory exists
output_dir = os.path.join(BASE_DIR, "data", "structured")
os.makedirs(output_dir, exist_ok=True)

# Save as JSON file
json_path = os.path.join(output_dir, "Workout1.json")
with open(json_path, "w", encoding="utf-8") as f:
    f.write(result)

print(f"✅ JSON saved at: {json_path}")
