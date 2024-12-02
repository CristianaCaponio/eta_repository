import socket

host = socket.gethostname()
port = 4440

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

sock.bind(('0.0.0.0', port))

while True:
    data, addr = sock.recvfrom(1024)
    print(f"Received message: {list((map(hex, data)))} from {addr}")

    response_message = "Messaggio ricevuto!"
    sent = sock.sendto(response_message.encode(), addr)
