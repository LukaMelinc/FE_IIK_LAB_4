###########################################################
######## Title: IIK - projekt 7                    ########
######## Author: Tilen Tinta                       ########
######## Program: BMS 1, Avtomatika in Informatika ########
######## Date: May, 2024                           ########
###########################################################

from PIL import Image

def qoiHeader(width, height, mode):
    # Magic - first 4 bytes
    magic = b'qoif'

    # Width, Height - each 4 bytes (8 bytes)
    # Channels, Colorspace - each 1 byte (2 bytes)
    if mode == 'RGB':
        channels = 3
        colorspace = 1
    elif mode == 'RGBA':
        channels = 4
        colorspace = 1

    header = magic + int(width).to_bytes(4, 'big') + int(height).to_bytes(4, 'big') + channels.to_bytes(1, 'big') + colorspace.to_bytes(1, 'big')
    return header

def qoiHash(pixel):
    return (pixel[0] * 3 + pixel[1] * 5 + pixel[2] * 7 + pixel[3] * 11) % 64

def encode_qoi(image_path, output_path):
    # Load image
    image = Image.open(image_path)
    width, height = image.size
    mode = image.mode
    pixels = list(image.getdata())

    # Prepare header and end marker
    qoi_header = qoiHeader(width, height, mode)
    qoi_end_marker = b'\x00\x00\x00\x00\x00\x00\x00\x01'

    array = [[0, 0, 0, 0]] * 64
    pxOld = [0, 0, 0, 255]
    run_length = 0
    pixelEncoded = bytearray()
    pixel_count = len(pixels)

    # Operation codes
    QOI_OP_RUN = 0b11000000
    QOI_OP_INDEX = 0b00000000
    QOI_OP_DIFF = 0b01000000
    QOI_OP_LUMA = 0b10000000
    QOI_OP_RGB = 0b11111110
    QOI_OP_RGBA = 0b11111111

    # Encoding
    for i in range(pixel_count):
        px = list(pixels[i])
        if mode == 'RGB':
            px.append(255)

        if px == pxOld:
            run_length += 1
            if run_length == 62 or i == (pixel_count - 1):
                pixelEncoded.append(QOI_OP_RUN | (run_length - 1))
                run_length = 0
        else:
            if run_length > 0:
                pixelEncoded.append(QOI_OP_RUN | (run_length - 1))
                run_length = 0

            index_pos = qoiHash(px)

            if array[index_pos] == px:
                pixelEncoded.append(QOI_OP_INDEX | index_pos)
            else:
                array[index_pos] = px
                vr = px[0] - pxOld[0]
                vg = px[1] - pxOld[1]
                vb = px[2] - pxOld[2]
                va = px[3] - pxOld[3]
                vr_vg = vr - vg
                vb_vg = vb - vg

                if -2 <= vr <= 1 and -2 <= vg <= 1 and -2 <= vb <= 1 and va == 0:
                    pixelEncoded.append(QOI_OP_DIFF | ((vr + 2) << 4) | ((vg + 2) << 2) | (vb + 2))
                elif -32 <= vg <= 31 and -8 <= vr_vg <= 7 and -8 <= vb_vg <= 7 and va == 0:
                    pixelEncoded.append(QOI_OP_LUMA | (vg + 32))
                    pixelEncoded.append(((vr_vg + 8) << 4) | (vb_vg + 8))
                else:
                    if va == 0:
                        pixelEncoded.append(QOI_OP_RGB)
                        pixelEncoded.extend(px[:3])
                    else:
                        pixelEncoded.append(QOI_OP_RGBA)
                        pixelEncoded.extend(px)

        pxOld = px

    # Combine header, encoded pixels, and end marker
    qoi_output = qoi_header + pixelEncoded + qoi_end_marker

    # Save to file
    with open(output_path, 'wb') as file:
        file.write(qoi_output)

if __name__ == "__main__":
    input_path = '/Users/lukamelinc/Desktop/Faks/MAG_1_letnik/2_semester/Informacije_in_Kodi/LAB/Projekt/kodim23.png'
    output_path = '/Users/lukamelinc/Desktop/Faks/MAG_1_letnik/2_semester/Informacije_in_Kodi/LAB/Projekt/kodim23_moje.qoi'
    encode_qoi(input_path, output_path)
