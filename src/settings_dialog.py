import os
import json
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QCheckBox, QFileDialog, QMessageBox, 
                             QDialogButtonBox, QGroupBox, QWidget, QTabWidget,
                             QPlainTextEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# 导入软件名称常量
from constants import APP_NAME

# 导入开机自启动管理模块
from startup_manager import update_startup_status, is_in_startup

# 导入监听管理器
from monitoring_manager import MonitoringManager

class SettingsDialog(QDialog):
    def __init__(self, config_manager, monitoring_manager=None):
        super().__init__()
        # 移除问号按钮
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        self.config_manager = config_manager
        self.config = self.config_manager.get_config()
        
        # 使用传入的监听管理器或创建新的实例
        if monitoring_manager is None:
            raise ValueError("MonitoringManager instance is required.")
        
        self.monitoring_manager = monitoring_manager
       
        # 设置窗口图标
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icon.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle(f'{APP_NAME}')
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)
        
        # 主布局
        main_layout = QVBoxLayout()
        
        # 创建选项卡控件
        self.tab_widget = QTabWidget()
        
        # 创建基本设置页
        self.basic_tab = QWidget()
        self.init_basic_tab()
        self.tab_widget.addTab(self.basic_tab, "基本设置")
        
        # 创建规则设置页
        self.rules_tab = QWidget()
        self.init_rules_tab()
        self.tab_widget.addTab(self.rules_tab, "规则设置")
        
        # 添加选项卡到主布局
        main_layout.addWidget(self.tab_widget)
        
        # 底部按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # 获取按钮并修改文本
        ok_button = button_box.button(QDialogButtonBox.Ok)
        cancel_button = button_box.button(QDialogButtonBox.Cancel)
        ok_button.setText('确定')
        cancel_button.setText('取消')
        
        main_layout.addWidget(button_box)
        
        self.setLayout(main_layout)
    
    def init_basic_tab(self):
        layout = QVBoxLayout()
        
        # 源文件夹设置
        source_group = QGroupBox('监听文件夹设置')
        source_layout = QHBoxLayout()
        
        self.source_folder_edit = QLineEdit(self.config.get('source_folder', ''))
        self.source_folder_edit.setReadOnly(True)
        
        browse_source_btn = QPushButton('浏览...')
        browse_source_btn.clicked.connect(self.browse_source_folder)
        
        source_layout.addWidget(self.source_folder_edit)
        source_layout.addWidget(browse_source_btn)
        source_group.setLayout(source_layout)
        
        # 目标文件夹设置
        target_group = QGroupBox('默认分类文件夹设置')
        target_layout = QHBoxLayout()
        
        self.target_folder_edit = QLineEdit(self.config.get('default_target_folder', ''))
        self.target_folder_edit.setReadOnly(True)
        
        browse_target_btn = QPushButton('浏览...')
        browse_target_btn.clicked.connect(self.browse_target_folder)
        
        target_layout.addWidget(self.target_folder_edit)
        target_layout.addWidget(browse_target_btn)
        target_group.setLayout(target_layout)
        
        # 其他设置
        options_group = QGroupBox('其他设置')
        options_layout = QVBoxLayout()
        
        # 检查实际的开机自启动状态
        actual_auto_start = is_in_startup()
        # 如果配置和实际状态不一致，以实际状态为准
        if self.config.get('auto_start', False) != actual_auto_start:
            self.config['auto_start'] = actual_auto_start
            self.config_manager.save_config(self.config)
        
        self.auto_start_checkbox = QCheckBox('开机自动启动')
        self.auto_start_checkbox.setChecked(self.config.get('auto_start', False))
        
        self.show_notifications_checkbox = QCheckBox('显示分类通知')
        self.show_notifications_checkbox.setChecked(self.config.get('show_notifications', True))
        
        self.monitoring_checkbox = QCheckBox('开启文件监听')
        self.monitoring_checkbox.setChecked(self.config.get('is_monitoring', False))
        
        options_layout.addWidget(self.auto_start_checkbox)
        options_layout.addWidget(self.show_notifications_checkbox)
        options_layout.addWidget(self.monitoring_checkbox)
        options_group.setLayout(options_layout)
        
        # 添加组件到布局
        layout.addWidget(source_group)
        layout.addWidget(target_group)
        layout.addWidget(options_group)
        layout.addStretch()
        
        self.basic_tab.setLayout(layout)
        
    def init_rules_tab(self):
        layout = QVBoxLayout()
        
        # 说明标签
        # info_label = QLabel("请在下方输入 JSON 格式的分类规则配置：\n"
        #                    "格式示例：\n"
        #                    "[\n"
        #                    "  {\n"
        #                    "    \"category\": \"图片\",\n"
        #                    "    \"extensions\": [\".jpg\", \".png\"],\n"
        #                    "    \"target_folder\": \"D:/Images\" (可选)\n"
        #                    "  }\n"
        #                    "]")
        # layout.addWidget(info_label)
        
        # JSON 编辑框
        self.json_edit = QPlainTextEdit()
        # 设置等宽字体
        font = self.json_edit.font()
        font.setFamily("Consolas")
        font.setStyleHint(font.Monospace)
        self.json_edit.setFont(font)
        
        # 加载现有规则
        rules = self.config.get('rules', [])
        try:
            json_str = json.dumps(rules, indent=2, ensure_ascii=False)
            self.json_edit.setPlainText(json_str)
        except Exception as e:
            self.json_edit.setPlainText("[]")
            
        layout.addWidget(self.json_edit)
        
        # 格式化按钮
        format_btn = QPushButton("格式化 JSON")
        format_btn.clicked.connect(self.format_json)
        layout.addWidget(format_btn)
        
        self.rules_tab.setLayout(layout)
    
    def browse_source_folder(self):
        folder = QFileDialog.getExistingDirectory(self, f'{APP_NAME} - 选择监听文件夹', self.source_folder_edit.text())
        if folder:
            self.source_folder_edit.setText(folder)
    
    def browse_target_folder(self):
        folder = QFileDialog.getExistingDirectory(self, f'{APP_NAME} - 选择默认分类文件夹', self.target_folder_edit.text())
        if folder:
            self.target_folder_edit.setText(folder)
    
    def format_json(self):
        """格式化 JSON 内容"""
        try:
            text = self.json_edit.toPlainText()
            if not text.strip():
                self.json_edit.setPlainText("[]")
                return
                
            data = json.loads(text)
            formatted_json = json.dumps(data, indent=2, ensure_ascii=False)
            self.json_edit.setPlainText(formatted_json)
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, f'{APP_NAME} - 错误', f'JSON 格式错误：\n{str(e)}')
            
    def accept(self):
        # 验证基本设置
        source_folder = self.source_folder_edit.text()
        target_folder = self.target_folder_edit.text()
        
        if not source_folder:
            QMessageBox.warning(self, f'{APP_NAME} - 警告', '请选择要监听的源文件夹！')
            # 切换到基本设置页
            self.tab_widget.setCurrentIndex(0)
            return
            
        # 验证并解析 JSON 规则
        try:
            json_text = self.json_edit.toPlainText()
            if not json_text.strip():
                rules = []
            else:
                rules = json.loads(json_text)
                
            if not isinstance(rules, list):
                raise ValueError("规则必须是一个列表")
                
            # 简单的结构验证
            for rule in rules:
                if not isinstance(rule, dict):
                    raise ValueError("规则列表中的每一项必须是对象")
                if 'category' not in rule:
                    raise ValueError("每条规则必须包含 'category' 字段")
                if 'extensions' not in rule:
                    raise ValueError("每条规则必须包含 'extensions' 字段")
                    
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, f'{APP_NAME} - 错误', f'规则配置 JSON 格式错误：\n{str(e)}')
            # 切换到规则设置页
            self.tab_widget.setCurrentIndex(1)
            return
        except ValueError as e:
            QMessageBox.warning(self, f'{APP_NAME} - 错误', f'规则配置格式错误：\n{str(e)}')
            # 切换到规则设置页
            self.tab_widget.setCurrentIndex(1)
            return
        
        # 获取开机自启动设置
        auto_start = self.auto_start_checkbox.isChecked()
        
        # 更新配置
        self.config['source_folder'] = source_folder
        self.config['default_target_folder'] = target_folder
        self.config['auto_start'] = auto_start
        self.config['show_notifications'] = self.show_notifications_checkbox.isChecked()
        self.config['is_monitoring'] = self.monitoring_checkbox.isChecked()
        self.config['rules'] = rules
        
        # 更新开机自启动状态
        update_result = update_startup_status(auto_start)
        if not update_result:
            QMessageBox.warning(self, f'{APP_NAME} - 警告', '更新开机自启动设置失败，可能需要管理员权限。')
            # 将配置中的auto_start设置为实际状态
            self.config['auto_start'] = is_in_startup()
        
        # 保存配置
        if self.config_manager.save_config(self.config):
            super().accept()
        else:
            QMessageBox.critical(self, f'{APP_NAME} - 错误', '保存配置失败！')
