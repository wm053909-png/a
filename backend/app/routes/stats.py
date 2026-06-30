from datetime import datetime, timedelta, date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, extract
from app import db
from app.models.diary import Diary
from app.models.emotion_analysis import EmotionAnalysis

stats_bp = Blueprint('stats', __name__)


@stats_bp.route('/calendar', methods=['GET'])
@jwt_required()
def get_calendar_data():
    """日历视图数据（按月）"""
    user_id = int(get_jwt_identity())
    year = request.args.get('year', date.today().year, type=int)
    month = request.args.get('month', date.today().month, type=int)

    # 查询该月的所有日记
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)

    diaries = Diary.query.filter(
        Diary.user_id == user_id,
        Diary.diary_date >= start_date,
        Diary.diary_date <= end_date
    ).all()

    # 组织日历数据
    calendar_data = {}
    for diary in diaries:
        day_str = diary.diary_date.strftime('%Y-%m-%d')
        if day_str not in calendar_data:
            calendar_data[day_str] = {
                'date': day_str,
                'count': 0,
                'mood_tags': [],
                'has_analysis': False
            }
        calendar_data[day_str]['count'] += 1
        calendar_data[day_str]['mood_tags'].append(diary.mood_tag)
        if diary.analysis:
            calendar_data[day_str]['has_analysis'] = True

    return jsonify({
        'code': 200,
        'data': {
            'year': year,
            'month': month,
            'days': list(calendar_data.values())
        }
    }), 200


@stats_bp.route('/trend', methods=['GET'])
@jwt_required()
def get_mood_trend():
    """心情趋势折线图数据"""
    user_id = int(get_jwt_identity())
    days = request.args.get('days', 30, type=int)

    # 查询最近N天的日记情绪
    start_date = date.today() - timedelta(days=days)

    # 按日期分组统计
    results = db.session.query(
        Diary.diary_date,
        func.count(Diary.id).label('diary_count'),
        func.avg(EmotionAnalysis.emotion_score).label('avg_score')
    ).outerjoin(
        EmotionAnalysis, Diary.id == EmotionAnalysis.diary_id
    ).filter(
        Diary.user_id == user_id,
        Diary.diary_date >= start_date
    ).group_by(
        Diary.diary_date
    ).order_by(
        Diary.diary_date
    ).all()

    # 组织趋势数据
    trend_data = []
    current_date = start_date
    today = date.today()

    # 创建日期到数据的映射
    data_map = {r.diary_date: r for r in results}

    while current_date <= today:
        if current_date in data_map:
            r = data_map[current_date]
            trend_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'diary_count': r.diary_count,
                'avg_score': round(float(r.avg_score), 2) if r.avg_score else 0.5
            })
        else:
            trend_data.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'diary_count': 0,
                'avg_score': None
            })
        current_date += timedelta(days=1)

    return jsonify({
        'code': 200,
        'data': {
            'days': days,
            'trend': trend_data
        }
    }), 200


@stats_bp.route('/emotion', methods=['GET'])
@jwt_required()
def get_emotion_stats():
    """按情绪标签统计分析"""
    user_id = int(get_jwt_identity())

    # 统计各情绪标签的数量
    results = db.session.query(
        Diary.mood_tag,
        func.count(Diary.id).label('count')
    ).filter(
        Diary.user_id == user_id
    ).group_by(
        Diary.mood_tag
    ).all()

    # 情绪标签中文映射
    emotion_cn = {
        'happy': '开心',
        'sad': '悲伤',
        'neutral': '平静',
        'anxious': '焦虑',
        'angry': '愤怒',
        'peaceful': '安宁',
        'excited': '兴奋',
        'grateful': '感恩',
        'tired': '疲惫',
        'confused': '困惑'
    }

    emotion_stats = []
    total_count = sum(r.count for r in results)

    for r in results:
        percentage = round(r.count / total_count * 100, 1) if total_count > 0 else 0
        emotion_stats.append({
            'emotion_tag': r.mood_tag,
            'emotion_name': emotion_cn.get(r.mood_tag, '未知'),
            'count': r.count,
            'percentage': percentage
        })

    # 按数量降序排列
    emotion_stats.sort(key=lambda x: x['count'], reverse=True)

    return jsonify({
        'code': 200,
        'data': {
            'total': total_count,
            'emotions': emotion_stats
        }
    }), 200


@stats_bp.route('/time-range', methods=['GET'])
@jwt_required()
def get_time_range_stats():
    """按时间段统计分析"""
    user_id = int(get_jwt_identity())
    start_date_str = request.args.get('start_date', '').strip()
    end_date_str = request.args.get('end_date', '').strip()

    # 默认查询最近30天
    if not start_date_str:
        start_date = date.today() - timedelta(days=30)
    else:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'code': 400, 'message': '开始日期格式错误'}), 400

    if not end_date_str:
        end_date = date.today()
    else:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'code': 400, 'message': '结束日期格式错误'}), 400

    # 查询时间段内的日记
    diaries = Diary.query.filter(
        Diary.user_id == user_id,
        Diary.diary_date >= start_date,
        Diary.diary_date <= end_date
    ).all()

    # 统计数据
    total_count = len(diaries)

    # 按情绪标签统计
    emotion_counts = {}
    for diary in diaries:
        tag = diary.mood_tag
        emotion_counts[tag] = emotion_counts.get(tag, 0) + 1

    # 计算平均情绪得分
    scores = []
    for diary in diaries:
        if diary.analysis:
            scores.append(float(diary.analysis.emotion_score))
    avg_score = sum(scores) / len(scores) if scores else 0.5

    # 按日期统计每日数量
    daily_counts = {}
    for diary in diaries:
        day_str = diary.diary_date.strftime('%Y-%m-%d')
        daily_counts[day_str] = daily_counts.get(day_str, 0) + 1

    return jsonify({
        'code': 200,
        'data': {
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'total_diaries': total_count,
            'avg_emotion_score': round(avg_score, 2),
            'emotion_distribution': emotion_counts,
            'daily_counts': daily_counts
        }
    }), 200
