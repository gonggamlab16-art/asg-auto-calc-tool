import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from cad_parser import parse_cad_file
from excel_export import build_excel_report
from quantity_calc import QuantityConfig, calculate_quantities


st.set_page_config(page_title="자동 물량 산출기", layout="wide")
st.title("건축 도면 기반 자동 물량 산출기")
st.caption("DXF/DWG와 도면 이미지를 업로드하면 항목별 물량과 산출근거서를 생성합니다.")


with st.sidebar:
    st.header("계산 설정")
    default_height = st.number_input("기본 벽 높이(m)", min_value=1.0, max_value=10.0, value=2.7, step=0.1)
    wall_thickness = st.number_input("기본 벽 두께(m)", min_value=0.05, max_value=1.0, value=0.2, step=0.01)
    slab_thickness = st.number_input("기본 바닥 두께(m)", min_value=0.05, max_value=1.0, value=0.15, step=0.01)
    ceiling_height = st.number_input("천장 마감 높이(m)", min_value=1.8, max_value=6.0, value=2.4, step=0.1)


st.subheader("1) 도면 파일 업로드")
cad_file = st.file_uploader("DXF 또는 DWG 파일을 업로드하세요.", type=["dxf", "dwg"])
image_file = st.file_uploader("참고용 도면 이미지(선택)", type=["png", "jpg", "jpeg"], accept_multiple_files=False)

if image_file:
    st.image(image_file, caption="업로드된 도면 이미지", use_container_width=True)

if cad_file:
    ext = Path(cad_file.name).suffix.lower()
    if ext == ".dwg":
        st.warning("DWG는 환경에 따라 직접 파싱이 제한될 수 있습니다. 가능하면 DXF로 변환 후 업로드하세요.")

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        tmp.write(cad_file.getvalue())
        tmp_path = tmp.name

    try:
        parsed_entities, metadata = parse_cad_file(tmp_path)
    except Exception as exc:
        st.error(f"CAD 파일 파싱 중 오류가 발생했습니다: {exc}")
        st.stop()

    st.success(f"파일 파싱 완료: 엔티티 {len(parsed_entities)}개")

    with st.expander("파싱 결과 미리보기"):
        st.json(metadata)
        preview_df = pd.DataFrame(parsed_entities[:100])
        if not preview_df.empty:
            st.dataframe(preview_df, use_container_width=True)

    st.subheader("2) 물량 자동 집계")
    config = QuantityConfig(
        wall_height=default_height,
        wall_thickness=wall_thickness,
        floor_thickness=slab_thickness,
        ceiling_height=ceiling_height,
    )

    result = calculate_quantities(parsed_entities, config)
    summary_df = pd.DataFrame(result.summary_rows)
    detail_df = pd.DataFrame(result.detail_rows)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 항목별 요약")
        st.dataframe(summary_df, use_container_width=True)
    with col2:
        st.markdown("### 산출 근거(상세)")
        st.dataframe(detail_df, use_container_width=True)

    st.subheader("3) 엑셀 산출근거서 생성")
    excel_bytes = build_excel_report(summary_df, detail_df, metadata)
    st.download_button(
        label="엑셀 산출근거서 다운로드",
        data=excel_bytes,
        file_name="물량산출근거서.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

else:
    st.info("먼저 CAD 파일을 업로드해 주세요.")
