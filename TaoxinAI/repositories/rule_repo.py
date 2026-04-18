from pathlib import Path
import yaml
from typing import Dict, Any

class RuleRepository:
    """Reads local rule configuration files."""

    def __init__(self, root: Path):
        self.root = root
        
    def get_rules(self, category: str, rule_type: str) -> Dict[str, Any]:
        """
        获取指定类别的规则配置。
        用法示例: get_rules('labor', 'verification_rules') 
        将读取 root/labor/verification_rules.yaml
        """
        file_path = self.root / category / f"{rule_type}.yaml"
        if not file_path.exists():
            print(f"⚠️ 警告: 找不到规则文件 {file_path}")
            return {}
            
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
