import socket


def init_client(host = '127.0.0.1', port = 65432):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))

        data = sock.recv(1024).decode('utf-8')
        print(f"{data}")
        
        while True:
            msg = input("YOU >>> ")
            
            sock.send(msg.encode('utf-8'))

            try:
                data = sock.recv(1024)
                length = len(data.decode('utf-8'))
                print(f"{str(data.decode('utf-8')):>{(lambda length: length if (length > 88) else 128)(length)}} <<< DYNA")
            except:
                pass

            if msg.lower() in ["exit", "quit"] or msg == "@Quit":
                break
        sock.close()
            
    except socket.error as msg:
        print("Socket Initialization failed: " + str(msg))

if __name__ == "__main__":
    init_client()