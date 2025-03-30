from openai import OpenAI
from dotenv import load_dotenv
import os
import json
import re

# =============================
# Garmin Workout JSON Generator
# =============================
# This script reads a Markdown training plan (in Portuguese 🇧🇷) and uses an LLM to
# extract structured workouts for Garmin devices, following the FIT CSV standard.
# It loads two Markdown specs:
#   - fit_workout_format.md → technical format guide
#   - fit_csv_mapping_guide.md → intensity/duration/target mapping explanations
# =============================

# Load environment variables from .env
load_dotenv()
token = os.getenv("GITHUB_TOKEN")

# Initialize OpenAI API
client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=token
)

# Paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
spec_format_path = os.path.join(BASE_DIR, "docs", "specs", "fit_workout_format.md")
spec_mapping_path = os.path.join(BASE_DIR, "docs", "specs", "fit_csv_mapping_guide.md")
markdown_path = os.path.join(BASE_DIR, "data", "processed", "Workout1.md")
json_output_dir = os.path.join(BASE_DIR, "data", "structured", "json")
debug_output_path = os.path.join(BASE_DIR, "data", "structured", "debug", "llm_raw_output.txt")

# Ensure output directories exist
os.makedirs(json_output_dir, exist_ok=True)
os.makedirs(os.path.dirname(debug_output_path), exist_ok=True)

# Load technical FIT specification
with open(spec_format_path, "r", encoding="utf-8") as f:
    spec_format = f.read()

# Load intensity and mapping guidance (also in Markdown)
with open(spec_mapping_path, "r", encoding="utf-8") as f:
    spec_mapping = f.read()

# Load Markdown training plan extracted from PDF
with open(markdown_path, "r", encoding="utf-8") as f:
    training_md = f.read().strip()

# Prompt (in Portuguese, tailored for LLM comprehension)
prompt = f"""
Você é um assistente virtual especializado em transformar planos de treinamento de corrida em arquivos compatíveis com dispositivos Garmin.

Abaixo estão duas documentações importantes que você deve usar como referência obrigatória:

1. Formato técnico dos arquivos de treino (.csv para .fit):
{spec_format}

2. Guia de mapeamento para interpretar tipos de intensidade, duração e frequência cardíaca (em português):
{spec_mapping}

Agora, com base no plano de treinos em Markdown abaixo, extraia **apenas os treinos das semanas 3 e 4**, no seguinte formato JSON:

Cada treino deve conter:
- `wkt_name`: string (ex: "S3T1")
- `sport`: número (use 1 para corrida)
- `sub_sport`: número (use 0)
- `steps`: lista de objetos com:
    - `index`: número sequencial da etapa
    - `intensity`: 0=corrida, 1=caminhada/recuperação, 2=aquecimento, 3=desaquecimento
    - `duration_type`: número (use 0 para tempo, 1 para distância, 6 para repetição)
    - `duration_value`: número (em segundos ou centímetros)
    - `target_type`: número (use 1 para frequência cardíaca)
    - `target_value`: zona de frequência cardíaca (1 a 5)
    - `duration_step`: (opcional) índice de início da repetição
    - `repeat_steps`: (opcional) número de repetições

⚠️ Importante:
- Sempre incluir `target_value` com zona de frequência cardíaca (obrigatório para funcionar no Garmin Connect).
- Sempre criar steps separados para repetição usando `duration_type = 6`.
- Nomear os treinos como `S3T1`, `S3T2`, `S3T3`, `S4T1`... conforme a semana e ordem.
- A saída deve ser um **array JSON puro**: `[{{...}}, {{...}}]`, sem comentários nem explicações.

Plano de treino:
{training_md}
"""

# Call the LLM
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "Você é um assistente especialista em JSONs para treinos Garmin."},
        {"role": "user", "content": prompt}
    ],
    temperature=0.4,
    max_tokens=3900
)

raw_output = response.choices[0].message.content.strip()

# Save raw output for debugging
with open(debug_output_path, "w", encoding="utf-8") as f:
    f.write(raw_output)

# Try to parse the JSON
try:
    json_data = json.loads(raw_output)
except json.JSONDecodeError:
    match = re.search(r"```json\s*(.*?)```", raw_output, re.DOTALL)
    if match:
        cleaned = match.group(1)
        json_data = json.loads(cleaned)
    else:
        raise ValueError("❌ Failed to parse JSON from LLM output")

# Save structured JSON to file
json_path = os.path.join(json_output_dir, "workouts.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(json_data, f, indent=2, ensure_ascii=False)

print(f"✅ JSON estruturado salvo em: {json_path}")
