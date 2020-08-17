from ij import IJ, ImageStack, ImagePlus


def median(imp, median_radius):
    if imp.getNSlices() > 1:
        stack = imp.getImageStack()
        for i in range(imp.getNSlices()):
            frame = ImagePlus(stack.getSliceLabel(i+1), stack.getProcessor(i+1))
            IJ.run(frame, "Median...", "radius=%s" % (median_radius))
    else:    
        IJ.run(imp, "Median...", "radius=%s" % (median_radius))

def unsharp(imp, unsharp_radius, unsharp_weight):
    if imp.getNSlices() > 1:
        stack = imp.getImageStack()
        for i in range(imp.getNSlices()):
            frame = ImagePlus(stack.getSliceLabel(i+1), stack.getProcessor(i+1))
            IJ.run(frame, "Unsharp Mask...", "radius=%s mask=%s" % (unsharp_radius, unsharp_weight))
    else:
        IJ.run(imp, "Unsharp Mask...", "radius=%s mask=%s" % (unsharp_radius, unsharp_weight))

def clahe(imp, clahe_block, clahe_bins, clahe_slope, clahe_mask):
    if imp.getNSlices() > 1:
        stack = imp.getImageStack()
        for i in range(imp.getNSlices()):
            frame = ImagePlus(stack.getSliceLabel(i+1), stack.getProcessor(i+1))
            IJ.run(frame, "Enhance Local Contrast (CLAHE)", "blocksize=%s histogram=%s maximum=%s mask=%s" % (clahe_block, clahe_bins, clahe_slope, clahe_mask))
    else:
        IJ.run(imp, "Enhance Local Contrast (CLAHE)", "blocksize=%s histogram=%s maximum=%s mask=%s" % (clahe_block, clahe_bins, clahe_slope, clahe_mask))


