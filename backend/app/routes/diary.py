from datetime import datetime, date
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.diary import Diary
from app.models.emotion_analysis import EmotionAnalysis
from app.services.emotion_service import EmotionService

diary_bp = Blueprint('diary', __name__)


@diary_bp.route('/diaries', methods=['GET'])
@jwt_required()
def get_diaries():
    """获取日记列表（支持分页、筛选）"""
    user_id = int(get_jwt_identity())
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    mood_tag = request.args.get('mood_tag', '').strip()
    start_date = request.args.get('start_date', '').strip()
    end_date = request.args.get('end_date', '').strip()

    # 构建查询
    query = Diary.query.filter_by(user_id=user_id)

    # 按情绪标签筛选
    if mood_tag:
        query = query.filter_by(mood_tag=mood_tag)

    # 按时间段筛选
    if start_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            query = query.filter(Diary.diary_date >= start)
        except ValueError:
            return jsonify({'code': 400, 'message': '开始日期格式错误'}), 400

    if end_date:
        try:
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            query = query.filter(Diary.diary_date <= end)
        except ValueError:
            return jsonify({'code': 400, 'message': '结束日期格式错误'}), 400

    # 按日期降序排列
    query = query.order_by(Diary.diary_date.desc(), Diary.created_at.desc())

    # 分页
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        'code': 200,
        'data': {
            'items': [diary.to_list_dict() for diary in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    }), 200


@diary_bp.route('/diaries', methods=['POST'])
@jwt_required()
def create_diary():
    """新建日记（触发AI情绪分析）"""
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data:
        return jsonify({'code': 400, 'message': '请提供日记内容'}), 400

    title = data.get('title', '').strip()
    content = data.get('content', '').strip()
    diary_date_str = data.get('diary_date', '').strip()
    mood_tag = data.get('mood_tag', 'neutral').strip()

    # 参数验证
    if not title:
        return jsonify({'code': 400, 'message': '日记标题不能为空'}), 400
    if not content:
        return jsonify({'code': 400, 'message': '日记内容不能为空'}), 400

    # 解析日期
    if diary_date_str:
        try:
            diary_date = datetime.strptime(diary_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'code': 400, 'message': '日期格式错误，请使用YYYY-MM-DD格式'}), 400
    else:
        diary_date = date.today()

    # 创建日记
    diary = Diary(
        user_id=user_id,
        title=title,
        content=content,
        diary_date=diary_date,
        mood_tag=mood_tag
    )

    try:
        db.session.add(diary)
        db.session.commit()

        # 触发AI情绪分析（异步处理）
        try:
            EmotionService.analyze_and_save(diary.id, content)
        except Exception as e:
            current_app.logger.error(f"AI情绪分析失败: {str(e)}")
            # AI分析失败不影响日记保存

        return jsonify({
            'code': 200,
            'message': '日记创建成功',
            'data': diary.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"创建日记失败: {str(e)}")
        return jsonify({'code': 500, 'message': '创建失败，请稍后再试'}), 500


@diary_bp.route('/diaries/<int:diary_id>', methods=['GET'])
@jwt_required()
def get_diary(diary_id):
    """获取日记详情"""
    user_id = int(get_jwt_identity())
    diary = Diary.query.filter_by(id=diary_id, user_id=user_id).first()

    if not diary:
        return jsonify({'code': 404, 'message': '日记不存在'}), 404

    return jsonify({
        'code': 200,
        'data': diary.to_dict()
    }), 200


@diary_bp.route('/diaries/<int:diary_id>', methods=['PUT'])
@jwt_required()
def update_diary(diary_id):
    """编辑日记"""
    user_id = int(get_jwt_identity())
    diary = Diary.query.filter_by(id=diary_id, user_id=user_id).first()

    if not diary:
        return jsonify({'code': 404, 'message': '日记不存在'}), 404

    data = request.get_json()
    if not data:
        return jsonify({'code': 400, 'message': '请提供要修改的内容'}), 400

    # 更新字段
    if 'title' in data:
        title = data['title'].strip()
        if title:
            diary.title = title

    if 'content' in data:
        content = data['content'].strip()
        if content:
            # 如果内容改变，重新进行AI分析
            if content != diary.content:
                diary.content = content
                try:
                    EmotionService.analyze_and_save(diary.id, content)
                except Exception as e:
                    current_app.logger.error(f"AI情绪分析失败: {str(e)}")

    if 'diary_date' in data:
        try:
            diary.diary_date = datetime.strptime(data['diary_date'], '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'code': 400, 'message': '日期格式错误'}), 400

    if 'mood_tag' in data:
        diary.mood_tag = data['mood_tag'].strip()

    try:
        db.session.commit()
        return jsonify({
            'code': 200,
            'message': '修改成功',
            'data': diary.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': '修改失败，请稍后再试'}), 500


@diary_bp.route('/diaries/<int:diary_id>', methods=['DELETE'])
@jwt_required()
def delete_diary(diary_id):
    """删除单篇日记"""
    user_id = int(get_jwt_identity())
    diary = Diary.query.filter_by(id=diary_id, user_id=user_id).first()

    if not diary:
        return jsonify({'code': 404, 'message': '日记不存在'}), 404

    try:
        db.session.delete(diary)
        db.session.commit()
        return jsonify({
            'code': 200,
            'message': '删除成功'
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': '删除失败，请稍后再试'}), 500


@diary_bp.route('/diaries/batch', methods=['POST'])
@jwt_required()
def batch_delete():
    """批量删除日记"""
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data or 'ids' not in data:
        return jsonify({'code': 400, 'message': '请提供要删除的日记ID列表'}), 400

    ids = data['ids']
    if not isinstance(ids, list) or len(ids) == 0:
        return jsonify({'code': 400, 'message': '日记ID列表不能为空'}), 400

    try:
        # 删除指定的日记
        deleted_count = Diary.query.filter(
            Diary.id.in_(ids),
            Diary.user_id == user_id
        ).delete(synchronize_session='fetch')

        db.session.commit()

        return jsonify({
            'code': 200,
            'message': f'成功删除{deleted_count}篇日记',
            'data': {'deleted_count': deleted_count}
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': '批量删除失败，请稍后再试'}), 500


@diary_bp.route('/diaries/batch/export', methods=['POST'])
@jwt_required()
def batch_export():
    """批量导出日记"""
    user_id = int(get_jwt_identity())
    data = request.get_json()

    ids = data.get('ids', []) if data else []

    # 构建查询
    query = Diary.query.filter_by(user_id=user_id)

    if ids:
        query = query.filter(Diary.id.in_(ids))

    diaries = query.order_by(Diary.diary_date.desc()).all()

    # 导出为JSON格式
    export_data = []
    for diary in diaries:
        diary_data = {
            'title': diary.title,
            'content': diary.content,
            'diary_date': diary.diary_date.strftime('%Y-%m-%d'),
            'mood_tag': diary.mood_tag,
            'created_at': diary.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        if diary.analysis:
            diary_data['analysis'] = {
                'emotion_label': diary.analysis.emotion_label,
                'emotion_score': float(diary.analysis.emotion_score),
                'ai_feedback': diary.analysis.ai_feedback
            }
        export_data.append(diary_data)

    return jsonify({
        'code': 200,
        'message': f'成功导出{len(export_data)}篇日记',
        'data': export_data
    }), 200


@diary_bp.route('/diaries/batch/mood', methods=['PUT'])
@jwt_required()
def batch_update_mood():
    """批量修改情绪标签"""
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data or 'ids' not in data or 'mood_tag' not in data:
        return jsonify({'code': 400, 'message': '请提供日记ID列表和新的情绪标签'}), 400

    ids = data['ids']
    mood_tag = data['mood_tag'].strip()

    if not isinstance(ids, list) or len(ids) == 0:
        return jsonify({'code': 400, 'message': '日记ID列表不能为空'}), 400

    if not mood_tag:
        return jsonify({'code': 400, 'message': '情绪标签不能为空'}), 400

    valid_mood_tags = ['happy', 'sad', 'neutral', 'anxious', 'angry', 'peaceful', 'excited', 'grateful', 'tired', 'confused']
    if mood_tag not in valid_mood_tags:
        return jsonify({'code': 400, 'message': '无效的情绪标签'}), 400

    try:
        # 更新指定日记的情绪标签
        updated_count = Diary.query.filter(
            Diary.id.in_(ids),
            Diary.user_id == user_id
        ).update(
            {'mood_tag': mood_tag},
            synchronize_session='fetch'
        )

        db.session.commit()

        return jsonify({
            'code': 200,
            'message': f'成功修改{updated_count}篇日记的情绪标签',
            'data': {'updated_count': updated_count}
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': '批量修改失败，请稍后再试'}), 500


@diary_bp.route('/diaries/<int:diary_id>/analysis', methods=['GET'])
@jwt_required()
def get_analysis(diary_id):
    """获取日记情绪分析结果"""
    user_id = int(get_jwt_identity())
    diary = Diary.query.filter_by(id=diary_id, user_id=user_id).first()

    if not diary:
        return jsonify({'code': 404, 'message': '日记不存在'}), 404

    if not diary.analysis:
        return jsonify({'code': 404, 'message': '该日记暂无情绪分析结果'}), 404

    return jsonify({
        'code': 200,
        'data': diary.analysis.to_dict()
    }), 200


# 在EmotionService中添加analyze_and_save方法
def analyze_and_save(diary_id, content):
    """分析情绪并保存结果"""
    from app.models.diary import Diary

    # 调用AI分析
    result = EmotionService.analyze_emotion(content)

    # 保存分析结果
    analysis = EmotionAnalysis(
        diary_id=diary_id,
        emotion_label=result['emotion_label'],
        emotion_score=result['emotion_score'],
        ai_feedback=result['ai_feedback'],
        model_name=result['model_name']
    )

    db.session.add(analysis)

    # 同时更新日记的情绪标签
    diary = Diary.query.get(diary_id)
    if diary:
        diary.mood_tag = result['emotion_label']

    db.session.commit()

    return analysis


# 给EmotionService添加类方法
EmotionService.analyze_and_save = staticmethod(analyze_and_save)
