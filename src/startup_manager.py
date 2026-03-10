import os
import sys
import winreg
from logger import logger

def get_app_path():
    """获取应用程序路径"""
    if getattr(sys, 'frozen', False):
        return os.path.abspath(sys.executable)
    return os.path.abspath(sys.argv[0])

def _get_run_key(access=winreg.KEY_READ):
    """获取 Windows 启动项注册表键"""
    return winreg.OpenKey(
        winreg.HKEY_CURRENT_USER, 
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", 
        0, 
        access
    )

def add_to_startup():
    """添加程序到开机启动项"""
    try:
        app_path = get_app_path()
        with _get_run_key(winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "FileClassifier", 0, winreg.REG_SZ, app_path)
        logger.info(f"已添加到开机启动: {app_path}")
        return True
    except Exception as e:
        logger.error(f"添加到开机启动项失败: {str(e)}")
        return False

def remove_from_startup():
    """从开机启动项中移除程序"""
    try:
        with _get_run_key(winreg.KEY_SET_VALUE) as key:
            try:
                winreg.DeleteValue(key, "FileClassifier")
            except FileNotFoundError:
                pass
        logger.info("已从开机启动中移除")
        return True
    except Exception as e:
        logger.error(f"从开机启动项移除失败: {str(e)}")
        return False

def is_in_startup():
    """检查程序是否在开机启动项中"""
    try:
        with _get_run_key(winreg.KEY_READ) as key:
            try:
                winreg.QueryValueEx(key, "FileClassifier")
                return True
            except FileNotFoundError:
                return False
    except Exception as e:
        logger.error(f"检查开机启动项失败: {str(e)}")
        return False

def update_startup_status(auto_start):
    """根据配置更新开机启动状态"""
    return add_to_startup() if auto_start else remove_from_startup()
