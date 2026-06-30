from datetime import datetime
from app import db


class EmotionAnalysis(db.Model):
    """情绪分析结果模型"""
    __tablename__ = 'emotion_analyses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    diary_id = db.Column(db.Integer, db.ForeignKey('diaries.id'), unique=True, nullable=False, comment='日记ID')
    emotion_label = db.Column(db.String(50), nullable=False, comment='AI分析的情绪标签')
    emotion_score = db.Column(db.Numeric(3, 2), default=0.50, comment='情绪得分(0-1)')
    ai_feedback = db.Column(db.Text, comment='AI生成的反馈建议')
    model_name = db.Column(db.String(100), comment='使用的AI模型名称')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='分析时间')

    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'diary_id': self.diary_id,
            'emotion_label': self.emotion_label,
            'emotion_score': float(self.emotion_score) if self.emotion_score else 0.5,
            'ai_feedback': self.ai_feedback,
            'model_name': self.model_name,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def __repr__(self):
        return f'<EmotionAnalysis for Diary {self.diary_id}>'
