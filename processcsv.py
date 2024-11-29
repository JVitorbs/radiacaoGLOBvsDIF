import pandas as pd
import tkinter as tk
from tkinter import filedialog, simpledialog

# Inicializar o Tkinter
root = tk.Tk()
root.withdraw()

# Selecionar a pasta onde está o arquivo CSV
pasta = filedialog.askdirectory()

# Definir o caminho do arquivo
arquivo = f"{pasta}/arquivo_final_date_vld.csv"

# Solicitar ao usuário que insira o ano desejado
ano = simpledialog.askstring("Input", "Digite o ano que deseja filtrar (ex: 2023):")

# Carregar o arquivo CSV, especificando o delimitador e a linha do cabeçalho
try:
    data = pd.read_csv(arquivo, delimiter=',', header=0)
    print("Arquivo carregado com sucesso")
except Exception as e:
    print(f"Erro ao carregar o arquivo: {e}")
    exit()

# Exibir as primeiras linhas do dataframe para verificação
print("Primeiras linhas do dataframe:")
print(data.head())

# Verificar as colunas disponíveis no dataframe
print("Colunas disponíveis no dataframe:")
print(data.columns)

# Verificar os tipos de dados das colunas
print("Tipos de dados das colunas:")
print(data.dtypes)

# Filtrar apenas as colunas necessárias e remover linhas com dados faltantes em 'Global_AVG' e 'Diffuse_AVG'
try:
    data_filtered = data[['Year', 'Day', 'Min', 'Global_AVG', 'Diffuse_AVG']].copy()
    data_filtered['Global_AVG'] = pd.to_numeric(data_filtered['Global_AVG'], errors='coerce')
    data_filtered['Diffuse_AVG'] = pd.to_numeric(data_filtered['Diffuse_AVG'], errors='coerce')
    data_filtered = data_filtered.dropna(subset=['Global_AVG', 'Diffuse_AVG'])
except KeyError as e:
    print(f"Erro ao filtrar colunas: {e}")
    exit()

# Exibir as primeiras linhas do dataframe filtrado para verificação
print("Primeiras linhas do dataframe filtrado:")
print(data_filtered.head())

# Verificar os valores únicos na coluna 'Year'
print("Valores únicos na coluna 'Year':")
print(data_filtered['Year'].unique())

# Filtrar os dados para o ano inserido pelo usuário
data_filtered = data_filtered[data_filtered['Year'] == int(ano)]

# Verificar se há linhas após o filtro do ano
print(f"Número de linhas após o filtro do ano {ano}: {len(data_filtered)}")

# Caso não haja linhas, encerrar o script
if len(data_filtered) == 0:
    print(f"Nenhum dado encontrado para o ano de {ano}.")
    exit()

# Converter 'Min' para inteiro
data_filtered['Min'] = data_filtered['Min'].astype(int)

# Filtrar para intervalos de 10 minutos
data_filtered = data_filtered[data_filtered['Min'] % 10 == 0]

# Exibir as primeiras linhas do dataframe após a filtragem
print("Primeiras linhas do dataframe após a filtragem:")
print(data_filtered.head())

# Salvar os dados filtrados em um novo arquivo CSV com delimitador especificado
output_file = f"{pasta}/csv_processado{ano}.csv"
data_filtered.to_csv(output_file, index=False, sep=',')

print(f"Dados processados foram salvos em: {output_file}")
