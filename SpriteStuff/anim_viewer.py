from PIL import Image, ImageDraw, ImageOps
import os

folder = os.getcwd() + "\\monke"

def add_background_color(images, background_color=(128, 128, 128)):
    bg = Image.new('RGB', (max([img.width for img in images]), max([img.height for img in images])), background_color)
    images_with_bg = [ImageOps.expand(img, border=0, fill=background_color) for img in images]
    return images_with_bg

images = []
for filename in os.listdir(folder):
    img = Image.open(os.path.join(folder, filename))
    images.append(img)

images = add_background_color(images, (30, 30, 30))

# save as GIF

images[0].save(f'{folder}\\animation.gif',
               save_all=True,
               append_images=images[1:],
               duration=100,
               loop=0,
               disposal=0)      