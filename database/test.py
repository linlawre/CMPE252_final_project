import os
pdf_dir = "PDF"
if os.path.exists(pdf_dir) and os.path.isdir(pdf_dir):
    pdf_files = [file for file in os.listdir(pdf_dir) if file.endswith(".pdf")]

    for pdf_file in pdf_files:
        print(pdf_file)