import sqlite3
from sqlite3 import Error
from pathlib import Path

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file, check_same_thread=False)
    except Error as e:
        print(e)

    return conn

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def select_last_client(conn):
    cur = conn.cursor()
    return cur.lastrowid

def select_client(conn):
    """
    Query all rows in the clients table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM client")

    rows = cur.fetchall()
    client = {}
    for row in rows:
        client[row[0]] = (row[1], row[2], row[3], row[4], row[5])
    
    return client

def select_comms(conn, client_id):
    """
    Query all rows in the clients table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    sql = "SELECT * FROM comms_archive WHERE client_id = ?"
    cur.execute(sql, client_id)

    rows = cur.fetchall()
    comms = {}
    for row in rows:
        comms[row[0]] = (row[2], row[3], row[4])
    
    return comms

def create_client(conn, client):
    """
    Create a newly accepted client
    :param conn:
    :param client:
    :return: client id
    """
    sql = ''' INSERT INTO client(name,host,port,connect_time,disconnect_time)
              VALUES(?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, client)
    conn.commit()

    return cur.lastrowid

def create_comms_archive(conn, comms_archive):
    """
    Create a new archive of communication for client
    :param conn:
    :param comms_archive:
    """
    sql = ''' INSERT INTO comms_archive(client_id,sent,received,recieve_time)
              VALUES(?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, comms_archive)
    conn.commit()

def update_client(conn, client):
    """
    update disconnection time
    :param conn:
    :param client:
    """
    sql = ''' UPDATE client
              SET disconnect_time = ?
              WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, client)
    conn.commit()

def update_comms_archive(conn, comms):
    """
    update sent or recieved date and time
    :param conn:
    :param client:
    """
    sql = ''' UPDATE comms_archive
              SET client_id = ?,
              sent = ?,
              received = ?,
              receive_time = ?
              WHERE
              WHERE id = ?'''
    cur = conn.cursor()
    cur.execute(sql, comms)
    conn.commit()


def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def main():
    database = str(Path.cwd()) + "/protected.db"

    sql_create_clients= """ CREATE TABLE IF NOT EXISTS client (
                                        id integer PRIMARY KEY,
                                        name text NOT NULL,
                                        host text NOT NULL,
                                        port text NOT NULL,
                                        connect_time text,
                                        disconnect_time text
                                    ); """

    sql_create_comms = """CREATE TABLE IF NOT EXISTS comms_archive (
                                    id integer PRIMARY KEY,
                                    client_id integer NOT NULL,
                                    sent text,
                                    received text,
                                    recieve_time text NOT NULL,
                                    FOREIGN KEY (client_id) REFERENCES client (client_id)
                                );"""

    # create a database connection
    conn = create_connection(database)

    # create tables
    if conn is not None:
        # create projects table
        create_table(conn, sql_create_clients)

        # create tasks table
        create_table(conn, sql_create_comms)
    else:
        print("Error! cannot create the database connection.")
    
    #select_all_comms(conn)

if __name__ == '__main__':
    main()
#with conn:
 #   create_client(conn, (label,host,port,connect_time,disconnect_time))
