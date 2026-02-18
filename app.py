import streamlit as st
from fpdf import FPDF
import pandas as pd
from io import BytesIO
import zipfile

# ========================== PDF CLASS ==========================
class AdmitCard(FPDF):
    def header(self):
        # Border around the entire admit card
        self.rect(5, 5, 200, 140)
        
        self.set_font("Arial", 'B', 16)
        self.cell(0, 10, "BOARD OF SECONDARY EDUCATION", ln=True, align='C')
        
        self.set_font("Arial", 'I', 11)
        self.cell(0, 10, "ANNUAL EXAMINATION 2026", ln=True, align='C')
        
        self.set_font("Arial", 'B', 14)
        self.cell(0, 12, "ADMIT CARD", ln=True, align='C')
        self.ln(5)


# ========================== PDF GENERATOR ==========================
def generate_pdf(name: str, roll: str, dob: str, center: str, subjects: dict):
    pdf = AdmitCard()
    pdf.add_page()
    pdf.set_auto_page_break(auto=False)

    # Student Details
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(50, 10, "Student Name :", 0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, name, 0, 1)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(50, 10, "Roll Number :", 0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, str(roll), 0, 1)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(50, 10, "Date of Birth :", 0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, dob, 0, 1)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(50, 10, "Exam Centre :", 0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, center, 0, 1)

    # Subjects Table
    pdf.ln(8)
    pdf.set_fill_color(0, 102, 204)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(100, 10, "Subject", 1, 0, 'C', fill=True)
    pdf.cell(90, 10, "Date of Examination", 1, 1, 'C', fill=True)

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", '', 11)
    
    for subject, date in subjects.items():
        pdf.cell(100, 10, subject, 1)
        pdf.cell(90, 10, date, 1, 1)

    # Footer note
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 9)
    pdf.cell(0, 10, "Note: This is a computer-generated admit card.", align='C')

    # Return as bytes for Streamlit
    return pdf.output(dest='S').encode('latin-1')


# ========================== STREAMLIT APP ==========================
st.set_page_config(page_title="Admit Card Generator", page_icon="🎓", layout="centered")

st.title("🎓 Smart Admit Card Generator")
st.markdown("**Board of Secondary Education • Annual Examination 2026**")

tab1, tab2 = st.tabs(["Single Student", "Bulk Upload (Excel/CSV)"])

# Fixed subjects for 2026 (you can change dates easily)
SUBJECTS = {
    "Mathematics": "20 March 2026",
    "Science": "22 March 2026",
    "Social Science": "24 March 2026",
    "English": "26 March 2026",
    "Hindi": "28 March 2026",
    "Sanskrit / Urdu": "30 March 2026"
}

# -------------------------- TAB 1: SINGLE --------------------------
with tab1:
    col1, col2 = st.columns(2)
    
    name = col1.text_input("Full Name", placeholder="Aarav Sharma")
    roll = col2.text_input("Roll Number", placeholder="456789")
    
    col1, col2 = st.columns(2)
    dob = col1.text_input("Date of Birth", placeholder="15/05/2010")
    center = col2.text_input("Examination Center", placeholder="Kendriya Vidyalaya, Delhi")

    if st.button("Generate Admit Card", type="primary", use_container_width=True):
        if not name or not roll or not dob or not center:
            st.error("Please fill all fields")
        else:
            pdf_bytes = generate_pdf(name, roll, dob, center, SUBJECTS)
            st.success(f"Admit card generated for **{name}**")
            
            st.download_button(
                label="⬇️ Download PDF",
                data=pdf_bytes,
                file_name=f"{name.replace(' ', '_')}_{roll}_Admit_Card.pdf",
                mime="application/pdf"
            )

# -------------------------- TAB 2: BULK --------------------------
with tab2:
    st.info("Upload Excel or CSV with columns: **Name, Roll, DOB, Center**")
    
    uploaded_file = st.file_uploader(
        "Upload student list", 
        type=["xlsx", "xls", "csv"],
        help="Maximum 500 students recommended"
    )

    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.success(f"Loaded {len(df)} students")
            st.dataframe(df.head(10), use_container_width=True)

            if st.button("Generate All Admit Cards", type="primary"):
                zip_buffer = BytesIO()
                
                with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                    for _, row in df.iterrows():
                        name = str(row.get("Name", "Student")).strip()
                        roll = str(row.get("Roll", "000000")).strip()
                        dob = str(row.get("DOB", "N/A")).strip()
                        center = str(row.get("Center", "N/A")).strip()

                        pdf_bytes = generate_pdf(name, roll, dob, center, SUBJECTS)
                        
                        filename = f"{name.replace(' ', '_')}_{roll}_Admit_Card.pdf"
                        zip_file.writestr(filename, pdf_bytes)

                zip_buffer.seek(0)
                
                st.download_button(
                    label="⬇️ Download ZIP (All Admit Cards)",
                    data=zip_buffer,
                    file_name="All_Admit_Cards_2026.zip",
                    mime="application/zip"
                )
                
                st.balloons()

        except Exception as e:
            st.error(f"Error reading file: {e}")

# Footer
st.caption("Made with ❤️ using Streamlit + FPDF")
