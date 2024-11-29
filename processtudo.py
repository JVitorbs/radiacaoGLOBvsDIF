import pandas as pd
import tkinter as tk
from tkinter import filedialog
import os

# Inicializar o Tkinter
root = tk.Tk()
root.withdraw()

# Selecionar a pasta onde está o arquivo CSV
pasta = filedialog.askdirectory()

# Definir o caminho do arquivo final
arquivo_final = os.path.join(pasta, "arquivo_final_date_vld.csv")

# Carregar o arquivo CSV, especificando o delimitador e a linha do cabeçalho
try:
    data = pd.read_csv(arquivo_final, delimiter=',', header=0)
    print("Arquivo carregado com sucesso")
except Exception as e:
    print(f"Erro ao carregar o arquivo: {e}")
    exit()

# Filtrar apenas as colunas necessárias e remover linhas com dados faltantes em 'Global_AVG' e 'Diffuse_AVG'
try:
    data_filtered = data[['Year', 'Day', 'Min', 'Global_AVG', 'Diffuse_AVG']].copy()
    data_filtered['Global_AVG'] = pd.to_numeric(data_filtered['Global_AVG'], errors='coerce')
    data_filtered['Diffuse_AVG'] = pd.to_numeric(data_filtered['Diffuse_AVG'], errors='coerce')
    data_filtered = data_filtered.dropna(subset=['Global_AVG', 'Diffuse_AVG'])
except KeyError as e:
    print(f"Erro ao filtrar colunas: {e}")
    exit()

# Criar um DataFrame vazio para armazenar os dados de todos os anos
data_final = pd.DataFrame()

# Processar dados para cada ano de 2007 a 2022
for ano in range(2007, 2023):
    print(f"Processando dados para o ano {ano}...")

    # Filtrar os dados para o ano atual
    data_ano = data_filtered[data_filtered['Year'] == ano]

    # Verificar se há linhas após o filtro do ano
    if len(data_ano) == 0:
        print(f"Nenhum dado encontrado para o ano de {ano}.")
        continue

    # Converter 'Min' para inteiro
    data_ano['Min'] = data_ano['Min'].astype(int)

    # Filtrar para intervalos de 10 minutos
    data_ano = data_ano[data_ano['Min'] % 10 == 0]

    # Adicionar dados do ano atual ao DataFrame final
    data_final = pd.concat([data_final, data_ano])

# Verificar as primeiras linhas do DataFrame final para verificação
print("Primeiras linhas do dataframe final:")
print(data_final.head())

# Salvar os dados filtrados em um único arquivo CSV com delimitador especificado
output_file = os.path.join(pasta, "csv_processado_2007_2022.csv")
data_final.to_csv(output_file, index=False, sep=',')

print(f"Dados processados foram salvos em: {output_file}")
print("Processamento concluído para todos os anos.")
