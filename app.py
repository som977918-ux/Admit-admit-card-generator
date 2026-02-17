import streamlit as st
from fpdf import FPDF  # Use fpdf (stable version)
import pandas as pd
from io import BytesIO
import zipfile
from PIL import Image  # For handling images

class AdmitCard(FPDF):
    def header(self):
        self.rect(5, 5, 200, 140)
        self.set_font("Arial", 'B', 16)
        self.cell(0, 10, "BOARD OF SECONDARY EDUCATION", ln=True, align='C')
        self.set_font("Arial", 'I', 11)
        self.cell(0, 10, "ANNUAL EXAMINATION 2026", ln=True, align='C')
        self.set_font("Arial", 'B', 14)
        self.cell(0, 12, "ADMIT CARD", ln=True, align='C')
        self.ln(5)

def generate_pdf(name, father_name, class_name, roll, dob, center, subjects, photo_bytes=None):
    pdf = AdmitCard()
    pdf.add_page()
    
    # Photo placement (if provided)
    if photo_bytes:
        try:
            img = Image.open(BytesIO(photo_bytes))
            pdf.image(BytesIO(photo_bytes), x=150, y=20, w=30, h=40)  # Adjust position/size as needed
        except:
            pass  # Skip if image invalid
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(50, 10, "Student Name :", 0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, name, 0, 1)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(50, 10, "Father's Name :", 0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, father_name, 0, 1)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(50, 10, "Class :", 0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, class_name, 0, 1)
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
    
    pdf.ln(8)
    pdf.set_fill_color(0, 102, 204)
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(100, 10, "Subject", 1, 0, 'C', True)
    pdf.cell(90, 10, "Date", 1, 1, 'C', True)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", '', 11)
    for sub, date in subjects.items():
        pdf.cell(100, 10, sub, 1)
        pdf.cell(90, 10, date, 1, 1)
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 9)
    pdf.cell(0, 10, "Computer Generated Admit Card", align='C')
    return pdf.output(dest='S').encode('latin-1')  # fpdf compatible

st.set_page_config(page_title="Admit Card", page_icon="🎓")
st.title("🎓 Smart Admit Card Generator 2026")

tab1, tab2 = st.tabs(["Single", "Bulk"])

SUBJECTS = {
    "Mathematics": "20 Mar 2026", "Science": "22 Mar 2026",
    "Social Science": "24 Mar 2026", "English": "26 Mar 2026",
    "Hindi": "28 Mar 2026", "Sanskrit": "30 Mar 2026"
}

with tab1:
    name = st.text_input("Full Name")
    father_name = st.text_input("Father's Name")
    class_name = st.text_input("Class")
    roll = st.text_input("Roll No")
    dob = st.text_input("DOB (DD/MM/YYYY)")
    center = st.text_input("Exam Center")
    photo = st.file_uploader("Upload Student Photo (optional)", type=["jpg", "jpeg", "png"])
    photo_bytes = photo.read() if photo else None
    if st.button("Generate PDF"):
        if not all([name, father_name, class_name, roll, dob, center]):
            st.error("Please fill all required fields")
        else:
            pdf = generate_pdf(name, father_name, class_name, roll, dob, center, SUBJECTS, photo_bytes)
            st.download_button("Download", pdf, f"{name}_admit.pdf", "application/pdf")

with tab2:
    st.info("Upload Excel/CSV with columns: Name, Father's Name, Class, Roll, DOB, Center. Photo upload not supported for bulk yet.")
    file = st.file_uploader("Excel/CSV Upload", type=["xlsx","csv"])
    if file:
        df = pd.read_excel(file) if file.name.endswith('xlsx') else pd.read_csv(file)
        st.dataframe(df)
        if st.button("Generate All PDFs (ZIP)"):
            zip_buf = BytesIO()
            with zipfile.ZipFile(zip_buf, "w") as z:
                for _, r in df.iterrows():
                    p = generate_pdf(
                        r.get('Name',''), 
                        r.get("Father's Name",''),
                        r.get('Class',''),
                        r.get('Roll',''), 
                        r.get('DOB',''), 
                        r.get('Center',''), 
                        SUBJECTS
                    )
                    z.writestr(f"{r.get('Name','')}_{r.get('Roll','')}.pdf", p)
            zip_buf.seek(0)
            st.download_button("Download ZIP", zip_buf.getvalue(), "admit_cards.zip", "application/zip")

st.caption("Made with ❤️ using Streamlit + fpdf")
