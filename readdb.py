import sqlite3
from sqlite3 import Error


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


def select_all_tasks(conn):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM Ar_Activity")

    rows = cur.fetchall()

    newList =[]
    for index,row in enumerate(rows):
        if '2021-08-20' in row[9] and row[6] is not None:
            newList.append({"name":row[2],"starttime":row[9],"notes":row[13]})
    newList.sort(key=lambda x: x['starttime'], reverse=False)
        
    print("name","starttime","notes")
    for x in newList:
        if 'None' not in str(x['notes']):
            n = str(x['notes']).replace('\n', '')
            notes = f" n: { n }"
        else:
            notes = ""
        print(x["starttime"],x["name"],notes )

""" 
2 is name 
9 is starttime 
13 is notes
6 not none means tag
"""
def select_task_by_priority(conn, priority):
    """
    Query tasks by priority
    :param conn: the Connection object
    :param priority:
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE priority=?", (priority,))

    rows = cur.fetchall()

    for row in rows:
        print(row)


def main():
    database = r"/home/ls/.config/manictime/ManicTimeReports.db"

    # create a database connection
    conn = create_connection(database)
    with conn:
        # print("1. Query task by priority:")
        # select_task_by_priority(conn, 1)

        print("printing rows")
        select_all_tasks(conn)


if __name__ == '__main__':
    main()