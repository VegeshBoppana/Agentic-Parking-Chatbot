from presidio_analyzer import AnalyzerEngine
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

_NLP_CONFIG = {
    "nlp_engine_name": "spacy",
    "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
}
_nlp_engine = NlpEngineProvider(nlp_configuration=_NLP_CONFIG).create_engine()

_analyzer = AnalyzerEngine(nlp_engine=_nlp_engine, supported_languages=["en"])
_anonymizer = AnonymizerEngine()

PII_ENTITIES = ["PERSON", "PHONE_NUMBER", "EMAIL_ADDRESS",  "CREDIT_CARD", "IBAN_CODE"]


def detect_pii(text: str) -> list[dict]:
    results = _analyzer.analyze(text=text, entities=PII_ENTITIES, language="en")
    return [
        {"entity_type": r.entity_type, "text": text[r.start:r.end], "score": r.score}
        for r in results
    ]


def redact_pii(text: str, allowlist: set[str] | None = None) -> str:
    allowlist = allowlist or set()
    results = _analyzer.analyze(text=text, entities=PII_ENTITIES, language="en")
    results = [r for r in results if text[r.start:r.end] not in allowlist]

    if not results:
        return text

    anonymized = _anonymizer.anonymize(
        text=text,
        analyzer_results=results,
        operators={"DEFAULT": OperatorConfig("replace", {"new_value": "[REDACTED]"})},
    )
    return anonymized.text