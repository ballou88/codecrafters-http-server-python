import socket
from typing import List  # noqa: F401


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
                request_data = data.split(CLRF)
                request = request_data[0]
                headers = request_data[1:-1]
                print(f"Recieved request: {request}")
                request_parts = request.split()
                path = request_parts[1]
                if path == "/":
                    connection.send(b"HTTP/1.1 200 OK\r\n\r\n")
                elif path == "/user-agent":
                    response = generate_user_agent_response(headers)
                    connection.send(response.encode())
                elif path.startswith("/echo/"):
                    response = generate_echo_response(path)
                    connection.send(response.encode())
                else:
                    connection.send(b"HTTP/1.1 404 Not Found\r\n\r\n")


def generate_user_agent_response(headers: List):
    for header in headers:
        if header.startswith("User-Agent:"):
            string = header.split()[1]
            length = len(string)
            return f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {length}\r\n\r\n{string}"
    return ""


def generate_echo_response(path):
    string = path.split("/")[2]
    length = len(string)
    return f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: {length}\r\n\r\n{string}"


if __name__ == "__main__":
    main()
