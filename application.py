import boto3
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from flaskext.mysql import MySQL

application = Flask(__name__)

# cors
cors = CORS(application, resources={r"/*": {"origins": "*"}})

# mysql
mysql = MySQL()
application.config['MYSQL_DATABASE_USER'] = os.environ["MYSQL_DATABASE_USER"]
application.config['MYSQL_DATABASE_PASSWORD'] = os.environ["MYSQL_DATABASE_PASSWORD"]
application.config['MYSQL_DATABASE_DB'] = os.environ["MYSQL_DATABASE_DB"]
application.config['MYSQL_DATABASE_HOST'] = os.environ["MYSQL_DATABASE_HOST"]
mysql.init_app(application)


@application.route('/')
def main():
    return "핵심 쏙쏙 AWS"

@application.route('/fileupload', methods=['POST'])
def file_upload():
    file = request.files['file']
    s3 = boto3.client('s3',
                      aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
                      aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"]
                      )
    s3.put_object(
        ACL="public-read",
        Bucket=os.environ["BUCKET_NAME"],
        Body=file,
        Key=file.filename,
        ContentType=file.content_type
    )

    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("insert into file(file_name) value('" + file.filename + "')")
    conn.commit()
    conn.close()

    return jsonify({'result': 'success'})

@application.route('/files', methods=['GET'])
def files():
    conn = mysql.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT file_name from file")
    data = cursor.fetchall()
    conn.close()

    return jsonify({'result': 'success', 'files':data})


if __name__ == '__main__':
    application.debug = True
    application.run()