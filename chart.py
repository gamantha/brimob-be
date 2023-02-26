import random

from flask import Blueprint, g
import time
from datetime import date
import os
import json

from mysql.connector import Date

from stats import Stats
from dbconfig import DBConfig
from dbconfig2 import DBConfig2
from flask import Flask, request
from flask_jwt import JWT
# from werkzeug.security import safe_str_cmp
import mysql.connector as mysql
import json
from flask import Flask
from flask import jsonify
from flask import request, flash, request, redirect, url_for
from flask_cors import CORS

from werkzeug.utils import secure_filename
from os.path import exists
from datetime import datetime
import hashlib
import bcrypt

import time
import pdfkit
import redis


from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from datetime import datetime
now = datetime.now()
from flask import send_from_directory

import bcrypt
from geopy.geocoders import GoogleV3




dbObj = DBConfig()
dbObj2 = DBConfig2()

r = redis.Redis(
    host='202.67.10.238',
    port=6379,
    password='')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'mysql_db'):
        g.mysql_db = dbObj.connect()
    return g.mysql_db

def get_db2():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'mysql_db2'):
        g.mysql_db2 = dbObj2.connect()
    return g.mysql_db2


UPLOAD_FOLDER = './uploads/'
UPLOAD_USERPHOTO_FOLDER = './uploads/userphoto/'
UPLOAD_GIATHARIAN_FOLDER = './uploads/giatharian/'
UPLOAD_GIATINSIDENTIL_FOLDER = './uploads/giatinsidentil/'
UPLOAD_KOMANDAN_FOLDER = './uploads/komandan/'
UPLOAD_WAKIL_FOLDER = './uploads/wakil/'
UPLOAD_REGION_FOLDER = './uploads/region/'
UPLOAD_DEPARTMENT_FOLDER = './uploads/department/'

DOWNLOAD_FOLDER = './downloads/'
DOWNLOAD_LAPORAN_FOLDER = './downloads/laporan/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg'}
chart_blueprint = Blueprint('chart_blueprint', __name__, url_prefix="/chart")

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_LAPORAN_FOLDER'] = DOWNLOAD_LAPORAN_FOLDER
app.config['UPLOAD_USERPHOTO_FOLDER'] = UPLOAD_USERPHOTO_FOLDER
app.config['UPLOAD_GIATHARIAN_FOLDER'] = UPLOAD_GIATHARIAN_FOLDER
app.config['UPLOAD_GIATINSIDENTIL_FOLDER'] = UPLOAD_GIATINSIDENTIL_FOLDER

app.config['DOWNLOAD_FOLDER'] = DOWNLOAD_FOLDER
app.config['UPLOAD_REGION_FOLDER'] = UPLOAD_REGION_FOLDER
app.config['UPLOAD_DEPARTMENT_FOLDER'] = UPLOAD_DEPARTMENT_FOLDER

app.config['UPLOAD_KOMANDAN_FOLDER'] = UPLOAD_KOMANDAN_FOLDER
app.config['UPLOAD_WAKIL_FOLDER'] = UPLOAD_WAKIL_FOLDER




@chart_blueprint.route('/get_config', methods=["GET"])
def get_config():
    db2 = get_db2()
    cursor = db2.cursor(dictionary=True)
    query = "SELECT * FROM configuration"
    cursor.execute(query)
    records = cursor.fetchall()
    res = dict()
    for record in records:
        res[record['key']] = record['value'];
    return jsonify(res)


@chart_blueprint.route('/chart', methods=["POST"])
def chart():

    operation_id = request.json.get("operation_id", None)
    db2 = get_db2()
    cursor = db2.cursor(dictionary=True)
    query = "select max(tracker_user.id), tracker_user.iduser, user.username, user_data.nama, user_data.pangkat, region.region_name, department.department_name, position.position_name, lat, lon, altitude, tracker_user.timestamp " \
            "from tracker_user LEFT JOIN user on tracker_user.iduser = user.iduser LEFT JOIN position on user.position_id = position.id " \
            "LEFT JOIN user_data on user_data.iduser = tracker_user.iduser LEFT JOIN department on department.id = position.department_id LEFT JOIN region on region.id = department.region_id " \
            "where tracker_user.iduser in (select user_id from operasi_anggota where status = 'active' and operasi_id = %s) AND `timestamp` > DATE_SUB(now(),INTERVAL 12 HOUR) group by tracker_user.iduser "

    cursor.execute(query,(operation_id,))
    record = cursor.fetchall()
    result = dict()
    result['data'] = record
    result['count'] = cursor.rowcount
    return jsonify(result)


@chart_blueprint.route('/chart_1', methods=["GET"])
def chart_1n():

    db2 = get_db2()
    cursor = db2.cursor(dictionary=True)
    query = "select tgl_laporan, laporan_subcategory_id, count(laporan_giat.id) as 'jumlah' " \
            "from laporan_giat join subkategori on subkategori.idsubkategori = laporan_giat.laporan_subcategory_id " \
            "where tgl_submitted >= DATE_SUB(CURDATE(), INTERVAL 1 week) GROUP BY tgl_laporan, laporan_subcategory_id ORDER BY tgl_laporan, region_id"

    cursor.execute(query,)
    record = cursor.fetchall()
    result = dict()
    result['data'] = record
    # result['count'] = cursor.rowcount
    return jsonify(result)
