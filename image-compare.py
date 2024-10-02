# images similarity calculator
import os
import math
import sys
import PIL
import PIL.IcnsImagePlugin
import PIL.Image
from time import sleep

from settings import *


class Image:
    def __init__(self, path: str) -> None:
        self.path = path
        self.filename = path.split("\\")[-1]
        self.pil_img = PIL.Image.Image()

        with PIL.Image.open(path) as im:
            self.pixels = im.load()
            self.width, self.height = im.size
    
    def show(self):
        with PIL.Image.open(os.path.join(self.path)) as im:
            im.show()
        
        sleep(1.5)


# TODO: rename methods
class ColourPalette:
    def __init__(self, img: Image) -> None:
        self.img = img
        self.pixels = None
        self.palette = None
        self.palette_size = None
    

    def legacy_dominative_colour(self) -> tuple:
        """
        Computes each pixel channel's arithmetic mean in image
        """
        img = self.img
        sum_rgb = [0, 0, 0]
        pixels = 0

        for j in range(img.height):
            for i in range(img.width):
                pix = img.pixels[i, j]
                sum_rgb[0] += pix[0]
                sum_rgb[1] += pix[1]
                sum_rgb[2] += pix[2]
                pixels += 1
        return tuple(map(lambda ch: round(ch / pixels), sum_rgb))


    def dominative_colour(self, chunk_pixels: list[tuple]) -> tuple:
        """
        Computes each pixel channel's arithmetic mean in chunk_pixels
        """
        sum_rgb = [0, 0, 0]
        pixels_count = 0

        for p in chunk_pixels:
            sum_rgb[0] += p[0]
            sum_rgb[1] += p[1]
            sum_rgb[2] += p[2]
            pixels_count += 1
        return tuple(map(lambda ch: round(ch / pixels_count), sum_rgb))


    def dominative_colours(self, num=1):
        """
        Constructs a palette with 'num' image's colours
        """
        if not self.pixels: self._get_pixels()
        self.palette_size = num

        pix_total = self.img.height * self.img.width
        chunk_len = pix_total // num
        
        palette = []
        start_i = 0
        end_i = chunk_len
        for i in range(num):
            palette.append(self.dominative_colour( self.pixels[start_i:end_i] ))
            start_i += chunk_len
            end_i += chunk_len
        print(palette)
        self.palette = palette


    def _get_pixels(self):
        """
        Adds all pixels in list (self.pixels)
        Need this, because cannot iterate self.img.pixels
        """
        pixels = []
        for j in range(self.img.height):
            for i in range(self.img.width):
                pixels.append(self.img.pixels[i, j])
        
        pixels.sort()
        # print(pixels)
        self.pixels = pixels
    

    def show_palette(self):
        """
        Constructs palette img and displays it
        """
        palette_img = PIL.Image.new("RGB", (720 * self.palette_size, 1280))
        
        colours = []
        start_pos = 0
        for col in self.palette:
            palette_entry = PIL.Image.new("RGB", (720, 1280), col)
            colours.append(palette_entry)
            palette_img.paste(palette_entry, (start_pos, 0))
            start_pos += 720
        palette_img.show()


class Comparer:
    def __init__(self, base_img: Image, target_img: Image) -> None:
        self.base_img = base_img
        self.target_img = target_img
        
        # dimensions must be same in both images
        # TODO: resize to proceed
        if self.base_img.width != self.target_img.width or self.base_img.height != self.target_img.height:
            raise NotImplementedError(f"Images must have same dimensions: \
                base({self.base_img.width}, {self.base_img.height}) \
                target({self.target_img.width}, {self.target_img.height})"
                )
        
        
    def compare_images(self, mode="SAD"):
        if mode == "Euclidian":
            similarity_func = self.pixel_euclidian_similarity
        else:
            similarity_func = self.pixel_SAD_similarity

        pixels = 0
        percs_sum = 0
        for j in range(self.base_img.height):
            for i in range(self.base_img.width):
                percs_sum += similarity_func(self.base_img.pixels[i, j], self.target_img.pixels[i,j])
                pixels += 1
        similarity = percs_sum / pixels
        print(f"Similarity between two images:\n{similarity}")
        return similarity


    def pixel_SAD_similarity(self, p1:tuple, p2:tuple) -> float:
        """
        Calculates SAD, returns similarity percentage between two pixels
        """
        max_dist = 255 * 3
        not_simi_perc = float(self._pixel_SAD(p1, p2)) / max_dist
        return 1 - not_simi_perc


    def _pixel_SAD(self, p1:tuple, p2:tuple) -> int:
        """
        Takes 2 pixels, returns SAD (sum of absolute distances) (0 <= SAD <= 3 * 255)
        """
        r1, g1, b1 = p1
        r2, g2, b2 = p2
        return  abs(r1 - r2) + abs(g1 - g2) + abs(b1 - b2)


    def pixel_euclidian_similarity(self, p1:tuple, p2:tuple) -> float:
        """
        Calculates euclidian dist, returns similarity percentage between two pixels
        """
        max_dist = 255 * 1.73205
        not_simi_perc = self._pixel_euclidian_dist(p1, p2) / max_dist
        return 1 - not_simi_perc


    def _pixel_euclidian_dist(self, p1:tuple, p2:tuple) -> float:
        """
        Takes 2 pixels (tuples of 3), returns euclidian diff (0 <= d <= 255 * 1,73)
        """
        dist_sqrd = (p1[0] - p2[0])**2  +  (p1[1] - p2[1])**2  +  (p1[2] - p2[2])**2
        return math.sqrt(dist_sqrd)     # bottleneck


class Comparison(object):
    def __init__(self, base_img: Image, target_img: Image) -> None:
        self.base_img = base_img
        self.target_img = target_img
        self.simi = Comparer(self.base_img, self.target_img).compare_images()

    def __lt__(self, other):
        return self.simi < other.simi
    
    def __le__(self, other):
        return self.simi <= other.simi
    
    def __gt__(self, other):
        return self.simi > other.simi
    
    def __ge__(self, other):
        return self.simi >= other.simi
    
    def __eq__(self, other):
        return self.simi == other.simi


# TODO: make iterative
def explore_compare_imgs(dir, comparisons: list):
    for filename in os.listdir(dir):
        if ".webp" in filename or ".png" in filename:
            if filename == im.filename: continue
            
            try:
                img2 = Image(os.path.join(dir, filename))
            except OSError:
                print(f"Error opening an image: {os.path.join(dir, filename)}")
            
            print(f"\nComparing")
            try:
                comparisons.append(Comparison(im, img2))
            except NotImplementedError:
                print("Failed, different dimensions")
            else:
                print(f"Success")
        else:
            explore_compare_imgs(os.path.join(dir, filename), comparisons)
    print(f"{dir} explored")


if __name__ == "__main__":

    # sys.setrecursionlimit(3000)
    im = Image(BASE_IMG_PATH)
    # comparisons = []
    # explore_compare_imgs(DIRECTORY, comparisons)
    # comparisons.sort()
    # print(f"Compared among {len(comparisons)}")
    # im.show()

    # print(f"\nTop five similarities:")
    # for i in range(1, 6):
    #     image = comparisons[-i].target_img
    #     image.show()
    #     print(f"{image.filename} : {comparisons[-i].simi}")

    # stranger = comparisons[0].target_img
    # stranger.show()
    # print(f"Least similarity with {stranger.filename} is {comparisons[0].simi}")
    palette = ColourPalette(im)
    print(palette.dominative_colours(10))
    palette.show_palette()
