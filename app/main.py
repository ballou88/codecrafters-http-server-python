import socket  # noqa: F401


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")
    CLRF = "\r\n"
    HOST = "localhost"
    PORT = 4221

    # Uncomment this to pass the first stage
    #
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        connection, address = s.accept()
        with connection:
            while True:
                print(f"New connection from {address}")
                data = connection.recv(1024).decode("utf-8")
                request = data.split(CLRF)[0]
                print(f"Recieved request: {request}")
                _, path, _ = request.split()
                if path == "/":
                    connection.send(b"HTTP/1.1 200 OK\r\n\r\n")
                else:
                    connection.send(b"HTTP/1.1 404 Not Found\r\n\r\n")


if __name__ == "__main__":
    main()
