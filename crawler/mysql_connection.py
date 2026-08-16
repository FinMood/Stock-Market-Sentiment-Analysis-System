# 負責「Python 如何連進 MySQL」

import os
import pymysql


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

    conn = pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        charset="utf8mb4"
    )

    print("✅ MySQL 連線成功")

    return conn