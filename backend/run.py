import os
from app import create_app

# 获取环境配置
config_name = os.getenv('FLASK_ENV', 'production')
app = create_app(config_name)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("=" * 50)
    print("AI心情日记系统后端服务")
    print("=" * 50)
    print(f"环境: {config_name}")
    print(f"访问地址: http://0.0.0.0:{port}")
    print("=" * 50)

    app.run(host='0.0.0.0', port=port, debug=False)
