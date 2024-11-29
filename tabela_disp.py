import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import tkinter as tk
from tkinter import filedialog

# Inicializar o Tkinter
root = tk.Tk()
root.withdraw()

# Selecionar a pasta onde está o arquivo .dat
pasta = filedialog.askdirectory(title='Selecione a pasta onde está o arquivo .dat')

# Definir o caminho do arquivo .dat
arquivo_dat = f"{pasta}/difusa_corrigida_com_geometria_solar.dat"

# Carregar o arquivo .dat
data_filtered = pd.read_csv(arquivo_dat, delimiter=',')  # Ajuste o delimitador conforme necessário

# Filtrar os dados para o ano de 2015
data_filtered = data_filtered[data_filtered['Year'] == 2015]

# Verificar e corrigir a falha de data (remover repetição dos primeiros 20 dias)
data_filtered = data_filtered.drop_duplicates(subset=['Year', 'Day', 'Min'])

# Calcular a elevação solar (Elev) se necessário
if 'Elev' not in data_filtered.columns:
    latitude = -5.836749  # Latitude correta
    longitude = -35.206500  # Longitude correta

    def calculate_solar_elevation(row, latitude, longitude):
        day_of_year = int(row['Day'])  # Dia do ano (1 a 365)
        solar_time = int(row['Min']) / 60  # Tempo solar (horas)
        declination = 23.45 * np.sin(np.radians(360 * (284 + day_of_year) / 365))
        hour_angle = 15 * (solar_time - 12)
        solar_zenith = np.degrees(np.arccos(
            np.sin(np.radians(latitude)) * np.sin(np.radians(declination)) +
            np.cos(np.radians(latitude)) * np.cos(np.radians(declination)) * np.cos(np.radians(hour_angle))
        ))
        solar_elevation = 90 - solar_zenith
        return solar_elevation

    data_filtered['Elev'] = data_filtered.apply(calculate_solar_elevation, axis=1, args=(latitude, longitude))

# Calcular a radiação extraterrestre (E0) se necessário
if 'E0' not in data_filtered.columns:
    data_filtered['E0'] = 1367 * (1 + 0.033 * np.cos(np.radians(360 * data_filtered['Day'] / 365)))

# Calcular o índice de claridade (Kt)
data_filtered['Kt'] = data_filtered['Global_AVG'] / data_filtered['E0']

# Calcular a fração difusa (Kd)
data_filtered['Kd'] = data_filtered['Diffuse_CORRIGIDA'] / data_filtered['Global_AVG']

# Excluir dados com Elev < 5 graus
data_filtered = data_filtered[data_filtered['Elev'] >= 5]

# Excluir dados suspeitos (Difusa = Global) para intervalos > 600 W/m² e difusa > 650 W/m²
data_filtered = data_filtered[~((data_filtered['Global_AVG'] > 600) & (data_filtered['Global_AVG'] == data_filtered['Diffuse_CORRIGIDA']))]
data_filtered = data_filtered[data_filtered['Diffuse_CORRIGIDA'] <= 650]

# Filtrar apenas os dados válidos para o gráfico de dispersão
filtered_data = data_filtered[(data_filtered['Kd'].notnull()) & (data_filtered['Kd'] >= 0) & (data_filtered['Kd'] <= 1) & (data_filtered['Kt'].notnull()) & (data_filtered['Kt'] >= 0) & (data_filtered['Kt'] <= 1)]

# Função de cálculo da fração difusa segundo o modelo de Erbs
def erbs_diffuse_fraction(Kt):
    if Kt <= 0.22:
        Kd = 1 - 0.09 * Kt
    elif Kt <= 0.8:
        Kd = 0.9511 - 0.1604 * Kt + 4.388 * Kt**2 - 16.638 * Kt**3 + 12.336 * Kt**4
    else:
        Kd = 0.165
    return Kd

# Calcular a curva de ajuste usando o modelo de Erbs
params = np.polyfit(filtered_data['Kt'], filtered_data['Kd'], 4)

# Calcular resíduos e RMSE
filtered_data['Kd_estimated'] = np.polyval(params, filtered_data['Kt'])
filtered_data['Residual'] = filtered_data['Kd'] - filtered_data['Kd_estimated']
std_residual = np.std(filtered_data['Residual'])
rmse = np.sqrt(np.mean(filtered_data['Residual']**2))

# Criar dataframe com os resultados
resultados = pd.DataFrame({
    'Parâmetro': ['beta_0', 'beta_1', 'Desvio padrão dos resíduos', 'RMSE'],
    'Valor': [round(params[0], 3), round(params[1], 3), round(std_residual, 3), round(rmse, 3)]
})

# Mostrar resultados em formato tabular com matplotlib
fig, ax = plt.subplots(figsize=(8, 4))
ax.axis('off')
ax.axis('tight')
ax.table(cellText=resultados.values, colLabels=resultados.columns, cellLoc='center', loc='center')

plt.title('Resultados da Curva Erbs Teórica e Estatísticas de Erro')
plt.show()

# Criar o gráfico de dispersão usando seaborn
plt.figure(figsize=(10, 6))
sns.scatterplot(x='Kt', y='Kd', data=filtered_data, s=10, color='blue', alpha=0.5)
plt.xlabel('Índice de claridade (Kt)')
plt.ylabel('Fração difusa (Kd)')
plt.title('Dispersão da fração difusa (Kd) vs. índice de claridade (Kt) - Ano 2015')
plt.grid(True)

# Plotar a curva de Erbs
erbs_kt_range = np.linspace(0, 1, 100)
erbs_kd_values = [erbs_diffuse_fraction(kt) for kt in erbs_kt_range]
plt.plot(erbs_kt_range, erbs_kd_values, color='red', label='Curva de Erbs')

plt.legend()
plt.show()
