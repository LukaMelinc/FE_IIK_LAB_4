import numpy as np
from PIL import Image
import matplotlib.pyplot as plt

def calculate_mse(image1_path, image2_path):

    image1 = Image.open(image1_path).convert('RGB')
    image2 = Image.open(image2_path).convert('RGB')
    

    if image1.size != image2.size:
        raise ValueError("Slike morajo biti enake velikosti")


    img1_array = np.asarray(image1)
    img2_array = np.asarray(image2)


    mse = np.mean((img1_array - img2_array) ** 2)
    
    return mse


image1_path = '/Users/lukamelinc/Desktop/Faks/MAG_1_letnik/2_semester/Informacije_in_Kodi/LAB/Projekt/kodim23.png'
image2_path = '/Users/lukamelinc/Desktop/Faks/MAG_1_letnik/2_semester/Informacije_in_Kodi/LAB/Projekt/test.png'

mse_value = calculate_mse(image1_path, image2_path)
print(f"Srednja kvadrantna napaka (MSE): {mse_value}")