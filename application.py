from flask import Flask, request, jsonify
from PyPDF2 import PdfMerger, PdfReader, PdfWriter
import base64
import io

app = Flask(__name__)

# Function to decode base64 to PDF

def decode_base64_to_pdf(base64_string):
    return io.BytesIO(base64.b64decode(base64_string))

# Function to encode PDF to base64

def encode_pdf_to_base64(pdf_stream):
    pdf_stream.seek(0)
    return base64.b64encode(pdf_stream.read()).decode('utf-8')

@app.route('/merge', methods=['POST'])
def merge_pdfs():
    try:
        pdfs_base64 = request.json.get('pdfs')
        if not pdfs_base64 or not isinstance(pdfs_base64, list):
            return jsonify({'error': 'Invalid input, expected a list of base64 encoded PDFs'}), 400

        merger = PdfMerger()
        for pdf_base64 in pdfs_base64:
            pdf_stream = decode_base64_to_pdf(pdf_base64)
            merger.append(pdf_stream)

        output_stream = io.BytesIO()
        merger.write(output_stream)
        merger.close()

        return jsonify({'merged_pdf': encode_pdf_to_base64(output_stream)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/watermark', methods=['POST'])
def watermark_pdf():
    try:
        pdf_base64 = request.json.get('pdf')
        watermark_base64 = request.json.get('watermark')
        if not pdf_base64 or not watermark_base64:
            return jsonify({'error': 'Invalid input, expected base64 encoded PDF and watermark'}), 400

        pdf_stream = decode_base64_to_pdf(pdf_base64)
        watermark_stream = decode_base64_to_pdf(watermark_base64)

        pdf_reader = PdfReader(pdf_stream)
        watermark_reader = PdfReader(watermark_stream)
        watermark_page = watermark_reader.pages[0]

        writer = PdfWriter()

        for page in pdf_reader.pages:
            page.merge_page(watermark_page)
            writer.add_page(page)

        output_stream = io.BytesIO()
        writer.write(output_stream)

        return jsonify({'watermarked_pdf': encode_pdf_to_base64(output_stream)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
