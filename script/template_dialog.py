from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QTextEdit, QPushButton, QListWidget, QMessageBox)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtCore import Qt
import json
import os
from logger import logger

class TemplateDialog(QDialog):
    # 定义信号
    template_saved = pyqtSignal()
    
    def __init__(self, template_type, parent=None):
        super().__init__(parent)
        self.template_type = template_type  # 'prompt' 或 'output'
        self.templates = {}
        self.load_templates()
        
        # 设置窗口标题
        title = '提示词模板管理' if template_type == 'prompt' else '输出模板管理'
        self.setWindowTitle(title)
        self.setGeometry(200, 200, 600, 400)
        
        # 创建布局
        layout = QHBoxLayout(self)
        
        # 左侧模板列表
        left_layout = QVBoxLayout()
        self.template_list = QListWidget()
        self.template_list.currentItemChanged.connect(self.on_template_selected)
        left_layout.addWidget(QLabel('模板列表'))
        left_layout.addWidget(self.template_list)
        
        # 添加和删除按钮
        btn_layout = QHBoxLayout()
        add_btn = QPushButton('新建')
        add_btn.clicked.connect(self.add_template)
        delete_btn = QPushButton('删除')
        delete_btn.clicked.connect(self.delete_template)
        btn_layout.addWidget(add_btn)
        btn_layout.addWidget(delete_btn)
        left_layout.addLayout(btn_layout)
        
        # 右侧编辑区域
        right_layout = QVBoxLayout()
        
        # 模板标题
        self.title_edit = QLineEdit()
        right_layout.addWidget(QLabel('模板标题:'))
        right_layout.addWidget(self.title_edit)
        
        # 模板内容
        self.content_edit = QTextEdit()
        content_label = '提示词内容 (使用{original_text}表示需要替换的原文):' if template_type == 'prompt' else \
                        '输出格式 (使用{original_text}表示原文，{output_text}表示AI输出):'
        right_layout.addWidget(QLabel(content_label))
        right_layout.addWidget(self.content_edit)
        
        # 保存按钮
        save_btn = QPushButton('保存')
        save_btn.clicked.connect(self.save_template)
        right_layout.addWidget(save_btn)
        
        # 添加左右布局到主布局
        layout.addLayout(left_layout, 1)
        layout.addLayout(right_layout, 2)
        
        # 更新模板列表
        self.update_template_list()
    
    def load_templates(self):
        # 确保模板目录存在
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        os.makedirs(template_dir, exist_ok=True)
        
        # 模板文件路径
        template_file = os.path.join(template_dir, f'{self.template_type}_templates.json')
        
        # 如果文件存在，加载模板
        if os.path.exists(template_file):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    self.templates = json.load(f)
            except Exception as e:
                logger.error(f"加载模板文件时发生错误: {e}")
                self.templates = {}
    
    def save_templates(self):
        template_dir = os.path.join(os.path.dirname(__file__), 'templates')
        template_file = os.path.join(template_dir, f'{self.template_type}_templates.json')
        
        try:
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(self.templates, f, ensure_ascii=False, indent=2)
            logger.info(f"成功保存{self.template_type}模板")
        except Exception as e:
            logger.error(f"保存模板文件时发生错误: {e}")
    
    def update_template_list(self):
        self.template_list.clear()
        for title in self.templates.keys():
            self.template_list.addItem(title)
    
    def on_template_selected(self, current, previous):
        if current is None:
            self.title_edit.clear()
            self.content_edit.clear()
            return
        
        title = current.text()
        if title in self.templates:
            self.title_edit.setText(title)
            self.content_edit.setText(self.templates[title])
    
    def add_template(self):
        self.title_edit.clear()
        self.content_edit.clear()
        self.title_edit.setFocus()
    
    def delete_template(self):
        current = self.template_list.currentItem()
        if current is None:
            return
        
        title = current.text()
        reply = QMessageBox.question(self, '确认删除', f'确定要删除模板 "{title}" 吗？',
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            del self.templates[title]
            self.save_templates()
            self.update_template_list()
            self.title_edit.clear()
            self.content_edit.clear()
            # 发送模板已保存的信号
            self.template_saved.emit()
    
    def save_template(self):
        title = self.title_edit.text().strip()
        content = self.content_edit.toPlainText().strip()
        
        if not title or not content:
            QMessageBox.warning(self, '错误', '标题和内容不能为空！')
            return
        
        self.templates[title] = content
        self.save_templates()
        self.update_template_list()
        
        # 选中新保存的模板
        items = self.template_list.findItems(title, Qt.MatchFlag.MatchExactly)
        if items:
            self.template_list.setCurrentItem(items[0])
        
        QMessageBox.information(self, '成功', '模板保存成功！')
        # 发送模板已保存的信号
        self.template_saved.emit()