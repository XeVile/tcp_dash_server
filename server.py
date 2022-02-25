from datetime import datetime
import logging
from pathlib import Path
import socket
from time import sleep
import db_func as db

# Setup logger
logging.basicConfig(filename='logged.log', filemode='w', format='%(name)s - %(levelname)s - %(message)s')

# Response information
options = "\n\n\tList of possible options:\n\t\t\
                > Calc\n\t\t\
                > Stat\n\t\t\
                > Now\n\t\t\
                > Chat\n\t\t\
                > Help\n\t\t\
                > @Quit to Kill Server!\n\
                Can also try other text\n"
welcomeResp = "\nWelcome! You are connected to Divoc V0.3" + options

stat = None

# Global variables for access
conn_List = []
addr_List = []
recv_list = []
send_list = []


def log(initializer, msg):
    print(f"{initializer}: {str(msg)}")
    logging.warning(f"{initializer}: {str(msg)}")

def time():
    return str(datetime.now().strftime("%H:%M:%S"))

# Server programming starts here

# Function to run each new thread as requested by server initialization
# Thread function


class server:
    """A server class that can create, bind and accept connections\n
        Initialize server using host, port and thread (Must have)
        Default: 127.0.0.1 (HOST), 65432 (PORT)
        1) create() -> Make socket and listen
        2) allow_connects() -> Accept an incoming connection and send response
        3) """

    def __init__(self, host, port, thread = None):
        self.__host = host
        self.__port = port
        self.__kill = False
        self.__timeout = False
        self.__thread= thread
        self.numOfConn = 0
    
    def __timeout__(self, sock):
        if self.numOfConn == 0 & self.__timeout == False:
            print('y')
            self.__timeout = True
            sock.settimeout(5.0)
        elif self.numOfConn > 0:
            print('x')
            self.__timeout = False
            sock.settimeout(300.0)

    def create(self):
        """Create and bind socket to the initialized Server host and port.\
        This bound socket can be used to start allowing connections to the server.\n\n\
        A Socket object is returned\n\n\
        If the host and\or port are already being used None object is returned"""

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
            # Binding the port and showing the port used
            sock.bind((self.__host, self.__port))
            print(f"Binding the port {self.__port}")

            # Waiting for client to connect to server
            # Once listening, the client has to be connected before any options can be allowed
            sock.listen()

            return sock

        except socket.error as msg:
            log("Socket init failed: ", msg)

            return None

    def allow_conns(self, sock, extra_func = None):
        """ Start accepting connection from possible clients.\n
            The IP and Port are stored into a list, connections are arranged into a list as well\n\n
            Each client gets their own thread, """
        
        db_conn = db.create_connection(str(Path.cwd()) + "/protected.db")

        while not self.__kill:
            # Test message to indicate still listening for client(s)
            print(f"Listening....")

            # Accepting connection
            # First variable is the connection to conn and 2nd one is address of conn
            try:
                if not self.__kill:
                    conn, addr = sock.accept()
                    conn_List.append(conn)
                    addr_List.append(addr)
                    self.numOfConn = self.numOfConn + 1
                else:
                    break
            except socket.error as msg:
                log("Error while accepting socket: ", msg)
            
            ## TRIGGER MSG
            label = "ROBO 00" + str(self.numOfConn)
            trigger = "Client " + label + " : Current time is " + time() + "\n" + welcomeResp

            # Display connection message
            print(f"Connection Established with | {addr[-2]}:{addr[-1]} |")
            # Create client connection db listing for server-side
            client_id = db.create_client(db_conn, (label, addr[-2], addr[-1], time(),"-"))

            # Send connected msg to client
            conn.send(trigger.encode("utf-8"))

            # Start creating client communication archive in server-side db
            db.create_comms_archive(db_conn, (client_id, "Server Connected", "-", time()))

            # Start thread for the client
            self.__thread.assign(target=self.__start_comms, args=(conn, client_id))
            self.__thread.start()
        
        db_conn.close()
        
        sock.close()

    def __start_comms(self, conn, client_id):
        global timeout

        db_conn = db.create_connection(str(Path.cwd()) + "/protected.db")

        while True:

            index = conn_List.index(conn)

            # Received from conn
            # Something sent through server-conn connection
            data = conn.recv(1024)
            db.create_comms_archive(db_conn, (client_id,"-", data.decode('utf-8'), time()))

            if not data:
                print("No command received")
                break
            
            # Exit function for conn
            if data.decode('utf-8').lower() in ["exit", "quit"]:
                print(f"Connection Closed with | {addr_List[index][0]}:{addr_List[index][1]} |")
                msg = "Connection Closed with Divoc"
                conn.send(msg.encode('utf-8'))
                db.create_comms_archive(db_conn, (client_id, msg, "-", time()))
                sleep(0.333)
                db.update_client(db_conn, (time(), client_id))
                conn.close()
                break
            elif data.decode('utf-8') == "@Quit":
                conn.send("Killing server".encode('utf-8'))
                conn.close()
                self.__kill = True
                break
            
            # Deploy functionality!
            # Comment  next 2 lines for server only debugging - FUNCTIONLESS STATE
            function = server_func(conn, data, db_conn)
            function.select(client_id)
        db_conn.close()

    def kill(self, sock):
        self.__kill = True
        sock.close()
        print(f"Killed server....")

    # Server Function class
class server_func:
    global options
    
    def __init__(self, conn, data, db_conn):
        self.conn = conn
        self.cmd = data.decode('utf-8').lower()
        self.__db_conn = db_conn
    
    def __send(self, msg):
        self.conn.send(msg.encode("utf-8"))
    
    def __recv(self):
        return self.conn.recv(1024).decode("utf-8")

    def __calc(self, client_id):
        """Calculation Mode: A function that calculates decimal numbers and sends results\n\n
        Handles input exceptions"""

        defaultMsg = "\n====== CALCULATION MODE ======\n\nSteps of usage\
            \n\n\t>> Input X \n\t>> Input Y \n\n\t>> Input Operator: + | - | / | * \n"
        
        db.create_comms_archive(self.__db_conn, (client_id,"Calculation Mode", "-", time()))
        # Function starts -----
        self.__send(defaultMsg)

        while True:
            # take input for the numbers and send back response
            try:
                a = float(self.__recv())
                aMsg = "X = " + str(int(a))
                self.__send(aMsg)
                db.create_comms_archive(self.__db_conn, (client_id, str(aMsg),"-", time()))

                b = float(self.__recv())
                bMsg = "Y = " + str(int(b))
                self.__send(bMsg)
                db.create_comms_archive(self.__db_conn, (client_id, str(bMsg),"-", time()))

                # Take operator input
                op = self.__recv()

                finalMsg = str(a) + str(op) + str(b)
                db.create_comms_archive(self.__db_conn, (client_id,"-", finalMsg, time()))
                
                if op == "+":
                    result = str(a + b)
                elif op == "-":
                    result = str(a - b)
                elif op == "/":
                    result = str(a / b)
                elif op == "*":
                    result = str(a * b)
                
                self.__send(result)
                db.create_comms_archive(self.__db_conn, (client_id, finalMsg + " = " + str(result), "-", time()))
                break

            except Exception as msg:
                # I SEE YOU, I KNOW WHAT YOU ARE TRYING
                # (ὸ_ό) BAD!
                self.__send("Try DECIMAL number for input!\nGo back to CALCULATION MODE?\n\
                    Type Y/N, anything else will exit mode: ")
                log("Non-DECIMAL used raising exception", msg)

                choice = self.__recv()
                if choice.lower() in ["y", "yes"]:
                    self.__send(defaultMsg)
                    db.create_comms_archive(self.__db_conn, (client_id, "Restarting", "-", time()))
                else:
                    msg = "Exited CALCULATION MODE"
                    self.__send(msg)
                    db.create_comms_archive(self.__db_conn, (client_id, msg, "-", time()))
                    break
    
    def __switch(self, client_id):
        """Allows status validation of a boolean"""

        global stat
        defaultMsg = "\n====== STATUS VALIDATION ======\n\n\t"

        if stat:
            onMsg = "STATUS: Currently ON\n\nChange Status? Y/N\n"
            statusMsg = defaultMsg + onMsg
            self.__send(statusMsg)
        else:
            offMsg = "STATUS: Currently OFF\n\nChange Status? Y/N\n"
            statusMsg = defaultMsg + offMsg
            self.__send(statusMsg)
        
        db.create_comms_archive(self.__db_conn, (client_id, statusMsg,"-",time()))
        
        choice = self.__recv()

        if choice.lower() in ["y", "yes"]:
            stat = not stat
            print(stat)
            if stat == True:
                msg = "Status Changed to ON"
                self.__send(msg)
            else:
                msg = "Status Changed to OFF"
                self.__send(msg)
            
            db.create_comms_archive(self.__db_conn, (client_id, msg, "-", time()))
        else:
            msg = "Going back to OPTIONS selection"
            self.__send(msg)
            db.create_comms_archive(self.__db_conn, (client_id, msg, "-", time()))

    def select(self, client_id):
        if self.cmd in ["calc", "calculator"]:
            self.__calc(client_id)
        
        # Check current datetime
        elif self.cmd in ["today", "date", "now"]:
            self.__send(time())
        
        # Status toggling
        elif self.cmd in ["stat", "status"]:
            self.__switch(client_id)

        # Show options
        elif self.cmd in ["options", "opt", "help"]:
            self.__send(options)
        
        # Echo Uppercase for everything else
        elif len(self.cmd) > 0:
            self.__send(self.cmd.upper())
            db.create_comms_archive(self.__db_conn, (client_id, str(self.cmd.upper()),"-",time()))