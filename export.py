from fpdf import FPDF

def generer_pdf(df, filename="fiche_tournee.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Fiche de tournée – Prospection", ln=True, align="C")
    for _, row in df.iterrows():
        ligne = f"{row['Adresse']} – {row['Nom affiché']} – {row['Intérêt']} – Relance: {row['Relance']}"
        pdf.cell(200, 10, txt=ligne, ln=True)
    pdf.output(filename)
