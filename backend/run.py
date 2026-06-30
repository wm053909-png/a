import os
from app import create_app

# 获取环境配置
config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    print("=" * 50)
    print("AI心情日记系统后端服务")
    print("=" * 50)
    print(f"环境: {config_name}")
    print(f"访问地址: http://localhost:5000")
    print(f"API文档: http://localhost:5000/api")
    print("=" * 50)

    app.run(host='0.0.0.0', port=5000, debug=True)
