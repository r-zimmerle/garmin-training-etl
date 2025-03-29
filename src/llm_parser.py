# src/llm_parse.py

import os
import re
import json
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

# Define base project directory and markdown file path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
markdown_path = os.path.join(BASE_DIR, "data", "processed", "Workout1.md")

# Read the markdown file containing the training plan
with open(markdown_path, "r", encoding="utf-8") as f:
    markdown_text = f.read()

# Optional: extract only weeks 3 and 4 using regex pattern
match = re.search(r"(## SEMANA 3.*?)(## SEMANA 5|$)", markdown_text, re.DOTALL | re.IGNORECASE)
selected_text = match.group(1).strip() if match else markdown_text

# Prompt is in Portuguese (pt-BR) because the original training plans are in this language
# English summary:
# ---
# You are a virtual assistant specializing in running training plans.
# Extract the workouts from weeks 3 and 4 and structure them in valid JSON format,
# grouping training days and blocks (warm-up, main, cooldown). Do not include comments or explanations.
# ---
prompt = f"""
Você é um assistente especializado em planilhas de treino de corrida.
Extraia os treinos das semanas 3 e 4 e organize no seguinte formato JSON puro, sem explicações ou comentários:

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

# Send prompt to the LLM
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "Você é um assistente especializado em planos de corrida."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.7,
    max_tokens=3000
)

# Extract raw model response
raw_result = response.choices[0].message.content.strip()

# Extract JSON block only (remove markdown syntax if present)
json_match = re.search(r"```json\s*(.*?)\s*```", raw_result, re.DOTALL)
cleaned_json = json_match.group(1) if json_match else raw_result

# Validate if the output is a valid JSON structure
try:
    parsed = json.loads(cleaned_json)
except json.JSONDecodeError as e:
    print("🚨 Error: Failed to parse JSON output. Please review the model's response:")
    print(cleaned_json)
    raise e

# Ensure the output directory exists
output_dir = os.path.join(BASE_DIR, "data", "structured")
os.makedirs(output_dir, exist_ok=True)

# Save validated and cleaned JSON to file
json_path = os.path.join(output_dir, "Workout1.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(parsed, f, indent=2, ensure_ascii=False)

print(f"✅ Clean JSON saved to: {json_path}")
