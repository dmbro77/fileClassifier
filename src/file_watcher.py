import os
import shutil
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PyQt5.QtCore import QObject, pyqtSignal

from logger import logger

class FileEventHandler(FileSystemEventHandler):
    def __init__(self, file_watcher):
        super().__init__()
        self.file_watcher = file_watcher
    
    def _is_temporary_file(self, file_path):
        """检查是否是临时文件"""
        if not os.path.exists(file_path):
            return True
            
        file_name = os.path.basename(file_path)
        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lower()
        
        return (file_extension in ('.tmp', '.crdownload') or 
                '.tmp' in file_name)

    def on_created(self, event):
        if event.is_directory:
            return
            
        time.sleep(0.5)  # 等待写入完成
        
        if self._is_temporary_file(event.src_path):
            logger.debug(f"忽略临时文件: {event.src_path}")
            return
            
        logger.info(f"处理新文件: {event.src_path}")
        self.file_watcher.process_new_file(event.src_path)
    
    def on_moved(self, event):
        if event.is_directory:
            return
            
        # 检查是否是临时文件重命名为正式文件
        is_src_temp = self._is_temporary_file(event.src_path)
        # 注意：dest_path 可能还不存在（如果重命名极快？不太可能），或者 _is_temporary_file 会检查存在性
        # 这里逻辑稍微调整：我们关心的是 dest_path 是否有效
        
        # 如果目标文件看起来像临时文件，忽略
        if self._is_temporary_file(event.dest_path):
            return

        # 如果源文件是临时文件，或者只是普通重命名，我们都检查目标文件
        # 但通常我们只关心下载完成（临时->正式）或移动进来
        
        time.sleep(0.5)
        if not os.path.exists(event.dest_path):
            return
            
        logger.info(f"处理重命名/移动文件: {event.dest_path}")
        self.file_watcher.process_new_file(event.dest_path)

class FileWatcher(QObject):
    file_classified = pyqtSignal(str, str)
    
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.observer = None
        self.is_monitoring = False
        logger.debug("FileWatcher 实例已创建")
    
    def start_monitoring(self):
        if self.is_monitoring:
            return
        
        config = self.config_manager.get_config()
        source_folder = config.get('source_folder', '')
        
        if not source_folder or not os.path.isdir(source_folder):
            logger.warning(f"源文件夹无效: {source_folder}")
            return
        
        self.observer = Observer()
        event_handler = FileEventHandler(self)
        self.observer.schedule(event_handler, source_folder, recursive=False)
        self.observer.start()
        self.is_monitoring = True
        logger.info(f"开始监听: {source_folder}")
    
    def stop(self):
        if self.observer and self.is_monitoring:
            self.observer.stop()
            self.observer.join()
            self.is_monitoring = False
            logger.info("停止监听")
    
    def process_new_file(self, file_path):
        if not os.path.exists(file_path):
            return
            
        config = self.config_manager.get_config()
        rules = config.get('rules', [])
        default_target_folder = config.get('default_target_folder', '')
        
        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lower()
        
        target_folder = None
        
        # 匹配规则
        for rule in rules:
            if file_extension in rule.get('extensions', []):
                target_folder = rule.get('target_folder')
                # 如果规则没指定目标文件夹，尝试使用 category + 默认目录
                if not target_folder and default_target_folder:
                    category = rule.get('category', '')
                    if category:
                        target_folder = os.path.join(default_target_folder, category)
                break
        
        # 默认规则
        if not target_folder and default_target_folder:
            category = file_extension[1:] if file_extension else 'other'
            target_folder = os.path.join(default_target_folder, category)
            
        if target_folder:
            self._move_file(file_path, target_folder)
        else:
            logger.debug(f"未找到匹配规则且无默认目录: {file_path}")

    def _move_file(self, src_path, target_folder):
        try:
            os.makedirs(target_folder, exist_ok=True)
            file_name = os.path.basename(src_path)
            target_path = os.path.join(target_folder, file_name)
            
            # 处理重名
            counter = 1
            name, ext = os.path.splitext(file_name)
            while os.path.exists(target_path):
                target_path = os.path.join(target_folder, f"{name}_{counter}{ext}")
                counter += 1
            
            shutil.move(src_path, target_path)
            logger.info(f"移动: {src_path} -> {target_path}")
            self.file_classified.emit(target_path, target_folder)
            
        except Exception as e:
            logger.error(f"移动文件失败 {src_path}: {str(e)}")
