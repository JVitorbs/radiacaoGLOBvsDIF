import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

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

# Função para calcular fração difusa (Kd) baseada no modelo de Erbs et al. (1982)
def calcular_kd_erbs(data):
    def kd_erbs(Kt):
        if Kt <= 0.22:
            return 1 - 0.09 * Kt
        elif Kt <= 0.80:
            return 0.9511 - 0.1604 * Kt + 4.388 * Kt**2 - 16.638 * Kt**3 + 12.336 * Kt**4
        else:
            return 0.165
    data['Kd'] = data['Kt'].apply(kd_erbs)
    return data

# Função logística para ajuste
def logistic_function(x, beta_0, beta_1):
    return 1 / (1 + np.exp(-(beta_0 + beta_1 * x)))

# Função principal para processar dados e calcular parâmetros da curva ajustada
def processar_dados():
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
    data_filtered = calcular_kd_erbs(data_filtered)

    # Filtrar dados válidos
    filtered_data = data_filtered[(data_filtered['Kd'].notnull()) & (data_filtered['Kd'] >= 0) & (data_filtered['Kd'] <= 1) & 
                                  (data_filtered['Kt'].notnull()) & (data_filtered['Kt'] >= 0) & (data_filtered['Kt'] <= 1)]

    # Ajustar a curva logística aos dados
    popt, pcov = curve_fit(logistic_function, filtered_data['Kt'], filtered_data['Kd'])

    # Calcular resíduos
    filtered_data['Kd_estimated'] = logistic_function(filtered_data['Kt'], *popt)
    filtered_data['Residual'] = filtered_data['Kd'] - filtered_data['Kd_estimated']
    
    # Calcular desvio padrão dos resíduos
    std_residual = np.std(filtered_data['Residual'])
    
    # Calcular RMSE (Raiz do Erro Quadrático Médio)
    rmse = np.sqrt(np.mean(filtered_data['Residual']**2))

    # Criar dataframe com os resultados
    resultados = pd.DataFrame({
        'Parâmetro': ['beta_0', 'beta_1', 'Desvio padrão dos resíduos', 'RMSE'],
        'Valor': [round(popt[0], 3), round(popt[1], 3), round(std_residual, 3), round(rmse, 3)]
    })

    # Mostrar resultados em formato tabular com matplotlib
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.axis('off')
    ax.axis('tight')
    ax.table(cellText=resultados.values, colLabels=resultados.columns, cellLoc='center', loc='center')

    plt.title('Resultados da regressão logística')
    plt.show()

    # Salvar dataframe em CSV se necessário
    arquivo_resultados = f"{pasta}/resultados_regressao.csv"
    resultados.to_csv(arquivo_resultados, index=False)
    print(f"\nResultados salvos em {arquivo_resultados}")

# Executar a função principal
processar_dados()
