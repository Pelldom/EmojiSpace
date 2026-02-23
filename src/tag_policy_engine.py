from __future__ import annotations

from typing import Iterable


RISK_ORDER = ("None", "Low", "Medium", "High", "Severe")
POSSIBLE_TAGS = {
    "luxury",
    "weaponized",
    "counterfeit",
    "stolen",
    "propaganda",
    "hazardous",
    "cybernetic",
}


def combine_risk_tier(current: str, incoming: str) -> str:
    return RISK_ORDER[max(RISK_ORDER.index(current), RISK_ORDER.index(incoming))]


def interpret_tags(government: object, tags: Iterable[str]) -> tuple[float, str, set[str]]:
    bias = 0.0
    risk = "None"
    interpreted: set[str] = set()
    for tag in tags:
        if tag not in POSSIBLE_TAGS:
            continue
        tag_risk = _tag_risk(government, tag)
        risk = combine_risk_tier(risk, tag_risk)
        interpreted.add(tag)
    return bias, risk, interpreted


def _tag_risk(government: object, tag: str) -> str:
    favored_tags = set(getattr(government, "ideological_modifiers").get("favored_tags", []))
    restricted_tags = set(getattr(government, "ideological_modifiers").get("restricted_tags", []))
    gov_id = getattr(government, "id")
    regulation = getattr(government, "regulation_level")
    enforcement = getattr(government, "enforcement_strength")
    tolerance = getattr(government, "tolerance_bias")
    bribery = getattr(government, "bribery_susceptibility")

    risk = "None"

    if tag == "luxury":
        if tolerance > 60:
            risk = combine_risk_tier(risk, "Low")
        if regulation > 70:
            risk = combine_risk_tier(risk, "Medium")
        if tag in favored_tags:
            risk = combine_risk_tier(risk, "Low")
        if tag in restricted_tags:
            risk = combine_risk_tier(risk, "Medium")
    elif tag == "weaponized":
        if gov_id in {"military", "fascist", "dictatorship"}:
            risk = combine_risk_tier(risk, "Medium")
        if gov_id in {"democracy", "collective_commune"}:
            risk = combine_risk_tier(risk, "High")
        if gov_id == "anarchic":
            risk = combine_risk_tier(risk, "Low")
        if tag in favored_tags:
            risk = combine_risk_tier(risk, "Medium")
        if tag in restricted_tags:
            risk = combine_risk_tier(risk, "High")
    elif tag == "counterfeit":
        if bribery > 60:
            risk = combine_risk_tier(risk, "Medium")
        if enforcement > 70:
            risk = combine_risk_tier(risk, "High")
        if regulation > 70:
            risk = combine_risk_tier(risk, "High")
        if gov_id == "anarchic":
            risk = combine_risk_tier(risk, "Low")
    elif tag == "stolen":
        if bribery > 60:
            risk = combine_risk_tier(risk, "High")
        if enforcement > 70:
            risk = combine_risk_tier(risk, "Severe")
        if tolerance > 70:
            risk = combine_risk_tier(risk, "Medium")
    elif tag == "propaganda":
        if tag in favored_tags:
            risk = combine_risk_tier(risk, "Low")
        if tag in restricted_tags:
            risk = combine_risk_tier(risk, "High")
        if regulation > 70:
            risk = combine_risk_tier(risk, "Medium")
    elif tag == "hazardous":
        if regulation > 70:
            risk = combine_risk_tier(risk, "High")
        if enforcement > 70:
            risk = combine_risk_tier(risk, "Medium")
        if gov_id == "anarchic":
            risk = combine_risk_tier(risk, "Low")
    elif tag == "cybernetic":
        if "technological" in favored_tags:
            risk = combine_risk_tier(risk, "Medium")
        if gov_id == "theocracy":
            risk = combine_risk_tier(risk, "High")
        if gov_id == "anarchic":
            risk = combine_risk_tier(risk, "Low")

    return risk

