from PIL import Image
import glob
import numpy as np

image_list = np.sort(glob.glob("../figures/comparison_figures/*.png"))
images = [
    Image.open(f'{image_name}')
    for image_name in image_list
]

# Remove the alpha channel (if present)
new_image_list = []
for image in images:
    image.load()
    n_image = Image.new("RGB", image.size, (255, 255, 255))
    n_image.paste(image, mask=image.split()[3])
    new_image_list.append(n_image)

pdf_file = "../figures/comparison_figures/comparison_figures.pdf"
new_image_list[0].save(pdf_file, save_all=True, append_images=new_image_list[1:])