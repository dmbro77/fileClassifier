import sys
import os
import time
import ctypes
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction, QMessageBox, QStyle
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QObject, pyqtSignal

from config_manager import ConfigManager
from settings_dialog import SettingsDialog
from notification_handler import NotificationHandler
from logger import logger
from monitoring_manager import MonitoringManager
from constants import APP_NAME
from startup_manager import update_startup_status, is_in_startup

class FileClassifierApp(QObject):
    def __init__(self):
        super().__init__()
        logger.info(f"{APP_NAME} 启动")
        
        # 设置 App User Model ID，以确保在 Windows 上显示通知
        try:
            myappid = APP_NAME
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        except Exception as e:
            logger.warning(f"无法设置 App User Model ID: {e}")

        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        self.config_manager = ConfigManager()
        self.notification_handler = NotificationHandler()
        self.monitoring_manager = MonitoringManager(self.config_manager)
        
        self._last_click_time = 0  # 用于托盘点击去抖动
        
        self._setup_signals()
        self._sync_auto_start()
        self._setup_tray()
        
        self.monitoring_manager.setup_file_watcher()
        logger.info("初始化完成")

    def _setup_signals(self):
        """连接信号"""
        self.monitoring_manager.monitoring_status_changed.connect(self.update_menu_state)
        self.monitoring_manager.file_classified_signal.connect(self.on_file_classified)

    def _sync_auto_start(self):
        """同步自启动状态"""
        config = self.config_manager.get_config()
        cfg_start = config.get('auto_start', False)
        actual_start = is_in_startup()
        
        if cfg_start != actual_start:
            if cfg_start:
                if not update_startup_status(True):
                    config['auto_start'] = False
                    self.config_manager.save_config(config)
            else:
                config['auto_start'] = actual_start
                self.config_manager.save_config(config)

    def _setup_tray(self):
        """初始化托盘"""
        self.tray_icon = QSystemTrayIcon(self.app)
        self.tray_icon.setToolTip(APP_NAME)
        
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.png')
        icon = QIcon(icon_path) if os.path.exists(icon_path) else self.app.style().standardIcon(QStyle.SP_FileIcon)
        self.tray_icon.setIcon(icon)
        
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.messageClicked.connect(self.on_notification_clicked)
        
        self._create_menu()
        self.tray_icon.show()
        self.update_menu_state()

    def _create_menu(self):
        """创建托盘菜单"""
        self.tray_menu = QMenu()
            # 打开分类文件夹
        self.open_classify_action = QAction('打开分类文件夹', self)
        self.open_classify_action.triggered.connect(self.open_target_folder)
        self.tray_menu.addAction(self.open_classify_action)

        # 打开监听文件夹
        self.open_monitor_action = QAction('打开监听文件夹', self)
        self.open_monitor_action.triggered.connect(self.open_source_folder)
        self.tray_menu.addAction(self.open_monitor_action)
        
        self.tray_menu.addSeparator()

        self.settings_action = QAction('设置', self)
        self.settings_action.triggered.connect(self.open_folder_settings)
        self.tray_menu.addAction(self.settings_action)
        
        self.log_action = QAction('查看日志', self)
        self.log_action.triggered.connect(self.open_log_file)
        self.tray_menu.addAction(self.log_action)
        
        self.tray_menu.addSeparator()

        self.exit_action = QAction('退出', self)
        self.exit_action.triggered.connect(self.exit_app)
        self.tray_menu.addAction(self.exit_action)
        
        self.tray_icon.setContextMenu(self.tray_menu)


    def open_path(self, path):
        """通用打开路径方法"""
        if not path:
            return
            
        if not os.path.exists(path):
            try: os.makedirs(path, exist_ok=True)
            except: return
        
        logger.info(f"打开路径: {path}")
        if sys.platform == 'win32': os.startfile(path)
        # 其他平台的实现略...

    def open_log_file(self):
        from constants import LOG_FILE
        log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'log', LOG_FILE)
        if os.path.exists(log_path): self.open_path(log_path)
        else: QMessageBox.information(None, APP_NAME, '日志文件尚未创建')

    def open_folder_settings(self):
        if SettingsDialog(self.config_manager, self.monitoring_manager).exec_():
            self.monitoring_manager.setup_file_watcher()
            self.update_menu_state()

    def open_source_folder(self):
        """打开监听文件夹"""
        config = self.config_manager.get_config()
        self.open_path(config.get('source_folder'))

    def open_target_folder(self):
        """打开分类文件夹"""
        config = self.config_manager.get_config()
        self.open_path(config.get('default_target_folder'))


    def update_menu_state(self):
        is_monitoring = self.config_manager.get_config().get('is_monitoring', False)
        self.tray_icon.setToolTip(f"{APP_NAME} ({'监听中' if is_monitoring else '监听未开启'})")

    def on_file_classified(self, file_path, target_folder):
        logger.info(f"收到文件分类信号: {file_path} -> {target_folder}")
        self.notification_handler.store_classified_file_info(file_path, target_folder)
        
        config = self.config_manager.get_config()
        if config.get('show_notifications', True):
            self.tray_icon.showMessage(
                f"分类成功",
                f"文件 {os.path.basename(file_path)} 已移动",
                QSystemTrayIcon.Information, 
                2000
            )

    def on_notification_clicked(self):
        self.notification_handler.open_folder_and_select_file()

    def on_tray_icon_activated(self, reason):
        # 增加简单的去抖动处理
        current_time = time.time()
        
        # 如果距离上次点击不足 1 秒，则忽略
        if (current_time - self._last_click_time < 0.5):
            return
            
        self._last_click_time = current_time
        
        # 只处理单击事件，Trigger
        if reason == QSystemTrayIcon.Trigger:
            logger.info("托盘图标被点击")
            
            # 优先尝试定位最新文件
            if self.notification_handler.open_folder_and_select_file():
                return
                
            # 如果没有最新文件，打开源文件夹
            src = self.config_manager.get_config().get('source_folder')
            if src and os.path.isdir(src):
                self.open_path(src)
            else:
                self.open_folder_settings()

    def exit_app(self):
        self.monitoring_manager.exit()
        self.tray_icon.hide()
        self.app.quit()

def main():
    app = FileClassifierApp()
    sys.exit(app.app.exec_())

if __name__ == '__main__':
    main()
