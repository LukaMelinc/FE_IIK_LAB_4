from PIL import Image
import struct
import numpy as np


def pixel_hash(pixel):
    return (pixel[0] * 3 + pixel[1] * 5 + pixel[2] * 7 + pixel[3] * 11) % 64


def decode_qoi(encoded_data):
    # Unpack the QOI header
    magic, width, height, channels, colorspace = struct.unpack('>4sII2B', encoded_data[:14])
    assert magic == b'qoif', "Invalid QOI file."

    # Define constants for QOI decoding
    QOI_OP_MASK = 0b11000000
    QOI_OP_DATA = 0b00111111
    QOI_OP_DIFF_R = 0b00110000
    QOI_OP_DIFF_G = 0b00001100
    QOI_OP_DIFF_B = 0b00000011
    QOI_LUMA_DG = 0b00111111
    QOI_LUMA_RG = 0b11110000
    QOI_LUMA_BG = 0b00001111
    QOI_END_MARKER = b'\x00\x00\x00\x00\x00\x00\x00\x01'

    # Extract pixel data excluding the end marker
    pixel_data = encoded_data[14:len(encoded_data) - len(QOI_END_MARKER)]
    
    # Initialize decoding state
    pixel_array = [[0, 0, 0, 255]] * 64
    current_pixel = [0, 0, 0, 255]
    decoded_pixels = bytearray()

    # Decode pixel data
    i = 0
    while i < len(pixel_data):
        byte = pixel_data[i]

        if byte == 0b11111110:  # QOI_OP_RGB
            current_pixel[0] = pixel_data[i + 1]
            current_pixel[1] = pixel_data[i + 2]
            current_pixel[2] = pixel_data[i + 3]
            decoded_pixels.extend(current_pixel[:channels])
            i += 4
        elif byte == 0b11111111:  # QOI_OP_RGBA
            current_pixel[0] = pixel_data[i + 1]
            current_pixel[1] = pixel_data[i + 2]
            current_pixel[2] = pixel_data[i + 3]
            current_pixel[3] = pixel_data[i + 4]
            decoded_pixels.extend(current_pixel[:channels])
            i += 5
        elif (QOI_OP_MASK & byte) == 0b00000000:  # QOI_OP_INDEX
            index = (byte & QOI_OP_DATA)
            current_pixel = pixel_array[index]
            decoded_pixels.extend(current_pixel[:channels])
            i += 1
        elif (QOI_OP_MASK & byte) == 0b01000000:  # QOI_OP_DIFF
            diff = (byte & QOI_OP_DATA)
            dr = ((diff & QOI_OP_DIFF_R) >> 4) - 2
            dg = ((diff & QOI_OP_DIFF_G) >> 2) - 2
            db = (diff & QOI_OP_DIFF_B) - 2
            current_pixel[0] = (current_pixel[0] + dr) & 0xFF
            current_pixel[1] = (current_pixel[1] + dg) & 0xFF
            current_pixel[2] = (current_pixel[2] + db) & 0xFF
            decoded_pixels.extend(current_pixel[:channels])
            i += 1
        elif (QOI_OP_MASK & byte) == 0b10000000:  # QOI_OP_LUMA
            byte2 = pixel_data[i + 1]
            dg = (byte & QOI_LUMA_DG) - 32
            dr_dg = ((byte2 & QOI_LUMA_RG) >> 4) - 8
            db_dg = (byte2 & QOI_LUMA_BG) - 8
            dr = dr_dg + dg
            db = db_dg + dg
            current_pixel[0] = (current_pixel[0] + dr) & 0xFF
            current_pixel[1] = (current_pixel[1] + dg) & 0xFF
            current_pixel[2] = (current_pixel[2] + db) & 0xFF
            decoded_pixels.extend(current_pixel[:channels])
            i += 2
        elif (QOI_OP_MASK & byte) == 0b11000000:  # QOI_OP_RUN
            run_length = (byte & QOI_OP_DATA) + 1
            for _ in range(run_length):
                decoded_pixels.extend(current_pixel[:channels])
            i += 1

        pixel_array[pixel_hash(current_pixel)] = current_pixel[:]

    return decoded_pixels, width, height, 'RGBA' if channels == 4 else 'RGB'


def save_as_png(decoded_pixels, width, height, mode, output_filename):
    if mode == 'RGBA':
        image_array = np.array(decoded_pixels, dtype=np.uint8).reshape((height, width, 4))
        image = Image.fromarray(image_array, 'RGBA')
    else:
        image_array = np.array(decoded_pixels, dtype=np.uint8).reshape((height, width, 3))
        image = Image.fromarray(image_array, 'RGB')
    image.show()
    image.save(output_filename)


# Use the provided QOI image for testing
with open('/Users/lukamelinc/Desktop/Faks/MAG_1_letnik/2_semester/Informacije_in_Kodi/LAB/Projekt/dice.qoi', "rb") as file:
    encoded_qoi_data = file.read()

# Decode the image
decoded_pixels, img_width, img_height, img_mode = decode_qoi(encoded_qoi_data)

# Save as PNG
save_as_png(decoded_pixels, img_width, img_height, img_mode, 'test.png')
