from PIL import Image
import numpy as np
import os
    
def MSE(img1, img2):
    return ((img1 - img2) ** 2).mean()

def read_image(path):
    with Image.open(path) as img:
        byti = img.convert("RGB")
        return np.array(byti) 

png_direktorij = "direktorij png"
qoi_direktorij = "direktorij qoi"
direktorij_path = "direktorij"


for datoteka in os.dirlist("direktorij"):
    png_path = os.path.join(png_direktorij, datoteka)
    qoi_path = os.path.join(qoi_direktorij, datoteka)

    png_pixels = read_image(png_path)
    qoi_pixels = read_image(qoi_path)

    error = MSE(png_pixels, qoi_pixels)
    print(f"MSE za {datoteka}: {error}")






