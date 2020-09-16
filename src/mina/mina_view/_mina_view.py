from javax.swing import JPanel, JFrame, JLabel, ImageIcon, JTextArea, JScrollPane, JSplitPane, JButton
from java.awt.event import ComponentListener, ComponentAdapter
from java.awt import Image, Color, Dimension, Graphics2D, RenderingHints
from java.awt.image import BufferedImage
from java.lang import Runnable

from ij import IJ, WindowManager
from ij.gui import ImageRoi, OvalRoi
from ij.gui import Overlay
from ij.plugin import Duplicator

from ij3d import Image3DUniverse;
from org.scijava.vecmath import Point3f;
from org.scijava.vecmath import Color3f;

from sc.fiji.analyzeSkeleton import AnalyzeSkeleton_;


def create_3Dmodel(imp_calibration, binary, skel_result):
    '''
    Create a 3D model of the stack with its end points, junctions and skeleton.
    '''
    
    univ = Image3DUniverse()
    univ.show()

    pixelWidth = imp_calibration.pixelWidth
    pixelHeight = imp_calibration.pixelHeight
    pixelDepth = imp_calibration.pixelDepth

    # Add end points in yellow
    end_points = skel_result.getListOfEndPoints()
    end_point_list = []
    for p in end_points:
        end_point_list.append(Point3f(p.x * pixelWidth, p.y * pixelHeight, p.z * pixelDepth))
    univ.addIcospheres(end_point_list, Color3f(255.0, 255.0, 0.0), 2, 1*pixelDepth, "endpoints")

    # Add junctions in bluish
    junctions = skel_result.getListOfJunctionVoxels()
    junction_list = []
    for p in junctions:
        junction_list.append(Point3f(p.x * pixelWidth, p.y * pixelHeight, p.z * pixelDepth))
    univ.addIcospheres(junction_list, Color3f(0, 169, 255), 2, 1*pixelDepth, "junctions")

    # Add the lines in green
    graphs = skel_result.getGraph()
    for graph in range(len(graphs)):
        edges = graphs[graph].getEdges()
        for edge in range(len(edges)):
            branch_points = []
            for p in edges[edge].getSlabs():
                branch_points.append(Point3f(p.x * pixelWidth, p.y * pixelHeight, p.z * pixelDepth))
            univ.addLineMesh(branch_points, Color3f(0.0, 255.0, 0.0), "branch-%s-%s"%(graph, edge), True)

    # Add the surface
    univ.addMesh(binary)
    univ.getContent("binary").setTransparency(0.5)
        

def overlay_2D(imp, binary, skeleton, skel_result):
    '''
    Adds the overlay to a 2D image. The overlay includes the skeleton in green, area in magenta,
    end points in yellow and junctions in blue.
    '''
    binary_outline = Duplicator().run(binary, 1, 1)
    binary_outline.show()
    IJ.run("Options...", "black")
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
    '''
    Prepares the preprocessed image and the one with the overlay to be positioned side by side including the
    table with the parameters used to preprocess the image.
    '''
    def zoom_image(image, label, factor):
        try:
            icon = label.getIcon()
            buf = BufferedImage(icon.getIconWidth()+factor, icon.getIconHeight()+factor, BufferedImage.TYPE_INT_RGB)
            grf = buf.createGraphics()
            grf.setRenderingHint(RenderingHints.KEY_INTERPOLATION, RenderingHints.VALUE_INTERPOLATION_BILINEAR)
            grf.drawImage(image, 0, 0, icon.getIconWidth()+factor, icon.getIconHeight()+factor, None)
            grf.dispose()
            label.setIcon(ImageIcon(buf))
        except:
            pass
    
    def zoom_in(event):
        zoom_image(overlay, overlay_label, 200)
        zoom_image(filtered, filtered_label, 200)

    def zoom_out(event):
        zoom_image(overlay, overlay_label, -200)
        zoom_image(filtered, filtered_label, -200)


    overlay = overlay.getImage()
    filtered = filtered.getImage()

    overlay_label = JLabel(ImageIcon(overlay))
    overlay_scroll = JScrollPane()
    overlay_scroll.setViewportView(overlay_label)

    filtered_label = JLabel(ImageIcon(filtered))
    filtered_scroll = JScrollPane()
    filtered_scroll.setViewportView(filtered_label)

    overlay_scroll.getHorizontalScrollBar().setModel(filtered_scroll.getHorizontalScrollBar().getModel())
    overlay_scroll.getVerticalScrollBar().setModel(filtered_scroll.getVerticalScrollBar().getModel())


    plus = JButton("+", actionPerformed=zoom_in)
    plus.setBounds(150,450,250,23)

    minus = JButton("-", actionPerformed=zoom_out)
    minus.setBounds(410,450,250,23)

    split_pane = JSplitPane(JSplitPane.HORIZONTAL_SPLIT, overlay_scroll, filtered_scroll)
    split_pane.setDividerLocation(400)
    split_pane.setBounds(0,0,813,450)

    frame = JFrame(" "*10 + "Orignal+Overlay" + " "*(split_pane.getWidth()*1/9) + "Preprocessed Image")
    frame.setSize(820,600)
    frame.add(split_pane)
    frame.add(plus);frame.add(minus)
    frame.add(table)
    frame.setResizable(False)
    frame.setLayout(None)
    frame.setVisible(True)

def prepare_table(params):
    '''
    Creates a table with the parameters used to preprocess the image
    '''
    panel = JPanel()
    param_space = 0
    i = 0

    for param in params:
        if param != "":
            p = JTextArea(param)
            if i%2 == 0:
                p.setBackground(Color.LIGHT_GRAY)
            else:
                p.setBackground(Color.white)
            i += 1

            if "Thresholding" in param:
                p.setBounds(param_space,0,177,100)
            else:
                p.setBounds(param_space,0,130,100)
            p.setEditable(False)
            panel.add(p)
            param_space += 130

    panel.setBounds(50,472,680,137)
    panel.setBackground(Color.white)
    panel.setLayout(None)
    panel.setVisible(True)
    return panel

def preview_images(imp, preprocessing_filters, threshold_image, use_ridge_detection, ridge_detect, rd_max, rd_min, rd_width, rd_length, param_strings, 
        user_preprocessing, preprocessor_path): 
    '''
    preview the image with the preprocessing selected.
    '''
        
    imp_original = Duplicator().run(imp, 1, 1)
    user_preprocessing(imp, preprocessor_path)
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


