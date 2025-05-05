import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QTextEdit, QPushButton, QFileDialog, QComboBox,
                             QGroupBox, QRadioButton, QButtonGroup, QMessageBox)
from template_dialog import TemplateDialog
from PyQt6.QtCore import Qt
from auto_ask import chat_with_ollama
from logger import logger

class AutoAskGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('自动AI提问程序')
        self.setGeometry(100, 100, 800, 600)
        logger.info('启动自动AI提问程序')
        
        # 创建主窗口部件和布局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 提示词模板选择区
        prompt_group = QVBoxLayout()
        prompt_header = QHBoxLayout()
        prompt_label = QLabel('提示词模板:')
        self.prompt_combo = QComboBox()
        manage_prompt_btn = QPushButton('管理模板')
        manage_prompt_btn.clicked.connect(lambda: self.manage_templates('prompt'))
        prompt_header.addWidget(prompt_label)
        prompt_header.addWidget(self.prompt_combo)
        prompt_header.addWidget(manage_prompt_btn)
        self.prompt_edit = QTextEdit()
        self.prompt_edit.setReadOnly(True)
        prompt_group.addLayout(prompt_header)
        prompt_group.addWidget(self.prompt_edit)
        layout.addLayout(prompt_group)
        
        # Ollama服务器配置
        ollama_group = QVBoxLayout()
        
        # 服务器地址
        server_layout = QHBoxLayout()
        server_label = QLabel('Ollama服务器地址:')
        self.server_edit = QLineEdit('http://localhost:11434')
        server_layout.addWidget(server_label)
        server_layout.addWidget(self.server_edit)
        ollama_group.addLayout(server_layout)
        
        # 模型名称
        model_layout = QHBoxLayout()
        model_label = QLabel('模型名称:')
        self.model_edit = QLineEdit('gemma3:1b')
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_edit)
        ollama_group.addLayout(model_layout)
        
        layout.addLayout(ollama_group)
        
        # 输出格式模板选择区
        output_group = QVBoxLayout()
        output_header = QHBoxLayout()
        output_label = QLabel('输出格式模板:')
        self.output_combo = QComboBox()
        manage_output_btn = QPushButton('管理模板')
        manage_output_btn.clicked.connect(lambda: self.manage_templates('output'))
        output_header.addWidget(output_label)
        output_header.addWidget(self.output_combo)
        output_header.addWidget(manage_output_btn)
        self.output_edit = QTextEdit()
        self.output_edit.setReadOnly(True)
        output_group.addLayout(output_header)
        output_group.addWidget(self.output_edit)
        layout.addLayout(output_group)
        
        # 文件选择区域
        file_group = QVBoxLayout()
        
        # 输入文件选择
        input_file_layout = QHBoxLayout()
        self.input_file_path = QLineEdit()
        input_file_button = QPushButton('选择输入文件')
        input_file_button.clicked.connect(self.select_input_file)
        input_file_layout.addWidget(QLabel('输入文件:'))
        input_file_layout.addWidget(self.input_file_path)
        input_file_layout.addWidget(input_file_button)
        
        # 分隔符设置
        separator_group = QGroupBox('分隔符 (自定义分隔符支持正则表达式)')
        separator_layout = QHBoxLayout()
        
        # 单选按钮组
        self.separator_radio_group = QButtonGroup(self)
        self.newline_radio = QRadioButton('换行符')
        self.comma_radio = QRadioButton('逗号')
        self.period_radio = QRadioButton('句号')
        self.custom_radio = QRadioButton('其他')
        
        # 添加单选按钮到按钮组
        self.separator_radio_group.addButton(self.newline_radio)
        self.separator_radio_group.addButton(self.comma_radio)
        self.separator_radio_group.addButton(self.period_radio)
        self.separator_radio_group.addButton(self.custom_radio)
        
        # 自定义分隔符输入框
        self.custom_separator_edit = QLineEdit()
        self.custom_separator_edit.setMaximumWidth(100)
        self.custom_separator_edit.setEnabled(False)
        
        # 添加控件到布局
        separator_layout.addWidget(self.newline_radio)
        separator_layout.addWidget(self.comma_radio)
        separator_layout.addWidget(self.period_radio)
        separator_layout.addWidget(self.custom_radio)
        separator_layout.addWidget(self.custom_separator_edit)
        
        # 设置默认选中换行符
        self.newline_radio.setChecked(True)
        
        # 连接自定义选项的信号
        self.custom_radio.toggled.connect(self.toggle_custom_separator)
        
        separator_group.setLayout(separator_layout)
        file_group.addWidget(separator_group)
        
        # 输出文件选择
        output_file_layout = QHBoxLayout()
        output_file_layout.addWidget(QLabel('输出文件夹:'))
        self.output_dir_path = QLineEdit()
        self.output_dir_path.setReadOnly(True)
        output_file_layout.addWidget(self.output_dir_path)
        output_dir_button = QPushButton('选择文件夹')
        output_dir_button.clicked.connect(self.select_output_dir)
        output_file_layout.addWidget(output_dir_button)
        
        # 输出文件名
        output_filename_layout = QHBoxLayout()
        output_filename_layout.addWidget(QLabel('输出文件名:'))
        self.output_filename_edit = QLineEdit()
        self.output_filename_edit.setPlaceholderText('输入文件名 (无需.txt后缀)')
        output_filename_layout.addWidget(self.output_filename_edit)
        
        file_group.addLayout(input_file_layout)
        file_group.addLayout(separator_layout)
        file_group.addLayout(output_file_layout)
        file_group.addLayout(output_filename_layout)
        layout.addLayout(file_group)
        
        # 开始按钮
        start_button = QPushButton('开始处理')
        start_button.clicked.connect(self.start_processing)
        layout.addWidget(start_button)
        
        # 状态显示区域
        self.status_edit = QTextEdit()
        self.status_edit.setReadOnly(True)
        layout.addWidget(self.status_edit)
        
        # 加载模板
        self.load_templates()
    
    def select_input_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, '选择输入文件', '', 'Text Files (*.txt);;All Files (*)')
        if file_name:
            self.input_file_path.setText(file_name)
    
    def select_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, '选择输出文件夹')
        if dir_path:
            self.output_dir_path.setText(dir_path)
    
    def toggle_custom_separator(self, checked):
        self.custom_separator_edit.setEnabled(checked)
    
    def load_templates(self):
        """加载提示词和输出模板"""
        import os
        import json
        
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        os.makedirs(template_dir, exist_ok=True)
        
        # 加载提示词模板
        prompt_file = os.path.join(template_dir, 'prompt_templates.json')
        if os.path.exists(prompt_file):
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    templates = json.load(f)
                    self.prompt_combo.clear()
                    self.prompt_combo.addItems(templates.keys())
                    if templates:
                        self.prompt_edit.setText(list(templates.values())[0])
            except:
                pass
        
        # 加载输出模板
        output_file = os.path.join(template_dir, 'output_templates.json')
        if os.path.exists(output_file):
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    templates = json.load(f)
                    self.output_combo.clear()
                    self.output_combo.addItems(templates.keys())
                    if templates:
                        self.output_edit.setText(list(templates.values())[0])
            except:
                pass
        
        # 连接信号
        self.prompt_combo.currentTextChanged.connect(self.on_prompt_template_changed)
        self.output_combo.currentTextChanged.connect(self.on_output_template_changed)
    
    def on_prompt_template_changed(self, title):
        """当选择提示词模板时更新内容"""
        import os
        import json
        
        if not title:
            return
            
        template_file = os.path.join(os.path.dirname(__file__), 'templates', 'prompt_templates.json')
        if os.path.exists(template_file):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    templates = json.load(f)
                    if title in templates:
                        self.prompt_edit.setText(templates[title])
            except:
                pass
    
    def on_output_template_changed(self, title):
        """当选择输出模板时更新内容"""
        import os
        import json
        
        if not title:
            return
            
        template_file = os.path.join(os.path.dirname(__file__), 'templates', 'output_templates.json')
        if os.path.exists(template_file):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    templates = json.load(f)
                    if title in templates:
                        self.output_edit.setText(templates[title])
            except:
                pass
    
    def manage_templates(self, template_type):
        """打开模板管理对话框"""
        dialog = TemplateDialog(template_type, self)
        # 连接模板保存信号
        dialog.template_saved.connect(self.load_templates)
        dialog.exec()
    
    def start_processing(self):
        input_file = self.input_file_path.text()
        output_dir = self.output_dir_path.text()
        output_filename = self.output_filename_edit.text()
        
        if not output_filename:
            self.status_edit.append('错误：请输入输出文件名')
            return
            
        # 确保文件名以.txt结尾
        if not output_filename.endswith('.txt'):
            output_filename += '.txt'
            
        output_file = os.path.join(output_dir, output_filename)
        # 获取选中的分隔符
        if self.custom_radio.isChecked():
            separator = self.custom_separator_edit.text()
        else:
            if self.newline_radio.isChecked():
                separator = '\n'
            elif self.comma_radio.isChecked():
                separator = '[,，]'  # 同时支持中英文逗号
            elif self.period_radio.isChecked():
                separator = '。'
            else:
                separator = ''
        server_url = self.server_edit.text()
        model = self.model_edit.text()
        prompt_template = self.prompt_edit.toPlainText()
        output_template = self.output_edit.toPlainText()
        
        if not all([input_file, output_file, prompt_template, output_template]):
            self.status_edit.append('错误：请填写所有必要信息')
            return
        
        try:
            # 检查输入文件是否存在
            if not os.path.exists(input_file):
                QMessageBox.critical(self, '错误', '输入文件不存在，请检查文件路径！')
                return
                
            # 检查输出目录是否存在
            if not os.path.exists(output_dir):
                QMessageBox.critical(self, '错误', '输出目录不存在，请选择有效的输出目录！')
                return
            
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            import re
            # 如果指定了分隔符，按分隔符分割；否则按行分割
            if separator:
                try:
                    # 使用正则表达式分割
                    segments = re.split(separator, content)
                except re.error as e:
                    QMessageBox.critical(self, '错误', f'正则表达式格式错误：{str(e)}')
                    return
            else:
                segments = content.splitlines()
            
            with open(output_file, 'w', encoding='utf-8') as f:
                for segment in segments:
                    if not segment.strip():
                        continue
                    
                    # 构造提示词
                    prompt = prompt_template.replace('{original_text}', segment)
                    
                    # 调用AI模型
                    response = chat_with_ollama(prompt, model, server_url)
                    
                    if response:
                        # 构造输出结果
                        result = output_template.replace('{original_text}', segment).replace('{output_text}', response)
                        f.write(result + '\n')
                        self.status_edit.append(f'处理完成: {segment[:50]}...')
                    else:
                        # 显示Ollama连接错误提示
                        QMessageBox.warning(self, 'Ollama连接错误',
                            f'无法连接到Ollama服务器({server_url})，请检查：\n'
                            '1. Ollama服务是否已启动\n'
                            '2. 服务器地址是否正确\n'
                            '3. 网络连接是否正常\n'
                            '4. 防火墙设置是否允许连接')
                        return
            
            QMessageBox.information(self, '完成', '所有处理完成！')
            self.status_edit.append('所有处理完成！')
            
        except Exception as e:
            error_msg = str(e)
            self.status_edit.append(f'发生错误: {error_msg}')
            QMessageBox.critical(self, '错误', f'处理过程中发生错误：\n{error_msg}')

def main():
    app = QApplication(sys.argv)
    window = AutoAskGUI()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()