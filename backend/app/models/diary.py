from datetime import datetime
from app import db


class Diary(db.Model):
    """日记模型"""
    __tablename__ = 'diaries'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='用户ID')
    title = db.Column(db.String(200), nullable=False, comment='日记标题')
    content = db.Column(db.Text, nullable=False, comment='日记内容')
    diary_date = db.Column(db.Date, nullable=False, comment='日记日期')
    mood_tag = db.Column(db.String(50), default='neutral', comment='情绪标签')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关联
    analysis = db.relationship('EmotionAnalysis', backref='diary', uselist=False, cascade='all, delete-orphan')

    def to_dict(self):
        """转换为字典"""
        result = {
            'id': self.id,
            'user_id': self.user_id,
            'title': self.title,
            'content': self.content,
            'diary_date': self.diary_date.strftime('%Y-%m-%d') if self.diary_date else None,
            'mood_tag': self.mood_tag,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
        if self.analysis:
            result['analysis'] = self.analysis.to_dict()
        return result

    def to_list_dict(self):
        """列表模式转换（不包含内容）"""
        return {
            'id': self.id,
            'title': self.title,
            'diary_date': self.diary_date.strftime('%Y-%m-%d') if self.diary_date else None,
            'mood_tag': self.mood_tag,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'has_analysis': self.analysis is not None
        }

    def __repr__(self):
        return f'<Diary {self.title}>'
