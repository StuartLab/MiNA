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

#@ String median_string
#@ String unsharp_string
#@ String clahe_string
#@ String ridge_string
#@ String thresh_string

#@ OpService ops
#@ ScriptService scripts
#@ StatusService status
#@ UIService ui

#@ Boolean preview_preprocessing

import mina.statistics 
import mina.tables 
import mina.filters 
from mina import mina_view

import warnings

from collections import OrderedDict

from ij import IJ
from ij import WindowManager
from ij.measure import Measurements
from ij.plugin import Duplicator

from net.imglib2.img.display.imagej import ImageJFunctions

from sc.fiji.analyzeSkeleton import AnalyzeSkeleton_;

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


def user_preprocessing(imp, preprocessor_path):
    if preprocessor_path != None:
        if preprocessor_path.exists():
            imp.show()
            preprocessor_thread = scripts.run(preprocessor_path, True)
            preprocessor_thread.get()
            imp = WindowManager.getCurrentImage()
    else:
        warnings.warn("Preprocessing file not found. Defaulting to None")


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
                                     ("network branches stdev", float),
                                     ("donuts", int)])

    # Perform any preprocessing steps...
    status.showStatus("Preprocessing image...")
    user_preprocessing(imp, preprocessor_path)
    preprocessing_filters(imp)

    # Store all of the analysis parameters in the table
    if preprocessor_path.exists():
        preprocessor_str = preprocessor_path.getCanonicalPath()
    else:
        preprocessor_str = ""

    if postprocessor_path.exists():
        postprocessor_str = postprocessor_path.getCanonicalPath()
    else:
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
        for slice in range(1, binary.getNSlices()+1):
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

    num_donuts = 0
    for graph in graphs:
        summed_length = 0.0
        edges = graph.getEdges()
        vertices = {}
        for edge in edges:
            length = edge.getLength()
            branch_lengths.append(length)
            summed_length += length

            # keep track of the number of times a vertex appears in edges in a given graph
            for vertex in [edge.getV1(), edge.getV2()]:
                if vertex in vertices:
                    vertices[vertex] += 1
                else:
                    vertices[vertex] = 1

        is_donut = True
        # donut_arms = 0
        for k in vertices:
            # if a vertex appeared less than twice
            if vertices[k] <= 1:
                # donut_arms += 1
                # if donut_arms > 1:
                is_donut = False
                break

        if is_donut and len(edges) >= 1:
            num_donuts += 1

        summed_lengths.append(summed_length)

    output_parameters["donuts"] = num_donuts

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
        mina_view.overlay_2D(imp_original, binary, skeleton, skel_result)

    # Generate a 3D model if a stack
    if imp.getNSlices() > 1:
        mina_view.create_3Dmodel(imp_calibration, binary, skel_result)

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
        param_table = [median_string, unsharp_string, clahe_string, ridge_string, thresh_string]
        mina_view.preview_images(imp, preprocessing_filters, threshold_image, use_ridge_detection, ridge_detect, rd_max, rd_min, rd_width, rd_length, param_table,
            user_preprocessing, preprocessor_path)
    else:
        run(imp, preprocessor_path, postprocessor_path, threshold_method, user_comment)
