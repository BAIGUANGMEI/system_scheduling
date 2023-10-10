from flask import Flask
from .views.views_front import front
from .views.views_admin import admin
from .exts import init_ext



def create_app():
    app = Flask(__name__)

    #注册蓝图
    app.register_blueprint(blueprint=front)#前端
    app.register_blueprint(blueprint=admin)#用户

    db_uri = 'mysql+pymysql://root:mzh553214@175.24.204.127:3306/systemdb'
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY']='meizhihan'

    init_ext(app)

    return app