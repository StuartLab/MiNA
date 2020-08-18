from javax.swing import JPanel, JFrame, JLabel, ImageIcon, JTextArea, JScrollPane, JSplitPane, JButton
from java.awt.event import ComponentListener, ComponentAdapter
from java.awt import Image, Color, Dimension, Graphics2D, RenderingHints
from java.awt.image import BufferedImage
from java.lang import Runnable

from ij import IJ, WindowManager
from ij.gui import ImageRoi, OvalRoi
from ij.gui import Overlay
from ij.plugin import Duplicator

from sc.fiji.analyzeSkeleton import AnalyzeSkeleton_;

        

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
    
    def overlay_z_in(event):
        zoom_image(overlay, overlay_label, 200)

    def overlay_z_out(event):
        zoom_image(overlay, overlay_label, -200)

    def filtered_z_in(event):
        zoom_image(filtered, filtered_label, 200)

    def filtered_z_out(event):
        zoom_image(filtered, filtered_label, -200)


    overlay = overlay.getImage()
    filtered = filtered.getImage()

    overlay_label = JLabel(ImageIcon(overlay))
    overlay_scroll = JScrollPane()
    overlay_scroll.setViewportView(overlay_label)

    filtered_label = JLabel(ImageIcon(filtered))
    filtered_scroll = JScrollPane()
    filtered_scroll.setViewportView(filtered_label)

    ovrl_sum = JButton("+", actionPerformed=overlay_z_in)
    ovrl_sum.setBounds(0,450,190,20)

    ovrl_minus = JButton("-", actionPerformed=overlay_z_out)
    ovrl_minus.setBounds(190,450,190,20)

    filt_sum = JButton("+", actionPerformed=filtered_z_in)
    filt_sum.setBounds(410,450,190,20)

    filt_minus = JButton("-", actionPerformed=filtered_z_out)
    filt_minus.setBounds(600,450,190,20)

    split_pane = JSplitPane(JSplitPane.HORIZONTAL_SPLIT, overlay_scroll, filtered_scroll)
    split_pane.setDividerLocation(400)
    split_pane.setBounds(0,0,800,450)

    frame = JFrame(" "*40 + "Orignal+Overlay" + " "*95 + "Preprocessed Image")
    frame.setSize(820,600)
    frame.add(split_pane)
    frame.add(ovrl_sum);frame.add(ovrl_minus)
    frame.add(filt_sum);frame.add(filt_minus)
    frame.add(table)
    frame.setResizable(False)
    frame.setLayout(None)
    frame.setVisible(True)

def prepare_table(params):
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


