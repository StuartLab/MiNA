from ij import IJ, ImageStack, ImagePlus, WindowManager
from ij.gui import GenericDialog
from ij.plugin import Duplicator
import sys

from java.lang import NullPointerException

def median(imp, median_radius):
    '''
    Applies a median filter to a 2D or 3D image
    '''
    if imp.getNSlices() > 1:
        stack = imp.getImageStack()
        for i in range(imp.getNSlices()):
            frame = ImagePlus(stack.getSliceLabel(i+1), stack.getProcessor(i+1))
            IJ.run(frame, "Median...", "radius=%s" % (median_radius))
    else:    
        IJ.run(imp, "Median...", "radius=%s" % (median_radius))

def unsharp(imp, unsharp_radius, unsharp_weight):
    '''
    Applies unsharp mask to a 2D or 3D image
    '''
    if imp.getNSlices() > 1:
        stack = imp.getImageStack()
        for i in range(imp.getNSlices()):
            frame = ImagePlus(stack.getSliceLabel(i+1), stack.getProcessor(i+1))
            IJ.run(frame, "Unsharp Mask...", "radius=%s mask=%s" % (unsharp_radius, unsharp_weight))
    else:
        IJ.run(imp, "Unsharp Mask...", "radius=%s mask=%s" % (unsharp_radius, unsharp_weight))

def clahe(imp, clahe_block, clahe_bins, clahe_slope, clahe_mask):
    '''
    Applies Enhance Local Contrast (CLAHE) to a 2D or 3D image
    '''
    try:
        img_mask = Duplicator().run(WindowManager.getImage(clahe_mask), 1, 1)
        new_title = "CLAHE_mina_mask_13423"
        img_mask.setTitle(new_title)
        img_mask.show()
        clahe_mask = new_title
    except NullPointerException:
        if clahe_mask != "*None*":
            d = GenericDialog("CLAHE")
            d.addMessage(clahe_mask + " is not currently open.")
            d.showDialog()
            sys.exit(0)

    try:
        if imp.getNSlices() > 1:
            stack = imp.getImageStack()
            for i in range(imp.getNSlices()):
                frame = ImagePlus(stack.getSliceLabel(i+1), stack.getProcessor(i+1))
                IJ.run(frame, "Enhance Local Contrast (CLAHE)", "blocksize=%s histogram=%s maximum=%s mask=%s" % (clahe_block, clahe_bins, clahe_slope, clahe_mask))
        else:
            IJ.run(imp, "Enhance Local Contrast (CLAHE)", "blocksize=%s histogram=%s maximum=%s mask=%s" % (clahe_block, clahe_bins, clahe_slope, clahe_mask))
    except:
        d = GenericDialog("CLAHE")
        d.addMessage("Mask should have the same width and hight as the image it is being applied to.")
        d.showDialog()
        print("\nMask should have the same width and hight as the image it is being applied to.")
        sys.exit(0)
    
    try:
        img_mask.close()
    except:
        pass


