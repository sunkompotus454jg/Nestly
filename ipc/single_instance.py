import sys
from PyQt6.QtNetwork import QLocalServer, QLocalSocket

class IPCManager:
    """Manages Single Instance enforcement and IPC messaging."""
    def __init__(self, server_name, on_create_new_callback):
        self.server_name = server_name
        self.on_create_new = on_create_new_callback
        self.server = None

    def check_running(self):
        """Checks if another instance is running. If so, sends CREATE_NEW if requested and returns True."""
        socket = QLocalSocket()
        socket.connectToServer(self.server_name)
        
        if socket.waitForConnected(500):
            if "--create" in sys.argv:
                socket.write(b"CREATE_NEW")
                socket.waitForBytesWritten(500)
            return True
        return False

    def start_server(self):
        """Starts the local server to listen for commands from other instances."""
        self.server = QLocalServer()
        self.server.removeServer(self.server_name)
        self.server.listen(self.server_name)
        self.server.newConnection.connect(self.handle_new_connection)

    def handle_new_connection(self):
        socket = self.server.nextPendingConnection()
        if socket.waitForReadyRead(1000):
            message = socket.readAll().data().decode('utf-8')
            if message == "CREATE_NEW" and self.on_create_new:
                self.on_create_new()
        socket.disconnectFromServer()
