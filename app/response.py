import gzip


class Response:
    RESPONSE = {200: "200 OK", 201: "201 Created", 404: "404 Not Found"}

    def __init__(self) -> None:
        self.status = 500
        self.content_type = ""
        self.content_encoding = ""
        self.body = ""
        self.accept_encoding = []
        self.encoded_body = ""

    def generate(self):
        response = [f"HTTP/1.1 {Response.RESPONSE[self.status]}"]
        if self.accept_encoding:
            for encoding in self.accept_encoding:
                if encoding in ["gzip"]:
                    self.body = gzip.compress(self.body.encode())
                    self.content_encoding = encoding
        response.append(f"Content-Type: {self.content_type}")
        response.append(f"Content-Encoding: {self.content_encoding}")
        response.append(f"Content-Length: {len(self.body)}")
        response = "\r\n".join(response) + "\r\n\r\n"
        if self.content_encoding != "":
            response = response.encode() + bytes(self.body)
        else:
            response = response.encode() + self.body.encode()
        return response
