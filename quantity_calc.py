from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class QuantityConfig:
    wall_height: float = 2.7
    wall_thickness: float = 0.2
    floor_thickness: float = 0.15
    ceiling_height: float = 2.4


@dataclass
class QuantityResult:
    summary_rows: list[dict[str, Any]]
    detail_rows: list[dict[str, Any]]


CATEGORY_MAP = {
    "벽": ["WALL", "벽", "A-WALL"],
    "창호": ["WINDOW", "WIN", "창", "DOOR", "문"],
    "바닥": ["FLOOR", "SLAB", "바닥"],
    "천장": ["CEILING", "CLG", "천장"],
}


def _classify(layer_name: str) -> str:
    upper = layer_name.upper()
    for category, keywords in CATEGORY_MAP.items():
        for kw in keywords:
            if kw.upper() in upper:
                return category
    return "기타"


def calculate_quantities(entities: list[dict[str, Any]], config: QuantityConfig) -> QuantityResult:
    """파싱된 CAD 엔티티를 기준으로 항목별 물량(길이/면적/체적/개수)을 계산한다."""

    aggregates: dict[str, dict[str, float]] = {}
    details: list[dict[str, Any]] = []

    for ent in entities:
        layer = ent.get("layer", "UNKNOWN")
        etype = ent.get("entity_type", "UNKNOWN")
        category = _classify(layer)

        length = float(ent.get("length") or 0.0)
        area = float(ent.get("area") or 0.0)
        count = int(ent.get("count") or 1)

        # 기본 계산 로직
        calc_area = area
        calc_volume = 0.0

        if category == "벽":
            # 벽은 주로 길이 기반 -> 벽체 면적/체적으로 변환
            if calc_area <= 0 and length > 0:
                calc_area = length * config.wall_height
            calc_volume = calc_area * config.wall_thickness
        elif category == "창호":
            # 창호는 개수 집계 중심, 면적 존재 시 반영
            if calc_area <= 0 and length > 0:
                calc_area = length * 0.1
        elif category == "바닥":
            # 바닥은 면적 중심, 길이만 있으면 임시 환산
            if calc_area <= 0 and length > 0:
                calc_area = length * 0.2
            calc_volume = calc_area * config.floor_thickness
        elif category == "천장":
            if calc_area <= 0 and length > 0:
                calc_area = length * 0.2
            calc_volume = calc_area * 0.01

        if category not in aggregates:
            aggregates[category] = {
                "길이(m)": 0.0,
                "면적(㎡)": 0.0,
                "체적(㎥)": 0.0,
                "개수(EA)": 0.0,
            }

        aggregates[category]["길이(m)"] += length
        aggregates[category]["면적(㎡)"] += calc_area
        aggregates[category]["체적(㎥)"] += calc_volume
        aggregates[category]["개수(EA)"] += count

        details.append(
            {
                "구분": category,
                "레이어": layer,
                "엔티티": etype,
                "핸들": ent.get("handle", ""),
                "길이(m)": round(length, 3),
                "면적(㎡)": round(calc_area, 3),
                "체적(㎥)": round(calc_volume, 3),
                "개수(EA)": count,
                "산출근거": _make_basis_text(category, length, calc_area, calc_volume, config),
            }
        )

    summary_rows = []
    for category, vals in aggregates.items():
        summary_rows.append(
            {
                "구분": category,
                "총길이(m)": round(vals["길이(m)"], 3),
                "총면적(㎡)": round(vals["면적(㎡)"], 3),
                "총체적(㎥)": round(vals["체적(㎥)"], 3),
                "총개수(EA)": int(vals["개수(EA)"]),
            }
        )

    summary_rows.sort(key=lambda x: x["구분"])
    return QuantityResult(summary_rows=summary_rows, detail_rows=details)


def _make_basis_text(
    category: str,
    length: float,
    area: float,
    volume: float,
    config: QuantityConfig,
) -> str:
    """엑셀 산출근거서에 표시할 한글 계산식 문자열 생성."""
    if category == "벽":
        return f"벽면적={length:.3f}×{config.wall_height:.2f}, 체적={area:.3f}×{config.wall_thickness:.2f}"
    if category == "바닥":
        return f"바닥체적={area:.3f}×{config.floor_thickness:.2f}"
    if category == "천장":
        return f"천장면적={area:.3f}, 체적(마감)=면적×0.01"
    if category == "창호":
        return "창호는 레이어 분류 기준으로 개수/면적 집계"
    return f"기본 집계: 길이={length:.3f}, 면적={area:.3f}, 체적={volume:.3f}"
