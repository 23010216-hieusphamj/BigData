import mysql.connector
from config import DB_CONFIG

conn = mysql.connector.connect(**DB_CONFIG)
cur = conn.cursor()

cur.execute("SELECT VERSION()")
print("Phiên bản MySQL:", cur.fetchone()[0])

cur.execute("SELECT DATABASE()")
print("Database hiện tại:", cur.fetchone()[0])

cur.execute("EXPLAIN ANALYZE SELECT 1")
print("EXPLAIN ANALYZE:", cur.fetchone()[0][:60], "...")

cur.close()
conn.close()
print("OK - kết nối thành công")