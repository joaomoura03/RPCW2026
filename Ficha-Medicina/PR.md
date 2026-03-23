# Ficha Medicina

## Metainformação
- **Título:** Povoamento e queries sobre ontologia medical.ttl
- **Data:** 2026-03-23
- **Autor:**
  - **Id:** PG60273
  - **Nome:** João Miguel Mendes Moura

### Povoamento

Na primeira fase do trabalho, temos de povoar a ontologia com 3 csv's e um json. Para isso corri dois scripts, um para os csv's e outro para o json.

#### populate_csv.py

Ao correr o primeiro script populate_csv.py, como dados de entrada temos a ontologia medical.ttl e os 3 ficheiros csv fornecidos (Disease_Description.csv, Disease_Syntoms.csv e Disease_Treatment.csv) e como resultado são nos devolvidas duas ontologias. A primeira ontologia é o resultado da povação da ontologia medical.ttl com base nos csv's Disease_Syntoms e Disease_Description que gera a ontologia med_doncas.ttl. Na segunda fase desse script, é usada a ontologia criada e o csv Disease_Treatment, que gera a ontologia med_tratamentos.ttl. 

#### populate_json.py

No segundo script, é usado como entrada a ontolofia med_tratamentos.ttl, que foi a ontologia criada mais recentemente e também é usado o ficheiro doentes.json. O resultado deste script é guardado na nova ontologia med_doentes.ttl.