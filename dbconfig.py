#!/usr/bin/env python
import mysql.connector as mysql


class DBConfig:
    def connect(self):
        # db = mysql.connect(
        #     host="202.67.14.247",
        #     user="ntmc_ccntmc",
        #     passwd="0uH7kc6ceEYt",
        #     database="ntmc_ccntmc"
        # )

        # dbcon = mysql.connect(
        #     host="202.67.10.238",
        #     user="root",
        #     passwd="dhe123!@#",
        #     database="cc_brimobdb"
        # )

        dbcon = mysql.connect(
            host="202.67.10.227",
            user="root",
            passwd="dhe123!@#",
            database="comcen_brimob"
        )



        return dbcon
