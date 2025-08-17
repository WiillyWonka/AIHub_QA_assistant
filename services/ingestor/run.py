from PIL import Image
from transformers import AutoTokenizer, AutoProcessor, AutoModelForImageTextToText
from pdf2image import convert_from_path
import os
import shutil

DATA_DIR = os.getenv("DATA_DIR", "/app/data")
PDF_DIR = os.path.join(DATA_DIR, "pdf")
MD_DIR = os.path.join(DATA_DIR, "md")
TMP_DIR = os.path.join(DATA_DIR, "tmp")
URL_AI = os.getenv("PROGRAM_URL_AI")
URL_AIP = os.getenv("PROGRAM_URL_AIPROD")

def ensure_pdf():
    paths = []
    if not os.path.exists(os.path.join(PDF_DIR, "ai.pdf")):
        os.system(f"python /app/scripts/playwright-download.py {URL_AI} {PDF_DIR} ai")
    if not os.path.exists(os.path.join(PDF_DIR, "ai_product.pdf")):
        os.system(f"python /app/scripts/playwright-download.py {URL_AIP} {PDF_DIR} ai_product")
    for x in ("ai.pdf","ai_product.pdf"):
        p = os.path.join(PDF_DIR, x)
        if os.path.exists(p):
            paths.append(p)
    return paths

def ensure_md(pdfs):
    if not os.path.exists(MD_DIR):
        os.mkdir(MD_DIR)

    for pdf_path in pdfs:
        md_path = os.path.join(MD_DIR, os.path.basename(pdf_path).split('.')[0] + ".md")
        if not os.path.exists(md_path):
            convert_pdf_2_markdown(pdf_path, md_path)

def convert_pdf_2_markdown(pdf_path, markdown_path):
    pages = convert_from_path(pdf_path, 200)

    reset_tmp_dir()

    for count, page in enumerate(pages):
        page.save(f'{TMP_DIR}/page_{count}.jpg', 'JPEG')

    print("Запуск конвертации изображений в markdown")
    extracted_table = convert_images_2_markdown([f'{TMP_DIR}/page_{count}.jpg' for count, page in enumerate(pages)], 15000)

    with open(markdown_path, 'w', encoding='utf-8') as f:
        f.write(extracted_table)

    print("Конвертация завершена")    

def convert_images_2_markdown(image_paths, max_new_tokens=4096):
    model_path = "nanonets/Nanonets-OCR-s"

    model = AutoModelForImageTextToText.from_pretrained(
        model_path, 
        torch_dtype="auto", 
        device_map="auto", 
        # attn_implementation="flash_attention_2"
    )
    model.eval()

    tokenizer = AutoTokenizer.from_pretrained(model_path)
    processor = AutoProcessor.from_pretrained(model_path)

    base_prompt = """Extract the text from the above document as if you were reading it naturally. Return the tables in markdown format."""
    
    all_texts = []
    for i, image_path in enumerate(image_paths):
        if i > 0:
            prompt = base_prompt + f"\nThis is {i+1}-th page of whole document. Content of previous page:\n{output_text}. Follow the consistent structure of the document when processing the current page."
        else:
            prompt = base_prompt

        image = Image.open(image_path)
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": [
                {"type": "image", "image": f"file://{image_path}"},
                {"type": "text", "text": prompt},
            ]},
        ]
        text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = processor(text=[text], images=[image], padding=True, return_tensors="pt")
        inputs = inputs.to(model.device)
        
        output_ids = model.generate(**inputs, max_new_tokens=max_new_tokens, do_sample=False)
        generated_ids = [output_ids[len(input_ids):] for input_ids, output_ids in zip(inputs.input_ids, output_ids)]
        
        output_text = processor.batch_decode(generated_ids, skip_special_tokens=True, clean_up_tokenization_spaces=True)
        all_texts.append(output_text[0])

    return "".join(all_texts)

def reset_tmp_dir():
    """
    Проверяет существование директории. Если она существует, очищает её.
    Если не существует - создаёт новую.
    
    :param directory_path: Путь к директории
    """
    if os.path.exists(TMP_DIR):
        # Проверяем, что это действительно директория
        if os.path.isdir(TMP_DIR):
            # Удаляем все содержимое директории
            for filename in os.listdir(TMP_DIR):
                file_path = os.path.join(TMP_DIR, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f'Не удалось удалить {file_path}. Причина: {e}')
            print(f"Директория {TMP_DIR} была очищена")
        else:
            print(f"{TMP_DIR} существует, но это не директория")
    else:
        # Создаем директорию
        os.makedirs(TMP_DIR)
        print(f"Директория {TMP_DIR} была создана")

def main():
    os.makedirs(PDF_DIR, exist_ok=True)
    pdfs = ensure_pdf()
    ensure_md(pdfs)
    

if __name__ == "__main__":
    main()
