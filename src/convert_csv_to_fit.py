import os
import subprocess

# Diretórios
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
csv_dir = os.path.join(BASE_DIR, "data", "structured", "csv_manual")
fit_dir = os.path.join(BASE_DIR, "data", "structured", "fit")
fit_tool_path = os.path.join(BASE_DIR, "tools", "FitCSVTool.jar")  # ajuste se necessário

# Garante que a pasta FIT existe
os.makedirs(fit_dir, exist_ok=True)

# Lista arquivos CSV na pasta csv_llm
csv_files = [f for f in os.listdir(csv_dir) if f.endswith(".csv")]

for csv_file in csv_files:
    csv_path = os.path.join(csv_dir, csv_file)
    fit_name = csv_file.replace(".csv", ".fit")
    fit_path = os.path.join(fit_dir, fit_name)

    print(f"🚀 Convertendo: {csv_file} → {fit_name}")
    
    try:
        subprocess.run(
            ["java", "-jar", fit_tool_path, "-c", csv_path, fit_path],
            check=True
        )
        print(f"✅ FIT gerado com sucesso: {fit_path}\n")
    except subprocess.CalledProcessError:
        print(f"❌ Erro ao converter: {csv_file}\n")
