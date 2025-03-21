import pymysql

try:
    print("🔍 Mencoba koneksi ke MySQL...")
    connection = pymysql.connect(
        host="localhost",
        user="root",
        password="Pramuka123@",
        database="ETL",
        port=3306
    )
    print("✅ Berhasil terhubung ke MySQL!")
    connection.close()
except pymysql.err.OperationalError as e:
    print(f"❌ OperationalError: {e}")
except pymysql.err.InternalError as e:
    print(f"❌ InternalError: {e}")
except Exception as e:
    print(f"❌ Error lain: {e}")
