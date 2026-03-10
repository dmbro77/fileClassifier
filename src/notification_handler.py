import os
import subprocess
import shlex
from PyQt5.QtCore import QObject
from logger import logger

class NotificationHandler(QObject):
    """处理通知相关的功能，包括点击通知打开目标文件所在文件夹并选中文件"""
    def __init__(self):
        super().__init__()
        self.last_classified_file = None
        self.last_target_folder = None
    
    def store_classified_file_info(self, file_path, target_folder):
        """存储最近一次分类的文件信息"""
        self.last_classified_file = file_path
        self.last_target_folder = target_folder
        logger.debug(f"存储分类信息: {file_path}")
    
    def open_folder_and_select_file(self):
        """打开目标文件夹并选中文件"""
        if not self.last_classified_file:
            return False
        
        # 规范化路径，Windows 下使用反斜杠
        target_file_path = os.path.normpath(self.last_classified_file)
        
        if os.path.exists(target_file_path):
            try:
                # Windows 下 explorer /select,filename
                # 注意：路径中可能包含空格，subprocess.run 在 Windows 下处理列表参数时会自动转义
                # 但 explorer 的 /select 参数比较特殊，有时候列表形式会有问题
                # 尝试使用字符串形式的命令，并手动处理引号
                
                logger.info(f"尝试定位文件: {target_file_path}")
                
                # 使用 os.startfile 无法直接选中文件，只能打开文件夹
                # 使用 subprocess 调用 explorer
                # 注意：explorer /select,"C:\path\to\file with spaces.txt"
                
                cmd = f'explorer /select,"{target_file_path}"'
                subprocess.Popen(cmd, shell=True)
                
                logger.info(f"成功执行打开文件命令: {target_file_path}")
                return True
            except Exception as e:
                logger.error(f"打开文件夹失败: {str(e)}")
        else:
            logger.warning(f"文件不存在，无法定位: {target_file_path}")
            
        return False
