import socket
import json

udp_ip = "10.0.0.103"  # Endereço IP local
udp_port = 1883

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((udp_ip, udp_port))

print(f"Listening on {udp_ip}:{udp_port}")

while True:
    try:
        data, addr = sock.recvfrom(65535)
        data_dict = json.loads(data.decode())
        print(f"Dados recebidos de {addr}: Canal 1 -> {data_dict['channel_1']}")
    except KeyboardInterrupt:
        print("Recepção de dados interrompida pelo usuário.")
        break
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

sock.close()
