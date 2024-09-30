# computes editing distance between two images' binary strs
import os
import sys
from PIL import Image as IMG
from time import sleep
from difflib import SequenceMatcher
from collections import defaultdict
from base64 import b64encode

from settings import *

def simmilarity(a, b) -> float:
    a_str = b64encode(a).decode('utf-8')
    b_str = b64encode(b).decode('utf-8')
    print(f"Inside matcher")
    matcher = SequenceMatcher(None, a_str, b_str)
    return matcher.ratio()


class Image:
    def __init__(self, path: str) -> None:
        self.path = path
        self.filename = path.split("\\")[-1]
        with open(path, "rb") as file:
            self.binary = file.read()
    
    def show(self):
        with IMG.open(os.path.join(self.path)) as im:
            im.show()
        sleep(1.5)

class Comparison(object):
    def __init__(self, base_img: Image, target_img: Image) -> None:
        self.base_img = base_img
        self.target_img = target_img
        self.simi = simmilarity(self.base_img.binary, self.target_img.binary)

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


def explore_compare_imgs(dir, comparisons: list):
    for filename in os.listdir(dir):
        if ".webp" in filename or ".png" in filename:
            # if filename == img.filename: continue
            img2 = Image(os.path.join(dir, filename))

            print(f"Comparing")
            comparisons.append(Comparison(img, img2))
            print(f"Success")
        else:
            explore_compare_imgs(os.path.join(dir, filename), comparisons)
    print(f"{dir} explored")

sys.setrecursionlimit(3000)

img = Image(os.path.join(DIRECTORY, BASE_IMG_PATH))
comparisons = []

explore_compare_imgs(DIRECTORY, comparisons)

print(f"Compared among {len(comparisons)}")
comparisons.sort()
img.show()

print(f"\nTop five similarities:")
for i in range(1, 6):
    image = comparisons[-i].target_img
    print(f"{image.filename} : {comparisons[-i].simi}")
    image.show()

stranger = comparisons[0].target_img
print(f"Least similarity with {stranger.filename} is {comparisons[0].simi}")
stranger.show()


# img2 = Image(os.path.join(TARGET_IMG_PATH))
# img2 = Image(TEST_IMG1)
# simi = simmilarity(img.binary, img2.binary)
# print(simi)