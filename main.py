from PIL import Image

def create_qoi_header(width, height, mode):
    magic = b'qoif'
    channels = 3 if mode == 'RGB' else 4
    colorspace = 1
    return (magic + 
            width.to_bytes(4, 'big') + 
            height.to_bytes(4, 'big') + 
            channels.to_bytes(1, 'big') + 
            colorspace.to_bytes(1, 'big'))

def qoi_pixel_hash(pixel):
    return (pixel[0] * 3 + pixel[1] * 5 + pixel[2] * 7 + pixel[3] * 11) % 64

def encode_qoi(image_path, output_path):
    image = Image.open(image_path)
    width, height = image.size
    mode = image.mode
    pixels = list(image.getdata())

    qoi_header = create_qoi_header(width, height, mode)
    qoi_end_marker = b'\x00\x00\x00\x00\x00\x00\x00\x01'

    color_index_array = [[0, 0, 0, 0]] * 64
    previous_pixel = [0, 0, 0, 255]
    run_length = 0
    encoded_pixels = bytearray()

    QOI_OP_RUN = 0b11000000
    QOI_OP_INDEX = 0b00000000
    QOI_OP_DIFF = 0b01000000
    QOI_OP_LUMA = 0b10000000
    QOI_OP_RGB = 0b11111110
    QOI_OP_RGBA = 0b11111111

    for i, pixel in enumerate(pixels):
        pixel = list(pixel) + [255] if mode == 'RGB' else list(pixel)

        if pixel == previous_pixel:
            run_length += 1
            if run_length == 62 or i == len(pixels) - 1:
                encoded_pixels.append(QOI_OP_RUN | (run_length - 1))
                run_length = 0
        else:
            if run_length > 0:
                encoded_pixels.append(QOI_OP_RUN | (run_length - 1))
                run_length = 0

            index_pos = qoi_pixel_hash(pixel)

            if color_index_array[index_pos] == pixel:
                encoded_pixels.append(QOI_OP_INDEX | index_pos)
            else:
                color_index_array[index_pos] = pixel
                red_diff = pixel[0] - previous_pixel[0]
                green_diff = pixel[1] - previous_pixel[1]
                blue_diff = pixel[2] - previous_pixel[2]
                alpha_diff = pixel[3] - previous_pixel[3]
                red_green_diff = red_diff - green_diff
                blue_green_diff = blue_diff - green_diff

                if all(-2 <= d <= 1 for d in [red_diff, green_diff, blue_diff]) and alpha_diff == 0:
                    encoded_pixels.append(QOI_OP_DIFF | ((red_diff + 2) << 4) | ((green_diff + 2) << 2) | (blue_diff + 2))
                elif -32 <= green_diff <= 31 and all(-8 <= d <= 7 for d in [red_green_diff, blue_green_diff]) and alpha_diff == 0:
                    encoded_pixels.append(QOI_OP_LUMA | (green_diff + 32))
                    encoded_pixels.append(((red_green_diff + 8) << 4) | (blue_green_diff + 8))
                else:
                    if alpha_diff == 0:
                        encoded_pixels.append(QOI_OP_RGB)
                        encoded_pixels.extend(pixel[:3])
                    else:
                        encoded_pixels.append(QOI_OP_RGBA)
                        encoded_pixels.extend(pixel)

        previous_pixel = pixel

    qoi_output = qoi_header + encoded_pixels + qoi_end_marker

    with open(output_path, 'wb') as file:
        file.write(qoi_output)

# Example usage
input_path = '/Users/lukamelinc/Desktop/Faks/MAG_1_letnik/2_semester/Informacije_in_Kodi/LAB/Projekt/dice.png'
output_path = '/Users/lukamelinc/Desktop/Faks/MAG_1_letnik/2_semester/Informacije_in_Kodi/LAB/Projekt/dice.qoi'
encode_qoi(input_path, output_path)
