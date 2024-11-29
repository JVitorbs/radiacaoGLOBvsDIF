import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog
import os

# Inicializar o Tkinter
root = tk.Tk()
root.withdraw()

# Função para calcular a declinação solar
def calc_declination(day_of_year):
    return -23.45 * np.cos(2 * np.pi * (day_of_year + 10) / 365)

# Função para corrigir os dados de difusa
def corrige_difusa_anel(obsdata, lat, dx):
    F = np.array([
        [1.1, 1.11, 1.12, 1.12, 1.13, 1.13, 1.14, 1.14, 1.14],
        [1.11, 1.11, 1.12, 1.13, 1.13, 1.13, 1.14, 1.14, 1.14],
        [1.11, 1.12, 1.12, 1.13, 1.13, 1.13, 1.14, 1.14, 1.14],
        [1.11, 1.12, 1.12, 1.13, 1.13, 1.14, 1.14, 1.14, 1.14],
        [1.12, 1.12, 1.13, 1.13, 1.13, 1.14, 1.14, 1.14, 1.14],
        [1.12, 1.12, 1.13, 1.13, 1.13, 1.14, 1.14, 1.13, 1.13],
        [1.12, 1.13, 1.13, 1.13, 1.13, 1.14, 1.13, 1.13, 1.13],
        [1.12, 1.13, 1.13, 1.13, 1.13, 1.13, 1.13, 1.13, 1.13],
        [1.13, 1.13, 1.13, 1.13, 1.13, 1.13, 1.13, 1.13, 1.12],
        [1.13, 1.13, 1.13, 1.13, 1.13, 1.13, 1.13, 1.12, 1.12],
        [1.13, 1.13, 1.13, 1.13, 1.13, 1.13, 1.13, 1.12, 1.12],
        [1.13, 1.13, 1.13, 1.13, 1.13, 1.13, 1.12, 1.12, 1.11],
        [1.13, 1.13, 1.13, 1.13, 1.13, 1.12, 1.12, 1.11, 1.11],
        [1.13, 1.13, 1.13, 1.13, 1.13, 1.12, 1.12, 1.11, 1.1],
        [1.13, 1.13, 1.13, 1.13, 1.12, 1.12, 1.11, 1.11, 1.1],
        [1.13, 1.13, 1.13, 1.13, 1.12, 1.11, 1.11, 1.1, 1.09],
        [1.13, 1.13, 1.13, 1.12, 1.12, 1.11, 1.1, 1.1, 1.09],
        [1.13, 1.13, 1.13, 1.12, 1.12, 1.11, 1.1, 1.09, 1.08],
        [1.13, 1.13, 1.12, 1.12, 1.11, 1.11, 1.1, 1.09, 1.08],
        [1.13, 1.13, 1.12, 1.12, 1.11, 1.1, 1.09, 1.08, 1.08],
        [1.13, 1.12, 1.12, 1.11, 1.11, 1.1, 1.09, 1.08, 1.07],
        [1.13, 1.12, 1.12, 1.11, 1.11, 1.1, 1.09, 1.08, 1.07],
        [1.12, 1.12, 1.11, 1.11, 1.1, 1.09, 1.08, 1.07, 1.07],
        [1.12, 1.12, 1.11, 1.1, 1.09, 1.08, 1.08, 1.07, 1.06],
        [1.12, 1.11, 1.11, 1.1, 1.09, 1.08, 1.07, 1.06, 1.05],
        [1.12, 1.11, 1.1, 1.09, 1.08, 1.08, 1.07, 1.06, 1.05]
    ])

    declindex = np.array([-24, -22, -20, -18, -16, -14, -12, -10, -8, -6, -4, -2, 0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24])
    latindex = np.array([5, 0, -5, -10, -15, -20, -25, -30, -35])

    # Converter a coluna 'Day' para o formato de dia do ano
    obsdata['Day'] = pd.to_datetime(obsdata['Day']).dt.dayofyear.astype(int)

    decl = calc_declination(obsdata['Day'].values)
    jlat = np.argmin(np.abs(latindex - lat))

    aux = np.array([decl - decli for decli in declindex])
    idecl = np.argmin(np.abs(aux), axis=0)

    k = F[idecl, jlat]
    obsdata.iloc[:, dx] = k * obsdata.iloc[:, dx]

    return obsdata

# Exemplo de uso com leitura de um arquivo CSV
# Selecionar a pasta onde está o arquivo CSV
pasta = filedialog.askdirectory()

# Definir o caminho do arquivo final
arquivo = os.path.join(pasta, "csv_processado_2022.csv")
data = pd.read_csv(arquivo)

# Especificar a latitude e o índice da coluna 'Diffuse_AVG' para correção
latitude = 0  # Substitua pela latitude da estação desejada
indice_dx = 4  # Índice da coluna 'Diffuse_AVG' (quinta coluna, índice 4)

# Aplicar a função para corrigir os dados de difusa
data_corrigida = corrige_difusa_anel(data, latitude, indice_dx)

# Salvar os dados corrigidos em um novo arquivo CSV
arquivo_saida = os.path.join(pasta, 'difusa_corrigida_2022.csv')
data_corrigida.to_csv(arquivo_saida, index=False)

print(f'Dados corrigidos foram salvos em: {arquivo_saida}')
