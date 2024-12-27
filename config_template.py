# 配置文件模板
# 复制此文件为 config.py 并填入你的配置

# DeepSeek API 配置
API_KEY = 'your-api-key-here'

# OCR 配置
OCR_LANGUAGES = ['ch_sim', 'en']  # 支持的语言

# 文件路径配置
SCREENSHOT_FOLDER = "截图"  # 保存截图的文件夹名称

# AI 配置
AI_MODEL = "deepseek-chat"
AI_BASE_URL = "https://api.deepseek.com"

# 物体识别配置
OBJECT_DETECTION = {
    'confidence': 0.5,  # 置信度阈值
    'max_objects': 3,   # 最多识别几个物体
    'translate': True   # 是否将英文翻译为中文
} 