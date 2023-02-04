from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io
from PyPDF2 import PdfWriter, PdfReader
from fastapi import FastAPI
from starlette.responses import FileResponse
import os
from hypercorn import Config as HyperConfig, run
from deta import Drive

files = Drive("files")

app = FastAPI(
    title="Custom invitation card for Uttam's wedding",
    version="1.0.0",
    description="Custom invitation card designed and developed by Er Vijay Raghuwanshi",
    docs_url="/"
)

# records = { "file_name_0.pdf": [names]}
records = []

# ==================================== pdf_function ========================
def write_on_pdf(names, x, y, file_name, font_size=14):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFillColorRGB(245, 0, 0, 1.0)
    can.setFont(psfontname="Helvetica", size=font_size)
    # def mapping_name(names):
    names_list = [i.strip() for i in str.split(names, '-')]
    for i in names_list:
        can.drawString(x, y, i)
        y -= 30
        x += 20
    # ================================================================
    records.append({file_name: names_list})
    can.save()

    # move to the beginning of the StringIO buffer
    packet.seek(0)

    # create a new PDF with Reportlab
    new_pdf = PdfReader(packet)
    # read your existing PDF
    existing_pdf = PdfReader(open("input.pdf", "rb"))
    output = PdfWriter()
    # add the "watermark" (which is the new pdf) on the existing page
    page = existing_pdf.pages[0]
    page.merge_page(new_pdf.pages[0])
    output.add_page(page)
    output.add_page(existing_pdf.pages[1])
    output.add_page(existing_pdf.pages[2])
    # finally, write "output" to a real file

    output_stream = open("output.pdf", "wb")
    output.write(output_stream)
    output_stream.close()

    # create a json file
    return {"message": file_name, "status": "success"}
# ==================================== pdf_function ========================
count = 0
temp_file = []
# ==================================== getPublicRooms ========================
@app.get("/getInvitation/", tags=["Uttam ❤ Neetu"])
def getInvitation(names:str):
    try:
        global count
        global temp_file
        file_name = names[0:25] + f"_{count}.pdf"
        output = write_on_pdf(names=names, file_name=file_name, x=225, y=495, font_size=14)
        count += 1
        file = os.getcwd() + "\\output.pdf"
        return FileResponse(
                # TPDF.name,
                file,
                media_type="application/pdf",
                headers = {'Content-Disposition': f'inline; {file}'},
                filename=file_name)
    except Exception as e:
        return {"message": str(e), "status": "error"}



@app.get("/getRecords/", tags=["Uttam ❤ Neetu"])
def getRecords():
    return records

# ==================================== getPublicRooms ========================
if __name__ == "__main__":
    config = HyperConfig()
    config.bind = ["0.0.0.0:5501"]
    config.application_path = 'Main'
    config.use_reloader = True

    run.run(config)
