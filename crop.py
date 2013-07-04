from common import Command, Image
import cv2
import collections
import math

class Crop(Command):
    __description__ = "Automatically crop a scan to the image it contains"
    @classmethod
    def arguments(cls, parser):
        parser.add_argument("--warp", default=16,
            help="How many lines to skip when a large crop seems likely. "
                "Lower numbers are more accurate, higher is faster.")
        parser.add_argument("-r", action='store_true', dest="r_trim",
            help="Crop using recursive trimming")
        parser.add_argument("input", help='input filename')
        parser.add_argument("output", help='output filename')
        parser.set_defaults(plugin=cls)
    
    def __call__(self):
        ''' Automatically search for the most contrasting rectangle in the image
    
            It trims edges of the image iteratively, maximizing crop metric:
                abs( average of border - average of crop)
        '''
        self.image = Image.load(self.args.input)
        a = self._recursive_rectangle_crop(step=self.image.array, parent_crop_score=-1)
        Image(a[0]).save(self.args.output)
    
    def _get_crop_score(self, step):
        if step.size == 0:
            # This is undefined
            return -1
        if self.image.array.size - step.size == 0:
            # This is also undefined
            return -1
        all_sum = self.image.sum # Image() not ndarray() : sum, not sum()
        crop_sum = step.sum()
        border_sum = all_sum - crop_sum
        
        all_count = self.image.size
        crop_count = step.size
        border_count = all_count-crop_count
        
        crop_mean = crop_sum / crop_count
        border_mean = border_sum / border_count
        return abs(math.log(crop_mean / border_mean))
        

    def _recursive_rectangle_crop(self, step, parent_crop_score):
        _all = slice(0, None)
        warp_speed = range(4)
        crop_options = [
            (_all, slice(0, -self.args.warp)), 
            (_all, slice(self.args.warp, None)),
            (slice(0, -self.args.warp), _all),
            (slice(self.args.warp, None), _all),
            (_all, slice(0, -1)), 
            (_all, slice(1, None)),
            (slice(0, -1), _all),
            (slice(1, None), _all)]
        crop_score = self._get_crop_score(step)
        print step.shape, crop_score
        if crop_score < parent_crop_score:
            # Prune this branch of computation
            return (step, crop_score)
        for crop_option in crop_options:
            step_crop = step[crop_option]
            winning_option, winning_option_score = self._recursive_rectangle_crop(step_crop, crop_score)
            if winning_option_score > crop_score:
                if winning_option is step_crop and crop_option in warp_speed:
                    # Ending on warp means you overshot. Prune this branch
                    pass
                else:
                    # Assume the first to do better works, since this is refined
                    return (winning_option, winning_option_score)
        # At this point, this is the winning formula
        return (step, crop_score)
