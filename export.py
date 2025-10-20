from fpdf import FPDF

def generer_pdf(df, filename="fiche_tournee.pdf"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for _, row in df.iterrows():
        ligne = f"{row['Adresse']} - {row['Nom affiché']} - {row['Intérêt']}"
        ligne = ligne.encode("latin-1", "replace").decode("latin-1")  # remplace les caractères non compatibles
        pdf.cell(200, 10, txt=ligne, ln=True)

    pdf.output(filename)
