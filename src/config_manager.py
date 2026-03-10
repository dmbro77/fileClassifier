import os
import json
import platform
from logger import logger

DEFAULT_CONFIG = {
    "source_folder": "",
    "default_target_folder": "",
    "rules": [
  {
    "extensions": [".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx", ".ppt", ".pptx", ".csv", ".md"],
    "target_folder": "",
    "category": "Documents"
  },
  {
    "extensions": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".tiff", ".jfif"],
    "target_folder": "",
    "category": "Images"
  },
  {
    "extensions": [".zip", ".rar", ".7z", ".tar", ".gz"],
    "target_folder": "",
    "category": "Zip"
  },
  {
    "extensions": [".mp4", ".avi", ".mov", ".wmv", ".flv", ".mkv"],
    "target_folder": "",
    "category": "Videos"
  },
  {
    "extensions": [".mp3", ".wav", ".flac", ".aac", ".ogg"],
    "target_folder": "",
    "category": "Audio"
  },
  {
    "extensions": [".ipa", ".apk", ".dmg", ".pkg", ".deb", ".rpm", ".exe", ".msi"],
    "target_folder": "",
    "category": "Exe"
  },
  {
    "extensions": [".py", ".json", ".js", ".html", ".css", ".java", ".c", ".cpp", ".h", ".php", ".sh", ".bat", ".xml", ".jsx", ".ts", ".tsx", ".scss", ".less", ".kt", ".cs", ".rb", ".go", ".swift", ".m", ".mm", ".bash", ".zsh", ".cmd", ".ps1", ".yml", ".yaml", ".ini", ".cfg", ".conf", ".sql", ".lua", ".pl", ".r", ".dart", ".rs", ".vue", ".svelte", ".gradle", ".properties", ".toml", ".lock", ".gitignore", ".dockerfile", ".makefile", ".htm", ".keystore", ".json5", ".plist", ".sketch"],
    "target_folder": "",
    "category": "Code"
  }
],
    "is_monitoring": True,
    "auto_start": True,
    "show_notifications": True
}

class ConfigManager:
    def __init__(self, config_file='config.json'):
        self.config_file = self._get_config_path(config_file)
        self.config = self.load_config()
        logger.info("配置管理器初始化完成")
    
    def _get_config_path(self, config_file):
        """获取配置文件路径"""
        system = platform.system()
        if system == 'Windows':
            base_dir = os.environ.get('LOCALAPPDATA', '')
        else:
            base_dir = os.path.join(os.path.expanduser('~'), '.config')
            
        app_data_dir = os.path.join(base_dir, 'FileClassifier')
        
        try:
            os.makedirs(app_data_dir, exist_ok=True)
        except Exception as e:
            logger.error(f"创建配置目录失败: {str(e)}")
            app_data_dir = os.path.dirname(os.path.abspath(__file__))
            
        return os.path.join(app_data_dir, config_file)
    
    def load_config(self):
        """加载配置，如果文件不存在则创建默认配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 简单的配置迁移：确保新字段存在
                    for key, value in DEFAULT_CONFIG.items():
                        if key not in config:
                            config[key] = value
                    return config
            except Exception as e:
                logger.error(f"加载配置文件失败: {str(e)}")
        
        # 如果文件不存在或加载失败，使用默认配置
        self.save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    
    def save_config(self, config):
        """保存配置"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            self.config = config
            logger.info("配置已保存")
            return True
        except Exception as e:
            logger.error(f"保存配置文件失败: {str(e)}")
            return False
            
    def get_config(self):
        return self.config
