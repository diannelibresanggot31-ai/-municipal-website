import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="dianne2005",
    database="testdb"
)

print("Connected successfully!")

# Create a cursor to execute queries
cursor = conn.cursor()

# Test query: Show all tables in testdb
cursor.execute("SHOW TABLES")
tables = cursor.fetchall()
print(f"Tables in testdb: {tables}")

# Close cursor and connection
cursor.close()
conn.close()