import pytest
from TaoxinAI.services.intake.normalizer import IntakeNormalizer
from TaoxinAI.services.intake.entity_extractor import EntityExtractor

class TestIntakeNormalizer:
    """测试文本预处理清洗功能"""
    
    def test_normalize_whitespace(self):
        normalizer = IntakeNormalizer()
        # 模拟用户输入时带了多余的空格、换行和制表符
        raw_text = "  老板   拖欠了我 \n \t 5000元  "
        clean_text = normalizer.normalize(raw_text)
        
        assert clean_text == "老板 拖欠了我 5000元", "Normalizer 未能正确清理多余的空白字符"

class TestEntityExtractor:
    """测试前台线索抽取功能"""
    
    def setup_method(self):
        """每个测试用例前都会执行，初始化抽取器"""
        self.extractor = EntityExtractor()

    def test_extract_amount(self):
        """测试金额提取（整数和小数）"""
        res1 = self.extractor.extract("欠了我5000块不给")
        assert res1.get("amount") == "5000块"
        
        res2 = self.extractor.extract("少发了 3500.50 元")
        assert res2.get("amount") == "3500.50元"

    def test_extract_employer_type(self):
        """测试用工主体类型的分类"""
        res_company = self.extractor.extract("我在建筑公司上班")
        assert res_company.get("employer_type") == "company"
        
        res_contractor = self.extractor.extract("跟着包工头干活")
        assert res_contractor.get("employer_type") == "contractor_or_employer"

    def test_extract_contract_status_with_negation(self):
        """测试合同状态及基础的否定判断逻辑"""
        res_has = self.extractor.extract("我们签了书面合同")
        assert res_has.get("has_contract") == "有"
        
        res_not_has = self.extractor.extract("当时没签劳动合同啊")
        assert res_not_has.get("has_contract") == "没有", "未能正确识别'没'字导致的否定语态"

    def test_extract_multiple_evidences(self):
        """测试多种证据的串联提取"""
        res = self.extractor.extract("我手里有微信聊天记录，还有他给我写的欠条，但是没有打卡记录。")
        evidence = res.get("evidence_types", "")
        
        assert "聊天记录" in evidence
        assert "欠条" in evidence
        assert "结算单" not in evidence

    def test_extract_empty_results(self):
        """测试防呆边界：完全没有命中任何规则时，应返回空字典或不含关键key"""
        res = self.extractor.extract("太欺负人了，我要告他！")
        
        assert "amount" not in res
        assert "employer_type" not in res
        assert "has_contract" not in res
        assert "evidence_types" not in res
