import sqlite3
from sqlite3 import Error
# con = sqlite3.connect('keyValPair.db')
database = r"./keyValPair.db"

def create_connection(db_file):
    
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


def select_all_key_values(conn):
 
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





def main():
    

    # create a database connection
    conn = create_connection(database)
    with conn:
        # print("1. Query task by priority:")
        # select_task_by_priority(conn, 1)

        print("printing rows")
        select_all_key_values(conn)


# if __name__ == '__main__':
#     main()



def create_table_in_DB():
    conn = create_connection(database)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE keyvalue (
                    id INT PRIMARY KEY,
                    key VARCHAR NOT NULL,
                    value VARCHAR DEFAULT 'not set yet'
                    )"""
    )


try:
    create_table_in_DB()
except Exception as e:
    print(e)