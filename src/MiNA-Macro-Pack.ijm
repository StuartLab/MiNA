////////////////////////////////////////////////////////////////////////////////
//	TITLE: MiNA - Macro Pack 2D/3D/4D
// 	AUTHOR: ScienceToolkit
////////////////////////////////////////////////////////////////////////////////

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
// House keeping arrays...
var HK_FILEPATH = newArray();
var HK_TITLE = newArray();

// Summary information...
var INFO_FILEPATH = newArray();
var INFO_TITLE = newArray();
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
var INFO_COMMENT = newArray();

// Settings...
var CHANNEL_NUMBER = 1;
var THRESHOLD_METHOD = "Otsu";
var PREPROCESSING_MACRO = "None";
var VIEWER_PATH = "None";


// SETTINGS --------------------------------------------------------------------
// User interface that lets users specify various macro settings and provide a
// path to a preprocessing script.
macro "MiNA - Settings Dialog" {

    // Get options and attempt to find python scripts
    thresholdingMethods = getList("threshold.methods");

    // Settings GUI
    Dialog.create("MiNA - Settings Dialog");
    Dialog.addNumber("Channel: ", CHANNEL_NUMBER)
    Dialog.addChoice("Thresholding Algorithm: ", thresholdingMethods, THRESHOLD_METHOD);
    Dialog.addString("Preprocessing Macro/Script Path: ", PREPROCESSING_MACRO);
    Dialog.addString("MiNA-3D-Viewer.py Installation Path: ", VIEWER_PATH);
    Dialog.show()

    CHANNEL_NUMBER = round(Dialog.getNumber());
    THRESHOLD_METHOD = Dialog.getChoice();
    PREPROCESSING_MACRO = Dialog.getString();
    VIEWER_PATH = Dialog.getString();

}

// RUN THE MITO ANALYSIS MACRO -------------------------------------------------
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

    // If the title is already used, append "-new" to the end of it to make interval
    // uniquely identified.
    titleExists = false;
    for (i=0;i<HK_TITLE.length;i++) {
        if (titleExists==false && title==HK_TITLE[i]) {
            titleExists = true;
            uniqueTitle = title + "-new";
            selectWindow(title);
            rename(uniqueTitle);
        }
    }
    if (titleExists==false) {
        uniqueTitle = title;
    }
    title = uniqueTitle;

    // Record the housekeeping information for later
    HK_FILEPATH = Array.concat(HK_FILEPATH, filepath);
    HK_TITLE = Array.concat(HK_TITLE, uniqueTitle);

    // Process the image set one frame at a time, appending information to
    // the global variables with each loop
    for (f=1; f<=frames; f++) {

        selectWindow(title);
        timestamp = frameInterval * (f-1);

        // Image information
        INFO_FILEPATH = Array.concat(INFO_FILEPATH, filepath);
        INFO_TITLE = Array.concat(INFO_TITLE, uniqueTitle);
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
        setAutoThreshold(THRESHOLD_METHOD+" dark");
        run("Make Binary", "background=Dark");
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
        }

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
        // TODO: Sort out the above issue...
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
                branchLengths = Array.concat(branchLengths, getResult("Branch length", i));
            }

            // Fill in the summary info where we can using the branch lengths
            INFO_MEAN_LENGTH = Array.concat(INFO_MEAN_LENGTH, mean(branchLengths));
            INFO_MEDIAN_LENGTH = Array.concat(INFO_MEDIAN_LENGTH, median(branchLengths));
            INFO_STDEV_LENGTH = Array.concat(INFO_STDEV_LENGTH, sd(branchLengths));
            INFO_COMMENT = Array.concat(INFO_COMMENT, "");
            run("Close");
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

// ADD COMMENT -----------------------------------------------------------------
// Add a comment or tag to an analysis
macro "MiNA - Add Comment" {

    // Create a dialogue and collect the result
    Dialog.create("MiNA - Add Comment");
    Dialog.addChoice("Analysis Entry: ", HK_TITLE, HK_TITLE[HK_TITLE.length - 1]);
    Dialog.addString("Comment: ","");
    Dialog.show();

    selectedID = Dialog.getChoice();
    commentText = Dialog.getString();

    // Add the comment by looping through rows and inserting the comment for
    // rows with a matching title. Titles are unique to the analysis.
    for (i=0;i<INFO_FILEPATH.length;i++) {
        if (INFO_TITLE[i] == selectedID) {
            INFO_COMMENT[i] = commentText;
        }
    }

}

// REMOVE RESULT ---------------------------------------------------------------
// Remove a result from the analysis
macro "MiNA - Remove Result" {

    // Create a dialogue
    Dialog.create("MiNA - Remove Result");
    Dialog.addChoice("Analysis Entry: ", HK_TITLE, HK_TITLE[HK_TITLE.length - 1]);
    Dialog.show();

    selectedID = Dialog.getChoice();

    // Remove the associated rows
    // Find the start and end of an analysis with the ID and the location in the
    // housekeeping arrays
    // TODO: Probably a better way to do this...
    startIndex = 0;
    startFound = false;

    endIndex = 0;
    endFound = false;

    HKIndex = 0;

    for (i=0;i<HK_TITLE.length;i++) {
        if (HK_TITLE[i] == selectedID) {
            HKIndex = i;
        }
    }

    for (i=0; i<INFO_TITLE.length; i++) {
        if (INFO_TITLE[i] == selectedID && startFound == false) {
            startIndex = i;
            startFound = true;
        }

        if (INFO_TITLE[i] == selectedID && endFound == false) {
            if (i != INFO_TITLE.length) {
                if (INFO_TITLE[i+1] != selectedID) {
                    endIndex = i;
                    endFound = true;
                }
                else {
                    endIndex = i;
                    endFound = true;
                }
            }
        }
    }

    // Use the indices to break up the arrays, then concat them
    HK_FILEPATH = Array.concat(Array.slice(HK_FILEPATH, 0, startIndex),Array.slice(HK_FILEPATH, endIndex, HK_FILEPATH.length));
    HK_TITLE = Array.concat(Array.slice(HK_TITLE, 0, startIndex),Array.slice(HK_TITLE, endIndex, HK_TITLE.length));

    // Summary information...
    INFO_FILEPATH = Array.concat(Array.slice(INFO_FILEPATH,0,startIndex),Array.slice(INFO_FILEPATH, endIndex, INFO_FILEPATH.length));
    INFO_TITLE = Array.concat(Array.slice(INFO_TITLE,0,startIndex),Array.slice(INFO_TITLE, endIndex, INFO_TITLE.length));
    INFO_FRAME = Array.concat(Array.slice(INFO_FRAME,0,startIndex),Array.slice(INFO_FRAME, endIndex, INFO_FRAME.length));
    INFO_INDIVIDUALS = Array.concat(Array.slice(INFO_INDIVIDUALS,0,startIndex),Array.slice(INFO_INDIVIDUALS, endIndex, INFO_INDIVIDUALS.length));
    INFO_NETWORKS = Array.concat(Array.slice(INFO_NETWORKS,0,startIndex),Array.slice(INFO_NETWORKS, endIndex, INFO_NETWORKS.length));
    INFO_MEAN_LENGTH = Array.concat(Array.slice(INFO_MEAN_LENGTH,0,startIndex),Array.slice(INFO_MEAN_LENGTH, endIndex, INFO_MEAN_LENGTH.length));
    INFO_MEDIAN_LENGTH = Array.concat(Array.slice(INFO_MEDIAN_LENGTH,0,startIndex),Array.slice(INFO_MEDIAN_LENGTH, endIndex, INFO_MEDIAN_LENGTH.length));
    INFO_STDEV_LENGTH = Array.concat(Array.slice(INFO_STDEV_LENGTH,0,startIndex),Array.slice(INFO_STDEV_LENGTH, endIndex, INFO_STDEV_LENGTH.length));
    INFO_MEAN_SIZE = Array.concat(Array.slice(INFO_MEAN_SIZE,0,startIndex),Array.slice(INFO_MEAN_SIZE, endIndex, INFO_MEAN_SIZE.length));
    INFO_MEDIAN_SIZE = Array.concat(Array.slice(INFO_MEDIAN_SIZE,0,startIndex),Array.slice(INFO_MEDIAN_SIZE, endIndex, INFO_MEDIAN_SIZE.length));
    INFO_STDEV_SIZE = Array.concat(Array.slice(INFO_STDEV_SIZE,0,startIndex),Array.slice(INFO_STDEV_SIZE, endIndex, INFO_STDEV_SIZE.length));
    INFO_FOOTPRINT = Array.concat(Array.slice(INFO_FOOTPRINT,0,startIndex),Array.slice(INFO_FOOTPRINT, endIndex, INFO_FOOTPRINT.length));
    INFO_FOOTPRINT_TYPE = Array.concat(Array.slice(INFO_FOOTPRINT_TYPE,0,startIndex),Array.slice(INFO_FOOTPRINT_TYPE, endIndex, INFO_FOOTPRINT_TYPE.length));
    INFO_COMMENT = Array.concat(Array.slice(INFO_COMMENT,0,startIndex),Array.slice(INFO_COMMENT, endIndex, INFO_COMMENT.length));

}

// 3D RENDERER -----------------------------------------------------------------
// Renders a 3D image of the binary and skeleton from a multichannel stacks
macro "MiNA - 3D Viewer" {

    // Create the datasets...
    im = getTitle();
    Stack.getPosition(channel, slice, frame);

    run("Duplicate...", "title=Binary" +
    " duplicate frames=" + toString(frame) +
    " channels=2");
    selectWindow(im);
    run("Duplicate...", "title=Skeleton" +
    " duplicate frames=" + toString(frame) +
    " channels=3");

    // Open the script for the viewer to run... this is a lousy way to do this
    open(VIEWER_PATH);

}

// RESULTS VIEWER --------------------------------------------------------------
// Displays all of the results in tables which can be saved to file.
macro "MiNA - Results Viewer" {

    // Additional Information (pulled from the binary)
    Array.show("MiNA Analyse Results",
                INFO_FILEPATH,
                INFO_TITLE,
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
                INFO_FOOTPRINT_TYPE,
                INFO_COMMENT);

}

// CLEAR RESULTS ---------------------------------------------------------------
// Resets all global variables to their initial state.
macro "MiNA - Clear Tables" {

    // House keeping arrays...
    HK_FILEPATH = newArray();
    HK_TITLE = newArray();
    HK_ID = newArray();

    // Summary information...
    INFO_FILEPATH = newArray();
    INFO_TITLE = newArray();
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
    INFO_COMMENT = newArray();

}

// Generate debugging table to make things easier...
macro "Debug Table Generator" {

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
