from flask import Blueprint
import time
from datetime import date
import os
import json
from dbconfig import DBConfig
from flask import Flask, request
from flask_jwt import JWT
from werkzeug.security import safe_str_cmp
import mysql.connector as mysql
import json
from flask import Flask
from flask import jsonify
from flask import request, flash, request, redirect, url_for
from flask_cors import CORS

from werkzeug.utils import secure_filename

from datetime import datetime
import hashlib
import bcrypt

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager
from datetime import datetime
now = datetime.now()
from flask import send_from_directory

import bcrypt

dbObj = DBConfig()
db = dbObj.connect()
UPLOAD_FOLDER = './uploads/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp4'}
cc_blueprint = Blueprint('cc_blueprint', __name__, url_prefix="/cc")

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
@cc_blueprint.route('/login_user', methods=["POST"])
def login_user():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    res = authenticate_user(username, password)
    return res

def authenticate_user(username, password):
    db.reconnect()
    cursor = db.cursor(dictionary=True)
    query = "SELECT iduser,username,password, level_user, position_id, position.position_name as 'position_name', department.id as 'department_id', department.department_name as 'department_name', " \
            "region.id as 'region_id', region.region_name as 'region_name' FROM user " \
            "LEFT JOIN position ON position.id = user.position_id " \
            "LEFT JOIN department ON department.id = position.department_id "\
            "LEFT JOIN region ON region.id = department.region_id "\
            "WHERE username = %s"
    cursor.execute(query, (username,))
    record = cursor.fetchall()
    cursor.close()
    level_user = ''
    position_id = ''
    position_name = ''
    region_id = ''
    region_name = ''
    department_id = ''
    department_name = ''

    valid = 0
    res = dict()
    if (len(record) > 0):
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)

        if bcrypt.checkpw(password.encode(), (record[0]['password']).encode()):
            valid = 1
            token = username
            access_token = create_access_token(identity=record[0]['iduser'])
            name = record[0]['username']
            level_user = record[0]['level_user']
            position_id = record[0]['position_id']
            position_name = record[0]['position_name']
            department_id = record[0]['department_id']
            department_name = record[0]['department_name']
            region_id = record[0]['region_id']
            region_name = record[0]['region_name']
            print(record[0])
            res['valid'] = valid
            res['response'] = 'success'
            res['username'] = name
            res['level_user'] = level_user
            res['position_id'] = position_id
            res['position_name'] = position_name
            res['department_id'] = department_id
            res['department_name'] = department_name
            res['region_id'] = region_id
            res['region_name'] = region_name
            res['token'] = token

            return jsonify(token=access_token, name=name, level_user=level_user, position_id=position_id, position_name=position_name,
                           department_id=department_id, department_name=department_name, region_id=region_id,region_name=region_name, valid=valid)
        else:
            valid = 2
            res['valid'] = valid
            res['response'] = 'password does not match'
    else:
        valid = 2
        res['valid'] = valid
        res['response'] = 'username does not exist'



    return res


@cc_blueprint.route('/simpan_user', methods=["POST"])
def simpan_user():
    username = request.json.get('username')
    password = request.json.get('password')
    level_user = request.json.get('level_user')
    position_id = request.json.get('position_id')
    nama = request.json.get('nama')
    telepon = request.json.get('telepon')
    alamat = request.json.get('alamat')
    email = request.json.get('email')
    ktp = request.json.get('ktp')
    db.reconnect()
    cursor = db.cursor(dictionary=True)
    query = "SELECT username,password FROM user WHERE username = %s"
    cursor.execute(query, (username,))
    record = cursor.fetchall()
    valid = 0

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    res = dict()
    if (len(record) > 0):
        valid = 2
        res['errorMessage'] = "username existed"
    else:
        valid = 1
        query = "INSERT INTO user (username, password, level_user, position_id " \
                ") " \
                "VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (username, hashed, level_user, position_id,))

        query = "INSERT INTO user_data (iduser, nama, telepon, alamat, email, ktp " \
                ") " \
                "VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (cursor.lastrowid, nama, telepon, alamat, email, ktp,))

        db.commit()

    res['valid'] = valid
    cursor.close()
    return res

# @cc_blueprint.route('/laporan_image_upload', methods=["POST"])
# @jwt_required()
# def laporan_image_upload():
#     # response = requests.post(URL, data=img, headers=headers)

@cc_blueprint.route('/get_laporan_no', methods=["POST"])
# @jwt_required()
def get_laporan_no():
    #format laporan 2022/bulan/subkategori
    db.reconnect()
    cursor = db.cursor(dictionary=True)
    result = dict()
    sub_kategori_id = request.json.get('sub_kategori_id')
    query_a = "SELECT idsubkategori, kategori_id, kategori.kategori, sub_kategori FROM subkategori " \
              "LEFT JOIN kategori ON kategori.idkategori = subkategori.kategori_id " \
              "WHERE idsubkategori = %s"
    cursor.execute(query_a, (sub_kategori_id,))
    record = cursor.fetchone()
    if record is None:
        result['valid'] = 0
        result['status'] = 'wrong sub_kategori_id'
        return jsonify(result)

    print(record)
    if(record['kategori_id'] == 1) :
        print("ini yg pertama")
        no_laporan_string = str(date.today().year) + "/" + str(date.today().month) + "/" + str(date.today().strftime("%d")) + "/" + str(sub_kategori_id)
    elif (record['kategori_id'] == 2) :
        print("ini yg kedua")
        no_laporan_string = str(date.today().year) + "/" + str(date.today().month) + "/" + str(sub_kategori_id)
    else :
        print(record['kategori_id'])
        no_laporan_string = str(date.today().year) + "/" + str(sub_kategori_id)
    print(no_laporan_string)


    query = "SELECT id, no_laporan, approved_by, date_submitted, date_approved, status FROM laporan_published WHERE no_laporan = %s"
    cursor.execute(query, (no_laporan_string,))
    record = cursor.fetchall()

    if (len(record) > 0):
        if record[0]['status'] == 'approved' :
            valid = 2
            result['no_laporan'] = ''
            result['status'] = "laporan approved"
        else :
            valid = 1
            result['status'] = 'laporan submitted'
            result['no_laporan'] = no_laporan_string
    else:
        formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
        query = "INSERT INTO laporan_published (no_laporan, date_submitted, status " \
                ") " \
                "VALUES (%s, %s, %s)"
        cursor.execute(query, (no_laporan_string, formatted_date, "submitted",))
        db.commit()
        valid = 1
        result['status'] = 'new laporan submitted'
        result['no_laporan'] = no_laporan_string
    result['valid'] = valid

    cursor.close()
    return jsonify(result)



@cc_blueprint.route('/laporan_approve', methods=["POST"])
@jwt_required()
def laporan_approve():
    db.reconnect()
    cursor = db.cursor(dictionary=True)
    user_id = get_jwt_identity()
    no_laporan = request.json.get('no_laporan')
    approved = "approved"
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
    query = "UPDATE laporan_published SET status =  %s, date_approved = %s, approved_by = %s WHERE no_laporan = %s"
    cursor.execute(query, (approved, formatted_date, user_id, no_laporan,))
    result = dict()
    try:
        db.commit()
    except mysql.connector.Error as error:
        print("Failed to update record to database rollback: {}".format(error))
        # reverting changes because of exception
        cursor.rollback()
        result['result'] = 'failed'
        result['valid'] = 2
    finally:

        cursor.close()
        result['result'] = 'success'
        result['valid'] = 1

    return jsonify(result)

@cc_blueprint.route('/laporan_published', methods=["GET"])
def laporan_published():
    db.reconnect()
    cursor = db.cursor(dictionary=True)
    query = "SELECT id, no_laporan, approved_by, user.username, date_submitted, date_approved, status FROM laporan_published " \
            "LEFT JOIN user ON user.iduser = laporan_published.approved_by "
    cursor.execute(query)
    record = cursor.fetchall()
    result = dict()
    result = record
    return jsonify(result)

@cc_blueprint.route('/laporan_add', methods=["POST"])
@jwt_required()
def laporan_add():
    db.reconnect()
    cursor = db.cursor(dictionary=True)
    user_id = get_jwt_identity()
    # user_id = '1'
    no_laporan = request.json.get('no_laporan')
    tgl_laporan = request.json.get('tgl_laporan')
    lat_pelapor = request.json.get('lat_pelapor')
    long_pelapor = request.json.get('long_pelapor')
    laporan_text = request.json.get('laporan_text')
    laporan_total = request.json.get('laporan_total')
    sub_kategori_id = request.json.get('sub_kategori_id')
    laporan_subcategory_id = request.json.get('laporan_subcategory_id')
    status = request.json.get('status')
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
    # tgl_approved = request.json.get('tgl_approved')

    query = "INSERT INTO laporan (no_laporan, tgl_laporan, user_id, lat_pelapor, long_pelapor, sub_kategori_id, " \
            "laporan_subcategory_id, laporan_text, laporan_total, status, tgl_submitted) " \
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor.execute(query, (no_laporan, tgl_laporan, user_id, lat_pelapor, long_pelapor, sub_kategori_id,laporan_subcategory_id, laporan_text, laporan_total, status, formatted_date))
    record = cursor.fetchone()

    result = dict()
    try:
        db.commit()
    except mysql.connector.Error as error:
        print("Failed to update record to database rollback: {}".format(error))
        # reverting changes because of exception
        cursor.rollback()
        result['result'] = 'failed'
        result['valid'] = 2
    finally:

        cursor.close()
        result['result'] = 'success'
        result['valid'] = 1

    return jsonify(result)


@cc_blueprint.route('/position', methods=["get"])
def position():
    db.reconnect()
    cursor = db.cursor(dictionary=True)
    query = "SELECT position.id as 'position_id', position.position_name, department.id as 'department_id', department.department_name,  region.id as 'region_id', region.region_name from position " \
            "LEFT JOIN department ON department.id = position.department_id " \
            "LEFT JOIN region ON region.id = department.region_id "
    cursor.execute(query,)
    record = cursor.fetchall()
    cursor.close()
    res = dict()
    res = record
    return jsonify(res)




@cc_blueprint.route('/laporan', methods=["POST"])
@jwt_required()
def laporan():
    db.reconnect()
    level_user = request.json.get('level_user')
    position_id = request.json.get('position_id')
    start = request.json.get('start')
    limit = request.json.get('limit')
    cursor = db.cursor(dictionary=True)
    res = dict()

    if (level_user == 'superadmin'):
        print("superadmin")
        query = "SELECT no_laporan, user_id, user_data.nama, user.position_id, position.position_name,sub_kategori_id,subkategori.sub_kategori, laporan.laporan_subcategory_id, laporan_subcategory.name, laporan_subcategory.description, " \
                "kesatuan_region_id, tgl_submitted,tgl_approved,laporan.status,status_detail.keterangan,laporan.id, laporan.laporan_total, " \
                "laporan.laporan_text, laporan.lat_pelapor, laporan.long_pelapor FROM laporan " \
                "LEFT JOIN status_detail ON status_detail.idstatus = laporan.status " \
                "LEFT JOIN user ON user.iduser = laporan.user_id " \
                "LEFT JOIN user_data ON user_data.iduser = laporan.user_id " \
                "LEFT JOIN laporan_subcategory ON laporan_subcategory.id = laporan.laporan_subcategory_id " \
                "LEFT JOIN position ON position.id = user.position_id " \
                "LEFT JOIN subkategori ON subkategori.idsubkategori = laporan.sub_kategori_id LIMIT %s, %s"
        cursor.execute(query, (start, limit,))
        record = cursor.fetchall()
        res = record
        print(res)
    # elif (level_user == 'spv'):
    #     query = "SELECT no_pengaduan,nama_pelapor,work_order.position_id,position.position_name,sub_kategori_id,subkategori.sub_kategori,tgl_kontak,tgl_close,status,status_detail.keterangan,idworkorder FROM work_order " \
    #             "LEFT JOIN position ON position.id = work_order.position_id " \
    #             "LEFT JOIN status_detail ON status_detail.idstatus = work_order.status " \
    #             "LEFT JOIN department ON department.id = position.department_id " \
    #             "LEFT JOIN region ON region.id = department.region_id " \
    #             "LEFT JOIN user ON user.iduser = work_order.user_id " \
    #             "LEFT JOIN subkategori ON subkategori.idsubkategori = work_order.sub_kategori_id " \
    #             "WHERE region.id = %s LIMIT %s, %s "
    #     cursor.execute(query, (region, start, limit, ))
    #     record = cursor.fetchall()
    #     res = record
    else:
        query = "SELECT no_laporan, tgl_laporan, user_id, user_data.nama, user.position_id, position.position_name,sub_kategori_id,subkategori.sub_kategori, laporan.laporan_subcategory_id, laporan_subcategory.name, laporan_subcategory.description, " \
                "kesatuan_region_id, tgl_submitted,tgl_approved,laporan.status,status_detail.keterangan,laporan.id, laporan.laporan_total,laporan.laporan_text, laporan.lat_pelapor, laporan.long_pelapor FROM laporan " \
                "LEFT JOIN status_detail ON status_detail.idstatus = laporan.status " \
                "LEFT JOIN user ON user.iduser = laporan.user_id " \
                "LEFT JOIN user_data ON user_data.iduser = laporan.user_id " \
                "LEFT JOIN laporan_subcategory ON laporan_subcategory.id = laporan.laporan_subcategory_id " \
                "LEFT JOIN position ON position.id = user.position_id " \
                "LEFT JOIN subkategori ON subkategori.idsubkategori = laporan.sub_kategori_id " \
                "WHERE laporan.position_id = %s LIMIT %s, %s "
        cursor.execute(query, (position_id, start, limit, ))
        record = cursor.fetchall()
        res = record
    cursor.close()
    return jsonify(res)

@cc_blueprint.route('/ebooks', methods=["GET"])
def ebooks():
    db.reconnect()
    cursor = db.cursor(dictionary=True)
    query = "SELECT idebook, filename, tanggal FROM ebook"

    cursor.execute(query)
    record = cursor.fetchall()
    valid = 0
    res = dict()
    res = record
    cursor.close()
    return jsonify(res)


@cc_blueprint.route('/laporan_subcategory', methods=["POST"])
# @jwt_required()
def laporan_subcategory():
    print("laporan subcat")
    group = request.json.get("group", None)
    db.reconnect()
    cursor = db.cursor(dictionary=True)
    query = "SELECT id, name, description, laporan_subcategory.group FROM laporan_subcategory where laporan_subcategory.group = %s"

    cursor.execute(query,(group,))
    record = cursor.fetchall()
    valid = 0
    res = dict()
    res = record
    cursor.close()
    return jsonify(res)


@cc_blueprint.route('/regions', methods=["GET"])
# @jwt_required()
def regions():
    db.reconnect()
    cursor = db.cursor(dictionary=True)
    query = "SELECT id, region_name, image FROM region"

    cursor.execute(query)
    record = cursor.fetchall()
    valid = 0
    res = dict()
    res = record
    cursor.close()
    return jsonify(res)


@cc_blueprint.route('/users', methods=["POST"])
# @jwt_required()
def users():
    db.reconnect()
    cursor = db.cursor(dictionary=True)
    query = "SELECT user.iduser, username, level_user, order_license, position_id, user_data.nama, user_data.telepon, " \
            "user_data.alamat, user_data.email, user_data.ktp FROM user LEFT JOIN user_data ON user_data.iduser = user.iduser "

    cursor.execute(query)
    record = cursor.fetchall()
    valid = 0
    res = dict()
    res = record
    cursor.close()
    return jsonify(res)


@cc_blueprint.route('/user_setpass', methods=["POST"])
def user_setpass():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    ol_password = request.json.get('ol_password')
    db.reconnect()
    cursor = db.cursor(dictionary=True)
    query = "SELECT iduser, username, password FROM user WHERE username = %s"
    cursor.execute(query, (username,))
    record = cursor.fetchall()
    valid = 0
    if (len(record) > 0):
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode(), salt)

        if bcrypt.checkpw(ol_password.encode(), (record[0]['password']).encode()):
            valid = 1

            query = "UPDATE user SET password =  %s WHERE username = %s"
            cursor.execute(query, (hashed, username,))
            db.commit()
        else:
            valid = 0

    else:
        valid = 0

    res = dict()
    res['valid'] = valid
    cursor.close()
    return res

@cc_blueprint.route('/laporan_map', methods=["POST"])
def laporan_map():
    level_user = request.json.get('level_user')
    start = request.json.get('start')
    regions = request.json.get('regions')
    subkategoris = request.json.get('subkategoris')
    # for region in regions:
    db.reconnect()
    cursor = db.cursor(dictionary=True)
    # print(regions)
    # print(str(regions)[1:-1])
    region = str(regions)[1:-1]

    subkategori = str(subkategoris)[1:-1]
    tuple_regions = tuple(regions)
    s = tuple(subkategoris)

    query = "SELECT laporan.no_laporan,laporan.user_id,laporan.lat_pelapor, laporan.long_pelapor, region.id as 'region_id', region.region_name, department.id as 'department_id', department.department_name, user.position_id as 'position_id', position.position_name, " \
            "laporan.sub_kategori_id as 'sub_kategori_id',subkategori.sub_kategori, " \
            "laporan.tgl_submitted,laporan.tgl_approved,laporan.status as 'status', status_detail.keterangan as 'status_keterangan',laporan.id as 'laporan_id', laporan.laporan_text FROM laporan " \
            "LEFT JOIN status_detail ON status_detail.idstatus = laporan.status " \
            "LEFT JOIN user ON user.iduser = laporan.user_id " \
            "LEFT JOIN position ON position.id = user.position_id " \
            "LEFT JOIN department ON department.id = position.department_id " \
            "LEFT JOIN region ON region.id = department.region_id " \
            "LEFT JOIN subkategori ON subkategori.idsubkategori = laporan.sub_kategori_id " \
            "WHERE laporan.sub_kategori_id IN %(ids)s" % {"ids": tuple(subkategoris)}
    res = dict()
    # cursor.execute(query)
    cursor.execute(query)
    record = cursor.fetchall()
    res = record
    return jsonify(res)


@cc_blueprint.route('/laporan_filter', methods=["POST"])
def laporan_filter():
    level_user = request.json.get('level_user')
    position_id = request.json.get('position_id')
    start = request.json.get('start')
    limit = request.json.get('limit')

    sub_kategori_id = request.json.get('sub_kategori_id')
    status = request.json.get('status')
    # tgl_submit = request.json.get('tgl_submit')
    # tgl_approve = request.json.get('tgl_approve')
    db.reconnect()
    cursor = db.cursor(dictionary=True)
    res = dict()

    query = "SELECT no_laporan,user_id,user.position_id, position.position_name,sub_kategori_id,subkategori.sub_kategori, " \
            "tgl_submitted,tgl_approved,status,status_detail.keterangan,laporan.id, laporan.text FROM laporan " \
            "LEFT JOIN status_detail ON status_detail.idstatus = laporan.status " \
            "LEFT JOIN user ON user.iduser = laporan.user_id " \
            "LEFT JOIN position ON position.id = user.position_id " \
            "LEFT JOIN subkategori ON subkategori.idsubkategori = laporan.sub_kategori_id " \
            "WHERE laporan.position_id = %s AND laporan.sub_kategori_id = %s AND laporan.status = %s and LIMIT %s, %s "

    cursor.execute(query, (position_id, sub_kategori_id, status, start, limit,))
    record = cursor.fetchall()
    res = record
    print(res)

    cursor.close()
    return jsonify(res)


@cc_blueprint.route('/load_video_banner')
def load_video_banner():
    db.reconnect()
    cursor = db.cursor()
    ## defining the Query
    query = "SELECT * FROM apps_video_banner WHERE id = '1'"
    query2 = "SELECT * FROM app_link_banner WHERE id = '1'"
    ## getting records from the table
    cursor.execute(query)

    ## fetching all records from the 'cursor' object
    # records = cursor.fetchall()
    record = cursor.fetchone()
    cursor.execute(query2)
    record_link = cursor.fetchone()
    cursor.close()
    ## Showing the data
    # for record in records:
    #     print(record)
    # print(record)
    res = dict()
    res['you_1'] = record[1]
    res['you_2'] = record[3]
    res['you_3'] = record[5]
    res['you_tit1'] = record[2]
    res['you_tit2'] = record[4]
    res['you_tit3'] = record[6]
    res['banner_twitter'] = record[7]
    res['banner_news'] = record[8]
    res['twitter_embed'] = record[9]
    res['news_embed'] = record[10]
    res['link_title'] = record_link[1]
    res['link_banner'] = record_link[2]
    res['link_reff'] = record_link[3]
    res['link_title_2'] = record_link[4]
    res['link_banner_2'] = record_link[5]
    res['link_reff_2'] = record_link[6]
    return json.dumps(res)


@cc_blueprint.route('/load_banner_news')
def load_banner_news():
    db.reconnect()
    cursor = db.cursor()

    ## defining the Query
    query = "SELECT * FROM apps_video_banner WHERE id = '1'"

    ## getting records from the table
    cursor.execute(query)
    record = cursor.fetchone()
    cursor.close()

    ## Showing the data
    # for record in records:
    #     print(record)
    # print(record)
    res = dict()
    res2 = dict()
    res['id'] = record[0]
    res['youtube_1'] = record[1]
    res['title_youtube_1'] = record[2]
    res['youtube_2'] = record[3]
    res['title_youtube_2'] = record[4]
    res['youtube_3'] = record[5]
    res['title_youtube_3'] = record[6]
    res['banner_twitter'] = record[7]
    res['banner_news'] = record[8]
    res['twitter_embed'] = record[9]
    res['news_embed'] = record[10]
    res2['list'] = res
    return json.dumps(res2)



@cc_blueprint.route('/user_get_history', methods=["POST"])
@jwt_required()
def user_get_history():
    id = get_jwt_identity()
    db.reconnect()
    cursor = db.cursor(dictionary=True)

    query = "SELECT no_laporan, sub_kategori_id, subkategori.sub_kategori, laporan_text, DATE_FORMAT(tgl_submitted, '%Y-%m-%d %T') as tgl_submitted FROM laporan " \
            "LEFT JOIN subkategori ON subkategori.idsubkategori = laporan.sub_kategori_id " \
            "WHERE user_id = %s ORDER BY tgl_submitted DESC "
    print("syaalala")
    ## getting records from the table
    cursor.execute(query, (id,))
    record = cursor.fetchall()
    cursor.close()

    res = dict()
    res['list'] = record
    res['valid'] = 1

    return res



@cc_blueprint.route('/user_get_picturesolve',methods=["POST"])
@jwt_required()
def user_get_picturesolve():
    id = request.json.get('id')
    db.reconnect()
    cursor = db.cursor(dictionary=True)
    # get the last rate & feedback - the latest ID
    query = "SELECT problem,solve FROM work_order_image WHERE work_order_id = %s ORDER BY idworkorderimage DESC"
    cursor.execute(query, (id,))
    record = cursor.fetchall()
    res = dict()
    res['list'] = record
    res['valid'] = 1
    cursor.close()
    return res



@cc_blueprint.route('/warga_get_mail', methods=["POST"])
@jwt_required()
def warga_get_mail():
    username = request.json.get('username', None)
#originalnya ada 3 query execution di satu API call ini
    cursor = db.cursor(dictionary=True)
    # query = "SELECT id_user_mobile, nama FROM user_mobile WHERE email = %s"
    # query2 = "SELECT id_user_mobile FROM work_order WHERE id_user_mobile = '5513'"
    query3 = "SELECT * from work_order WHERE id_user_mobile IN (select id_user_mobile from user_mobile where email = %s)"
    db.reconnect()
    cursor.execute(query3, (username,))
    record = cursor.fetchall()

    res = dict()
    res['list'] = record
    res['valid'] = 0

    if (cursor.rowcount > 0) :
        query4 = "SELECT no_pengaduan AS 'NoPengaduan'," \
                 "idworkorder AS 'IdWorkOrder'," \
                 "nama_pelapor AS 'NamePelapor'," \
                 "telp_pelapor AS 'TelpPelapor'," \
                 "alamat_pelapor AS 'AlamatPelapor'," \
                 "lat_pelapor AS 'LatPelapor'," \
                 "long_pelapor AS 'LonPelapor'," \
                 "tgl_kontak AS 'TanggalKontak'," \
                 "tgl_received AS 'Tanggal Received'," \
                 "tgl_on_process AS 'Tanggal On Process'," \
                 "tgl_close AS 'Tanggal Selesai'," \
                 "problem AS 'Picture'," \
                 "status AS 'StatusLaporan', " \
                 "TIMESTAMPDIFF(Hour,tgl_kontak,tgl_close) AS 'Durasi (Jam)', " \
                 "TIMESTAMPDIFF(Minute,tgl_kontak,tgl_close) AS 'Durasi (Menit)', " \
                 "TIMESTAMPDIFF(Second,tgl_kontak,tgl_close) AS 'Durasi (Detik)', " \
                 "position.position_name AS 'Position', " \
                 "department.department_name AS 'Department', " \
                 "region.region_name AS 'Region', " \
                 "kategori.kategori AS 'Kategori', " \
                 "subkategori.sub_kategori AS 'SubKategori', " \
                 "user.username AS 'User Creator', " \
                 "pengaduan AS 'Pengaduan', IF(STATUS=1,'Open', IF(STATUS=2,'Received', IF(STATUS=3,'On Process', IF(STATUS=4,'Done','')))) AS STATUS " \
                 "from work_order LEFT JOIN position ON position.id = work_order.position_id  " \
                 "LEFT JOIN department ON department.id = position.department_id " \
                 "LEFT JOIN region ON region.id = department.region_id " \
                 "LEFT JOIN work_order_image ON work_order_image.work_order_id = work_order.idworkorder " \
                 "LEFT JOIN subkategori ON subkategori.idsubkategori = work_order.sub_kategori_id " \
                 "LEFT JOIN kategori ON kategori.idkategori = subkategori.kategori_id " \
                 "LEFT JOIN user ON user.iduser = work_order.user_id " \
                 "WHERE work_order.id_user_mobile = %s ORDER BY idworkorder DESC"
        cursor.execute(query4, (res['list'][0]['id_user_mobile'],))
        record = cursor.fetchall()
        res['list'] = record
        res['sitrep'] = len(record)
        res['valid'] = 1
    res['sitrep'] = len(record)
    cursor.close()
    return res

# @cc_blueprint.route('/user_get_category')
# def user_get_category():
#     cursor = db.cursor(dictionary=True)
#     query = "SELECT idsubkategori AS 'id', sub_kategori AS 'name', icon, nomor FROM subkategori WHERE kategori_id = %s ORDER BY nomor ASC"
#     cursor.execute(query, ('1',))
#     record = cursor.fetchall()
#     res = dict()
#     res['list'] = record
#     res['valid'] = 1
#     cursor.close()
#     return res

@cc_blueprint.route('/subkategori', methods=["get"])
def subkategori():
    db.reconnect()
    cursor = db.cursor(dictionary=True)
    query = "SELECT idsubkategori, sub_kategori, icon,  nomor, kategori_id, kategori.kategori from subkategori " \
            "LEFT JOIN kategori ON kategori.idkategori = subkategori.kategori_id "
    cursor.execute(query,)
    record = cursor.fetchall()
    cursor.close()
    res = dict()
    res = record
    return jsonify(res)


@cc_blueprint.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@cc_blueprint.route('/upload', methods=["POST"])
@jwt_required()
def upload_file():
    res = dict()
    user_id = get_jwt_identity()
    newfilename = ''
    if request.method == 'POST':
        print('post')
        # check if the post request has the file part
        if 'file' not in request.files:
            print('no file part')
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        laporan_no = request.form['laporan_no']
        laporan_subcategory_id = request.form['laporan_subcategory_id']
        # print(request.form['laporan_no'])
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            print(os.path.join(app.config['UPLOAD_FOLDER']))
            ts = time.time()
            newfilename = str(laporan_no) + "-" + str(laporan_subcategory_id) + "-" + str(user_id) + "-" + os.path.splitext(str(ts))[0] + os.path.splitext(filename)[1]

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], newfilename ))
            db.reconnect()
            cursor = db.cursor(dictionary=True)
            # get the last rate & feedback - the latest ID
            formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
            query = "INSERT INTO file_uploads (file_name, file_type, laporan_no, laporan_subcategory_id, user_id, date_submitted) VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(query, (newfilename, "file", laporan_no, laporan_subcategory_id, user_id, formatted_date,))
            db.commit()
            res['valid'] = '1'
            # res['thumb_path'] ='https://ccntmc.1500669.com/ntmc_upload/'.$uploadfile
            return res
            # return redirect(url_for('download_file', name=newfilename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''








@cc_blueprint.route('/save_token',methods=["POST"])
@jwt_required()
def save_token():
    username = request.json.get('username')
    token = request.json.get('token')


    stamp2 = datetime.now()

    stamp = stamp2.strftime("%Y-%m-%d %H:%M:%S")
    db.reconnect()
    cursor = db.cursor(dictionary=True)
    # get the last rate & feedback - the latest ID
    query = "INSERT INTO notif_token (username, token, stamp) VALUES (%s, %s, %s)"
    cursor.execute(query, (username, token, stamp,))
    db.commit()

    # record = cursor.fetchall()
    res = dict()
    # res['list'] = record
    res['valid'] = 1
    cursor.close()
    return res

@cc_blueprint.route('/user_idle', methods=["POST"])
@jwt_required()
def user_idle():
    username = request.json.get('username', None)
    if (username == "") :
        valid = 0
        name = ""
    else :
        db.reconnect()
        cursor = db.cursor(dictionary=True)
        query = "SELECT id_user_mobile, nama FROM user_mobile WHERE email = %s"
        cursor.execute(query, (username,))
        record = cursor.fetchall()
        if (len(record) > 0) :
            valid = 1
            name = record[0]['nama']
        else :
            valid = 0
            name = ""


    res = dict()
    res['name'] = name
    res['valid'] = valid
    cursor.close()
    return res




@cc_blueprint.route('/verify', methods=["POST"])
@jwt_required()
def verify():
    email = request.json.get('email')
    passwd = request.json.get('pass')
    db.reconnect()
    cursor = db.cursor(dictionary=True)
    query = "SELECT id_user_mobile,password FROM user_mobile WHERE email = %s"
    cursor.execute(query, (email,))
    record = cursor.fetchall()
    cursor.close()
    valid = 0

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(passwd.encode(), salt)

    if bcrypt.checkpw(passwd.encode(), (record[0]['password']).encode()):
        print("match")
    else:
        print("does not match")
    return 'valid'



@cc_blueprint.route('/user_upload_ktp', methods=["POST"])
@jwt_required()
def warga_upload_ktp():
    email = request.json.get('email')
    passwd = request.json.get('pass')

@cc_blueprint.route('/user_upload_photo', methods=["POST"])
@jwt_required()
def warga_upload_photo():
    email = request.json.get('email')
    passwd = request.json.get('pass')

@cc_blueprint.route('/user_upload_video', methods=["POST"])
@jwt_required()
def warga_upload_video():
    email = request.json.get('email')
    passwd = request.json.get('pass')


@cc_blueprint.route('/laporan_review', methods=["POST"])
def laporan_review():
    db.reconnect()
    cursor = db.cursor(dictionary=True)
    no_laporan = request.json.get('no_laporan')
    query = "SELECT laporan.id, laporan.no_laporan, laporan_published.status, laporan.sub_kategori_id, subkategori.sub_kategori, " \
            "laporan.laporan_subcategory_id, laporan_subcategory.name FROM laporan " \
            "LEFT JOIN laporan_published ON laporan_published.no_laporan = laporan.no_laporan " \
            "LEFT JOIN laporan_subcategory ON laporan_subcategory.id = laporan.laporan_subcategory_id " \
            "LEFT JOIN subkategori ON subkategori.idsubkategori = laporan.sub_kategori_id " \
            "WHERE laporan.no_laporan = %s"
    cursor.execute(query, (str(no_laporan),))
    record = cursor.fetchall()
    cursor.close()
    result = dict()
    result = record
    return jsonify(result)

@cc_blueprint.route('/laporan_print', methods=["POST"])
def laporan_print():
    db.reconnect()
    cursor = db.cursor(dictionary=True)
    no_laporan = request.json.get('no_laporan')
    query = "SELECT laporan.id, laporan.no_laporan, laporan_published.status, laporan.sub_kategori_id, subkategori.sub_kategori, " \
            "laporan.laporan_subcategory_id, laporan_subcategory.name, laporan_published.date_submitted, " \
            "laporan_published.date_approved FROM laporan " \
            "LEFT JOIN laporan_published ON laporan_published.no_laporan = laporan.no_laporan " \
            "LEFT JOIN laporan_subcategory ON laporan_subcategory.id = laporan.laporan_subcategory_id " \
            "LEFT JOIN subkategori ON subkategori.idsubkategori = laporan.sub_kategori_id " \
            "WHERE laporan.no_laporan = %s"
    cursor.execute(query, (str(no_laporan),))
    record = cursor.fetchall()
    cursor.close()
    result = dict()
    result = record
    return jsonify(result)