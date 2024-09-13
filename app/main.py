import socket  # noqa: F401


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    print("Logs from your program will appear here!")

    # Uncomment this to pass the first stage
    #
    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    client, address = server_socket.accept()

    print(f"New connection from {address}")
    response = "HTTP/1.1 200 OK\r\n\r\n"

    client.send(response.encode("utf-8"))
    print("Response Sent")

    client.close()


if __name__ == "__main__":
    main()
