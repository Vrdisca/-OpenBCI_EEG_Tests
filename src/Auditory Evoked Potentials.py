from brainflow import BrainFlowInputParams, BoardIds, BoardShim
import numpy as np
import time
import matplotlib.pyplot as plt
import sounddevice as sd

#Configurando os parâmetros de acordo com a Biblioteca Brainflow
params=BrainFlowInputParams()

#Inicialização da placa
board_id=BoardIds.CYTON_DAISY_BOARD.value
board=BoardShim(board_id, params)
board.prepare_session()

# Função para gerar um tom senoidal
def generate_sine_wave(frequency, duration, sample_rate=44100):
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    wave = 0.5 * np.sin(2 * np.pi * frequency * t)
    # plt.plot(wave)
    # plt.ylim(-1,1)
    # plt.xlim(0,640)
    # plt.show()
    return wave

# Frequências para os potenciais auditivos evocados (por exemplo, 1000 Hz e 2000 Hz)
frequencies = [300]  # Frequências em Hz
duration = 0.1  # Duração em segundos

#Configuração do número de amostras e inicilização da transmissão
num_samples=256
print(board.get_board_descr(board_id))
board.start_stream(num_samples)
time.sleep(5)
wave = generate_sine_wave(300, duration)
sd.play(wave, samplerate=44100)
time.sleep(1)
data=board.get_current_board_data(num_samples)
plt.subplot(2,1,1)
plt.plot(data[14])
plt.title("Canal 1")
plt.subplot(2,1,2)
plt.plot(data[14])
plt.title("Canal 2")
plt.show()

