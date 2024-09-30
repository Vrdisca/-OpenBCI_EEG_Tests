from brainflow import BrainFlowInputParams, BoardIds, BoardShim
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
import socket
import json
import numpy as np

# Configurando os parâmetros de acordo com a Biblioteca
params = BrainFlowInputParams()
params.serial_port='/dev/ttyUSB0'
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
curve1 = plot1.plot(pen='y')
curve2 = plot2.plot(pen='r')

# Configuração do socket UDP
udp_ports = [1883, 1884]  # Portas diferentes para evitar conflitos
udp_ips = ["10.0.0.103", "10.0.0.104"]  # Endereços IP dos computadores receptores
socks = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM) for _ in udp_ips]

# Função de atualização dos gráficos
def update():
    new_data = board.get_current_board_data(256)
    curve1.setData(new_data[1])  # Atualiza o gráfico do canal 1
    curve2.setData(new_data[14])  # Atualiza o gráfico do canal 2

    # Cria o dicionário data_dict e as listas dos canais
    data_dict = {"channel_1": new_data[1].tolist(), "channel_2": new_data[2].tolist()}
    message = json.dumps(data_dict)
    for i in range(len(udp_ips)):
        socks[i].sendto(message.encode(), (udp_ips[i], udp_ports[i]))

# Configuração do timer
timer = QTimer()
timer.timeout.connect(update)
timer.start(50)

# Execute a aplicação
app.exec_()

# Encerre a sessão da placa ao sair da aplicação
board.stop_stream()
board.release_session()
