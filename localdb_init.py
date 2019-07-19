'checks whether the the local database and its components exist. If not, it creates them.'


import mysql.connector as cn

mydb = cn.connect(user='PBRcontrol')

cursor = mydb.cursor()
cursor.execute('DROP DATABASE localdb')
cursor.execute('CREATE DATABASE IF NOT EXISTS localdb')

mydb = cn.connect(user='PBRcontrol', db = 'localdb')

cursor = mydb.cursor()

cursor.execute('CREATE TABLE IF NOT EXISTS commands ('
               'id INT,'
               't TIMESTAMP,'
               'args VARCHAR(255))')

cursor.execute('CREATE TABLE IF NOT EXISTS log ('
               't TIMESTAMP,'
               'event VARCHAR(255),'
               'status INT)')

cursor.execute('CREATE TABLE IF NOT EXISTS measurement (' #TODO arguments
               't time,'
               'log INT)')

cursor.execute('INSERT INTO commands (id, t, args) VALUES (1, current_timestamp, "text")')

mydb.commit()

