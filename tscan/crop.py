from common import Filter, ImageMeta
import cv2
import math

# Oh Snap! Y then X?! Yes, that's life!
class Point(object):
    def __init__(self, y, x):
        self.y, self.x = y, x
    
    def __getitem__(self, i):
        return (self.y, self.x)[i]
    
    def almost(self, pt, precision=10):
        ''' Are these points almost equal? '''
        return max(abs(self.y - pt.y), abs(self.x - pt.x)) < precision
        

class Region(object):
    def __init__(self, start, stop):
        self.start, self.stop = start, stop
        if issubclass(self.start, dict):
            self.start = Point(**self.start)
        if issubclass(self.stop, dict):
            self.stop = Point(**self.stop)
    
    def almost(self, region, precision=10):
        ''' Are these regions almost equal? '''
        return (self.start.almost(region.start, precision)
            and self.stop.almost(region.stop, precision))

class Crop(Filter):
    ''' Automatically crop a scan to the image it contains
        
        Works by repeated trimming, looking for the greatest contrast between
        the crop and the border. This automatic cropping method:
            is slow
            handles non-rectangular images
            doesn't require the image to be level, but
            doesn't make any effort to straighten unlevel images
    '''
    @classmethod
    def arguments(cls, parser):
        parser.add_argument("--warp",
            help="How many lines to skip when a large crop seems likely. "
                "Lower numbers are more accurate, higher is faster (for use with -r)")
        Filter.arguments(parser)
        parser.set_defaults(warp=16)
    
    def run_one(self):
        ''' Automatically search for the most contrasting rectangle in the image
    
            It trims edges of the image iteratively, maximizing crop metric:
                abs(log( average of border / average of crop))
        '''
        self.image = self.meta.load()
        image = self.recursive_rectangle_crop(step=self.image, parent_crop_score=-1)
        self.meta.save(image[0])

        if step.size == 0:
            # This is undefined
            return -1
        if self.image.size - step.size == 0:
            # This is also undefined
            return -1
        all_sum = self.meta.sum # Image() not ndarray() : sum, not sum()
        crop_sum = step.sum()
        border_sum = all_sum - crop_sum
        
        all_count = self.image.size
        crop_count = step.size
        border_count = all_count-crop_count
        
        crop_mean = crop_sum / crop_count
        border_mean = border_sum / border_count
        return abs(math.log(crop_mean / border_mean))
        

    def recursive_rectangle_crop(self, step, parent_crop_score):
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
        crop_score = self.get_crop_score(step)
        if crop_score < parent_crop_score:
            # Prune this branch of computation
            return (step, crop_score)
        for crop_option in crop_options:
            step_crop = step[crop_option]
            winning_option, winning_option_score = self.recursive_rectangle_crop(step_crop, crop_score)
            if winning_option_score > crop_score:
                if winning_option is step_crop and crop_option in warp_speed:
                    # Ending on warp means you overshot. Prune this branch
                    pass
                else:
                    # Assume the first to do better works, since this is refined
                    return (winning_option, winning_option_score)
        # At this point, this is the winning formula
        return (step, crop_score)
