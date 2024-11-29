import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog

# Inicializar o Tkinter
root = tk.Tk()
root.withdraw()

# Selecionar a pasta onde está o arquivo CSV
pasta = filedialog.askdirectory(title='Selecione a pasta onde está o arquivo CSV')

# Definir o caminho do arquivo
arquivo = f"{pasta}/arquivo_final_date_vld.csv"

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

# Filtrar apenas as colunas necessárias e remover linhas com dados faltantes em 'Year'
try:
    data_filtered = data[['Year']].copy()
    data_filtered['Year'] = pd.to_numeric(data_filtered['Year'], errors='coerce')
    data_filtered = data_filtered.dropna(subset=['Year'])
except KeyError as e:
    print(f"Erro ao filtrar colunas: {e}")
    exit()

# Exibir as primeiras linhas do dataframe filtrado para verificação
print("Primeiras linhas do dataframe filtrado:")
print(data_filtered.head())

# Contar a quantidade de dados por ano
data_count_by_year = data_filtered['Year'].value_counts().sort_index()

# Exibir os dados contados por ano para verificação
print("Quantidade de dados por ano:")
print(data_count_by_year)

# Plotar o gráfico de barras
plt.figure(figsize=(10, 6))
data_count_by_year.plot(kind='bar', color='skyblue')
plt.xlabel('Ano')
plt.ylabel('Quantidade de Dados')
plt.title('Quantidade de Dados por Ano')
plt.grid(True)

# Exibir o gráfico
plt.show()
