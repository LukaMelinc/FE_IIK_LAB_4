import PIL as PIL
from PIL import Image

class QOIEncoder:
    def __init__(self, data, width, height, channels):
        self.data = data
        self.width = width
        self.height = height
        self.channels = channels
        self.encoded = bytearray()  # inicializiramo array bajtov



    def encode(self):
        """
        the data, we want to encode with QOI algorithm,
        the width and the height of the image, so we know the size of the pictrue,
        number of colour channels (3 or 4)
        """

        """constructing the header based on QOI specifications, we create initial segment of a QOI image file with neceseary info about the image"""
        self.encoded.extend(b'qoif')        # magic identifier for QOI identifier, a signature that signals the file is QOI image, helps when reading the file to indentify
        self.encoded.extend(self.width.to_bytes(4, 'big'))      # converts thewidth of the image to 4 byte representation and appends it
        self.encoded.extend(self.height.to_bytes(4, 'big'))     # converts the heigth of the image into 4 byte represenattion and appends it
        self.encoded.extend(self.channels.to_bytes(1, 'big'))   # converts the number of channels in the image into a single byte and appends it
        self.encoded.extend(b'\x00')    # appends the byte for the colour space, 0x00 represents default RGB space 

        previous_pixel = [0, 0, 0, 255] if self.channels == 4 else [0, 0, 0]
        run_length = 0

        for i in range(0, len(self.data), self.channels):
            pixel = self.data[i:i + self.channels]
            if pixel == previous_pixel:
                run_length += 1
                if run_length == 62:  # Max run length for QOI_OP_RUN
                    self.encoded.append(0b11000000 | (run_length - 1))
                    run_length = 0
            else:
                if run_length > 0:
                    self.encoded.append(0b11000000 | (run_length - 1))
                    run_length = 0

                if self.channels == 4:
                    self.encoded.extend([0b11111110] + pixel)  # QOI_OP_RGBA
                else:
                    self.encoded.extend([0b11111110] + pixel[:3])  # QOI_OP_RGB

            previous_pixel = pixel
        if run_length > 0:
            self.encoded.append(0b11000000 | (run_length - 1))

    
    def save_to_file(self, file_path):
        with open(file_path, "wb") as file:
            file.write(self.encoded)

def open_image(file_path):
    "Opens image and converts it into RGB/RGBA format"
    img = Image.open(file_path)
    if img.mode not in ["RGB", "RGBA"]:
        img = img.convert("RGBA")
    return img

def process_image(file_path, output_path):
    """Process an image file to QOI format and save it."""
    img = open_image(file_path)
    if img is not None:
        data = list(img.getdata())
        flat_data = [channel for pixel in data for channel in pixel]  # Flatten the list of tuples
        encoder = QOIEncoder(flat_data, img.width, img.height, len(img.mode))
        encoded_image = encoder.encode()
        encoder.save_to_file(output_path)

input_path = "/Users/lukamelinc/Desktop/Faks/MAG_1_letnik/2_semester/Informacije_in_Kodi/LAB/Projekt/archive/kodim01.png"
output_path = "/Users/lukamelinc/Desktop/Faks/MAG_1_letnik/2_semester/Informacije_in_Kodi/LAB/Projekt/test.png"
process_image(input_path, output_path)

   
