# import sqlite3
# from sqlite3 import Error
# # con = sqlite3.connect('keyValPair.db')
# database = r"./keyValPair.db"


# def create_connection(db_file):
    
#     conn = None
#     try:
#         conn = sqlite3.connect(db_file)
#     except Error as e:
#         print(e)

#     return conn
# conn = create_connection(database)
# cur = conn.cursor()

# def select_all_key_values():
#     cur.execute("SELECT * FROM keyvalue")

#     rows = cur.fetchall()

#     newList =[]
#     for index,row in enumerate(rows):
#         newList.append((row[1],row[2]))
        
    
#     text = str(("key","value"))
#     for tupple in newList:
#         text += str(tupple)
#     print(text)
#     return text



# def main():
    

#     # create a database connection
    
#     with conn:
#         # print("1. Query task by priority:")
#         # select_task_by_priority(conn, 1)

#         print("printing rows")
#         select_all_key_values(conn)


# # if __name__ == '__main__':
# #     main()



# def create_table_in_DB():
#     cur.execute("""CREATE TABLE keyvalue (
#                     id INT PRIMARY KEY,
#                     key VARCHAR NOT NULL,
#                     value VARCHAR DEFAULT 'not set yet'
#                     )"""
#     )




# def add_to_db(key,value):
#     cur.execute("SELECT * FROM keyvalue")
#     rows = cur.fetchall()

#     for row in rows:
#         if key  == row[1]:
#             cur.execute(f""" INSERT INTO keyvalue(key,value)
#                     VALUES({key},{value});
#     """)

#     cur.execute(f""" INSERT INTO keyvalue(key,value)
#                     VALUES({key},{value});
#     """)
#     cur.execute("COMMIT")





# # try:
# # create_table_in_DB()
# key = '"who Am I?"'
# value = '"Ni shi Programmer!"'
# add_to_db(key,value)
# select_all_key_values()

# # except Exception as e:
# #     print(str(e)+"\n\n\n\n\n")
    
