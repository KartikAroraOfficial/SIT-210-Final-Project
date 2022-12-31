import mysql.connector
from data_handler import add_patient, remove_pat, get_all

host='localhost' 
user='root' 
passwd='rootbar'
database='mydatabase'

db = mysql.connector.connect(host=host, user=user, password=passwd)

mycursor = db.cursor()
print(db)
print(mycursor)

mycursor.execute("CREATE DATABASE mydatabase")

mycursor.execute("SHOW DATABASES")

for x in mycursor:
    print(x)
db.commit()
db.close()

db = mysql.connector.connect(host=host, user=user, password=passwd, database=database)
mycursor=db.cursor()
mycursor.execute("CREATE TABLE patients(name VARCHAR(100), id VARCHAR(12), mail VARCHAR(100) , device VARCHAR(30), age VARCHAR(3), sex CHAR(1))")
mycursor.execute("CREATE TABLE device(did VARCHAR(20), aid VARCHAR(12))")
mycursor.execute("CREATE TABLE dataArd(did VARCHAR(20), dt DATETIME, heart DECIMAL(4,2), temp DECIMAL(4,2), spo DECIMAL(4,2))")


mycursor.execute("SHOW TABLES")

for x in mycursor:
    print(x)

db.commit()
db.close()


add_patient("Kartik", "69696","fakemail@xyz.com", "1", "19", "M")
remove_pat("aaaaaaaa")
get_all()