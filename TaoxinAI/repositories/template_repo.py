from pathlib import Path
import yaml
from typing import Dict, Any

class TemplateRepository:
    """Reads local text and yaml templates used by the reasoning flow."""

    def __init__(self, root: Path):
        self.root = root

    def get_yaml_template(self, category: str, template_name: str) -> Dict[str, Any]:
        """
        读取 YAML 格式的结构化模板 
        用法示例: get_yaml_template('labor', 'issue_templates')
        """
        file_path = self.root / category / f"{template_name}.yaml"
        if not file_path.exists():
            print(f"⚠️ 警告: 找不到 YAML 模板文件 {file_path}")
            return {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}

    def get_text_prompt(self, category: str, prompt_name: str) -> str:
        """
        读取纯文本格式的 Prompt 模板
        用法示例: get_text_prompt('labor', 'irac_prompt')
        """
        file_path = self.root / category / f"{prompt_name}.txt"
        if not file_path.exists():
            print(f"⚠️ 警告: 找不到文本模板文件 {file_path}")
            return ""
            
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
