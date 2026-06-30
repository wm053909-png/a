import json
import requests
from flask import current_app


class EmotionService:
    """AI情绪分析服务"""

    # 情绪标签定义
    EMOTION_LABELS = {
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

    @staticmethod
    def analyze_emotion(content, model_type='openai'):
        """
        调用AI分析日记情绪

        Args:
            content: 日记内容
            model_type: 模型类型 ('openai' 或 'deepseek')

        Returns:
            dict: {
                'emotion_label': 情绪标签,
                'emotion_score': 情绪得分,
                'ai_feedback': AI反馈,
                'model_name': 模型名称
            }
        """
        prompt = EmotionService._build_prompt(content)

        try:
            if model_type == 'deepseek' and current_app.config.get('DEEPSEEK_API_KEY'):
                return EmotionService._call_deepseek(prompt)
            else:
                return EmotionService._call_openai(prompt)
        except Exception as e:
            current_app.logger.error(f"AI情绪分析失败: {str(e)}")
            # 返回默认分析结果
            return {
                'emotion_label': 'neutral',
                'emotion_score': 0.5,
                'ai_feedback': '情绪分析暂时不可用，请稍后再试。',
                'model_name': 'fallback'
            }

    @staticmethod
    def _build_prompt(content):
        """构建AI分析提示词"""
        return f"""请分析以下日记内容的情绪倾向，并给出简短的反馈建议。

日记内容：
{content}

请按以下JSON格式返回分析结果：
{{
    "emotion_label": "情绪标签(happy/sad/neutral/anxious/angry/peaceful/excited/grateful/tired/confused中的一个)",
    "emotion_score": 情绪得分(0-1之间的小数，1表示非常积极，0表示非常消极),
    "ai_feedback": "用一两句话给出的温暖、有建设性的反馈建议"
}}

注意：
1. 只返回JSON格式，不要有其他内容
2. emotion_label必须是预定义的情绪标签之一
3. ai_feedback要温暖、积极、有帮助
"""

    @staticmethod
    def _call_openai(prompt):
        """调用OpenAI API"""
        api_key = current_app.config.get('OPENAI_API_KEY')
        api_base = current_app.config.get('OPENAI_API_BASE', 'https://api.openai.com/v1')
        model = current_app.config.get('AI_MODEL', 'gpt-3.5-turbo')

        if not api_key:
            raise ValueError("OpenAI API Key未配置")

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        data = {
            'model': model,
            'messages': [
                {'role': 'system', 'content': '你是一个专业的情绪分析师，擅长分析文本中的情绪倾向。'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.7,
            'max_tokens': 500
        }

        response = requests.post(
            f"{api_base}/chat/completions",
            headers=headers,
            json=data,
            timeout=10
        )

        if response.status_code != 200:
            raise Exception(f"OpenAI API调用失败: {response.text}")

        result = response.json()
        content = result['choices'][0]['message']['content']

        # 解析JSON结果
        analysis = EmotionService._parse_analysis(content)
        analysis['model_name'] = model
        return analysis

    @staticmethod
    def _call_deepseek(prompt):
        """调用DeepSeek API"""
        api_key = current_app.config.get('DEEPSEEK_API_KEY')
        api_base = current_app.config.get('DEEPSEEK_API_BASE', 'https://api.deepseek.com')

        if not api_key:
            raise ValueError("DeepSeek API Key未配置")

        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }

        data = {
            'model': 'deepseek-chat',
            'messages': [
                {'role': 'system', 'content': '你是一个专业的情绪分析师，擅长分析文本中的情绪倾向。'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.7,
            'max_tokens': 500
        }

        response = requests.post(
            f"{api_base}/chat/completions",
            headers=headers,
            json=data,
            timeout=10
        )

        if response.status_code != 200:
            raise Exception(f"DeepSeek API调用失败: {response.text}")

        result = response.json()
        content = result['choices'][0]['message']['content']

        # 解析JSON结果
        analysis = EmotionService._parse_analysis(content)
        analysis['model_name'] = 'deepseek-chat'
        return analysis

    @staticmethod
    def _parse_analysis(content):
        """解析AI返回的分析结果"""
        try:
            # 尝试直接解析JSON
            # 移除可能的markdown代码块标记
            content = content.strip()
            if content.startswith('```'):
                content = content.split('```')[1]
                if content.startswith('json'):
                    content = content[4:]
            content = content.strip()

            analysis = json.loads(content)

            # 验证情绪标签
            valid_labels = list(EmotionService.EMOTION_LABELS.keys())
            if analysis.get('emotion_label') not in valid_labels:
                analysis['emotion_label'] = 'neutral'

            # 验证情绪得分
            score = float(analysis.get('emotion_score', 0.5))
            analysis['emotion_score'] = max(0.0, min(1.0, score))

            return analysis

        except (json.JSONDecodeError, ValueError) as e:
            current_app.logger.error(f"解析AI返回结果失败: {str(e)}")
            # 返回默认结果
            return {
                'emotion_label': 'neutral',
                'emotion_score': 0.5,
                'ai_feedback': '感谢你的分享，记录日记是一个很好的习惯。'
            }

    @staticmethod
    def get_emotion_label_cn(label):
        """获取情绪标签的中文名称"""
        return EmotionService.EMOTION_LABELS.get(label, '未知')
