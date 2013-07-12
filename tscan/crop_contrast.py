import cli
from crop import Region, Point

@cli.register
class CropContrast(object):
    ''' Crop an image by searching for the region of highest contrast
        
        Works by repeated trimming, looking for the greatest contrast between
        the crop and the border. This automatic cropping method
            is slow,
            handles non-rectangular images,
            doesn't require the image to be level, but
            doesn't make any effort to straighten unlevel images.
    '''
    _name = 'crop_contrast'
    _args = [ dict(name='--warp', default=16,
        help="Number of lines to skip per step before fine tuning."
            "Lower numbers are more accurate, higher is faster.") ]
    
    def run(self):
        ''' Automatically search for the most contrasting rectangle in the image
    
            It trims edges of the image iteratively, maximizing crop metric:
                abs(log( average of border / average of crop))
        '''
        self.meta = meta
        self.image = self.meta.data
        image = self.recursive_rectangle_crop(step=self.image, parent_crop_score=-1)
        self.meta.data = image[0]
        return self.meta

    def get_crop_score(self):
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