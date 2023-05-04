import argparse
import os

import cv2
import pytesseract
from PIL import Image
from cnstd import CnStd, LayoutAnalyzer
from pdf2image import convert_from_path
from pytesseract import Output

std = CnStd()


def parse_args():
    parser = argparse.ArgumentParser(
        prog='ProgramName',
        description='What the program does',
        epilog='Text at the bottom of help')

    parser.add_argument('-f', '--file')  # positional argument
    parser.add_argument('-d', '--directory')  # option that takes a value
    args = parser.parse_args()
    return args.file, args.directory


# Press the green button in the gutter to run the script.
def check_args(pdf_file, directory):
    if not pdf_file:
        print(f"PDF FILE ${pdf_file} is invalid")
        exit(1)
    if not directory:
        print(f"NO DIR SPECIFIED")
        exit(2)


def save_image(directory, name, image_bytes, image_ext, page_index):
    with open(f"{directory}${page_index}_{name}.{image_ext}", "wb") as new_image_file:
        new_image_file.write(image_bytes)
        new_image_file.close()


def image_is_a_formula(crop_img):
    d = (pytesseract.image_to_data(crop_img, output_type=Output.DICT))
    return "=" in d['text']


def process_page(page, count, output):
    page_path = f'temp/out{count}.jpg'
    page.save(page_path, 'JPEG')
    img = Image.open(page_path)
    result = LayoutAnalyzer('mfd').analyze([img])
    cvimg = cv2.imread(page_path)
    i = 0
    for res in result:
        for j in res:
            if j['type'] == "isolated" or j['type'] == "embedding":
                box = j['box']
                (x, y, w, h) = (box[0][0], box[0][1], box[1][0] - box[0][0], box[2][1] - box[0][1])
                x, y, w, h = int(x), int(y), int(w), int(h)
                crop_img = cvimg[y:y + h, x:x + w]
                if image_is_a_formula(crop_img):
                    print("FOUND FORMULA ", j['type'], count)
                    cv2.imwrite(f"{output}/page{count}_f{i}.png", crop_img)
                    i += 1


def parse_pdf(pdf_file_name, directory):
    pages = convert_from_path(pdf_file_name, 500)
    for count, page in enumerate(pages):
        print(f"PROCESS PAGE ${count}")
        process_page(page, count, directory)


def check_dir_exists(path):
    is_exist = os.path.exists(path)
    if not is_exist:
        # Create a new directory because it does not exist
        os.makedirs(path)
    remove_files(path)


def remove_files(path):
    for f in os.listdir(path):
        os.remove(os.path.join(path, f))


if __name__ == '__main__':
    # pdf_file, directory = parse_args()
    pdf_file, directory = "pdfs/Datasheet_SHT4x.pdf", "output/"
    check_args(pdf_file, directory)
    check_dir_exists(directory)
    parse_pdf(pdf_file, directory)
    remove_files("temp/")

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
