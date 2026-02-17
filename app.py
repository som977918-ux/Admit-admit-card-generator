import streamlit as st
from fpdf import FPDF
import pandas as pd
from io import BytesIO
import zipfile
from PIL import Image  # For image handling

class AdmitCard(FPDF):
    def header(self):
        self.rect(5, 5, 200, 150)  # Height badhaya photo ke liye
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
    
    # Student Photo (right top corner)
    if photo_bytes:
        try:
            # Open image with PIL
            img = Image.open(BytesIO(photo_bytes))
            img = img.convert('RGB')  # Convert to RGB for JPEG
            jpg_buffer = BytesIO()
            img.save(jpg_buffer, format='JPEG')
            jpg_bytes = jpg_buffer.getvalue()
            
            # Add to PDF as JPEG bytes
            pdf.image(jpg_bytes, x=155, y=25, w=35, h=45, type='JPEG')
        except Exception as e:
            st.warning(f"Photo add karne mein issue: {e}")
            pass
    
    # Student Details (left side)
    pdf.set_xy(10, 50)  # Details ko neeche shift kiya photo space ke liye
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(60, 10, "Student Name :", 0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, name, 0, 1)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(60, 10, "Father's Name :", 0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, father_name, 0, 1)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(60, 10, "Class :", 0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, class_name, 0, 1)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(60, 10, "Roll Number :", 0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, str(roll), 0, 1)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(60, 10, "Date of Birth :", 0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, dob, 0, 1)
    
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(60, 10, "Exam Centre :", 0)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, center, 0, 1)
    
    # Subjects Table
    pdf.ln(10)
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
    
    # Footer
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 9)
    pdf.cell(0, 10, "Computer Generated Admit Card", align='C')
    
    return pdf.output(dest='S').encode('latin-1')

st.set_page_config(page_title="Admit Card Generator", page_icon="🎓")
st.title("🎓 Smart Admit Card Generator 2026")

tab1, tab2 = st.tabs(["Single Student", "Bulk Upload"])

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
    photo = st.file_uploader("Upload Student Photo (JPG/PNG, optional)", type=["jpg", "jpeg", "png"])
    photo_bytes = photo.read() if photo else None
    
    if st.button("Generate PDF"):
        if not all([name, father_name, class_name, roll, dob, center]):
            st.error("Please fill all required fields")
        else:
            pdf_bytes = generate_pdf(name, father_name, class_name, roll, dob, center, SUBJECTS, photo_bytes)
            st.download_button("⬇️ Download PDF", pdf_bytes, f"{name}_admit_card.pdf", "application/pdf")

with tab2:
    st.info("Upload Excel/CSV with columns: Name, Father's Name, Class, Roll, DOB, Center. (Photo not supported for bulk)")
    file = st.file_uploader("Upload File", type=["xlsx", "csv"])
    if file:
        df = pd.read_excel(file) if file.name.endswith('xlsx') else pd.read_csv(file)
        st.dataframe(df.head())
        if st.button("Generate All PDFs (ZIP)"):
            zip_buf = BytesIO()
            with zipfile.ZipFile(zip_buf, "w") as z:
                for _, r in df.iterrows():
                    pdf_bytes = generate_pdf(
                        r.get('Name', ''), r.get("Father's Name", ''),
                        r.get('Class', ''), r.get('Roll', ''),
                        r.get('DOB', ''), r.get('Center', ''),
                        SUBJECTS
                    )
                    z.writestr(f"{r.get('Name','')}_{r.get('Roll','')}.pdf", pdf_bytes)
            zip_buf.seek(0)
            st.download_button("⬇️ Download ZIP", zip_buf.getvalue(), "all_admit_cards.zip", "application/zip")

st.caption("Made with ❤️ using Streamlit + fpdf")
