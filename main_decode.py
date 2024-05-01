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


        # glede na pravo opcodo določimo bitno operacijo
        if byte == 0b11111110:  # RGB, bytes are represented directly -> QOI_OP_RGB
            """directly specify the RGB values of a pixle
            extract the RGB values from encoded_bytes, between 0 and 255
            if we have opacity, then it is 255,
            at the end, we move three bytes forward"""
            r, g, b = encoded_bytes[pos:pos+3]
            pixel = (r, g, b, 255) if channels == 4 else (r,g,b)
            pos += 3
        elif byte == 0b11111111:    # RGBA, bytes are represented directly -> QOI_OP_RGBA
            """directly specify RGBA values of a pixle
            extract RGBA values from encoded bytes
            assign the values to the pixel
            mode four bytes forward
            """
            r, g, b, a = encoded_bytes[pos:pos+4]
            pixel = (r, g, b, a)
            pos += 4
        elif byte >> 6 == 0:    # če sta MSB bajta 0 -> QOI_OP_INDEX, biti so povejo barvo
            """ remaining 6 bits of opcode is used as an inde to a look up table index holding previously seen colurs
            we acces the index array at the byte place, index is predefined
            6 LSB bits determine the colour
            """
            pixel = index[byte]
        elif byte >> 6 == 1:    # MSB bajta sta 1 -> QOI_OP_DIFF, mala razlika
            """bitshift for 4/2 and use 0011 mask (3)
            reduce by 2 to make it signed from -2 to 1
            1 and 2 from MSB for r, 3, 4 from MSB for g, 5 and LSB for b
            """
            r += ((byte >> 4) & 0x03) - 2
            g += ((byte >> 2) & 0x03) - 2
            b += (byte & 0x03) - 2
            pixel = (r, g, b, a)
        elif byte >> 6 == 2:    # MSB bajta sta 2 -> QOI_OP_LUMA, večja razlika
            """
            dg are the lower 6 bits of the byte, represent green colour, ranging form -32 to 31
            dr - the upper 4 bits in the two bytesrepresent the red colour difference, from -8 to 7
            db - the lower 4 bits for calculating blue
            we apply the difference to the current levels"""
            dg = (byte & 0x3F) - 32
            dr = dg + (encoded_bytes[pos] >> 4) - 8
            db = dg + (encoded_bytes[pos] & 0x0F) - 8
            r += dr
            g += dg
            b += db
            pixel = (r, g, b, a)
            pos += 1
        elif byte >> 6 == 3:  # MSB bajta sta 3 -> QOI_OP_RUN
            """
            we keep the lower 6 bits, with those 6 bits we represent the repetition of the pixel,
            max num of repetition 2^6 = 64, max 64 consecutive same pixels
            +1 so we can go 1-64, 3F means 1-63
            """
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
    


with open('image.qoi', "rb") as file:
    encoded_data = file.read()

    # Decode the image
pixels, width, height, mode = decode_QOI(encoded_data)

# Save as PNG
save_as_png(pixels, width, height, mode, 'decoded.png')