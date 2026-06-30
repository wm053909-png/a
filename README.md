# AI心情日记系统

一个基于B/S模式的智能心情日记系统，支持用户记录日记、查看日历视图、分析心情趋势，并通过AI大模型进行情绪分析和反馈。

## ✨ 功能特性

### 核心功能
- **用户系统**：注册、登录、修改个人信息
- **日记管理**：创建、编辑、删除、查看日记
- **AI情绪分析**：保存日记后自动调用AI分析情绪并给出建议
- **日历视图**：按月展示每日日记，一目了然
- **心情趋势**：折线图展示情绪变化趋势

### 统计分析
- 按情绪标签统计分布
- 按时间段统计分析
- 情绪得分趋势图

### 批量操作
- 批量删除日记
- 批量导出日记（JSON格式）
- 批量修改情绪标签

## 🛠️ 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | Vue 3 + Vite + Element Plus + ECharts |
| 后端 | Python Flask |
| 数据库 | MySQL 8.0 |
| AI服务 | OpenAI API / DeepSeek API |

## 📁 项目结构

```
ai_mood_diary/
├── backend/                 # 后端Flask项目
│   ├── app/
│   │   ├── __init__.py     # 应用初始化
│   │   ├── models/         # 数据模型
│   │   ├── routes/         # API路由
│   │   ├── services/       # 业务逻辑
│   │   └── utils/          # 工具函数
│   ├── config.py           # 配置文件
│   ├── requirements.txt    # 依赖
│   └── run.py              # 启动文件
├── frontend/                # 前端Vue3项目
│   ├── src/
│   │   ├── api/            # API请求
│   │   ├── components/     # 公共组件
│   │   ├── views/          # 页面组件
│   │   ├── router/         # 路由配置
│   │   ├── store/          # 状态管理
│   │   └── utils/          # 工具函数
│   └── package.json
├── database/
│   └── schema.sql          # 数据库表结构
└── README.md
```

## 🚀 快速开始

### 1. 数据库初始化

```bash
# 登录MySQL并执行建表脚本
mysql -u root -p < database/schema.sql
```

### 2. 后端启动

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库和AI API密钥

# 启动服务
python run.py
```

### 3. 前端启动

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 4. 访问应用

- 前端地址：http://localhost:3000
- 后端API：http://localhost:5000

## ⚙️ 配置说明

### 环境变量配置 (backend/.env)

```env
# Flask配置
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key

# 数据库配置
DATABASE_URI=mysql+pymysql://root:password@localhost:3306/ai_mood_diary

# OpenAI配置
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_API_BASE=https://api.openai.com/v1
AI_MODEL=gpt-3.5-turbo

# DeepSeek配置（备用）
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_API_BASE=https://api.deepseek.com
```

## 📚 API接口

### 用户模块
| 接口 | 方法 | 说明 |
|------|------|------|
| /api/auth/register | POST | 用户注册 |
| /api/auth/login | POST | 用户登录 |
| /api/auth/user/profile | GET | 获取用户信息 |
| /api/auth/user/profile | PUT | 修改用户信息 |

### 日记模块
| 接口 | 方法 | 说明 |
|------|------|------|
| /api/diaries | GET | 获取日记列表 |
| /api/diaries | POST | 创建日记 |
| /api/diaries/:id | GET | 获取日记详情 |
| /api/diaries/:id | PUT | 编辑日记 |
| /api/diaries/:id | DELETE | 删除日记 |
| /api/diaries/batch | POST | 批量删除 |
| /api/diaries/batch/export | POST | 批量导出 |
| /api/diaries/batch/mood | PUT | 批量修改情绪 |

### 统计模块
| 接口 | 方法 | 说明 |
|------|------|------|
| /api/stats/calendar | GET | 日历视图数据 |
| /api/stats/trend | GET | 心情趋势数据 |
| /api/stats/emotion | GET | 情绪统计 |
| /api/stats/time-range | GET | 时间段统计 |

## 🎨 界面预览

- **登录/注册页面**：简洁美观的表单设计
- **日记列表**：卡片式展示，支持多选批量操作
- **日记编辑**：富文本编辑器，保存后自动触发AI分析
- **日历视图**：直观展示每日日记和情绪状态
- **心情趋势**：ECharts折线图和饼图展示情绪变化

## 📝 开发说明

1. 前后端分离架构，通过RESTful API通信
2. 使用JWT进行身份认证
3. 密码使用bcrypt加密存储
4. AI分析失败不影响日记保存（降级处理）
5. 支持OpenAI和DeepSeek两种AI服务

## 📄 License

MIT License
