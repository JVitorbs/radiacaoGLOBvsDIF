import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
from scipy.optimize import curve_fit

# Função para inicializar Tkinter e selecionar pasta
def selecionar_pasta():
    root = tk.Tk()
    root.withdraw()
    pasta = filedialog.askdirectory(title='Selecione a pasta onde está o arquivo CSV processado')
    return pasta

# Função para carregar dados do CSV
def carregar_dados(arquivo):
    try:
        data = pd.read_csv(arquivo)
        data['Day'] = pd.to_datetime(data['Day'], errors='coerce').dt.dayofyear
        data = data.dropna(subset=['Day'])
        return data
    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
        return None

# Função para calcular ângulo zenital
def calcular_angulo_zenital(data, latitude, longitude):
    def calc_zenith(row):
        day_of_year = int(row['Day'])
        solar_time = int(row['Min']) / 60
        declination = 23.45 * np.sin(np.radians(360 * (284 + day_of_year) / 365))
        hour_angle = 15 * (solar_time - 12)
        solar_zenith = np.degrees(np.arccos(
            np.sin(np.radians(latitude)) * np.sin(np.radians(declination)) +
            np.cos(np.radians(latitude)) * np.cos(np.radians(declination)) * np.cos(np.radians(hour_angle))
        ))
        return solar_zenith
    data['solar_zenith'] = data.apply(calc_zenith, axis=1)
    return data

# Função para calcular radiação extraterrestre
def calcular_radiacao_extraterrestre(data):
    data['extra_radiation'] = 1367 * (1 + 0.033 * np.cos(np.radians(360 * data['Day'] / 365)))
    return data

# Função para calcular índice de claridade (Kt)
def calcular_kt(data):
    data['Kt'] = data['Global_AVG'] / (data['extra_radiation'] * np.cos(np.radians(data['solar_zenith'])))
    return data

# Função para calcular fração difusa (Kd)
def calcular_kd(data):
    data['Kd'] = data['Diffuse_AVG'] / data['Global_AVG']
    return data

# Função polinomial para ajuste
def polynomial_function(x, a, b, c):
    return a + b * x + c * x**2

# Função principal para processar dados e plotar gráfico
def processar_e_plotar():
    pasta = selecionar_pasta()
    if not pasta:
        print("Nenhuma pasta selecionada.")
        return

    arquivo_processado = f"{pasta}/difusa_corrigida_2015.csv"
    data_filtered = carregar_dados(arquivo_processado)
    if data_filtered is None:
        return

    latitude = -5.836749  # Latitude correta
    longitude = -35.206500  # Longitude correta

    data_filtered = calcular_angulo_zenital(data_filtered, latitude, longitude)
    data_filtered = calcular_radiacao_extraterrestre(data_filtered)
    data_filtered = calcular_kt(data_filtered)
    data_filtered = calcular_kd(data_filtered)

    # Filtrar dados válidos
    filtered_data = data_filtered[(data_filtered['Kd'].notnull()) & (data_filtered['Kd'] >= 0) & (data_filtered['Kd'] <= 1) & 
                                  (data_filtered['Kt'].notnull()) & (data_filtered['Kt'] >= 0) & (data_filtered['Kt'] <= 1)]

    # Ajustar a curva polinomial aos dados
    popt, pcov = curve_fit(polynomial_function, filtered_data['Kt'], filtered_data['Kd'])

    # Criar o gráfico de dispersão
    plt.figure(figsize=(10, 6))
    plt.scatter(filtered_data['Kt'], filtered_data['Kd'], s=1, color='blue', alpha=0.5)
    plt.xlabel('Índice de claridade (Kt)')
    plt.ylabel('Fração difusa (Kd)')
    plt.title('Dispersão da fração difusa (Kd) vs. índice de claridade (Kt) no ano de 2015 corrigido')
    plt.grid(True)

    # Plotar a curva polinomial ajustada
    kt_range = np.linspace(filtered_data['Kt'].min(), filtered_data['Kt'].max(), 100)
    plt.plot(kt_range, polynomial_function(kt_range, *popt), color='red')

    plt.show()

    # Imprimir os coeficientes ajustados
    print(f"Coeficientes ajustados: a={popt[0]}, b={popt[1]}, c={popt[2]}")

# Executar a função principal
processar_e_plotar()