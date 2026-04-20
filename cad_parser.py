from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import ezdxf


@dataclass
class ParsedEntity:
    """CAD 엔티티를 물량 계산에 필요한 공통 구조로 변환한 데이터 클래스."""

    entity_type: str
    layer: str
    handle: str
    length: float | None = None
    area: float | None = None
    radius: float | None = None
    count: int = 1


def _safe_get_layer(entity: Any) -> str:
    try:
        return entity.dxf.layer or "UNKNOWN"
    except Exception:
        return "UNKNOWN"


def _polyline_length(entity: Any) -> float:
    try:
        return float(entity.length())
    except Exception:
        return 0.0


def _polyline_area(entity: Any) -> float | None:
    # 닫힌 폴리라인은 면적으로 간주한다.
    try:
        if hasattr(entity, "closed") and entity.closed:
            return abs(float(entity.area()))
    except Exception:
        return None
    return None


def parse_cad_file(file_path: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """DXF/DWG 파일을 파싱해 엔티티 리스트와 메타정보를 반환한다."""
    file_ext = Path(file_path).suffix.lower()
    if file_ext not in {".dxf", ".dwg"}:
        raise ValueError("지원하지 않는 파일 형식입니다. DXF/DWG만 업로드하세요.")

    if file_ext == ".dwg":
        raise ValueError("DWG 직접 파싱은 제한됩니다. DXF로 변환 후 다시 시도하세요.")

    doc = ezdxf.readfile(file_path)
    msp = doc.modelspace()

    parsed: list[dict[str, Any]] = []
    for entity in msp:
        etype = entity.dxftype()
        layer = _safe_get_layer(entity)
        handle = getattr(entity.dxf, "handle", "")

        item = ParsedEntity(entity_type=etype, layer=layer, handle=handle)

        if etype == "LINE":
            item.length = float(entity.dxf.start.distance(entity.dxf.end))
        elif etype in {"LWPOLYLINE", "POLYLINE"}:
            item.length = _polyline_length(entity)
            item.area = _polyline_area(entity)
        elif etype == "CIRCLE":
            item.radius = float(entity.dxf.radius)
            item.length = 2 * 3.141592 * item.radius
            item.area = 3.141592 * (item.radius**2)
        elif etype == "ARC":
            radius = float(entity.dxf.radius)
            start_a = float(entity.dxf.start_angle)
            end_a = float(entity.dxf.end_angle)
            sweep = (end_a - start_a) % 360
            item.length = 2 * 3.141592 * radius * (sweep / 360)
        elif etype == "HATCH":
            # HATCH의 경계 면적이 제공되는 경우 활용
            area = getattr(entity.dxf, "area", None)
            if area is not None:
                item.area = abs(float(area))
        elif etype == "INSERT":
            item.count = 1

        parsed.append(item.__dict__)

    metadata = {
        "filename": Path(file_path).name,
        "dxf_version": doc.dxfversion,
        "entity_count": len(parsed),
        "layer_count": len(doc.layers),
    }
    return parsed, metadata
