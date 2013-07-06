from common import Filter, ImageMeta
import cv2
import numpy
class CropGradient(Filter):
    __description__ = "Crops out an image by searching for the corners of the print"

    def run_one(self):        
        self.image = self.meta.load()
        self.get_tlc()
        self.get_max()
        self.meta.save(self.image)
