import numpy as np
import time
import matplotlib.pyplot as plt
import sounddevice as sd
from brainflow import BrainFlowInputParams, BoardIds, BoardShim
import random
from datetime import datetime

# Configurando os parâmetros de acordo com a Biblioteca Brainflow
params = BrainFlowInputParams()
params.serial_port='/dev/ttyUSB0'

# Inicialização da placa
board_id = BoardIds.CYTON_DAISY_BOARD.value
board = BoardShim(board_id, params)
board.prepare_session()

# Função para gerar um tom senoidal
def generate_sine_wave(frequency, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = 0.5 * np.sin(2 * np.pi * frequency * t)
    return wave

# Frequências para os potenciais auditivos evocados (exemplo: 1000 Hz e 2000 Hz)
frequencies = [300]  # Frequências em Hz
duration = 0.5  # Duração em segundos

# Configuração do número de amostras e inicialização da transmissão
num_samples = 256
board.start_stream(num_samples)
# time.sleep(5)

# Duração total em segundos (5 minutos)
total_duration = 5 * 60
start_time = time.time()
end_time = start_time + total_duration

# Lista para registrar os horários dos sinais sonoros
signal_times = []
graph_files = []  # Lista para armazenar os nomes dos arquivos de gráficos

# Lista para registrar os tempos relativos dos disparos
signal_relative_times = []

# Loop até completar os 5 minutos
signal_count = 0  # Contador de sinais sonoros
while time.time() < end_time:
    # Tempo aleatório entre 5 e 10 segundos para disparar o próximo sinal
    next_signal_time = random.uniform(5, 20)
    time.sleep(next_signal_time)

    # Gerar e tocar o sinal sonoro
    frequency = random.choice(frequencies)
    wave = generate_sine_wave(frequency, duration)
    sd.play(wave, samplerate=44100)

    # Registrar o tempo do sinal sonoro
    signal_time = datetime.now()
    signal_relative_time = time.time() - start_time  # Tempo relativo ao início
    signal_times.append(signal_time)
    signal_relative_times.append(signal_relative_time)
    print(f"Sinal sonoro disparado em: {signal_time}")

    # Esperar o sinal terminar
    sd.wait()

    # Capturar o EEG por 2 segundos após o sinal sonoro
    post_signal_duration = 2
    time.sleep(post_signal_duration)

    # Coletar dados do EEG
    data = board.get_current_board_data(num_samples)
    
    # Gerar nome de arquivo para o gráfico
    graph_filename = f"eeg_graph_{signal_count}.png"
    
    # Plotar e salvar o gráfico sem mostrar ainda
    plt.figure()
    plt.subplot(2, 1, 1)
    plt.plot(data[14])
    plt.title(f"Canal 1 - Tentativa {signal_count}")
    plt.subplot(2, 1, 2)
    plt.plot(data[14])
    plt.title(f"Canal 2 - Tentativa {signal_count}")
    
    plt.savefig(graph_filename)  # Salvar o gráfico
    graph_files.append(graph_filename)  # Adicionar o nome do arquivo à lista
    plt.close()  # Fechar o gráfico para economizar memória
    
    signal_count += 1  # Incrementar o contador de sinais

# Encerrar a sessão da placa
board.stop_stream()
board.release_session()

# Exibir os horários dos sinais sonoros
print("Horários dos sinais sonoros:")
for time_signal in signal_times:
    print(time_signal)

# Mostrar todos os gráficos salvos após os 5 minutos
for graph_file in graph_files:
    img = plt.imread(graph_file)
    plt.figure()
    plt.imshow(img)
    plt.axis('off')  # Desativar os eixos
    plt.show()

# Gráfico adicional para mostrar os momentos dos disparos dos sinais sonoros
plt.figure()
plt.eventplot(signal_relative_times, orientation='horizontal', colors='r')
plt.title("Registro dos Disparos dos Sinais Sonoros")
plt.xlabel("Tempo (segundos)")
plt.yticks([])  # Remover os ticks do eixo y para simplificar
plt.show()
