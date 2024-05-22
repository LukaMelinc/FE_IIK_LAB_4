from PIL import Image
import struct

def decode_QOI(encoded_bytes):
    magic, width, height, channels, colorspace = struct.unpack('>4sII2B', encoded_bytes[:14])   # unpack the data into five variables
    assert magic == b'qoif', "Invalid QOI file."    # checks, if magic bytes match the expected bytes 'qoif'

    pixels = []
    pos = 14
    index = [(0, 0, 0, 255)] * 64

    r, g, b, a = 0, 0, 0, 255
    pixel = (r, g, b, a)

    def index_pos(rgb):
        return (rgb[0] * 3 + rgb[1] * 5 + rgb[2] * 7 + rgb[3] * 11) % 64

    while pos < len(encoded_bytes) - 8: # zadnjih osem bajtov je footer, zato tega ne beremo
        byte = encoded_bytes[pos]
        pos += 1

        # glede na pravo opcodo določimo bitno operacijo
        if byte == 0b11111110:  # RGB, bytes are represented directly -> QOI_OP_RGB
            r, g, b = encoded_bytes[pos:pos+3]
            pixel = (r, g, b, 255) if channels == 4 else (r, g, b)
            pos += 3
        elif byte == 0b11111111:    # RGBA, bytes are represented directly -> QOI_OP_RGBA
            r, g, b, a = encoded_bytes[pos:pos+4]
            pixel = (r, g, b, a)
            pos += 4
        elif byte >> 6 == 0:    # QOI_OP_INDEX
            pixel = index[byte]
        elif byte >> 6 == 1:    # QOI_OP_DIFF
            r = (r + ((byte >> 4) & 0x03) - 2) & 0xFF
            g = (g + ((byte >> 2) & 0x03) - 2) & 0xFF
            b = (b + (byte & 0x03) - 2) & 0xFF
            pixel = (r, g, b, a)
        elif byte >> 6 == 2:    # QOI_OP_LUMA
            dg = (byte & 0x3F) - 32
            byte = encoded_bytes[pos]
            pos += 1
            dr_dg = ((byte >> 4) & 0x0F) - 8
            db_dg = (byte & 0x0F) - 8
            r = (r + dr_dg + dg) & 0xFF
            g = (g + dg) & 0xFF
            b = (b + db_dg + dg) & 0xFF
            pixel = (r, g, b, a)
        elif byte >> 6 == 3:  # QOI_OP_RUN
            length = (byte & 0x3F) + 1  # pove, kolikokrat se more ta piksel ponovit
            pixels.extend([pixel] * length)
            continue
        pixels.append(pixel)                    #appendamo pixel pixellistu in
        index[index_pos(pixel)] = pixel         # pixel dodamo v idex table

    return pixels, width, height, 'RGBA' if channels == 4 else 'RGB'

def save_as_png(pixels, width, height, mode, output):
    image = Image.new(mode, (width, height))
    image.putdata(pixels)
    image.save(output)

with open('dice.qoi', "rb") as file:
    encoded_data = file.read()

# Decode the image
pixels, width, height, mode = decode_QOI(encoded_data)

# Save as PNG
save_as_png(pixels, width, height, mode, 'decoded.png')