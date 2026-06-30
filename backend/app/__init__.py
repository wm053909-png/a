from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from config import config

# 初始化扩展
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()


def create_app(config_name='default'):
    """创建Flask应用"""
    app = Flask(__name__)

    # 加载配置
    app.config.from_object(config[config_name])

    # 初始化扩展
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # 注册蓝图
    from app.routes.auth import auth_bp
    from app.routes.diary import diary_bp
    from app.routes.stats import stats_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(diary_bp, url_prefix='/api')
    app.register_blueprint(stats_bp, url_prefix='/api/stats')

    # 创建数据库表
    with app.app_context():
        from app.models import user, diary, emotion_analysis
        db.create_all()

    return app
