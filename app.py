import streamlit as st
import pandas as pd
import json
from google import genai
from google.genai import types

# 1. Konfigurasi Tampilan Web
st.set_page_config(
    page_title="HSE AI Safety Copilot",
    page_icon="🛡️",
    layout="wide"
)

# Custom Styling CSS
st.markdown("""
    <style>
    .main-header { font-size: 2.2rem; font-weight: bold; color: #1E3A8A; }
    .sub-header { font-size: 1.1rem; color: #4B5563; margin-bottom: 25px; }
    .stMetric { background-color: #f8fafc; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0; }
    </style>
""", unsafe_allow_html=True)

# Title & Description
st.markdown('<div class="main-header">🛡️ HSE Safety Analytics Copilot</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Platform AI untuk Analisis Laporan Keselamatan & Inspeksi K3 Lapangan</div>', unsafe_allow_html=True)

# 2. Sidebar Konfigurasi API Key
with st.sidebar:
    st.header("⚙️ System Config")
    api_key = st.text_input("Masukkan Gemini API Key:", type="password")
    st.info("💡 API Key dibutuhkan untuk menghubungkan aplikasi ke engine AI Gemini (Bisa didapat gratis dari Google AI Studio).")

# Peringatan Jika API Key Belum Diisi
if not api_key:
    st.warning("👈 Silakan masukkan Gemini API Key kamu di sidebar sebelah kiri untuk mengaktifkan AI Copilot.")
    st.stop()

# Inisialisasi Engine Gemini
client = genai.Client(api_key=api_key)

# 3. Tab Navigasi Fitur
tab1, tab2 = st.tabs(["📊 Analisis Data Laporan (Excel/CSV)", "💬 AI Safety Expert Consultant"])

# TAB 1: UPLOAD & ANALISIS DATA
with tab1:
    st.write("### Upload Data Laporan Lapangan")
    uploaded_file = st.file_uploader("Upload file laporan Near-miss / Unsafe Condition / Unsafe Act:", type=["csv", "xlsx"])

    if uploaded_file:
        try:
            # Baca File Upload
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.write("#### Preview Data Mentah:")
            st.dataframe(df.head(5), use_container_width=True)
            
            # Tombol Eksekusi AI
            if st.button("🚀 Jalankan Analisis AI Copilot", type="primary"):
                with st.spinner("AI sedang membaca laporan, menganalisis root cause & severity level..."):
                    
                    data_json = df.to_json(orient='records')
                    
                    prompt = f"""
                    Kamu adalah Expert HSE Specialist (K3). Analisis data laporan keselamatan berikut:
                    {data_json}

                    Tugasmu:
                    1. Klasifikasikan Kategori menjadi 'Unsafe Act' atau 'Unsafe Condition'.
                    2. Tentukan Risk Severity level: 'High', 'Medium', atau 'Low'.
                    3. Analisis Root Cause utama.
                    4. Berikan Rekomendasi Action Plan konkret untuk pencegahan.

                    Kembalikan HASIL HANYA dalam format JSON Array murni dengan key persis seperti ini:
                    - Tanggal
                    - Lokasi
                    - Deskripsi_Laporan
                    - Kategori
                    - Severity
                    - Root_Cause
                    - Action_Plan
                    """

                    # Panggil AI Gemini
                    response = client.models.generate_content(
                        model='gemini-2.0-flash',
                        contents=prompt,
                        config=types.GenerateContentConfig(response_mime_type="application/json")
                    )
                    
                    # Output Processing
                    result_df = pd.DataFrame(json.loads(response.text))
                    
                    st.success("✅ Analisis AI Selesai!")
                    
                    # Metric Summary Cards
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total Insiden Analyzed", len(result_df))
                    col2.metric("High Risk Identified", len(result_df[result_df['Severity'] == 'High']))
                    col3.metric("Unsafe Acts", len(result_df[result_df['Kategori'] == 'Unsafe Act']))
                    
                    st.write("#### Hasil Analisis Otomatis AI:")
                    st.dataframe(result_df, use_container_width=True)
                    
                    # Download CSV
                    csv_data = result_df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Hasil Analisis (CSV)",
                        data=csv_data,
                        file_name="Laporan_Analisis_K3_AI.csv",
                        mime="text/csv"
                    )

        except Exception as e:
            st.error(f"Terjadi kesalahan saat memproses file: {e}")

# TAB 2: CONSULTANT CHATBOT
with tab2:
    st.write("### 💬 Konsultasi Standard K3 & Regulasi")
    st.caption("Tanyakan regulasi Permenaker, ISO 45001, OSHA, atau SOP penanganan keselamatan spesifik.")
    
    user_query = st.text_area(
        "Tuliskan pertanyaan K3 kamu di sini:", 
        placeholder="Contoh: Berapa standar pencahayaan minimum untuk area fabrikasi berdasarkan aturan K3?"
    )
    
    if st.button("Tanya AI Expert", type="primary"):
        if user_query:
            with st.spinner("AI sedang mencari referensi regulasi & jawaban..."):
                try:
                    resp = client.models.generate_content(
                        model='gemini-2.0-flash',
                        contents=f"Kamu adalah Senior HSE Specialist berpengalaman. Jawab pertanyaan berikut dengan jelas, rinci, dan sertakan standar/regulasi resmi K3 jika ada: {user_query}"
                    )
                    st.markdown("### Jawaban AI Expert:")
                    st.info(resp.text)
                except Exception as e:
                    st.error(f"Gagal mendapatkan jawaban: {e}")
        else:
            st.warning("Mohon tuliskan pertanyaan terlebih dahulu.")
