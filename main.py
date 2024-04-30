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

        previous_pixels = [0] * self.channels

        for i in range(0, len(data), st_kanalov):
