import os
import sys
from PyQt5.QtCore import QObject, pyqtSignal, QThread
from PyQt5.QtWidgets import QMessageBox

from file_watcher import FileWatcher
from logger import logger
from constants import APP_NAME

class MonitoringManager(QObject):
    """文件监听管理器，封装文件监听的核心功能，可被主程序和对话框页面调用"""
    
    # 定义信号
    monitoring_status_changed = pyqtSignal(bool)  # 监听状态变化信号，参数为是否正在监听
    file_classified_signal = pyqtSignal(str, str)  # 文件分类信号，参数为文件路径和目标文件夹
    
    def __init__(self, config_manager):
        super().__init__()
        self.config_manager = config_manager
        self.file_watcher = None
        self.watcher_thread = None
        logger.info("文件监听管理器初始化完成")
    
    def setup_file_watcher(self):
        """设置并启动文件监视器"""
        logger.info("设置文件监视器")
        config = self.config_manager.get_config()
        source_folder = config.get('source_folder', '')
        is_monitoring = config.get('is_monitoring', False)
        
        # 停止现有监视器
        self._stop_watcher_thread()
        
        if not is_monitoring:
            logger.debug("监听状态为关闭，不启动监视器")
            return

        if not source_folder or not os.path.isdir(source_folder):
            logger.warning(f"源文件夹无效: {source_folder}，无法启动监视器")
            return

        # 创建并启动新监视器
        self.file_watcher = FileWatcher(self.config_manager)
        self.file_watcher.file_classified.connect(self.file_classified_signal)
        
        self.watcher_thread = QThread()
        self.file_watcher.moveToThread(self.watcher_thread)
        self.watcher_thread.started.connect(self.file_watcher.start_monitoring)
        
        logger.info(f"启动文件监视器线程，监听文件夹: {source_folder}")
        self.watcher_thread.start()

    def _stop_watcher_thread(self):
        """停止文件监视器线程"""
        if self.file_watcher and self.watcher_thread and self.watcher_thread.isRunning():
            logger.info("停止现有的文件监视器")
            self.file_watcher.stop()
            self.watcher_thread.quit()
            self.watcher_thread.wait()

    def start_monitoring(self):
        """开始监听"""
        return self._set_monitoring_state(True)

    def stop_monitoring(self):
        """停止监听"""
        return self._set_monitoring_state(False)

    def toggle_monitoring(self, parent_widget=None):
        """切换监听状态
        
        Args:
            parent_widget: 父窗口部件，用于显示消息框，如果为None则使用None作为父窗口
        
        Returns:
            bool: 操作是否成功
        """
        logger.info("切换监听状态")
        config = self.config_manager.get_config()
        is_monitoring = config.get('is_monitoring', False)
        
        return self._set_monitoring_state(not is_monitoring)

    def exit(self):
        """程序退出时停止监听（不保存状态）"""
        self._stop_watcher_thread()
        self.monitoring_status_changed.emit(False)
        return True

    def _set_monitoring_state(self, enable):
        """设置监听状态的通用方法"""
        action = "开始" if enable else "停止"
        logger.info(f"{action}监听")
        
        config = self.config_manager.get_config()
        source_folder = config.get('source_folder', '')

        if enable and (not source_folder or not os.path.isdir(source_folder)):
            logger.warning("未设置有效的源文件夹，无法开始监听")
            return False
            
        if config.get('is_monitoring', False) == enable:
            logger.debug(f"当前已经是{action}状态，无需操作")
            return True

        # 更新配置
        config['is_monitoring'] = enable
        self.config_manager.save_config(config)
        
        # 应用变更
        self.setup_file_watcher()
        self.monitoring_status_changed.emit(enable)
        return True

    def get_monitoring_status(self):
        """获取当前监听状态"""
        return self.config_manager.get_config().get('is_monitoring', False)
    