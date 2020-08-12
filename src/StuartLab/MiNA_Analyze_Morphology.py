#@ ImagePlus imp
#@ File(label="Pre-processor path:", value = "", required=False) preprocessor_path
#@ File(label="Post-processing path:", value ="", required=False) postprocessor_path
#@ String(label = "Thresholding Op:", value="otsu", choices={"huang", "ij1", "intermodes", "isoData", "li", "maxEntropy", "maxLikelihood", "mean", "minError", "minimum", "moments", "otsu", "percentile", "renyiEntropy", "rosin", "shanbhag", "triangle", "yen"}) threshold_method
#@ Boolean(label="Use ridge detection (2D only):", value=False) use_ridge_detection
#@ BigInteger(label="High contrast:", value=75, required=False) rd_max
#@ BigInteger(label="Low contrast:", value=5, required=False) rd_min
#@ BigInteger(label="Line width:", value=1, required=False) rd_width
#@ BigInteger(label="Line length:", value=3, required=False) rd_length
#@ String(label="User comment: ", value="") user_comment

#@ Boolean use_median
#@ Boolean use_unsharp
#@ Boolean use_clahe

#@ Integer order_median
#@ Integer order_unsharp
#@ Integer order_clahe

#@ Integer median_radius
#@ Integer unsharp_radius
#@ Float unsharp_weight
#@ Integer clahe_block
#@ Integer clahe_bins
#@ Integer clahe_slope
#@ String clahe_mask

#@ OpService ops
#@ ScriptService scripts
#@ StatusService status
#@ UIService ui

#@ Boolean preview_preprocessing



import mina.statistics 
import mina.tables 
import mina.filters 

import warnings

from collections import OrderedDict

from java.awt import Color
from java.io import File

from ij import IJ
from ij import ImagePlus
from ij import WindowManager
from ij.gui import ImageRoi, OvalRoi
from ij.gui import Overlay
from ij.measure import ResultsTable, Measurements
from ij.plugin import Duplicator
from ij.process import ImageStatistics

from net.imglib2.img.display.imagej import ImageJFunctions
from net.imglib2.type.numeric.integer import UnsignedByteType

from sc.fiji.analyzeSkeleton import AnalyzeSkeleton_;

from ij3d import Image3DUniverse;

from org.scijava.vecmath import Point3f;
from org.scijava.vecmath import Color3f;

# Helper functions..............................................................
def ridge_detect(imp, rd_max, rd_min, rd_width, rd_length):
    title = imp.getTitle()
    IJ.run(imp, "8-bit", "");
    IJ.run(imp, "Ridge Detection", "line_width=%s high_contrast=%s low_contrast=%s make_binary method_for_overlap_resolution=NONE minimum_line_length=%s maximum=0" % (rd_width, rd_max, rd_min, rd_length))
    IJ.run(imp, "Remove Overlay", "")
    skel = WindowManager.getImage(title + " Detected segments")
    IJ.run(skel, "Skeletonize (2D/3D)", "")
    skel.hide()
    return(skel)

def preprocessing_filters(imp):
    filter_dict = {order_median : (lambda:mina.filters.median(imp, median_radius), use_median), 
                   order_unsharp: (lambda:mina.filters.unsharp(imp, unsharp_radius, unsharp_weight), use_unsharp), 
                   order_clahe:   (lambda:mina.filters.clahe(imp, clahe_block, clahe_bins, clahe_slope, clahe_mask), use_clahe)}

    for i in range(3):
        pre_filter, use_filter = filter_dict[i]
        if use_filter:
            pre_filter()

def overlay_2D(imp, binary, skeleton, skel_result):
    binary_outline = Duplicator().run(binary, 1, 1)
    binary_outline.show()
    IJ.run(binary_outline, "Make Binary", "")
    IJ.run(binary_outline, "Outline", "")
    
    status.showStatus("Generate overlays...")
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
        point_ROI = OvalRoi(p.x, p.y, 3.5, 3.5)
        point_ROI.setStrokeColor(endp_color)
        point_ROI.setFillColor(endp_color)
        overlay.add(point_ROI)  
    
    # add junctions in cyan
    junctions = skel_result.getListOfJunctionVoxels()
    for junction in junctions:
        junct_color = Color(0,255,255,150)
        junction_ROI = OvalRoi(junction.x, junction.y, 3.5, 3.5)
        junction_ROI.setStrokeColor(junct_color)
        junction_ROI.setFillColor(junct_color)
        overlay.add(junction_ROI)

    imp.setOverlay(overlay)
    imp.updateAndDraw()   

def threshold_image(imp):
    # Create and ImgPlus copy of the ImagePlus for thresholding with ops...
    status.showStatus("Determining threshold level...")
    slices = imp.getNSlices()
    frames = imp.getNFrames()
    if imp.getRoi() != None:
        ROI_pos = (imp.getRoi().getBounds().x, imp.getRoi().getBounds().y)
    else:
        ROI_pos = (0, 0)

    imp_calibration = imp.getCalibration()
    imp_channel = Duplicator().run(imp, imp.getChannel(), imp.getChannel(), 1, slices, 1, frames)
    img = ImageJFunctions.wrap(imp_channel)

    # Determine the threshold value if not manual...
    binary_img = ops.run("threshold.%s"%threshold_method, img)
    binary = ImageJFunctions.wrap(binary_img, 'binary')
    binary.setCalibration(imp_calibration)
    binary.setDimensions(1, slices, 1)
    return binary


# The run function..............................................................
def run(imp_original, preprocessor_path, postprocessor_path, threshold_method, user_comment):
    imp = Duplicator().run(imp_original, imp_original.getChannel(), imp_original.getChannel(), 1, imp_original.getNSlices(), 1, imp_original.getNFrames())
    
    output_parameters = OrderedDict([("image title", ""),
                                     ("preprocessor path", float),
                                     ("post processor path", float),
                                     ("thresholding op", float),
                                     ("use ridge detection", ""),
                                     ("high contrast", int),
                                     ("low contrast", int),
                                     ("line width", int),
                                     ("minimum line length", int),
                                     ("mitochondrial footprint", float),
                                     ("branch length mean", float),
                                     ("branch length median", float),
                                     ("branch length stdev", float),
                                     ("summed branch lengths mean", float),
                                     ("summed branch lengths median", float),
                                     ("summed branch lengths stdev", float),
                                     ("network branches mean", float),
                                     ("network branches median", float),
                                     ("network branches stdev", float)])

    # Perform any preprocessing steps...
    status.showStatus("Preprocessing image...")
    preprocessing_filters(imp)
    if preprocessor_path != None:
        if preprocessor_path.exists():
            imp.show()
            preprocessor_thread = scripts.run(preprocessor_path, True)
            preprocessor_thread.get()
            imp = WindowManager.getCurrentImage()
        else:
                # Somewhat of a patch to deal with working directory being used
                # I am not sure why that gets used. It does not happen for the
                # postprocessing path.
                warnings.warn("Preprocessing file not found. Defaulting to None")
                preprocessor_path = None

    # Store all of the analysis parameters in the table
    try:
        preprocessor_str = preprocessor_path.getCanonicalPath()
    except:
        preprocessor_str = ""

    try:
        postprocessor_str = preprocessor_path.getCanonicalPath()
    except:
        postprocessor_str = ""

    output_parameters["preprocessor path"] = preprocessor_str
    output_parameters["post processor path"] = postprocessor_str
    output_parameters["thresholding op"] = threshold_method
    output_parameters["use ridge detection"] = str(use_ridge_detection)
    output_parameters["high contrast"] = rd_max
    output_parameters["low contrast"] = rd_min
    output_parameters["line width"] = rd_width
    output_parameters["minimum line length"] = rd_length

    imp_title = imp.getTitle()
    output_parameters["image title"] = imp_title
    
    # Determine the threshold value if not manual...
    binary = threshold_image(imp)

    imp_calibration = imp.getCalibration()
    # Get the total_area
    if binary.getNSlices() == 1:
        area = binary.getStatistics(Measurements.AREA).area
        area_fraction = binary.getStatistics(Measurements.AREA_FRACTION).areaFraction
        output_parameters["mitochondrial footprint"] =  area * area_fraction / 100.0
    else:
        mito_footprint = 0.0
        for slice in range(binary.getNSlices()):
            	binary.setSliceWithoutUpdate(slice)
                area = binary.getStatistics(Measurements.AREA).area
                area_fraction = binary.getStatistics(Measurements.AREA_FRACTION).areaFraction
                mito_footprint += area * area_fraction / 100.0
        output_parameters["mitochondrial footprint"] = mito_footprint * imp_calibration.pixelDepth

    # Generate skeleton from masked binary ...
    if use_ridge_detection and (imp.getNSlices() == 1):
        # Generate ridges using Ridge Detection if selected
        skeleton = ridge_detect(imp, rd_max, rd_min, rd_width, rd_length)
        # Crop and clear it if there is a ROI
        if imp.getRoi() != None:
            skeleton.setRoi(imp.getRoi())
            skeleton = Duplicator().crop(skeleton)
    else:
        # Generate skeleton from masked binary otherwise
        skeleton = Duplicator().run(binary)
        IJ.run(skeleton, "Skeletonize (2D/3D)", "")

    # Analyze the skeleton...
    status.showStatus("Setting up skeleton analysis...")
    skel = AnalyzeSkeleton_()
    skel.setup("", skeleton)
    status.showStatus("Analyzing skeleton...")
    skel_result = skel.run()

    status.showStatus("Computing graph based parameters...")
    branch_lengths = []
    summed_lengths = []
    graphs = skel_result.getGraph()

    for graph in graphs:
        summed_length = 0.0
        edges = graph.getEdges()
        for edge in edges:
            length = edge.getLength()
            branch_lengths.append(length)
            summed_length += length
        summed_lengths.append(summed_length)

    output_parameters["branch length mean"] = mina.statistics.mean(branch_lengths)
    output_parameters["branch length median"] = mina.statistics.median(branch_lengths)
    output_parameters["branch length stdev"] = mina.statistics.stdev(branch_lengths)

    output_parameters["summed branch lengths mean"] = mina.statistics.mean(summed_lengths)
    output_parameters["summed branch lengths median"] = mina.statistics.median(summed_lengths)
    output_parameters["summed branch lengths stdev"] = mina.statistics.stdev(summed_lengths)

    branches = list(skel_result.getBranches())
    output_parameters["network branches mean"] = mina.statistics.mean(branches)
    output_parameters["network branches median"] = mina.statistics.median(branches)
    output_parameters["network branches stdev"] = mina.statistics.stdev(branches)

    # Create/append results to a ResultsTable...
    morphology_tbl = mina.tables.SimpleSheet("Mito Morphology")
    morphology_tbl.writeRow(output_parameters, mina.tables.commentToDict(user_comment))
    morphology_tbl.updateDisplay()

	# Create overlays on the original ImagePlus and display them if 2D...
    if imp.getNSlices() == 1:
        overlay_2D(imp_original, binary, skeleton, skel_result)

    # Generate a 3D model if a stack
    if imp.getNSlices() > 1:

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

        # Add junctions in magenta
        junctions = skel_result.getListOfJunctionVoxels()
        junction_list = []
        for p in junctions:
            junction_list.append(Point3f(p.x * pixelWidth, p.y * pixelHeight, p.z * pixelDepth))
        univ.addIcospheres(junction_list, Color3f(255.0, 0.0, 255.0), 2, 1*pixelDepth, "junctions")

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

    # Perform any postprocessing steps...
    status.showStatus("Running postprocessing...")
    if postprocessor_path != None:
        if postprocessor_path.exists():
            postprocessor_thread = scripts.run(postprocessor_path, True)
            postprocessor_thread.get()

    else:
        warnings.warn("Postprocessing file not found. Defaulting to None")

    status.showStatus("Done analysis!")

# Run the script...
if (__name__=="__main__") or (__name__=="__builtin__"):
    if preview_preprocessing:
        # preview preprocessing filters but do not run the analysis 
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
            mina.filters.preview_side_by_side(imp_original, imp_filtered)
            imp_original.close()
        else:
            imp.show()

    else:
        run(imp, preprocessor_path, postprocessor_path, threshold_method, user_comment)
