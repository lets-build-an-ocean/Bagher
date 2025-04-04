import socket


port = 80

def get_local_ipv4():
    """This function retrieves the machine's local IPv4 address."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            # Connect to an arbitrary address
            s.connect(('11.22.8.0', 80))
            local_ipv4 = s.getsockname()[0]
        return local_ipv4

    except Exception as e:
        print(f"Error getting local IPv4 address: {e}")
        return None