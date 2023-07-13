from flask import Blueprint
import json
from ntmcdbconfig import DBConfig
from flask import Flask, request
from flask_jwt import JWT
# from werkzeug.security import safe_str_cmp
import mysql.connector as mysql
import json
from flask import Flask
from flask import jsonify
from flask import request
from flask_cors import CORS

from datetime import datetime
import hashlib
import bcrypt

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

import bcrypt

dbObj = DBConfig()
db = dbObj.connect()

korlantas_blueprint = Blueprint('korlantas_blueprint', __name__, url_prefix="/korlantas")



@korlantas_blueprint.route('/data_pengaduan', methods=["GET"])
def data_pengaduan():

    cursor = db.cursor(dictionary=True)
    #
    # query = "SELECT no_laporan, sub_kategori_id, subkategori.sub_kategori, laporan_text, DATE_FORMAT(tgl_submitted, '%Y-%m-%d %T') as tgl_submitted FROM laporan " \
    #         "LEFT JOIN subkategori ON subkategori.idsubkategori = laporan.sub_kategori_id " \
    #         "WHERE user_id = %s ORDER BY tgl_submitted DESC "
    # print("syaalala")
    # ## getting records from the table
    # cursor.execute(query, (id,))
    # record = cursor.fetchall()
    # cursor.close()

    res = dict()
    # res['list'] = record
    res['valid'] = 1

    return res

