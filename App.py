import streamlit as st
import pandas as pd
import json
from google import genai
from google.genai import types

# Config Tampilan
st.set_page_config(page_title="HSE AI Safety Copilot", page_icon="🛡️", layout="wide")

# Styling CSS biar tampilannya modern
st.markdown("""
    <style>
    .main-header { font-size: 2.2rem; font-weight: bold; color: #1E3A8A; }
    .sub-header { font-size: 1.1rem; color: #4B5563; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🛡️ HSE Safety Analytics Copilot</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Platform AI untuk Analisis Laporan Keselamatan & Inspeksi K3</div>', unsafe_allow_html=True)

# Sidebar Konfigurasi API
with st.sidebar:
    st.header("⚙️ Konfigurasi System")
    api_key = st.text_input("Masukkan Gemini API Key:", type="password")
    st.info("💡 API Key dibutuhkan untuk menghubungkan aplikasi ke engine AI Gemini.")

if not api_key:
    st.warning("👈 Silakan masukkan Gemini API Key kamu di sidebar untuk mengaktifkan AI Copilot.")
    st.stop()

# Inisialisasi Gemini Client
client = genai.Client(api_key=api_key)

# Tab Fitur
tab1, tab2 = st.tabs(["📊 Upload Data Laporan", "💬 Tanya Expert AI K3"])

with tab1:
    st.write("### Upload Data Laporan Lapangan (CSV/Excel)")
    uploaded_file = st.file_uploader("Pilih file laporan K3 (Near-miss / Unsafe Condition)", type=["csv", "xlsx"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
        
        st.write("#### Preview Data Mentah:")
        st.dataframe(df.head(5), use_container_width=True)
        
        if st.button("🚀 Analisis & Kategorikan dengan AI", type="primary"):
            with st.spinner("AI sedang menganalisis tingkat keparahan, kategori, dan tindakan korektif..."):
                try:
                    prompt = f"""
                    Kamu adalah Expert HSE Specialist (K3). Analisis data laporan berikut:
                    {df.to_json(orient='records')}

                    Kembalikan HASIL HANYA dalam format JSON Array murni dengan struktur key ini:
                    - Tanggal
                    - Lokasi
                    - Deskripsi_Laporan
                    - Kategori (Pilih: Unsafe Act / Unsafe Condition)
                    - Severity (Pilih: High / Medium / Low)
                    - Root_Cause (Contoh: Human Error, Housekeeping, Lack of PPE, Equipment Defect)
                    - Action_Plan (Rekomendasi tindakan pencegahan konkret)
                    """

                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=prompt,
                        config=types.GenerateContentConfig(response_mime_type="application/json")
                    )
                    
                    result_df = pd.DataFrame(json.loads(response.text))
                    
                    # Dashboard Ringkasan
                    st.success("✅ Analisis AI Selesai!")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total Insiden Analyzed", len(result_df))
                    col2.metric("High Risk Identified", len(result_df[result_df['Severity'] == 'High']))
                    col3.metric("Unsafe Acts", len(result_df[result_df['Kategori'] == 'Unsafe Act']))
                    
                    st.write("#### Hasil Analisis Otomatis AI:")
                    st.dataframe(result_df, use_container_width=True)
                    
                    # Download Hasil
                    st.download_button(
                        label="📥 Download Laporan Hasil Analisis (CSV)",
                        data=result_df.to_csv(index=False).encode('utf-8'),
                        file_name="Laporan_Analisis_K3_AI.csv",
                        mime="text/csv"
                    )
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat memproses AI: {e}")

with tab2:
    st.write("### 💬 Konsultasi Standard K3 & Regulasi")
    st.caption("Tanyakan regulasi Permenaker, ISO 45001, OSHA, atau cara penanganan insiden spesifik.")
    
    user_query = st.text_area("Tuliskan pertanyaan K3 kamu di sini:", placeholder="Misal: Berapa standar pencahayaan minimum untuk area fabrikasi?")
    if st.button("Tanya AI Expert"):
        if user_query:
            with st.spinner("Menjawab..."):
                resp = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=f"Kamu adalah Senior HSE Specialist. Jawab pertanyaan K3 berikut dengan jelas dan sesuai regulasi resmi: {user_query}"
                )
                st.markdown("### Jawaban Expert:")
                st.write(resp.text)
