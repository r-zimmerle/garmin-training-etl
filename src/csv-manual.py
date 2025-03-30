import os
import json

# Caminhos de entrada/saída (ajuste conforme sua estrutura de diretórios)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
json_path = os.path.join(BASE_DIR, "data", "structured", "json", "workouts.json")
csv_output_dir = os.path.join(BASE_DIR, "data", "structured", "csv_manual")
os.makedirs(csv_output_dir, exist_ok=True)

# Cabeçalhos comuns para o CSV (File Id e Workout)
file_id_header = (
    "Type,Local Number,Message,Field 1,Value 1,Units 1,Field 2,Value 2,Units 2,"
    "Field 3,Value 3,Units 3,Field 4,Value 4,Units 4,Field 5,Value 5,Units 5,"
    "Field 6,Value 6,Units 6,Field 7,Value 7,Units 7,Field 8,Value 8,Units 8,"
)
file_id_definition = (
    "Definition,0,file_id,type,1,,manufacturer,1,,product,1,,serial_number,1,,time_created,1,,"
)
file_id_data = (
    'Data,0,file_id,type,"5",,manufacturer,"255",,product,"0",,serial_number,"960241704",,time_created,"960241704",,'
)
workout_definition = (
    "Definition,0,workout,wkt_name,13,,sport,1,,sub_sport,1,,num_valid_steps,1,,,,,"
)
# A linha de dados do workout será construída com base nos valores do JSON.
workout_step_definition = (
    "Definition,0,workout_step,message_index,1,,intensity,1,,duration_type,1,,duration_value,1,,"
    "target_type,1,,target_value,1,,custom_target_value_low,1,,custom_target_value_high,1,"
)

# Função para gerar a linha de dados de cada etapa (step)
def generate_step_line(step):
    index = step["index"]
    duration_type = step["duration_type"]
    # Se não for etapa de repetição (duration_type != 6), utiliza duration_value e demais campos
    if duration_type != 6:
        intensity = step["intensity"]
        duration_value = step["duration_value"]
        target_type = step["target_type"]
        target_value = step["target_value"]
        # Formata a duração como float com uma casa decimal (ex.: "600.0")
        line = (
            f'Data,0,workout_step,message_index,"{index}",,intensity,"{intensity}",,'
            f'duration_type,"{duration_type}",,duration_time,"{float(duration_value):.1f}",s,'
            f'target_type,"{target_type}",,target_value,"{target_value}",,'
            f'custom_target_value_low,"0",,custom_target_value_high,"0",'
        )
    else:
        # Para etapas de repetição, usamos duration_step e repeat_steps
        duration_step = step["duration_step"]
        repeat_steps = step["repeat_steps"]
        line = (
            f'Data,0,workout_step,message_index,"{index}",,duration_type,"6",,'
            f'duration_step,"{duration_step}",,repeat_steps,"{repeat_steps}",,,,,,,,,'
        )
    return line

# Carrega o JSON de treinos
with open(json_path, "r", encoding="utf-8") as f:
    workouts = json.load(f)

# Para cada treino, gera o CSV correspondente
for workout in workouts:
    wkt_name = workout["wkt_name"]
    sport = workout["sport"]
    sub_sport = workout["sub_sport"]
    steps = workout["steps"]
    num_steps = len(steps)

    # Monta as linhas do CSV
    lines = []
    lines.append(file_id_header)
    lines.append(file_id_definition)
    lines.append(file_id_data)
    lines.append(workout_definition)
    workout_data_line = f'Data,0,workout,wkt_name,"{wkt_name}",,sport,"{sport}",,sub_sport,"{sub_sport}",,num_valid_steps,"{num_steps}",,,,,,,'
    lines.append(workout_data_line)
    lines.append(workout_step_definition)
    
    for step in steps:
        lines.append(generate_step_line(step))
    
    # Junta todas as linhas com quebra de linha
    csv_content = "\n".join(lines)
    
    # Define o caminho e nome do arquivo CSV (baseado no wkt_name)
    filename = f"{wkt_name}.csv"
    csv_path = os.path.join(csv_output_dir, filename)
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write(csv_content)
    print(f"✅ CSV salvo: {csv_path}")
