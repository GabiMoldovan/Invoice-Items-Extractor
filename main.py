from pdf2image import convert_from_path
from paddleocr import PaddleOCR
import json

# Config to use the OCR model
ocr = PaddleOCR(use_angle_cls=True, lang='en')


def convert_pdf_to_images(pdf_path: str) -> list:
    '''
    Converts a pdf to images
    :param pdf_path: the pdf path in the current project folder
    :return: a list of all the images
    '''
    print("Converting pdf to image...\n")
    try:
        images = convert_from_path(pdf_path)
        print("Successfully converted pdf to image...\n")
        return images
    except Exception as e:
        print(f"Error in converting pdf to image: {str(e)}")

    return []


def extract_text_from_image(image_path: str) -> list:
    '''
    The function that extracts the text from an image
    :param image_path: image path in the current project folder
    :return: a list of sentences from the image
    '''
    print("Extracting text from image...\n")
    rez = []
    try:
        result = ocr.ocr(image_path)
        if not result or not isinstance(result, list) or not isinstance(result[0], dict):
            print("Unexpected result format:", result)
            return []

        extracted_text = result[0].get('rec_texts', [])

        return extracted_text

    except Exception as e:
        print(f"Error in extract_text_from_image: {str(e)}")
        return []


def extract_text_from_all_images(images: list) -> list:
    '''
    The function that extracts the text from a list of images using PaddleOCR
    :param images: a list of all the images
    :return: the extracted text from all the images
    '''
    extracted_text = []

    for i in range(len(images)):
        # saving the image locally
        img_name = "page" + str(i) + ".jpg"
        images[i].save(img_name, "JPEG")

        # extracting the text from the image
        extracted_text_from_page = extract_text_from_image(img_name)

        # saving the result
        for text in extracted_text_from_page:
            extracted_text.append(text)

    return extracted_text


def extract_invoice_number(text_list: list) -> str:
    '''
    :param text_list: the list of all the sentences from all the images
    :return: the extracted invoice number
    '''
    invoice_number = ""
    for text in text_list:
        if "Invoice #:" in text:
            invoice_number = text
            invoice_number = invoice_number.replace("Invoice #:", "")

    return invoice_number


def extract_invoice_date(text_list: list) -> str:
    '''
    :param text_list: the list of all the sentences from all the images
    :return: the extracted invoice date
    '''
    date = ""
    for text in text_list:
        if "Date:" in text:
            date = text
            date = date.replace("Date:", "")

    return date


def extract_invoice_from(text_list: list) -> str:
    '''
    :param text_list: the list of all the sentences from all the images
    :return: the extracted name that the invoice is from
    '''
    inv_from = ""
    for text in text_list:
        if "From:" in text:
            inv_from = text
            inv_from = inv_from.replace("From:", "")

    return inv_from


def extract_invoice_to(text_list: list) -> str:
    '''
    :param text_list: the list of all the sentences from all the images
    :return: the extracted name that the invoice is going to
    '''
    inv_to = ""
    for text in text_list:
        if "To:" in text:
            inv_to = text
            inv_to = inv_to.replace("From:", "")

    return inv_to


def extract_invoice_items(text_list: list) -> list:
    '''
    :param text_list: the list of all the sentences from all the images
    :return: the extracted invoice items
    '''
    item_index = text_list.index("Item") + 5
    quantity_index = text_list.index("Quantity") + 5
    unit_price_index = text_list.index("Unit Price") + 5
    total_index = text_list.index("Total") + 5
    currency_index = text_list.index("Currency") + 5

    items = []

    currency = ["S", "$"]

    while text_list[currency_index] in currency:

        items.append({
            "itemName": text_list[item_index],
            "quantity": text_list[quantity_index],
            "unitPrice": text_list[unit_price_index],
            "total": text_list[total_index],
            "currency": text_list[currency_index]
        })

        if currency_index + 5 <= len(text_list):
            item_index += 5
            quantity_index += 5
            unit_price_index += 5
            total_index += 5
            currency_index += 5
        else:
            break

    return items


if __name__ == '__main__':
    # convert pdf to images
    pdf_path = "./prod.pdf"
    images = convert_pdf_to_images(pdf_path)

    # array to save the extracted sentences from all the images
    extracted_text = extract_text_from_all_images(images)

    print("Extracted text:", extracted_text)

    invoice_number = extract_invoice_number(extracted_text)
    invoice_date = extract_invoice_date(extracted_text)
    invoice_from = extract_invoice_from(extracted_text)
    invoice_to = extract_invoice_to(extracted_text)
    invoice_items = extract_invoice_items(extracted_text)

    # forming a dictionary with all the extracted data
    invoice_data = {
        "invoiceNumber": invoice_number,
        "invoiceDate": invoice_date,
        "invoiceFrom": invoice_from,
        "invoiceTo": invoice_to,
        "invoiceItems": invoice_items
    }

    print(json.dumps(invoice_data, indent=4))

    total = 0
    for item in invoice_items:
        price = item["total"]
        price = price.replace("$", "")
        total += float(price)

    print("\nThe total price is $" + str(total))
