from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models.user import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    data = request.get_json()

    # 参数验证
    if not data:
        return jsonify({'code': 400, 'message': '请提供注册信息'}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    email = data.get('email', '').strip()
    nickname = data.get('nickname', '').strip()

    if not username:
        return jsonify({'code': 400, 'message': '用户名不能为空'}), 400
    if not password:
        return jsonify({'code': 400, 'message': '密码不能为空'}), 400
    if not email:
        return jsonify({'code': 400, 'message': '邮箱不能为空'}), 400
    if len(password) < 6:
        return jsonify({'code': 400, 'message': '密码长度不能少于6位'}), 400

    # 检查用户名是否已存在
    if User.query.filter_by(username=username).first():
        return jsonify({'code': 400, 'message': '用户名已存在'}), 400

    # 检查邮箱是否已存在
    if User.query.filter_by(email=email).first():
        return jsonify({'code': 400, 'message': '邮箱已被注册'}), 400

    # 创建用户
    user = User(
        username=username,
        email=email,
        nickname=nickname or username
    )
    user.set_password(password)

    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({
            'code': 200,
            'message': '注册成功',
            'data': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': '注册失败，请稍后再试'}), 500


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.get_json()

    if not data:
        return jsonify({'code': 400, 'message': '请提供登录信息'}), 400

    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({'code': 400, 'message': '用户名和密码不能为空'}), 400

    # 查找用户
    user = User.query.filter_by(username=username).first()

    if not user or not user.check_password(password):
        return jsonify({'code': 401, 'message': '用户名或密码错误'}), 401

    # 生成JWT Token
    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        'code': 200,
        'message': '登录成功',
        'data': {
            'token': access_token,
            'user': user.to_dict()
        }
    }), 200


@auth_bp.route('/user/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """获取当前用户信息"""
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))

    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404

    return jsonify({
        'code': 200,
        'data': user.to_dict()
    }), 200


@auth_bp.route('/user/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """修改个人信息"""
    user_id = get_jwt_identity()
    user = User.query.get(int(user_id))

    if not user:
        return jsonify({'code': 404, 'message': '用户不存在'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请提供要修改的信息'}), 400

    # 更新允许的字段
    if 'email' in data:
        email = data['email'].strip()
        if email and email != user.email:
            if User.query.filter_by(email=email).first():
                return jsonify({'code': 400, 'message': '邮箱已被使用'}), 400
            user.email = email

    if 'nickname' in data:
        user.nickname = data['nickname'].strip()

    # 修改密码
    if 'password' in data:
        old_password = data.get('old_password', '').strip()
        new_password = data['password'].strip()

        if not old_password:
            return jsonify({'code': 400, 'message': '请输入原密码'}), 400
        if not user.check_password(old_password):
            return jsonify({'code': 400, 'message': '原密码错误'}), 400
        if len(new_password) < 6:
            return jsonify({'code': 400, 'message': '新密码长度不能少于6位'}), 400

        user.set_password(new_password)

    try:
        db.session.commit()
        return jsonify({
            'code': 200,
            'message': '修改成功',
            'data': user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': '修改失败，请稍后再试'}), 500
