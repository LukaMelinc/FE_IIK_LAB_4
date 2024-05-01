from PIL import Image
import struct

def decode_QOI(encoded_bytes):
    magic, width, height, channels, colorspace = struct.unpack('>4sII2B', encoded_bytes[:14])   # unpack the data into five variables
    """
    >4sII2b
    > - data is big endian format, msb is stored first
    4s - next 4 bytes should be interpreted as string
    II - each represents unsigned integer, one for the width, one for the height
    2b - each b for unsigned byte, to unpack channels and colorspace values
    [:14] - slice off the first 14 bytes from encoded_bytes, which contain encoded image data
    """
    # magic stores first 4 bytes, the string
    assert magic == b'qoif', "Invalid QOI file."    # checks, if magic bytes match the expected bytes 'qoif'

    pixels = []
    pos = 14
    index = [None] * 64

    def index_pos(rgb):
        return(rgb[0] * 3 + rgb[1] * 5 + rgb[2] * 7 + rgb[3] * 11)%64
    
    while pos < len(encoded_bytes) - 8: # zadnjih osem bajtov je footer, zato tega ne beremo
        byte = encoded_bytes[pos]
        pos += 1

        if byte == 0b11111110:  # RGB, bytes are represented directly
            r, g, b = encoded_bytes[pos:pos+3]
            pixel = (r, g, b, 255) if channels == 4 else (r,g,b)
            pos += 3
        elif byte == 0b11111111:    # RGBA, bytes are represented directly
            r, g, b, a = encoded_bytes[pos:pos+4]
            pixel = (r, g, b, a)
            pos += 4
        elif byte >> 6 == 0:
            pixel = index[byte]
        elif byte >> 6 == 1:
            r += ((byte >> 4) & 0x03) - 2
            g += ((byte >> 2) & 0x03) - 2
            b += (byte & 0x03) - 2
            pixel = (r, g, b, a)
        elif byte >> 6 == 2:
            dg = (byte & 0x3F) - 32
            dr = dg + (encoded_bytes[pos] >> 4) - 8
            db = dg + (encoded_bytes[pos] & 0x0F) - 8
            r += dr
            g += dg
            b += db
            pixel = (r, g, b, a)
            pos += 1
        elif byte >> 6 == 3:  # QOI_OP_RUN
            length = (byte & 0x3F) + 1
            pixels.extend([pixel] * length)
            continue
        pixels.append(pixel)
        index[index_pos(pixel)] = pixel

    return pixels, width, height, 'RGBA' if channels == 4 else 'RGB'




def save_as_png(pixels, width, height, mode, output):
    image = Image.new(mode, (width, height))
    image.putdata(pixels)
    image.save(output)
    


with open('image.qoi', "rb") as file:
    encoded_data = file.read()

    # Decode the image
pixels, width, height, mode = decode_QOI(encoded_data)

# Save as PNG
save_as_png(pixels, width, height, mode, 'decoded.png')