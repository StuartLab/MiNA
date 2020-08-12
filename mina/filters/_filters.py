from ij import IJ, ImageStack, ImagePlus
from javax.swing import JPanel, JFrame, JLabel, ImageIcon
from java.awt.event import ComponentListener, ComponentAdapter
from java.awt import Image, Color
from java.lang import Runnable

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


class resize_listener(ComponentAdapter): 
    def __init__(self, app):
        self.app = app
    
    def componentResized(self, ce):
        frame = self.app.frame
        frame_size = frame.getSize()
        img1 = self.app.img1.getScaledInstance(frame_size.width/2, frame_size.height-38, Image.SCALE_SMOOTH)
        img2 = self.app.img2.getScaledInstance(frame_size.width/2, frame_size.height-38, Image.SCALE_SMOOTH)
        self.app.img1_lbl.setBounds(0,0,frame_size.width,frame_size.height-38)
        self.app.img2_lbl.setBounds(frame_size.width/2,0,frame_size.width,frame_size.height-38)
        self.app.img1_lbl.setIcon(ImageIcon(img1))
        self.app.img2_lbl.setIcon(ImageIcon(img2))

class Frame(Runnable):
    def __init__(self, title, img1, img2, w, h):
        self.img1 = img1
        self.title = title
        self.w = w
        self.h = h

        self.img1_icon = ImageIcon(img1)
        self.img1_lbl = JLabel()
        self.img1_lbl.setBounds(0,0,w,h)
        self.img1_lbl.setIcon(self.img1_icon)

        self.img2 = img2
        self.img2_icon = ImageIcon(img2)
        self.img2_lbl = JLabel()
        self.img2_lbl.setBounds(w,0,w,h)
        self.img2_lbl.setIcon(self.img2_icon)

        
    def run(self):
        self.frame = JFrame(self.title, size=(self.w*2+15,self.h+38),layout=None)
        self.frame.addComponentListener(resize_listener(self))
        self.frame.add(self.img1_lbl);self.frame.add(self.img2_lbl)
        self.frame.getContentPane().setBackground(Color.black)
        self.frame.setVisible(True)


def preview_side_by_side(overlay, filtered):

    width = filtered.getWidth()
    height = filtered.getHeight()
    title = filtered.getTitle()
    overlay = overlay.getImage()
    filtered = filtered.getImage()

    frame = Frame(title, overlay, filtered, width, height)
    frame.run()