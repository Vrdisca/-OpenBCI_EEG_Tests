from brainflow import BrainFlowInputParams, BoardIds, BoardShim
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
import socket
import json
import numpy as np
from scipy.stats import entropy

# Configuração da BrainFlow
params = BrainFlowInputParams()

# Inicializa a placa
board_id = BoardIds.CYTON_DAISY_BOARD.value
board = BoardShim(board_id, params)
board.prepare_session()

# Inicia a transmissão de dados
num_samples = 256
board.start_stream(num_samples)

# Inicialize a aplicação Qt
app = QApplication([])

# Crie o layout gráfico
layout = pg.GraphicsLayoutWidget(show=True, title="Sinais de EEG")
plot1 = layout.addPlot(title="Canal 1")
layout.nextRow()
plot2 = layout.addPlot(title="Canal 2")
layout.nextRow()
plot3 = layout.addPlot(title="Entropia")
layout.nextRow()
plot4 = layout.addPlot(title="Relação Sinal/Ruído")
curve1 = plot1.plot(pen='y')
curve2 = plot2.plot(pen='r')
curve3 = plot3.plot(pen='g')
curve4 = plot4.plot(pen='b')

# Configuração do socket UDP
udp_ip = "0.0.0.0"  # Endereço IP local
udp_port = 1883
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Função de cálculo da relação sinal/ruído
def signal_to_noise(data):
    mean = np.mean(data)
    std_dev = np.std(data)
    return mean / std_dev if std_dev != 0 else 0

# Função de cálculo da entropia e relação sinal/ruído
def calculate_metrics(data):
    ent = entropy(data)
    snr = signal_to_noise(data)
    return ent, snr

# Função de atualização dos gráficos
def update():
    new_data = board.get_current_board_data(256)
    curve1.setData(new_data[1])
    curve2.setData(new_data[2])
    
    ent1, snr1 = calculate_metrics(new_data[1])
    ent2, snr2 = calculate_metrics(new_data[2])
    
    entropies = [ent1, ent2]
    snrs = [snr1, snr2]
    
    curve3.setData(entropies)
    curve4.setData(snrs)
    
    data_dict = {"channel_1": new_data[1].tolist(), "channel_2": new_data[2].tolist()}
    message = json.dumps(data_dict)
    sock.sendto(message.encode(), (udp_ip, udp_port))

# Configuração do timer
timer = QTimer()
timer.timeout.connect(update)
timer.start(50)

# Execute a aplicação
app.exec_()

# Encerre a sessão da placa ao sair da aplicação
board.stop_stream()
board.release_session()
