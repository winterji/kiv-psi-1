import socket

def startup():
    print("Server is starting up...")
    # Create a socket object
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Get the hostname
    host = socket.gethostname()
    # Reserve a port for your service.
    port = 8080
    # Bind to the port
    server.bind((host, port))
    # Now wait for client connection.
    server.listen(5)
    print("Server is ready to receive connections!")
    return server

welcome_msg = b"<html><body><h1>Thanks for connecting</h1></body></html>"


if __name__ == "__main__":
    server = startup()
    while True:
        # Establish connection with client.
        client, addr = server.accept()
        print("Got connection from", addr)
        data = client.recv(1024)
        # return html page
        client.send(b"HTTP/1.1 200 OK\r\nConent-Type: text/html\r\nContent-Length: " + str(len(welcome_msg)).encode() + b"\r\n\r\n" + welcome_msg + b"\r\n")
        # client.send(b"<html><body><h1>Thanks for connecting</h1></body></html>")
        client.close()