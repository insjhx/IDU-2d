# 作者: 黄羿杰
# 感谢黄羿杰提供的高斯模糊算法！
Copyright = '黄羿杰 (uid: 29968040)'
# +-----------------------------------------------+

from PIL import Image, ImageFilter
import pygame, sys
import numpy as np

pygame.init()

# 给画布高斯模糊
def blur_sf(sf, radius):
    arr = pygame.surfarray.pixels2d(sf)
    arr_3d = np.zeros((*arr.shape, 4), dtype=np.uint8)
    arr_3d[:, :, 2] = arr[:, :] & 0xFF
    arr_3d[:, :, 1] = (arr[:, :] >> 8) & 0xFF
    arr_3d[:, :, 0] = (arr[:, :] >> 16) & 0xFF
    arr_3d[:, :, 3] = (arr[:, :] >> 24) & 0xFF
    arr_3d[arr==4294967295, 3] = 0
    pil_image = Image.fromarray(np.swapaxes(arr_3d, 0, 1))
    img1 = pil_image.filter(ImageFilter.GaussianBlur(radius=radius))
    return pygame.image.fromstring(img1.tobytes(), img1.size, 'RGBA').convert_alpha()

# 生成画布
def generate_surface(w, h, circle_r, blur_r):
    sf = pygame.Surface((w, h), pygame.SRCALPHA)
    sf.fill((0, 0, 0, 255))
    pygame.draw.circle(sf, (255, 255, 255, 255), (w//2, h//2), circle_r)
    return blur_sf(sf, blur_r)