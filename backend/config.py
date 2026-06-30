import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """基础配置"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'ai-mood-diary-secret-key-2024')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-2024')

    # 数据库配置（支持PostgreSQL和SQLite）
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f'sqlite:///{os.path.join(BASEDIR, "mood_diary.db")}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # AI服务配置
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_API_BASE = os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
    AI_MODEL = os.getenv('AI_MODEL', 'gpt-3.5-turbo')

    # DeepSeek配置（备用）
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
    DEEPSEEK_API_BASE = os.getenv('DEEPSEEK_API_BASE', 'https://api.deepseek.com')

    # JWT配置
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24小时


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
