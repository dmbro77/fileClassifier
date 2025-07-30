import os
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from PyQt5.QtCore import QObject, pyqtSignal
import time

from logger import logger  # 导入日志模块

class FileEventHandler(FileSystemEventHandler):
    def __init__(self, file_watcher):
        super().__init__()
        self.file_watcher = file_watcher
    
    def on_created(self, event):
        # 只处理文件创建事件，忽略目录创建事件
        if not event.is_directory:
            # 给文件一点时间完成写入
            time.sleep(0.5)
            # 检查文件是否仍然存在，以及是否是临时文件
            file_path = event.src_path
            _, file_extension = os.path.splitext(file_path)
            file_extension = file_extension.lower()
            file_name = os.path.basename(file_path)
            
            logger.debug(f"检测到文件创建事件: {file_path}")
            
            # 忽略明显的临时文件
            if file_extension == '.tmp' or file_extension == '.crdownload' or '.tmp' in file_name:
                logger.debug(f"忽略临时文件: {file_path}")
                return
                
            # 检查文件是否仍然存在
            if not os.path.exists(file_path):
                logger.debug(f"文件不再存在，可能是临时文件: {file_path}")
                return
                
            # 处理文件
            logger.info(f"处理新创建的文件: {file_path}")
            self.file_watcher.process_new_file(file_path)
    
    def on_moved(self, event):
        # 处理文件重命名事件（包括Chrome下载完成后的.tmp文件重命名）
        if not event.is_directory:
            # 获取目标文件路径（重命名后的文件路径）
            dest_path = event.dest_path
            
            # 检查源文件是否是临时文件
            src_path = event.src_path
            _, src_extension = os.path.splitext(src_path)
            src_extension = src_extension.lower()
            src_name = os.path.basename(src_path)
            
            logger.debug(f"检测到文件移动/重命名事件: {src_path} -> {dest_path}")
            
            # 如果源文件是临时文件，而目标文件不是，则处理目标文件
            if (src_extension == '.tmp' or src_extension == '.crdownload' or '.tmp' in src_name):
                # 检查目标文件是否也是临时文件
                _, dest_extension = os.path.splitext(dest_path)
                dest_extension = dest_extension.lower()
                dest_name = os.path.basename(dest_path)
                
                if dest_extension == '.tmp' or dest_extension == '.crdownload' or '.tmp' in dest_name:
                    logger.debug(f"目标文件也是临时文件，忽略: {dest_path}")
                    return
                logger.debug(f"检测到临时文件重命名: {src_path} -> {dest_path}")
                
                # 给文件一点时间完成写入
                time.sleep(0.5)
                
                # 检查目标文件是否存在
                if not os.path.exists(dest_path):
                    logger.warning(f"重命名后的文件不存在: {dest_path}")
                    return
                
                # 处理重命名后的文件
                logger.info(f"处理重命名后的文件: {dest_path}")
                self.file_watcher.process_new_file(dest_path)

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
            logger.debug("文件监视器已经在运行中，不需要重新启动")
            return
        
        config = self.config_manager.get_config()
        source_folder = config.get('source_folder', '')
        
        if not source_folder or not os.path.isdir(source_folder):
            logger.warning(f"源文件夹无效或不存在: {source_folder}，无法启动监视器")
            return
        
        self.observer = Observer()
        event_handler = FileEventHandler(self)
        self.observer.schedule(event_handler, source_folder, recursive=False)
        self.observer.start()
        self.is_monitoring = True
        logger.info(f"开始监听文件夹: {source_folder}")
    
    def stop(self):
        if self.observer and self.is_monitoring:
            logger.info("停止文件监视器")
            self.observer.stop()
            self.observer.join()
            self.is_monitoring = False
        else:
            logger.debug("文件监视器未运行，无需停止")
    
    def process_new_file(self, file_path):
        # 再次检查文件是否存在
        if not os.path.exists(file_path):
            logger.warning(f"文件不再存在，无法处理: {file_path}")
            return
            
        # 获取文件扩展名并检查是否是临时文件
        _, file_extension = os.path.splitext(file_path)
        file_extension = file_extension.lower()
        file_name = os.path.basename(file_path)
        
        if file_extension == '.tmp' or file_extension == '.crdownload' or '.tmp' in file_name:
            logger.debug(f"忽略临时文件: {file_path}")
            return
            
        # 获取配置
        config = self.config_manager.get_config()
        rules = config.get('rules', [])
        default_target_folder = config.get('default_target_folder', '')
        
        # 查找匹配的规则
        target_folder = None
        category = None
        
        logger.info(f"处理新文件: {file_path}, 扩展名: {file_extension}")
        
        for rule in rules:
            if file_extension in rule.get('extensions', []):
                target_folder = rule.get('target_folder', '')
                category = rule.get('category', '')
                logger.debug(f"找到匹配规则: {category}, 目标文件夹: {target_folder}")
                break
        
        # 如果规则中的target_folder为空，但有category和default_target_folder，则使用默认目标文件夹下的子文件夹
        if not target_folder and category and default_target_folder:
            target_folder = os.path.join(default_target_folder, category)
            logger.debug(f"使用默认目标文件夹下的子文件夹: {target_folder}")
        
        # 如果没有找到匹配的规则，使用默认目标文件夹和扩展名作为分类
        if not target_folder and default_target_folder:
            target_folder = os.path.join(default_target_folder, file_extension[1:] if file_extension else 'other')
            category = file_extension[1:] if file_extension else 'other'
            logger.debug(f"使用扩展名作为分类: {category}, 目标文件夹: {target_folder}")
        
        # 如果找到了目标文件夹，移动文件
        if target_folder:
            try:
                # 再次检查文件是否存在
                if not os.path.exists(file_path):
                    logger.warning(f"文件不再存在，无法移动: {file_path}")
                    return
                    
                # 确保目标文件夹存在
                os.makedirs(target_folder, exist_ok=True)
                logger.debug(f"确保目标文件夹存在: {target_folder}")
                
                # 构建目标文件路径
                file_name = os.path.basename(file_path)
                target_file_path = os.path.join(target_folder, file_name)
                
                # 处理目标路径已存在的情况
                counter = 1
                while os.path.exists(target_file_path):
                    name, ext = os.path.splitext(file_name)
                    target_file_path = os.path.join(target_folder, f"{name}_{counter}{ext}")
                    counter += 1
                    logger.debug(f"目标文件已存在，重命名为: {os.path.basename(target_file_path)}")
                
                # 移动文件
                logger.info(f"移动文件: {file_path} -> {target_file_path}")
                shutil.move(file_path, target_file_path)
                
                # 发出信号，传递重命名后的文件路径和目标文件夹路径
                self.file_classified.emit(target_file_path, target_folder)
                logger.debug(f"文件分类完成，发出信号: {target_file_path}")
            except Exception as e:
                logger.error(f"移动文件 {file_path} 时出错: {str(e)}")
        else:
            logger.warning(f"未找到目标文件夹，文件 {file_path} 不会被移动")