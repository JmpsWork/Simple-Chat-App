import socket
import _thread


class Server:
    def __init__(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port = 6666
        self.address = 'ADDRESS'
        self.connections = {}

    def setup(self):
        self.server.bind((self.address, self.port))
        self.server.listen()  # Listen for client connections

    def client_thread(self, conn):
        data = conn.recv(4096)
        decoded = data.decode()
        print(decoded)
        name, discrim = decoded.split(',')
        conn.send(f'Successfully connected.'.encode())
        conn_id = len(self.connections)
        conn.send(f'There are {len(conn_id) - 1} users online.'.encode())
        self.forward(f'{name}#{discrim} has joined the chat room. Say hi!', conn_id)
        self.connections[conn_id] = conn
        while True:
            try:
                data = conn.recv(4096)
                decoded = data.decode()
                if not decoded:
                    break
                print(f'Data received: {decoded}')
                self.forward(decoded, conn_id)
            except Exception as _:
                print(_)
                break
        self.connections.pop(conn_id)
        self.forward(f'{name}#{discrim} has left the chat room.', conn_id)

    def send_to(self, send_id: int, text: str):
        conn = self.connections[send_id]
        conn.send(text.encode())

    def forward(self, text: str, avoid_id: int):
        encoded = text.encode()
        for conn_id, conn in self.connections.items():
            if conn_id != avoid_id:
                try:
                    conn.send(encoded)
                except Exception as _:
                    raise _


print('Starting server...')
s = Server()
s.setup()
print('Setup complete. Now waiting for a connection.')

while True:
    conn, address = s.server.accept()
    print(f'Connection from {address}')
    _thread.start_new_thread(s.client_thread, (conn,))
