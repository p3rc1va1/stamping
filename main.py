from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse
from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import io
import os

app = FastAPI()

def create_watermark(text1, text2, text3, selection):
    packet = io.BytesIO()
    c = canvas.Canvas(packet, pagesize=letter)
    width, height = letter
    
    rect_height = 50  # Height of the rectangle
    text1_width = c.stringWidth(text1, "Helvetica", 12)
    text2_width = c.stringWidth(text2, "Helvetica", 12)
    space_between_texts = 20  # Space between text1 and text2
    rect_width = text1_width + text2_width + space_between_texts + 20  # Adding some padding

    # Determine the position based on the selection parameter
    column_width = width / 4  # Width of each column
    if selection == 1:
        rect_x = column_width * 0 + 10
        rect_y = height - rect_height - 10
    elif selection == 2:
        rect_x = column_width * 1 + 10
        rect_y = height - rect_height - 10
    elif selection == 3:
        rect_x = column_width * 2 + 10
        rect_y = height - rect_height - 10
    elif selection == 4:
        rect_x = column_width * 3 + 10
        rect_y = height - rect_height - 10

    # Draw rectangle
    c.rect(rect_x, rect_y, rect_width, rect_height, stroke=1, fill=0)
    
    # Add three different text elements inside the rectangle
    c.drawString(rect_x + 10, rect_y + rect_height - 15, text1)
    c.drawString(rect_x + 10 + text1_width + space_between_texts, rect_y + rect_height - 15, text2)
    c.drawString(rect_x + 10, rect_y + rect_height - 35, text3)
    
    c.save()
    packet.seek(0)
    return packet

def add_watermark(input_pdf, watermark_packet, output_pdf):
    watermark = PdfReader(watermark_packet)
    watermark_page = watermark.pages[0]

    pdf_reader = PdfReader(input_pdf)
    pdf_writer = PdfWriter()

    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        page.merge_page(watermark_page)
        pdf_writer.add_page(page)

    with open(output_pdf, 'wb') as out_file:
        pdf_writer.write(out_file)

@app.post("/upload_pdf/")
async def upload_pdf(file: UploadFile = File(...), text1: str = Form(...), text2: str = Form(...), text3: str = Form(...), selection: int = Form(...)):
    input_pdf = f"temp_{file.filename}"
    output_pdf = f"watermarked_{file.filename}"
    
    with open(input_pdf, "wb") as f:
        f.write(await file.read())
    
    watermark_packet = create_watermark(text1, text2, text3, selection)
    
    add_watermark(input_pdf, watermark_packet, output_pdf)
    
    os.remove(input_pdf)
    
    return FileResponse(output_pdf, media_type='application/pdf', filename=output_pdf)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0")
