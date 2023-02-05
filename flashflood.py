import pygame
from pygame import gfxdraw
from PIL import Image
import os


SPRITESHEET_PATH = r"SPRITESHEET PATH (in assets folder: donk2.png)"
TARGET_FOLDER = r"eg. Monke Folder"
IMG_NAME = "Monke Walk"

frogs = list(filter(lambda file: True if IMG_NAME in file else False, os.listdir(TARGET_FOLDER))).sort()
j = frogs[-1][-1] if frogs != None else 1

spritesheet = pygame.image.load(SPRITESHEET_PATH)
spritesheet_pil = Image.open(SPRITESHEET_PATH)
dimensions = spritesheet.get_size()

screen = pygame.display.set_mode(dimensions)
selection_surf = pygame.Surface(dimensions, pygame.SRCALPHA)
sprite_pixels_to_check = []
SELECTION_COL = (50, 200, 160)
# sprite_pixels = []

l = r = u = d = None

run = True
while run:
    for event in pygame.event.get():
        
        if event.type == pygame.QUIT:
            run = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                sprite_pixels_to_check.append(event.pos)
                l = r = event.pos[0]
                u = d = event.pos[1]
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                img = spritesheet_pil.crop((l, u+1, r+1, d+1))
                print((l, u, r, d))
                img.save(f"{TARGET_FOLDER}\\{IMG_NAME} {j}.png")
                j += 1
                selection_surf = pygame.Surface(dimensions, pygame.SRCALPHA)
                l = r = u = d = None
                print("Saved Image")
            
            elif event.key = pygame.K_ESC:
                selection_surf = pygame.Surface(dimensions, pygame.SRCALPHA)
                l = r = u = d = None
    
    if len(sprite_pixels_to_check):
        # for pixel_pos in sprite_pixels_to_check[::-1]:
        for i in range(len(sprite_pixels_to_check)-1, -1, -1):
            
            pixel_pos = sprite_pixels_to_check[-1]            
            if 0 <= pixel_pos[0] <= dimensions[0] and 0 <= pixel_pos[1] <= dimensions[1]:
                if spritesheet.get_at(pixel_pos) != (0, 0, 0, 0) and selection_surf.get_at(pixel_pos) == (0, 0, 0, 0):
                    gfxdraw.pixel(selection_surf, *pixel_pos, SELECTION_COL)
                    if pixel_pos[0] < l: l = pixel_pos[0]
                    if pixel_pos[0] > r: r = pixel_pos[0]
                    if pixel_pos[1] < u: u = pixel_pos[1]
                    if pixel_pos[1] > d: d = pixel_pos[1]
                    
                    sprite_pixels_to_check.append((pixel_pos[0]+1, pixel_pos[1]))
                    sprite_pixels_to_check.append((pixel_pos[0], pixel_pos[1]+1))
                    sprite_pixels_to_check.append((pixel_pos[0]-1, pixel_pos[1]))
                    sprite_pixels_to_check.append((pixel_pos[0], pixel_pos[1]-1))
            
                    sprite_pixels_to_check.append((pixel_pos[0]-1, pixel_pos[1]-1))
                    sprite_pixels_to_check.append((pixel_pos[0]+1, pixel_pos[1]+1))
                    sprite_pixels_to_check.append((pixel_pos[0]+1, pixel_pos[1]-1))
                    sprite_pixels_to_check.append((pixel_pos[0]-1, pixel_pos[1]+1))
                    
            sprite_pixels_to_check.pop()
        print((l, r, u, d))
        
    screen.fill((30, 30, 30))
    screen.blit(spritesheet, (0, 0))
    screen.blit(selection_surf, (0, 0))
    
    pygame.display.update()

pygame.quit()

