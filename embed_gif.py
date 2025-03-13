import base64

with open("background.gif", "rb") as img_file:
    encoded_string = base64.b64encode(img_file.read()).decode('utf-8')

with open("encoded_gif.py", "w") as output_file:
    output_file.write(f'GIF_DATA = """{encoded_string}"""')
