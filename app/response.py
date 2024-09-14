class Response:
    RESPONSE = {200: "200 OK", 201: "201 Created", 404: "404 Not Found"}

    def __init__(self) -> None:
        self.status = 500
        self.content_type = ""
        self.content_encoding = ""
        self.body = None

    def out(self):
        response = [f"HTTP/1.1 {Response.RESPONSE[self.status]}"]
        response.append(f"Content-Type: {self.content_type}")
        response.append(f"Content-Encoding: {self.content_encoding}")
        if self.body:
            response.append(f"Content-Length: {len(self.body)}")
        response = "\r\n".join(response) + "\r\n\r\n"
        if self.body:
            response = response.encode() + bytes(self.body)
        else:
            response = response.encode()
        return response
