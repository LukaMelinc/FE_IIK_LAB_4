from PIL import Image
import struct
import numpy as np


def qoiHash(pixel):
    # Hash je ostanek
    return (pixel[0] * 3 + pixel[1] * 5 + pixel[2] * 7 + pixel[3] * 11) % 64


def decode_QOI(encoded_bytes):
    # Unpack the header
    magic, width, height, channels, colorspace = struct.unpack('>4sII2B', encoded_bytes[:14])
    assert magic == b'qoif', "Invalid QOI file."

    QOI_OP_RUN = 0b11000000
    QOI_OP_INDEX = 0b00000000
    QOI_OP_DIFF = 0b01000000
    QOI_OP_LUMA = 0b10000000
    QOI_OP_RGB = 0b11111110
    QOI_OP_RGBA = 0b11111111

    QOI_op_maska = 0b11000000  # maska za ukaz
    QOI_op_data = 0b00111111  # maska za podatke
    QOI_df_red = 0b00110000  # maska za razliko rdeče
    QOI_df_green = 0b00001100  # maska za razliko zelene
    QOI_df_blue = 0b00000011  # maska za razliko modre
    QOI_luma_dg = 0b00111111  # maska za luma zeleno
    QOI_luma_rg = 0b11110000  # maska za luma rdečo
    QOI_luma_bg = 0b00001111  # maska za luma modro

    qoi_end_marker = b'\x00\x00\x00\x00\x00\x00\x00\x01'
    buffer = encoded_bytes[14:(len(encoded_bytes) - len(qoi_end_marker))]  # buffer pixlov brez headerja in konca

    array = [[0, 0, 0, 255]] * 64
    px = [0, 0, 0, 255]
    bufferEnd = bytearray()

    # Dekodiranje
    i = 0
    while i < len(buffer):
        byte = buffer[i]

        # QOI_OP_RGB #
        if byte == QOI_OP_RGB:
            px[0] = buffer[i + 1]
            px[1] = buffer[i + 2]
            px[2] = buffer[i + 3]
            bufferEnd.extend(px[:channels])
            i += 4

        # QOI_OP_RGBA #
        elif byte == QOI_OP_RGBA:
            px[0] = buffer[i + 1]
            px[1] = buffer[i + 2]
            px[2] = buffer[i + 3]
            px[3] = buffer[i + 4]
            bufferEnd.extend(px[:channels])
            i += 5

        # QOI_OP_INDEX #
        elif (QOI_op_maska & byte) == QOI_OP_INDEX:
            index = (byte & QOI_op_data)
            px = array[index]
            bufferEnd.extend(px[:channels])
            i += 1

        # QOI_OP_DIFF #
        elif (QOI_op_maska & byte) == QOI_OP_DIFF:
            data = (byte & QOI_op_data)
            dr = ((data & QOI_df_red) >> 4) - 2
            dg = ((data & QOI_df_green) >> 2) - 2
            db = (data & QOI_df_blue) - 2
            px[0] = (px[0] + dr) & 0xFF
            px[1] = (px[1] + dg) & 0xFF
            px[2] = (px[2] + db) & 0xFF
            bufferEnd.extend(px[:channels])
            i += 1

        # QOI_OP_LUMA #
        elif (QOI_op_maska & byte) == QOI_OP_LUMA:
            byte2 = buffer[i + 1]
            dg = (byte & QOI_luma_dg) - 32  # bias
            drdg = ((byte2 & QOI_luma_rg) >> 4) - 8
            dbdg = (byte2 & QOI_luma_bg) - 8

            dr = drdg + dg
            db = dbdg + dg

            px[0] = (px[0] + dr) & 0xFF
            px[1] = (px[1] + dg) & 0xFF
            px[2] = (px[2] + db) & 0xFF
            bufferEnd.extend(px[:channels])
            i += 2

        # QOI_OP_RUN #
        elif (QOI_op_maska & byte) == QOI_OP_RUN:
            run = (byte & QOI_op_data) + 1  # bias
            for j in range(run):
                bufferEnd.extend(px[:channels])
            i += 1

        array[qoiHash(px)] = px[:]

    return bufferEnd, width, height, 'RGBA' if channels == 4 else 'RGB'


def save_as_png(bufferEnd, width, height, mode, output):
    if mode == 'RGBA':
        pic = np.array(bufferEnd, dtype=np.uint8).reshape((height, width, 4))
        image = Image.fromarray(pic, 'RGBA')
    else:
        pic = np.array(bufferEnd, dtype=np.uint8).reshape((height, width, 3))
        image = Image.fromarray(pic, 'RGB')
    image.show()
    image.save(output)


# Use the provided QOI image for testing
with open('/Users/lukamelinc/Desktop/Faks/MAG_1_letnik/2_semester/Informacije_in_Kodi/LAB/Projekt/qoi_test_images_2/kodim10.qoi', "rb") as file:
    encoded_data = file.read()

# Decode the image
bufferEnd, width, height, mode = decode_QOI(encoded_data)

# Save as PNG
save_as_png(bufferEnd, width, height, mode, 'test.png')
