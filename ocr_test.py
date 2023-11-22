import ddddocr

ocr = ddddocr.DdddOcr(show_ad=False)

with open("captcha.jpg", 'rb') as f:
    image = f.read()

res = ocr.classification(image)
print(res)