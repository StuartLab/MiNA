////////////////////////////////////////////////////////////////////////
//	TITLE: MiNA - Macro Pack 2D/3D/4D
// 	CONTACT: valentaj94@gmail.com
////////////////////////////////////////////////////////////////////////

//	This program is free software: you can redistribute it and/or modify
//	it under the terms of the GNU General Public License as published by
//	the Free Software Foundation, either version 3 of the License, or
//	(at your option) any later version.
//
//	This program is distributed in the hope that it will be useful,
//	but WITHOUT ANY WARRANTY; without even the implied warranty of
//	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//	GNU General Public License for more details.
//
//	You should have received a copy of the GNU General Public License
//	along with this program.  If not, see <http://www.gnu.org/licenses/>.

// GLOBAL VARIABLES ------------------------------------------------------------
// Summary information...
var INFO_FILEPATH = newArray();
var INFO_FRAME = newArray();
var INFO_INDIVIDUALS = newArray();
var INFO_NETWORKS = newArray();
var INFO_MEAN_LENGTH = newArray();
var INFO_MEDIAN_LENGTH = newArray();
var INFO_STDEV_LENGTH = newArray();
var INFO_MEAN_SIZE = newArray();
var INFO_MEDIAN_SIZE = newArray();
var INFO_STDEV_SIZE = newArray();
var INFO_FOOTPRINT = newArray();
var INFO_FOOTPRINT_TYPE = newArray();

// Analyze Skeleton 2D/3D "Results" arrays...
var RESULTS_FILEPATH = newArray();
var RESULTS_TIMESTAMP = newArray();
var RESULTS_FRAME = newArray();
var RESULTS_BRANCHES = newArray();
var RESULTS_JUNCTIONS = newArray();
var RESULTS_END_POINTS = newArray();
var RESULTS_JUNCTION_VOXELS = newArray();
var RESULTS_SLAB_VOXELS = newArray();
var RESULTS_MEAN_LENGTH = newArray();
var RESULTS_TRIPLE_POINTS = newArray();
var RESULTS_QUAD_POINTS = newArray();
var RESULTS_MAX_LENGTH = newArray();

// Analyze Skeleton 2D/3D "Branch Information" (BI) arrays...
var BI_FILEPATH = newArray();
var BI_FRAME = newArray();
var BI_SKELETON_ID = newArray();
var BI_BRANCH_LENGTH = newArray();
var BI_V1X = newArray();
var BI_V1Y = newArray();
var BI_V1Z = newArray();
var BI_V2X = newArray();
var BI_V2Y = newArray();
var BI_V2Z = newArray();
var BI_EUCLIDEAN = newArray();
var BI_RUNNING_AVERAGE = newArray();
var BI_INNER_THIRD = newArray();
var BI_AVERAGE_INTENSITY = newArray();

// Settings...
var CHANNEL_NUMBER = 1;
var THRESHOLD_METHOD = "Otsu";
var PREPROCESSING_MACRO = "None";

// SINGLE IMAGE ANALYSIS MACRO -------------------------------------------------
macro "MiNA - Analyze Mitochondrial Morphology" {

    // Run some checks
    if (nImages < 1) {
        showMessage("Mina Warning!", "No images are open. Open an image first!");
        exit();
    }

    // If there is a preprocessing script, run that first
    if (PREPROCESSING_MACRO != "None" && File.exists(PREPROCESSING_MACRO) == 1) {
        runMacro(PREPROCESSING_MACRO);
    }

    // Enter background execution
    setBatchMode(true);

    // Get general information about the image being processed
    title = getTitle();
    getDimensions(imWidth, imHeight, channels, slices, frames);
    getVoxelSize(width, height, depth, unit);

    filepath = getInfo("image.directory") + '/' + getInfo("image.filename");

    if (frames > 1) {
        binaryConcatenator = "  title=BINARY open";
        skeletonConcatenator = "  title=SKELETON open";
        frameInterval = Stack.getFrameInterval();
        Stack.getUnits(xUnits, yUnits, zUnits, timeUnits, valueUnits);
    }
    else {
        frameInterval = 0.0;
    }

    // Process the image set one frame at a time, appending information to
    // the global variables with each loop
    for (f=1; f<=frames; f++) {

        selectWindow(title);
        timestamp = frameInterval * (f-1);

        // Image information
        INFO_FILEPATH = Array.concat(INFO_FILEPATH, filepath);
        INFO_FRAME = Array.concat(INFO_FRAME, f);

        // Duplicate the stack, frame by frame if time series
        if (frames > 1 && slices > 1) {
            run("Duplicate...", "title=COPY-" + toString(f) +
            " duplicate frames=" + toString(f) +
            " channels=" + toString(CHANNEL_NUMBER));
        }
        if (frames > 1 && slices ==1) {
            Stack.setFrame(f);
            run("Duplicate...", "title=COPY-" + toString(f) +
            " channels=" + toString(CHANNEL_NUMBER));
        }
        else {
            run("Duplicate...", "title=COPY-" + toString(f) +
            " duplicate channels=" + toString(CHANNEL_NUMBER));
        }

        // Create a binary copy.
        selectWindow("COPY-"+toString(f));
        run("8-bit");
        run("Duplicate...", "title=binary-" + toString(f) + " duplicate");
        selectWindow("binary-" + toString(f));
        run("Make Binary", "method=" + THRESHOLD_METHOD + " background=Dark");
        run("Magenta");

        // Calculate the mitochondrial footprint/volume (coverage)
        if (slices > 1) {
            footprint = 0.0;
            INFO_FOOTPRINT_TYPE = Array.concat(INFO_FOOTPRINT_TYPE, "Volume");
            for (s=0; s<slices; s++) {
                getStatistics(imArea, imMean);
                footprint = footprint + (imMean/255) * (imWidth*width) * (imHeight*height) * depth;
            }
        }
        else {
            getStatistics(imArea, imMean);
            INFO_FOOTPRINT_TYPE = Array.concat(INFO_FOOTPRINT_TYPE, "Area");
            footprint = (imMean/255) * (imWidth*width) * (imHeight*height);
        }
        INFO_FOOTPRINT = Array.concat(INFO_FOOTPRINT, footprint);

        // Create a skeletonized copy.
        selectWindow("binary-"+toString(f));
        run("Duplicate...", "title=skeleton-" + toString(f) + " duplicate");
        selectWindow("skeleton-"+toString(f));
        run("Skeletonize (2D/3D)");
        run("Green");

        // Analyze the skeletonized copy
        run("Analyze Skeleton (2D/3D)", "prune=none show");
        close("Tagged skeleton");
        close("COPY-" + toString(f));

        // Harvest all the information from the tables and close them.
        // Results Table...
        resultBranches = newArray();

        selectWindow("Results");
        for (i=0; i<nResults; i++) {
            // Grab the array we need for counting individuals and networks
            resultBranches = Array.concat(resultBranches, getResult("# Branches",i));

            // Grab the rest
            RESULTS_FILEPATH = Array.concat(RESULTS_FILEPATH, filepath);
            RESULTS_FRAME = Array.concat(RESULTS_FRAME, f);
            RESULTS_JUNCTIONS = Array.concat(RESULTS_JUNCTIONS, getResult("# Junctions",i));
            RESULTS_END_POINTS = Array.concat(RESULTS_END_POINTS, getResult("# End-point voxels",i));
            RESULTS_JUNCTION_VOXELS = Array.concat(RESULTS_JUNCTION_VOXELS, getResult("# Junction voxels",i));
            RESULTS_SLAB_VOXELS = Array.concat(RESULTS_SLAB_VOXELS, getResult("#Slab voxels",i));
            RESULTS_MEAN_LENGTH = Array.concat(RESULTS_MEAN_LENGTH, getResult("Average Branch Length",i));
            RESULTS_TRIPLE_POINTS = Array.concat(RESULTS_TRIPLE_POINTS, getResult("# Triple points",i));
            RESULTS_QUAD_POINTS = Array.concat(RESULTS_QUAD_POINTS, getResult("# Quadruple points",i));
            RESULTS_MAX_LENGTH = Array.concat(RESULTS_MAX_LENGTH, getResult("Branch information",i));
        }

        // Plop the result table branches into the global variable
        RESULTS_BRANCHES = Array.concat(RESULTS_BRANCHES, resultBranches);

        // Fill in the summary info depending on the branch information
        INFO_INDIVIDUALS = Array.concat(INFO_INDIVIDUALS, countIndividuals(resultBranches));
        INFO_NETWORKS = Array.concat(INFO_NETWORKS, countNetworks(resultBranches));

        //Strip non networked branches
    	networkBranchCounts = newArray(0);
    	for (i=0; i<resultBranches.length; i++) {
    		if (resultBranches[i]>1) {
    			networkBranchCounts = Array.concat(networkBranchCounts, resultBranches[i]);
    		}
    	}
        INFO_MEAN_SIZE = Array.concat(INFO_MEAN_SIZE, mean(networkBranchCounts));
        INFO_MEDIAN_SIZE = Array.concat(INFO_MEDIAN_SIZE, median(networkBranchCounts));
        INFO_STDEV_SIZE = Array.concat(INFO_STDEV_SIZE, sd(networkBranchCounts));
        run("Close");

        // Branch Information...
        // I haven't figured this out, but sometimes the program will abort with
        // no "Branch information" window being found and there will be a window.
        // I have attributed this to either some sort of a race condition, or
        // insconsistent naming of the window. As such, I will now check it
        // exists and if it doesn't, we skip this and warn later.
        windowTitles = getList("window.titles");
        exists=false;
        for (i=0; i<lengthOf(windowTitles); i++) {
            if (windowTitles[i] == "Branch information") {
                exists=true;
            }
            else {
                continue;
            }
        }
        if (exists==true) {
            IJ.renameResults("Branch information", "Results");
            selectWindow("Results");
            branchLengths = newArray();
            for (i=0; i<nResults; i++) {
                BI_FILEPATH = Array.concat(BI_FILEPATH, filepath);
                BI_FRAME = Array.concat(BI_FRAME, f);
                BI_SKELETON_ID = Array.concat(BI_SKELETON_ID, getResult("Skeleton ID", i));
                branchLengths = Array.concat(branchLengths, getResult("Branch length", i));
                BI_V1X = Array.concat(BI_V1X, getResult("V1 x",i));
                BI_V1Y = Array.concat(BI_V1Y, getResult("V1 y",i));
                BI_V1Z = Array.concat(BI_V1Z, getResult("V1 z",i));
                BI_V2X = Array.concat(BI_V2X, getResult("V2 x",i));
                BI_V2Y = Array.concat(BI_V2Y, getResult("V2 y",i));
                BI_V2Z = Array.concat(BI_V2Z, getResult("V2 z",i));
                BI_EUCLIDEAN = Array.concat(BI_EUCLIDEAN, getResult("Euclidean distance",i));
                BI_RUNNING_AVERAGE = Array.concat(BI_RUNNING_AVERAGE, getResult("running average length",i));
                BI_INNER_THIRD = Array.concat(BI_INNER_THIRD, getResult("average intensity (inner 3rd)", i));
                BI_AVERAGE_INTENSITY = Array.concat(BI_AVERAGE_INTENSITY, getResult("average intensity", i));
            }

            // Add the branch length information to the global variables
            BI_BRANCH_LENGTH = Array.concat(BI_BRANCH_LENGTH, branchLengths);

            // Fill in the summary info where we can using the branch lengths
            INFO_MEAN_LENGTH = Array.concat(INFO_MEAN_LENGTH, mean(branchLengths));
            INFO_MEDIAN_LENGTH = Array.concat(INFO_MEDIAN_LENGTH, median(branchLengths));
            INFO_STDEV_LENGTH = Array.concat(INFO_STDEV_LENGTH, sd(branchLengths));
            run("Close");

            // Make the binary a bit "transparent"...
            selectWindow("binary-" + toString(f));
            run("Divide...", "value=4.000 stack");

        }

        // Merge the time series data
        if (frames > 1) {
            binaryConcatenator = binaryConcatenator + " image" + toString(f) + "=binary-" + toString(f);
        }
        if (frames > 1) {
            skeletonConcatenator = skeletonConcatenator + " image" + toString(f) + "=skeleton-" + toString(f);
        }

        // Update the user with a progress bar
        showProgress(f,frames);
    }

    // Create a time series from the images/stack
    if (frames > 1) {

        // Exclude other images
        binaryConcatenator = binaryConcatenator + " image" + toString(frames+1) + "=[-- None --]";
        binaryConcatenator = binaryConcatenator + " image" + toString(frames+1) + "=[-- None --]";

        // Make a stack for each channel
        run("Concatenate...", binaryConcatenator);
        run("Concatenate...", skeletonConcatenator);

        //Merge threm together with a copy of the original data
        selectWindow(title);
        run("Duplicate...", "title=COPY duplicate channels=" + toString(CHANNEL_NUMBER));
        selectWindow("COPY");
        run("8-bit");
        run("Grays");
        run("Merge Channels...", "c1=COPY c2=BINARY c3=SKELETON create");
    }

    // For non time series, just merge 'em
    else {
        selectWindow(title);
        run("Duplicate...", "title=COPY duplicate channels=" + toString(CHANNEL_NUMBER));
        selectWindow("COPY");
        run("8-bit");
        run("Grays");
        run("Merge Channels...", "c1=COPY c2=binary-1 c3=skeleton-1 create");
    }

    //Display the output stack
    setBatchMode("exit and display");

}

// RESULTS VIEWER --------------------------------------------------------------
// Displays all of the results in tables which can be saved to file.
macro "MiNA - Results Viewer" {

    // Additional Information (pulled from the binary)
    Array.show("Additional Parameters",
                INFO_FILEPATH,
                INFO_FRAME,
                INFO_INDIVIDUALS,
                INFO_NETWORKS,
                INFO_MEAN_LENGTH,
                INFO_MEDIAN_LENGTH,
                INFO_STDEV_LENGTH,
                INFO_MEAN_SIZE,
                INFO_MEDIAN_SIZE,
                INFO_STDEV_SIZE,
                INFO_FOOTPRINT,
                INFO_FOOTPRINT_TYPE);


    // Display AnalyzeSkeleton Results Table Output
    Array.show("Results",
                RESULTS_FILEPATH,
                RESULTS_FRAME,
                RESULTS_BRANCHES,
                RESULTS_JUNCTIONS,
                RESULTS_END_POINTS,
                RESULTS_JUNCTION_VOXELS,
                RESULTS_SLAB_VOXELS,
                RESULTS_MEAN_LENGTH,
                RESULTS_TRIPLE_POINTS,
                RESULTS_QUAD_POINTS,
                RESULTS_MAX_LENGTH);

    // Display AnalyzeSkeleton Branch Information output
    Array.show("Branch Information",
                BI_FILEPATH,
                BI_FRAME,
                BI_SKELETON_ID,
                BI_BRANCH_LENGTH,
                BI_V1X,
                BI_V1Y,
                BI_V1Z,
                BI_V2X,
                BI_V2Y,
                BI_V2Z,
                BI_EUCLIDEAN,
                BI_RUNNING_AVERAGE,
                BI_INNER_THIRD,
                BI_AVERAGE_INTENSITY);

}

// CLEAR RESULTS ---------------------------------------------------------------
// Resets all global variables to their initial state.
macro "MiNA - Clear Tables" {

    // Summary information table
    INFO_FILEPATH = newArray();
    INFO_FRAME = newArray();
    INFO_INDIVIDUALS = newArray();
    INFO_NETWORKS = newArray();
    INFO_MEAN_LENGTH = newArray();
    INFO_MEDIAN_LENGTH = newArray();
    INFO_STDEV_LENGTH = newArray();
    INFO_MEAN_SIZE = newArray();
    INFO_MEDIAN_SIZE = newArray();
    INFO_STDEV_SIZE = newArray();
    INFO_FOOTPRINT = newArray();
    INFO_FOOTPRINT_TYPE = newArray();

    // Analyze Skeleton 2D/3D "Results" arrays...
    RESULTS_FILEPATH = newArray();
    RESULTS_FRAME = newArray();
    RESULTS_BRANCHES = newArray();
    RESULTS_JUNCTIONS = newArray();
    RESULTS_END_POINTS = newArray();
    RESULTS_JUNCTION_VOXELS = newArray();
    RESULTS_SLAB_VOXELS = newArray();
    RESULTS_MEAN_LENGTH = newArray();
    RESULTS_TRIPLE_POINTS = newArray();
    RESULTS_QUAD_POINTS = newArray();
    RESULTS_MAX_LENGTH = newArray();

    // Analyze Skeleton 2D/3D "Branch Information" (BI) arrays...
    BI_FILEPATH = newArray();
    BI_FRAME = newArray();
    BI_SKELETON_ID = newArray();
    BI_BRANCH_LENGTH = newArray();
    BI_V1X = newArray();
    BI_V1Y = newArray();
    BI_V1Z = newArray();
    BI_V2X = newArray();
    BI_V2Y = newArray();
    BI_V2Z = newArray();
    BI_EUCLIDEAN = newArray();
    BI_RUNNING_AVERAGE = newArray();
    BI_INNER_THIRD = newArray();
    BI_AVERAGE_INTENSITY = newArray();

}

// SETTINGS --------------------------------------------------------------------
// User interface that lets users specify various macro settings and provide a
// path to a preprocessing script.
macro "MiNA - Settings Dialog" {

    // Get options
    thresholdingMethods = getList("threshold.methods");

    // Settings GUI
    Dialog.create("MiNA - Settings Dialog");
    Dialog.addNumber("Channel: ", CHANNEL_NUMBER)
    Dialog.addChoice("Thresholding Algorithm: ", thresholdingMethods, THRESHOLD_METHOD);
    Dialog.addString("Preprocessing Macro: ", PREPROCESSING_MACRO);
    Dialog.show()

    CHANNEL_NUMBER = round(Dialog.getNumber());
    THRESHOLD_METHOD = Dialog.getChoice();
    PREPROCESSING_MACRO = Dialog.getString();
}


// SUBROUTINES -----------------------------------------------------------------
/*
*   Count the number of individuals in an image.
*
*   @param: {array} branchCounts The 1D array of branch counts pulled from the
*                   output of the Analyze Skeleton 2D/3D plugin.
*   @return: {float} individuals The number of individuals detected, returned as
*                    a floating point for future statistical calculations.
*/
function countIndividuals(branchCounts) {
	entries = branchCounts.length;
	individuals = 0.0;
	for (i=0; i<entries; i++) {
		if (branchCounts[i] <= 1) {
			individuals = individuals + 1.0;
		}
		else {
		}
	}
	return(individuals);
}

/*
*   Count the number of networks in an image.
*
*   @param: {array} branchCounts The 1D array of branch counts pulled from the
*                                output of the Analyze Skeleton 2D/3D plugin.
*   @return: {float} networks The number of networks detected, returned as
*                             a floating point for future statistical
*                             calculations.
*/
function countNetworks(branchCounts) {
	entries = branchCounts.length;
	networks = 0.0;
	for (i=0; i<entries; i++) {
		if (branchCounts[i] > 1) {
			networks = networks + 1.0;
		}
		else {
		}
	}
	return(networks);
}

/*
*   Count the number of branches in network structures.
*
*   @param: {array} branchCounts The 1D array of branch counts pulled from the
*                                output of the Analyze Skeleton 2D/3D plugin.
*   @return {float} networkBranches The total number of branches that exist in
*                                   network structures.
*/
function countNetworkBranches(branchCounts) {
	entries = data.length;
	networkBranches = 0.0;
	for (i=0; i<entries; i++) {
		if (branchCounts[i] > 1) {
			networkBranches = networkBranches + branchCounts[i];
		}
		else {
		}
	}
	return(total);
}

/*
*   Calculates the mean from an array.
*
*   @param: {array} data The array to calculate the mean on.
*   @return: {float} ave The array mean.
*/
function mean(data) {
	entries = data.length;
	total = 0.0;
	for (i=0; i<entries; i++) {
		total = total + data[i];
	}
	ave = total/parseFloat(entries);
	return(ave);
}

/*
*   Calculates the median from an array.
*
*   @param: {array} data The array to calculate the mean on.
*   @return: {float} med The array median.
*/
function median(data) {
	entries = data.length;
	sorted = Array.sort(data);
    if (entries > 0) {
    	if (entries%2 == 0) {
    		iF = (entries/2);
    		med = parseFloat((sorted[(iF-1)] + sorted[iF])/2.0);
    	}
    	else {
    		iF = ((entries-1)/2);
    		med = sorted[iF];
    	}

    	return(med);
    }
    else {
        return("");
    }
}

/*
*   Calculates the population standard deviation from an array.
*
*   @param: {array} data The array to calculate the mean on.
*   @return: {float} std The array's population standard deviation.
*/
function sd(data) {
	entries = data.length;
	N = parseFloat(entries);
	u = mean(data);
	sse = 0.0;
	for (i=0; i<entries; i++) {
		sse = sse + (pow((data[i] - u),2.0)/N);
	}
	std = sqrt(sse);
	return(std);
}
