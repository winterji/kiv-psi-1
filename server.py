import socket
import re

ENVELOPE_START = "<html><head><style>table {border: 1px solid; width: 90%} th {border: 1px solid; font-weight: normal} td {border: 1px solid} .gateway {font-weight: bold}</style></head><body><h1>Routing table - winterji</h1>"
ENVELOPE_END = "</body></html>"

def startup():
    """
    Initializes and starts the server.

    This function performs the following steps:
    1. Prints a message indicating the server is starting up.
    2. Creates a socket object for network communication.
    3. Sets the server to listen to all incoming connections.
    4. Reserves a port (8080) for the service.
    5. Binds the server to the specified host and port.
    6. Puts the server in a listening state to accept client connections.
    7. Prints a message indicating the server is ready to receive connections.

    Returns:
        socket.socket: The initialized server socket ready to accept connections.
    """

    print("Server is starting up...")
    # Create a socket object
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # listen to all incoming connections
    host = "0.0.0.0"
    # Reserve a port for your service.
    port = 8080
    # Bind to the port
    server.bind((host, port))
    # Now wait for client connection.
    server.listen(5)
    print("Server is ready to receive connections!")
    return server

def read_route_table():
    """
    Reads the system's routing table from /proc/net/route and returns it as a list of dictionaries.
    Each dictionary in the list represents a route and contains the following keys:
    - iface: Interface name
    - dest: Destination address
    - gateway: Gateway address
    - flags: Flags
    - refcnt: Reference count
    - use: Number of uses
    - metric: Metric
    - mask: Netmask
    - mtu: Maximum transmission unit
    - window: Window size
    - irtt: Initial round trip time
    Returns:
        list: A list of dictionaries, each representing a route in the routing table.
    """

    with (open("/proc/net/route", "r")) as f:
        routes = []
        first_line = f.readline()
        while True:
            line = f.readline()
            if not line:
                break
            line = line.strip()
            line = line.split("\t")
            # print(line)
            line_dict = {
                "iface": line[0],
                "dest": line[1],
                "gateway": line[2],
                "flags": line[3],
                "refcnt": line[4],
                "use": line[5],
                "metric": line[6],
                "mask": line[7],
                "mtu": line[8],
                "window": line[9],
                "irtt": line[10]
            }
            routes.append(line_dict)
    return routes

def parse_flags(flags):
    """
    Parses a hexadecimal string of flags into a human-readable format and determines if the 'GATEWAY' flag is set.
    Args:
        flags (str): A string representing the flags in hexadecimal format.
    Returns:
        tuple: A tuple containing:
            - buff (str): A comma-separated string of flag names that are set.
            - is_gateway (bool): A boolean indicating if the 'GATEWAY' flag is set.
    """

    flags = int(flags, 16)
    is_gateway = False
    buff = ""
    if flags & 1:
        buff += "UP, "
    if flags & 2:
        buff += "GATEWAY, "
        is_gateway = True
    if flags & 4:
        buff += "HOST, "
    if flags & 8:
        buff += "REINSTATE, "
    if flags & 16:
        buff += "MODIFIED, "
    if flags & 32:
        buff += "DYNAMIC, "
    if flags & 64:
        buff += "XRESOLVE, "
    return buff, is_gateway

def print_route_table(routes):
    """
    Generates an HTML table representation of the given routing table.
    Args:
        routes (list of dict): A list of dictionaries where each dictionary represents a route.
            Each dictionary should have the following keys:
            - "iface" (str): The interface name.
            - "dest" (str): The destination address in hexadecimal format.
            - "mask" (str): The subnet mask in hexadecimal format.
            - "metric" (str): The metric value.
            - "gateway" (str): The gateway address in hexadecimal format.
            - "flags" (str): The flags associated with the route.
    Returns:
        str: An HTML string representing the routing table.
    """

    buff = '<table style="width: 90%"><tr><th>Interface</th><th>Destination</th><th>Mask</th><th>Metric</th><th>Gateway</th><th>Flags</th></tr>'
    for route in routes:
        flags, is_gateway = parse_flags(route["flags"])
        if is_gateway:
            buff += "<tr class='gateway'>"
        else:
            buff += "<tr>"
        buff += "<td>" + route["iface"] + "</td>"

        # format destination to 255.255.255.255 in decimal
        dest = route["dest"]
        dest = re.findall('..', dest)
        dest = [str(int(x, 16)) for x in dest][::-1]
        # reversed(dest)
        dest = ".".join(dest)
        buff += "<td>" + dest + "</td>"

        # format mask like destination
        mask = route["mask"]
        mask = re.findall('..', mask)
        mask = [str(int(x, 16)) for x in mask][::-1]
        # reversed(mask)
        mask = ".".join(mask)
        buff += "<td>" + mask + "</td>"

        buff += "<td>" + route["metric"] + "</td>"

        # format
        gateway = route["gateway"]
        gateway = re.findall('..', gateway)
        gateway = [str(int(x, 16)) for x in gateway][::-1]
        gateway = ".".join(gateway)
        buff += "<td>" + gateway + "</td>"

        # format flags
        buff += "<td>" + flags + "</td>"
        buff += "</tr>"
    buff += "</table>"
    return buff

def send_page(client: socket.socket, page: str):
    """
    Sends an HTTP response with the given HTML page content to the client.
    Args:
        client (socket.socket): The client socket to which the response will be sent.
        page (str): The HTML content to be sent as the response body.
    Returns:
        None
    """

    client.send(b"HTTP/1.1 200 OK\r\nConent-Type: text/html\r\nContent-Length: " + str(len(page)).encode() + b"\r\n\r\n" + page.encode() + b"\r\n")


if __name__ == "__main__":
    with startup() as server:
        while True:
            # Establish connection with client.
            client, addr = server.accept()
            print("Got connection from", addr)
            data = client.recv(1024)
            # return html page
            page = ENVELOPE_START + print_route_table(read_route_table()) + ENVELOPE_END
            send_page(client, page)
            # client.send(b"<html><body><h1>Thanks for connecting</h1></body></html>")
            client.close()