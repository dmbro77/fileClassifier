# 麦悠 - 文件自动分类器

这是一个Windows桌面应用程序，能够实时监听指定文件夹中的新增文件，并根据文件后缀名自动将其分类到不同的目标文件夹中。
应用运行后会显示在系统托盘中，提供便捷的设置和管理界面。


## 使用场景
- 1、监听浏览器下载目录的文件，监测到有新文件，会自动转移到指定的目录中。
- 2、另一种用法，如果想将一堆文件进行分类，可以复制文件粘贴到被监听的目录，文件会被转移到指定的文件夹下

## 功能特点

- 实时监听指定文件夹中的新增文件
- 根据文件后缀名自动分类文件
- 支持自定义分类规则
- 系统托盘运行，不占用桌面空间
- 文件分类完成后显示通知
- 点击通知可直接打开目标文件夹并定位文件
- 支持开机自动启动
- 支持日志记录

## 预览

![设置界面](https://github.com/D2073620106/fileClassifier/blob/master/preview/1.png?raw=true)
![分类规则界面](https://github.com/D2073620106/fileClassifier/blob/master/preview/2.png?raw=true)
![系统托盘界面](https://github.com/D2073620106/fileClassifier/blob/master/preview/3.png?raw=true)

## 安装要求

- Windows 10/11 操作系统
- Python 3.6 或更高版本
- PyQt5 库
- Watchdog 库

## 安装步骤

### 方法一：直接下载可执行文件

1. 在 [Releases](https://github.com/D2073620106/fileClassifier/releases) 页面下载最新版本的可执行文件
2. 下载后直接运行 `FileClassifier.exe`

### 方法二：从源码安装

1. 确保已安装 Python 3.6 或更高版本
2. 克隆本仓库：
   ```
   git clone https://github.com/D2073620106/fileClassifier.git
   cd fileClassifier
   ```
3. 安装所需的依赖库：
   ```
   pip -m venv .venv
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. 运行应用程序：
   ```
   python main.py
   ```
5. 打包引用程序
   ```
   .\build_exe.bat
   ```


## 使用方法

1. 运行应用程序后，它将在系统托盘中显示图标
2. 右键点击托盘图标可以访问菜单
3. 首次使用时，请点击「文件夹设置」配置要监听的源文件夹和默认分类文件夹
4. 点击「规则设置」可以自定义文件分类规则
5. 设置完成后，点击「开启监听」开始监听文件夹
6. 当有新文件添加到监听文件夹时，应用程序会自动将其移动到对应的分类文件夹

## 配置说明

### 设置

- **监听文件夹**：应用程序将监听此文件夹中的新增文件
- **默认分类文件夹**：当没有匹配的分类规则时，文件将被移动到此文件夹下的子文件夹中
- **开机自动启动**：设置应用程序是否在系统启动时自动运行
- **显示通知**：设置是否在文件分类完成后显示通知
- **是否开启监听**：设置是否启用文件分类功能

### 规则设置

每条规则包含以下信息：

- **分类名称**：规则的名称
- **文件扩展名**：要匹配的文件扩展名列表，用逗号分隔
- **目标文件夹**：匹配的文件将被移动到此文件夹

## 项目结构

```
├── src/                 # 源代码目录
│   ├── main.py          # 主应用程序入口
│   ├── file_watcher.py  # 文件监视器逻辑
│   ├── config_manager.py # 配置管理逻辑
│   ├── settings_dialog.py # 设置界面 UI
│   ├── monitoring_manager.py # 监听状态管理
│   ├── notification_handler.py # 通知处理
│   ├── startup_manager.py # 开机自启动管理
│   ├── constants.py     # 常量定义
│   ├── logger.py        # 日志记录模块
│   └── icon.png         # 应用图标
├── preview/             # 项目预览截图
├── .gitignore           # Git 忽略文件配置
├── build_exe.bat        # Windows 可执行文件打包脚本
├── LICENSE              # 项目许可证
├── README.md            # 项目说明文档
└── requirements.txt     # 项目依赖列表
```


## 注意事项

- 如果目标文件夹中已存在同名文件，新文件将被重命名
- 监听大型文件夹可能会增加系统资源使用,目前没有测试过大型文件
- 目前只在windows系统上测试过，其他系统未测试，不知能否运行

## 故障排除

如果应用程序无法正常工作，请检查：

1. 确保已正确设置源文件夹和目标文件夹
2. 确保应用程序有足够的权限访问这些文件夹
3. 检查配置文件 `config.json` 是否损坏
4. 查看应用程序日志输出
5. 尝试重新启动应用程序


## 许可证

本项目采用 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。

## 联系方式

如有任何问题或建议，请通过 GitHub Issues 与我们联系。