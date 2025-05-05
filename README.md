# AutoAI问答助手

一个基于Ollama的本地AI问答工具，支持批量处理文本并生成AI回答。

## 功能特点

- 支持自定义提示词模板
- 支持自定义输出格式模板
- 支持多种文本分隔方式（换行符、逗号、句号等）
- 支持批量处理文本文件
- 使用本地Ollama模型，保护数据隐私

## 安装说明

### 1. 安装Ollama

请先安装Ollama并下载所需模型，访问[Ollama官网](https://ollama.ai)获取安装说明。

### 2. 运行程序

#### 方式一：直接运行

1. 安装Python 3.8或更高版本
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 运行程序：
   ```bash
   python script/auto_ask_gui.py
   ```

#### 方式二：使用打包版本

1. 从[Releases](https://github.com/你的用户名/autoai/releases)下载最新版本
2. 解压后直接运行`AutoAI问答助手.exe`

## 使用说明

1. 启动Ollama服务
2. 运行程序，配置Ollama服务器地址（默认为http://localhost:11434）
3. 选择或创建提示词模板
4. 选择或创建输出格式模板
5. 选择输入文本文件
6. 设置分隔符（默认为换行符）
7. 选择输出文件夹和文件名
8. 点击"开始处理"按钮

## 开发说明

### 打包程序

1. 安装PyInstaller：
   ```bash
   pip install pyinstaller
   ```

2. 执行打包命令：
   ```bash
   pyinstaller auto_ask.spec
   ```

打包后的程序位于`dist`文件夹中。

## 许可证

MIT License