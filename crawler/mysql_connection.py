# 負責「Python 如何連進 MySQL」

import os
import mysql.connector


def get_connection():

    host = os.getenv(
        "MYSQL_HOST",
        "127.0.0.1"
    )

    port = int(
        os.getenv(
            "MYSQL_PORT",
            "3306"
        )
    )

    user = os.getenv(
        "MYSQL_ACCOUNT",
        "root"
    )

    password = os.getenv(
        "MYSQL_PASSWORD",
        "1234"
    )

    database = os.getenv(
        "MYSQL_DATABASE",
        "mydb"
    )
# MySQL Server 診斷
    # print("🔌 MySQL 連線資訊")
    # print(f"   host     = {host}")
    # print(f"   port     = {port}")
    # print(f"   user     = {user}")
    # print(f"   database = {database}")

    conn = mysql.connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database
    )

    print("✅ MySQL 連線成功")

    return conn