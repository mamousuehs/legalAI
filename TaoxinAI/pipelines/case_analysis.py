from __future__ import annotations

from typing import Any
from pathlib import Path

from TaoxinAI.schemas.intake import CaseInput
from TaoxinAI.schemas.reasoning import (
    AnalysisResponse,
    DocumentGenerationRequest,
    DocumentGenerationResponse,
    FullAnalysisResponse,
)
from TaoxinAI.schemas.retrieval import RetrievedAuthority
from TaoxinAI.repositories.chroma_repo import ChromaRepository
from TaoxinAI.services.fact.rule_based_extractor import RuleBasedFactExtractor
from TaoxinAI.services.intake.entity_extractor import EntityExtractor
from TaoxinAI.services.intake.normalizer import IntakeNormalizer
from TaoxinAI.services.issue.rule_based_identifier import RuleBasedIssueIdentifier
from TaoxinAI.services.matching.element_matcher import ElementMatcher
from TaoxinAI.services.reasoning.irac_generator import IRACGenerator
from TaoxinAI.services.reasoning.reason_builder import ReasonBuilder
from TaoxinAI.services.retrieval.case_retriever import CaseRetriever
from TaoxinAI.services.retrieval.law_retriever import LawRetriever
from TaoxinAI.services.retrieval.reranker import Reranker
from TaoxinAI.services.retrieval.template_retriever import TemplateRetriever
from TaoxinAI.services.verification.completeness_checker import CompletenessChecker


class CaseAnalysisPipeline:
    """High-level workflow for the wage-recovery reasoning prototype."""

    def __init__(self, collection: Any, llm_client: Any):
        self.collection = collection
        self.llm_client = llm_client
        self.intake_normalizer = IntakeNormalizer()
        self.entity_extractor = EntityExtractor()
        self.chroma_repo = ChromaRepository(collection)
        template_root = Path(__file__).resolve().parents[1] / "templates" / "taoxin"
        self.law_retriever = LawRetriever(self.chroma_repo)
        self.case_retriever = CaseRetriever(self.chroma_repo)
        self.template_retriever = TemplateRetriever(template_root)
        self.reranker = Reranker()
        self.issue_identifier = RuleBasedIssueIdentifier()
        self.fact_extractor = RuleBasedFactExtractor()
        self.element_matcher = ElementMatcher()
        self.reason_builder = ReasonBuilder()
        self.irac_generator = IRACGenerator()
        self.completeness_checker = CompletenessChecker()

    async def analyze_chat_turn(self, case_input: CaseInput) -> AnalysisResponse:
        query_text = self.intake_normalizer.normalize(self._get_last_user_message(case_input))
        retrieved = self._retrieve_authorities(query_text)
        stage = case_input.extracted_info.get("_stage", "initial")
        next_stage, reply, quick_replies = self._chat_flow(stage)

        extracted_info = dict(case_input.extracted_info)
        extracted_info["_stage"] = next_stage
        extracted_info.update(self.entity_extractor.extract(query_text))

        if "公司" in query_text or "单位" in query_text:
            extracted_info["employer_type"] = "company"
        elif "包工头" in query_text or "老板" in query_text:
            extracted_info["employer_type"] = "contractor_or_employer"

        if "合同" in query_text:
            extracted_info["has_contract"] = "有" if "没" not in query_text else "没有"

        issues = self.issue_identifier.identify(case_input, retrieved)
        can_generate_doc = bool(
            extracted_info.get("employer_type") and extracted_info.get("has_contract")
        )

        return AnalysisResponse(
            reply=reply,
            quick_replies=quick_replies,
            conversation_stage=next_stage,
            extracted_info=extracted_info,
            retrieved_authorities=retrieved,
            issues=issues,
            facts=[],
            element_matches=[],
            reasoning_summary={},
            verification={},
            can_generate_doc=can_generate_doc,
        )

    async def run_full_analysis(self, case_input: CaseInput) -> FullAnalysisResponse:
        query_text = self.intake_normalizer.normalize(self._get_last_user_message(case_input))
        retrieved = self._retrieve_authorities(query_text)
        issues = self.issue_identifier.identify(case_input, retrieved)
        facts = self.fact_extractor.extract(case_input, issues)
        matches = self.element_matcher.match(issues, facts, retrieved)
        reasons = self.reason_builder.build(issues, matches)
        irac = self.irac_generator.generate(issues, matches, reasons, retrieved)
        verification = self.completeness_checker.check(issues, matches, irac)

        return FullAnalysisResponse(
            case_summary=query_text,
            retrieved_authorities=retrieved,
            issues=issues,
            facts=facts,
            element_matches=matches,
            reason_bundles=reasons,
            irac_drafts=irac,
            verification=verification,
        )

    async def generate_document(
        self,
        payload: DocumentGenerationRequest,
    ) -> DocumentGenerationResponse:
        analysis = payload.analysis
        extracted = payload.case_input.extracted_info
        amount = extracted.get("amount") or "待补充"
        employer = extracted.get("employer_name") or extracted.get("employer_type") or "被申请人"
        worker = extracted.get("worker_name") or "申请人"

        document = (
            f"劳动维权申请书\n\n"
            f"申请人：{worker}\n"
            f"被申请人：{employer}\n\n"
            f"申请事项：请求支付拖欠工资 {amount}。\n\n"
            f"事实与理由：\n"
            f"{analysis.irac_drafts[0].application if analysis.irac_drafts else '目前已完成基础案件分析，后续将补充完整 IRAC 论证。'}\n"
        )

        risk_notes = list(analysis.verification.consistency_warnings)
        if not risk_notes:
            risk_notes.append("当前文书为骨架版本，仍需补充金额、时间和证据细节。")

        citations = analysis.irac_drafts[0].citations if analysis.irac_drafts else []

        return DocumentGenerationResponse(
            document=document,
            citations=citations,
            risk_notes=risk_notes,
        )

    def _get_last_user_message(self, case_input: CaseInput) -> str:
        for message in reversed(case_input.messages):
            if message.role == "user":
                return message.content
        return ""

    def _retrieve_authorities(self, query_text: str) -> list[RetrievedAuthority]:
        if not query_text:
            return []

        retrieved = []
        retrieved.extend(self.law_retriever.retrieve(query_text, n_results=4))
        retrieved.extend(self.case_retriever.retrieve(query_text, n_results=4))
        retrieved.extend(self.template_retriever.retrieve(query_text, n_results=2))
        return self.reranker.rerank(retrieved)[:6]

    def _chat_flow(self, stage: str) -> tuple[str, str, list[str]]:
        if stage == "initial":
            return (
                "basic_facts",
                "请先告诉我几个基础事实：您是给公司干活，还是给包工头/老板干活？有没有签合同？",
                ["给公司干活", "给包工头干活", "有合同", "没有合同"],
            )

        if stage == "basic_facts":
            return (
                "evidence_check",
                "我还需要确认证据情况。您目前有没有工资结算单、聊天记录、考勤记录或者转账记录？",
                ["有聊天记录", "有转账记录", "有考勤记录", "暂时没有"],
            )

        return (
            "analysis_ready",
            "基础信息已经记录。下一步可以进入完整分析，输出争点、要件匹配和文书草稿。",
            ["开始完整分析", "继续补充信息"],
        )
