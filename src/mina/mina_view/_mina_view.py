from javax.swing import JPanel, JFrame, JLabel, ImageIcon, JTextArea
from java.awt.event import ComponentListener, ComponentAdapter
from java.awt import Image, Color
from java.lang import Runnable

from ij import IJ, WindowManager
from ij.gui import ImageRoi, OvalRoi
from ij.gui import Overlay
from ij.plugin import Duplicator

from sc.fiji.analyzeSkeleton import AnalyzeSkeleton_;


class resize_listener(ComponentAdapter): 
    def __init__(self, app):
        self.app = app
    
    def componentResized(self, ce):
        frame = self.app.frame
        frame_size = frame.getSize()
        img1 = self.app.img1.getScaledInstance(frame_size.width/2, frame_size.height-self.app.table_height, Image.SCALE_SMOOTH)
        img2 = self.app.img2.getScaledInstance(frame_size.width/2, frame_size.height-self.app.table_height, Image.SCALE_SMOOTH)
        self.app.img1_lbl.setBounds(0,0,frame_size.width,frame_size.height-self.app.table_height)
        self.app.img2_lbl.setBounds(frame_size.width/2,0,frame_size.width,frame_size.height-self.app.table_height)
        self.app.img1_lbl.setIcon(ImageIcon(img1))
        self.app.img2_lbl.setIcon(ImageIcon(img2))
        self.table_x = 8
        if (frame_size.width > self.app.table_width):
            self.table_x = frame_size.width/2 - self.app.table_width/2
        self.app.table.setBounds(self.table_x,frame_size.height-self.app.table_height, self.app.table_width, self.app.table_height)

class Frame(Runnable):
    def __init__(self, title, img1, img2, w, h, table):
        if w*h > 2000:
            w -= w/3
            h -= h/3
            img1 = img1.getScaledInstance(w, h, Image.SCALE_SMOOTH)
            img2 = img2.getScaledInstance(w, h, Image.SCALE_SMOOTH)
        self.img1 = img1
        self.title = title
        self.w = w
        self.h = h
        self.table = table

        self.img1_icon = ImageIcon(img1)
        self.img1_lbl = JLabel()
        self.img1_lbl.setBounds(0,0,w,h)
        self.img1_lbl.setIcon(self.img1_icon)

        self.img2 = img2
        self.img2_icon = ImageIcon(img2)
        self.img2_lbl = JLabel()
        self.img2_lbl.setBounds(w,0,w,h)
        self.img2_lbl.setIcon(self.img2_icon)

        self.table_width = self.table.getSize().width
        self.table_height = self.table.getSize().height
        self.table.setBounds(8, h, self.table_width,self.table_height)

        
    def run(self):
        self.frame = JFrame(self.title, size=(max(self.w*2+15, self.table_width), self.h+self.table_height), layout=None)
        self.frame.addComponentListener(resize_listener(self))
        self.frame.add(self.img1_lbl);self.frame.add(self.img2_lbl)
        self.frame.add(self.table)
        self.frame.getContentPane().setBackground(Color.white)
        self.frame.setVisible(True)
        

def overlay_2D(imp, binary, skeleton, skel_result):
    binary_outline = Duplicator().run(binary, 1, 1)
    binary_outline.show()
    IJ.run(binary_outline, "Make Binary", "")
    IJ.run(binary_outline, "Outline", "")
    
    IJ.run(skeleton, "Green", "")
    IJ.run(binary, "Magenta", "")
    IJ.run(binary_outline, "Magenta", "")

    skeleton_ROI = ImageRoi(0,0,skeleton.getProcessor())
    skeleton_ROI.setZeroTransparent(True)
    skeleton_ROI.setOpacity(1.0)
    binary_ROI = ImageRoi(0,0,binary.getProcessor())
    binary_ROI.setZeroTransparent(True)
    binary_ROI.setOpacity(0.10)
    binary_outline_ROI = ImageRoi(0,0,binary_outline.getProcessor())
    binary_outline_ROI.setZeroTransparent(True)
    binary_outline_ROI.setOpacity(0.5)

    binary_outline.changes = False
    binary_outline.close()

    overlay = Overlay()
    overlay.add(binary_ROI)
    overlay.add(binary_outline_ROI)
    overlay.add(skeleton_ROI)

    # add end points in yellow
    end_points = skel_result.getListOfEndPoints()
    for p in end_points:
        endp_color = Color(255,255,0,150)
        point_ROI = OvalRoi(p.x, p.y, 3.8, 3.8)
        point_ROI.setStrokeColor(endp_color)
        point_ROI.setFillColor(endp_color)
        overlay.add(point_ROI)  
    
    # add junctions in bluish
    junctions = skel_result.getListOfJunctionVoxels()
    for junction in junctions:
        junct_color = Color(0,169,255,150)
        junction_ROI = OvalRoi(junction.x, junction.y, 3.8, 3.8)
        junction_ROI.setStrokeColor(junct_color)
        junction_ROI.setFillColor(junct_color)
        overlay.add(junction_ROI)

    imp.setOverlay(overlay)
    imp.updateAndDraw()   


def preview_side_by_side(overlay, filtered, table):
    width = filtered.getWidth()
    height = filtered.getHeight()
    title = filtered.getTitle()
    overlay = overlay.getImage()
    filtered = filtered.getImage()

    frame = Frame(title, overlay, filtered, width, height, table)
    frame.run()

def prepare_table(params):
    panel = JPanel()
    param_space = 0
    table_h = 70

    for param in params:
        if param != "":
            p = JTextArea(param)
            if "Thresholding" in param:
                p.setBounds(param_space,0,177,100)
            else:
                p.setBounds(param_space,0,130,100)
            p.setEditable(False)
            panel.add(p)
            param_space += 130

            if "Median" in param:
                table_h = 100
            elif "Thresholding" not in param:
                table_h = 137

    panel.setBounds(0,0,680,table_h)
    panel.setBackground(Color.white)
    panel.setLayout(None)
    panel.setVisible(True)
    return panel

def preview_images(imp, preprocessing_filters, threshold_image, use_ridge_detection, ridge_detect, rd_max, rd_min, rd_width, rd_length, param_strings): 
    imp_original = Duplicator().run(imp, 1, 1)
    preprocessing_filters(imp)
    imp_filtered = Duplicator().run(imp, 1, 1)
    binary = threshold_image(imp)
    if imp.getNSlices() == 1:
        if use_ridge_detection:
            skeleton = ridge_detect(imp, rd_max, rd_min, rd_width, rd_length)
        else:
            skeleton = Duplicator().run(binary)
            IJ.run(skeleton, "Skeletonize (2D/3D)", "")
        skel = AnalyzeSkeleton_()
        skel.setup("", skeleton)
        skel_result = skel.run()
        overlay_2D(imp_original, binary, skeleton, skel_result)
        IJ.run(imp_original, "Flatten", "")
        imp_original = WindowManager.getCurrentImage()
        table = prepare_table(param_strings)
        preview_side_by_side(imp_original, imp_filtered, table)
        imp_original.close()
    else:
        imp.show()


