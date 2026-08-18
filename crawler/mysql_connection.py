# 負責「Python 如何連進 MySQL」
import os
import pymysql


def get_connection():
    return pymysql.connect(
        host=os.getenv(
            "MYSQL_HOST",
            "localhost"
        ),

        port=int(
            os.getenv(
                "MYSQL_PORT",
                "3306"
            )
        ),

        user=os.getenv(
            "MYSQL_USER",
            "root"
        ),

        password=os.getenv(
            "MYSQL_PASSWORD",
            "1234"
        ),

        database=os.getenv(
            "MYSQL_DATABASE",
            "mydb"
        ),

        charset="utf8mb4",

        autocommit=False,
    )