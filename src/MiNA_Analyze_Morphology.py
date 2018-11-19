#@ ImagePlus imp
#@ File(label="Pre-processor path:", value = "", required=False) preprocessor_path
#@ File(label="Post-processing path:", required=False) postprocessor_path
#@ String(label = "Thresholding Op:", value="otsu", choices={"huang", "ij1", "intermodes", "isoData", "li", "maxEntropy", "maxLikelihood", "mean", "minError", "minimum", "moments", "otsu", "percentile", "renyiEntropy", "rosin", "shanbhag", "triangle", "yen"}) threshold_method
#@ Boolean(label="Use ridge detection (2D only):", value=False) use_ridge_detection
#@ BigInteger(label="Maximum threshold:", value=75, required=False) rd_max
#@ BigInteger(label="Minimum threshold:", value=5, required=False) rd_min
#@ BigInteger(label="Line width:", value=1, required=False) rd_width
#@ BigInteger(label="Line length:", value=3, required=False) rd_length
#@ String(label="User comment: ", value="") user_comment

#@ OpService ops
#@ ScriptService scripts
#@ StatusService status
#@ UIService ui

import java.awt.Color
from java.io import File

import eztables.statistical


from ij import IJ
from ij import ImagePlus
from ij import WindowManager
from ij.gui import ImageRoi
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

# The run function..............................................................
def run(imp, preprocessor_path, postprocessor_path, threshold_method, user_comment):

    output_parameters = {"image title" : "",
    "mitochondrial footprint" : float,
    "branch length mean" : float,
    "branch length median" : float,
    "branch length stdevp" : float,
    "network branches mean" : float,
    "network branches median" : float,
    "network branches stdevp" : float}

    output_order = ["image title",
    "mitochondrial footprint",
    "branch length mean",
    "branch length median",
    "branch length stdevp",
    "network branches mean",
    "network branches median",
    "network branches stdevp"]

    # Perform any preprocessing steps...
    status.showStatus("Preprocessing image...")
    if preprocessor_path != None:
        if preprocessor_path.exists():
            preprocessor_thread = scripts.run(preprocessor_path, True)
            preprocessor_thread.get()
            imp = WindowManager.getCurrentImage()
    else:
        pass

    # Create and ImgPlus copy of the ImagePlus for thresholding with ops...
    status.showStatus("Determining threshold level...")
    imp_title = imp.getTitle()
    slices = imp.getNSlices()
    frames = imp.getNFrames()
    output_parameters["image title"] = imp_title
    imp_calibration = imp.getCalibration()
    imp_channel = Duplicator().run(imp, imp.getChannel(), imp.getChannel(), 1, slices, 1, frames)
    img = ImageJFunctions.wrap(imp_channel)

    # Determine the threshold value if not manual...
    binary_img = ops.run("threshold.%s"%threshold_method, img)
    binary = ImageJFunctions.wrap(binary_img, 'binary')
    binary.setCalibration(imp_calibration)
    binary.setDimensions(1, slices, 1)

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
    # Generate ridges first if using Ridge Detection
    if use_ridge_detection and (imp.getNSlices() == 1):
        skeleton = ridge_detect(imp, rd_max, rd_min, rd_width, rd_length)
    else:
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
    graphs = skel_result.getGraph()

    for graph in graphs:
        edges = graph.getEdges()
        for edge in edges:
            branch_lengths.append(edge.getLength())

    output_parameters["branch length mean"] = eztables.statistical.average(branch_lengths)
    output_parameters["branch length median"] = eztables.statistical.median(branch_lengths)
    output_parameters["branch length stdevp"] = eztables.statistical.stdevp(branch_lengths)

    branches = list(skel_result.getBranches())
    output_parameters["network branches mean"] = eztables.statistical.average(branches)
    output_parameters["network branches median"] = eztables.statistical.median(branches)
    output_parameters["network branches stdevp"] = eztables.statistical.stdevp(branches)

    # Create/append results to a ResultsTable...
    status.showStatus("Display results...")
    if "Mito Morphology" in list(WindowManager.getNonImageTitles()):
        rt = WindowManager.getWindow("Mito Morphology").getTextPanel().getOrCreateResultsTable()
    else:
        rt = ResultsTable()

    rt.incrementCounter()
    for key in output_order:
        rt.addValue(key, str(output_parameters[key]))

    # Add user comments intelligently
    if user_comment != None and user_comment != "":
        if "=" in user_comment:
            comments = user_comment.split(",")
            for comment in comments:
                rt.addValue(comment.split("=")[0], comment.split("=")[1])
        else:
            rt.addValue("Comment", user_comment)

    rt.show("Mito Morphology")

	# Create overlays on the original ImagePlus and display them if 2D...
    if imp.getNSlices() == 1:
    	status.showStatus("Generate overlays...")
    	IJ.run(skeleton, "Green", "")
    	IJ.run(binary, "Magenta", "")

    	skeleton_ROI = ImageRoi(0,0,skeleton.getProcessor())
    	skeleton_ROI.setZeroTransparent(True)
    	skeleton_ROI.setOpacity(1.0)
    	binary_ROI = ImageRoi(0,0,binary.getProcessor())
    	binary_ROI.setZeroTransparent(True)
    	binary_ROI.setOpacity(0.35)

    	overlay = Overlay()
    	overlay.add(binary_ROI)
    	overlay.add(skeleton_ROI)

    	imp.setOverlay(overlay)
    	imp.updateAndDraw()

    # Generate a 3D model if a stack
    if imp.getNSlices() > 1:

        univ = Image3DUniverse()
        univ.show()
        univ.addMesh(binary)

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

    # Perform any postprocessing steps...
	status.showStatus("Running postprocessing...")
    if postprocessor_path != None:
    	if postprocessor_path.exists():
            postprocessor_thread = scripts.run(postprocessor_path, True)
            postprocessor_thread.get()

    else:
		pass

    status.showStatus("Done analysis!")

# Run the script...
if (__name__=="__main__") or (__name__=="__builtin__"):
    run(imp, preprocessor_path, postprocessor_path, threshold_method, user_comment)
