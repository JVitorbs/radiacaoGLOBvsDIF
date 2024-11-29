import pandas as pd
import numpy as np
import tkinter as tk
from tkinter import filedialog
import seaborn as sns
import matplotlib.pyplot as plt
import pvlib

# Função para inicializar Tkinter e selecionar pasta
def selecionar_pasta():
    root = tk.Tk()
    root.withdraw()
    pasta = filedialog.askdirectory(title='Selecione a pasta onde está o arquivo CSV processado')
    return pasta

# Função para carregar dados do arquivo .dat
def carregar_dados(arquivo):
    try:
        data = pd.read_csv(arquivo, delimiter=',')
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
        declination = row['declinacao']
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

# Função para calcular fração difusa (Kd) usando o modelo Erbs
def calcular_kd_erbs(data):
    results = pvlib.irradiance.erbs(data['Global_AVG'], data['solar_zenith'], data['Day'])
    data['Kd_estimada'] = results['dhi'] / data['Global_AVG']
    data['DHI'] = results['dhi']
    data['DNI'] = results['dni']
    return data

# Função para calcular fração difusa usando a fórmula de Erbs ajustada
def erbs_model(Kt):
    if Kt <= 0.22:
        return 1.0 - 0.09 * Kt
    elif Kt <= 0.80:
        return 0.9511 - 0.1604 * Kt + 4.388 * Kt**2 - 16.638 * Kt**3 + 12.336 * Kt**4
    else:
        return 0.165

# Função para detectar e remover outliers
def remover_outliers(data):
    Q1 = data['Kd_estimada'].quantile(0.25)
    Q3 = data['Kd_estimada'].quantile(0.75)
    IQR = Q3 - Q1
    filtro = (data['Kd_estimada'] >= (Q1 - 1.5 * IQR)) & (data['Kd_estimada'] <= (Q3 + 1.5 * IQR))
    return data[filtro]

# Função principal para processar dados e calcular parâmetros da curva ajustada
def processar_dados():
    pasta = selecionar_pasta()
    if not pasta:
        print("Nenhuma pasta selecionada.")
        return

    arquivo_processado = f"{pasta}/difusa_corrigida_com_geometria_solar.dat"
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
    filtered_data = data_filtered[(data_filtered['Kd_estimada'].notnull()) & 
                                  (data_filtered['Kd_estimada'] >= 0) & 
                                  (data_filtered['Kd_estimada'] <= 1) & 
                                  (data_filtered['Kt'].notnull()) & 
                                  (data_filtered['Kt'] >= 0) & 
                                  (data_filtered['Kt'] <= 1)]

    # Remover outliers
    filtered_data = remover_outliers(filtered_data)

    # Criar dataframe com os resultados
    resultados = pd.DataFrame({
        'Kt': filtered_data['Kt'],
        'Kd_estimada': filtered_data['Kd_estimada']
    })

    # Calcular Kd teórico usando a fórmula de Erbs
    Kt_values = np.linspace(0, 1, 100)
    Kd_teorico = [erbs_model(Kt) for Kt in Kt_values]

    # Plotar curva real vs curva ajustada (Erbs) usando Seaborn
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='Kt', y='Kd_estimada', data=filtered_data, color='blue', label='Dados reais', s=30, alpha=0.6)
    plt.plot(Kt_values, Kd_teorico, color='red', linestyle='-', label='Curva teórica (Erbs)', linewidth=2)

    # Ajustar limites dos eixos
    plt.xlim(0, 1)
    plt.ylim(0, 1)

    plt.xlabel('Kt')
    plt.ylabel('Kd')
    plt.title('Curva real vs Curva teórica (Erbs)')
    plt.legend()
    plt.show()

    # Salvar dataframe em CSV se necessário
    arquivo_resultados = f"{pasta}/resultados_erbs.csv"
    resultados.to_csv(arquivo_resultados, index=False)
    print(f"\nResultados salvos em {arquivo_resultados}")

# Executar a função principal
processar_dados()
