# Guia de Mapeamento: Markdown → JSON → CSV para .FIT (Garmin)

Este documento serve como base para a LLM gerar CSVs compatíveis com a ferramenta **FitCSVTool** e o **Garmin Connect**.

---

## 1. Mapeamento de Intensidade

A intensidade deve ser mapeada com base nas instruções do treino (como "caminhar", "trotar", etc):

| Descrição do treino          | Intensidade |
|-----------------------------|-------------|
| Aquecimento                 | 2           |
| Caminhada / Recuperação     | 1           |
| Corrida / Trote / Esforço   | 0           |
| Desaquecimento              | 3           |

---

## 2. Zona de Frequência Cardíaca (Obrigatória)

Para que o treino funcione no Garmin Connect, **é obrigatório** preencher:

- `target_type` = 1 (Heart Rate)
- `target_hr_zone` (valores de 1 a 5, conforme a meta do treino)
- `custom_target_heart_rate_low` e `custom_target_heart_rate_high` (usualmente 0 se não definido)

---

## 3. Estrutura de Blocos no CSV

Cada treino deve conter:

1. Bloco de `file_id`  
2. Bloco de `workout` com `wkt_name`, `sport`, `sub_sport`, `num_valid_steps`
3. Blocos `workout_step` para cada etapa, com:
   - `duration_type` = 0 (tempo em segundos)
   - `duration_time` = valor em segundos (`60.0`, `120.0`, etc.)
   - `intensity`, `target_type`, `target_hr_zone`
   - `repeat_steps` se necessário (`duration_type` = 6)

---

## 4. Exemplo de JSON Esperado da LLM

```json
{
  "wkt_name": "S3T3",
  "sport": 1,
  "sub_sport": 0,
  "steps": [
    { "index": 0, "label": "aquecimento", "intensity": 2, "duration_type": 0, "duration_value": 600 },
    { "index": 1, "label": "caminhada", "intensity": 1, "duration_type": 0, "duration_value": 60 },
    { "index": 2, "label": "corrida", "intensity": 0, "duration_type": 0, "duration_value": 120 },
    { "index": 3, "label": "repetição", "duration_type": 6, "duration_step": 1, "repeat_steps": 6 },
    { "index": 4, "label": "desaquecimento", "intensity": 3, "duration_type": 0, "duration_value": 300 }
  ]
}
