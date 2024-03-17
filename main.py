import io
import hashlib
import logging
from PIL import Image
import base64
import re
from flask import Flask, render_template, request

app = Flask(__name__)

def get_data(data, awal, akhir):
    hasil = []
    pos_awal = 0
    while True:
        pos_awal = data.find(awal, pos_awal)
        if pos_awal == -1:
            break
        pos_akhir = data.find(akhir, pos_awal + len(awal))
        if pos_akhir == -1:
            break
        hasil.append(data[pos_awal:pos_akhir + len(akhir)])
        pos_awal = pos_akhir + len(akhir)

    return hasil


def hex_to_base64(hex_string):
    binary_data = bytes.fromhex(hex_string)
    base64_image = base64.b64encode(binary_data).decode('utf-8')
    
    return base64_image


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/extract", methods=["POST"])
def convert():
    if request.method == "POST":
        file_pdf = request.files["file_pdf"]
        binary_data = file_pdf.read()
        nama_file = file_pdf.filename
        hex_string = ' '.join(format(byte, '02X') for byte in binary_data)

        # Simpan hex_string ke dalam file teks
        nama_file_plain = re.sub(r'\W+', '_', nama_file)
        with open("hex/"+nama_file_plain+".txt", "w") as file:
            file.write(hex_string)

        # Baca kembali data dari file teks
        # with open("file.txt", "r") as file:
        #     data = file.read()
        jpeg_blob = []
        extract_jpeg = get_data(hex_string, "FF D8 FF E0", "FF D9")
        if extract_jpeg:
            for string in extract_jpeg:
                baseSixFour = hex_to_base64(string)
                jpeg_blob.append(baseSixFour)

        png_blob = []
        extract_jpeg = get_data(hex_string, "89 50 4E 47 0D 0A 1A 0A", "49 45 4E 44 AE 42 60 82")
        if extract_jpeg:
            for string in extract_jpeg:
                baseSixFour = hex_to_base64(string)
                png_blob.append(baseSixFour)

        
        return render_template("result.html", jpegs=jpeg_blob, pngs=png_blob)

if __name__ == "__main__":
    # app.run(debug=True)
    app.run(port=8080, debug=True)
    app.logger.setLevel(logging.DEBUG)
