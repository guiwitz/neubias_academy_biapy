import skimage.morphology
import skimage.filters
import numpy as np
from skimage.measure import label, regionprops_table
from skimage.feature import match_template, peak_local_max

import matplotlib

def detect_nuclei(image, size = 200):
    """Detect nuclei in image using binary operations
    
    Parameters
    ----------
    image : 2D numpy array
        image to be segmented
    size: number  
        maximal nucleus size
        
    Returns
    -------
    newimage : 2D numpy array
        mask of nuclei
    """
    
    # filtering
    image = skimage.filters.median(image,selem=np.ones((2,2)))
    # local thresholding
    image_local_threshold = skimage.filters.threshold_local(image,block_size=51)
    image_local = image > image_local_threshold
    # remove tiny features
    image_local_open = skimage.morphology.binary_opening(image_local, selem=skimage.morphology.disk(2))
    # label image
    image_labeled = label(image_local_open)
    # analyze regions
    our_regions = regionprops_table(image_labeled, properties = ('label','area','coords'))
    # create a new mask with constraints on the regions to keep
    newimage = np.zeros(image.shape)
    # fill in using region coordinates
    for x in range(len(our_regions['area'])):
        if our_regions['area'][x] > size:
            newimage[our_regions['coords'][x][:,0],our_regions['coords'][x][:,1]] = 1
            
    return newimage

def detect_nuclei_template(image, template):
    """Detect nuclei in image using template matching
    
    Parameters
    ----------
    image : 2D numpy array
        image to be segmented
    template: 2D numpy array  
        template for nucleus shape
        
    Returns
    -------
    masked_peaks : 2D numpy array
        mask where each nucleus is represented by a single white pixel
    otsu_mask : maks obtained using the Otsu threshold
    """
    
    matched = match_template(image=image, template=template, pad_input=True)

    local_max = peak_local_max(matched, min_distance=10,indices=False)

    otsu = skimage.filters.threshold_otsu(image)
    otsu_mask = image > otsu
    
    otsu_mask = skimage.morphology.binary_dilation(otsu_mask, np.ones((5,5)))
    masked_peaks = local_max*otsu_mask
    
    return masked_peaks, otsu_mask

def create_disk_template(radius):
    """Create a disk image
    
    Parameters
    ----------
    radius : int
        radius of disk
        
    Returns
    -------
    template : 2D numpy array
        binary image of a disk
    """
    
    template = np.zeros((2*radius+5,2*radius+5))
    center = [(template.shape[0]-1)/2,(template.shape[1]-1)/2]
    Y, X = np.mgrid[0:template.shape[0],0:template.shape[1]]
    dist_from_center = np.sqrt((X - center[0])**2 + (Y-center[1])**2)
    template[dist_from_center<=radius] = 1
    
    return template

def random_cmap():
    np.random.seed(42)
    cmap = matplotlib.colors.ListedColormap (np.random.rand(256,4))
    # value 0 should just be transparent
    cmap.colors[:,3] = 0.5
    cmap.colors[0,:] = 1
    cmap.colors[0,3] = 0
    
    # if image is a mask, color (last value) should be red
    cmap.colors[-1,0] = 1
    cmap.colors[-1,1:3] = 0
    return cmap

def myfun_in_script():
    a = 2
    print(f'final defintion: {a}')
    
def myfun_in_script2():
    print(f'final defintion: {a}')