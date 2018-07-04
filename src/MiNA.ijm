////////////////////////////////////////////////////////////////////////////////
//                                                                            //
//      MACRO: Mitochondrial Network Analysis (MiNA) - V2.0.0                 //
//      AUTHOR: Andrew Valente                                                //
//      EMAIL: valentaj94@gmail.com                                           //
//      LAST EDITED: October 6th,2017                                         //
////////////////////////////////////////////////////////////////////////////////

//    This program is free software: you can redistribute it and/or modify
//    it under the terms of the GNU General Public License as published by
//    the Free Software Foundation, either version 3 of the License, or
//   (at your option) any later version.
//
//    This program is distributed in the hope that it will be useful,
//    but WITHOUT ANY WARRANTY; without even the implied warranty of
//    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//    GNU General Public License for more details.
//
//    You should have received a copy of the GNU General Public License
//    along with this program.  If not, see <http://www.gnu.org/licenses/>.


//Global Variables--------------------------------------------------------------
//Output Arrays...
var filenameARRAY = newArray();
var individualsARRAY = newArray();
var networksARRAY = newArray();
var meanLengthARRAY = newArray();
var medianLengthARRAY = newArray();
var sdLengthARRAY = newArray();
var meanBranchesARRAY = newArray();
var medianBranchesARRAY = newArray();
var sdBranchesARRAY = newArray();
var mitoAreaARRAY = newArray();

//Preprocessing Modifiers
var CLAHE = false;
var CLAHE_BLOCKSIZE = 127;
var CLAHE_HISTOGRAM = 256;
var CLAHE_MAXSLOPE = 3;

var MED = false;
var MED_RADIUS = 2;

var TOPHAT = false;

var UNSHARP = false;
var UNSHARP_RADIUS = 2;
var UNSHARP_STRENGTH = 0.6;


// Macro Main-------------------------------------------------------------------
macro "MiNA - Analyze Morphology" {

    if (nImages == 0) {
		showMessage("No images are open.");
		exit();
	}

	//Produce GUI to set preprocessing preferences
	setUp();

    //Duplicate region of interest and collect general information
    showStatus("MiNA: Getting image information...");
	run("Duplicate...", "title=Original");
	selectWindow("Original");
	run("Grays");
	getDimensions(width, height, channels, slices, frames);
	getPixelSize(unit, pixelWidth, pixelHeight);

	//Preprocess image
	preprocessing();

	//Produce binary duplicate image for skeleton and binary outline...
	showStatus("MiNA: Producing test skeleton...");
	run("Duplicate...", "title=TestSkeleton");
	selectWindow("TestSkeleton");
	run("32-bit");
	run("Make Binary");
	run("8-bit");
    run("Duplicate...", "title=Outline");

    //Calculate the mitochondrial footprint
	getStatistics(area, Mean, min, max);
	mitoArea = pow(pixelWidth, 2.0) * parseFloat(width) * parseFloat(height) * (Mean / parseFloat(max)) ;

    //Skeletonize the binary image and overlay it onto the original
    selectWindow("TestSkeleton");
	run("Skeletonize (2D/3D)");
	run("Green");
	selectWindow("Original");
	run("Add Image...", "image=TestSkeleton x=0 y=0 opacity=100 zero");

    //Create an outline and overlay it...
    selectWindow("Outline");
    run("Find Edges");
    run("Magenta");
    selectWindow("Original");
    run("Add Image...", "image=Outline x=0 y=0 opacity=100 zero");

	//Add a scale bar to it.
	size = toString(round(0.25*parseFloat(width)*parseFloat(pixelWidth)));
	run("Scale Bar...", "width=" + size + " height=4 font=14 color=White background=Black location=[Lower Right] bold overlay");

	//Ask the user if this is acceptable.
	Dialog.create("Skeleton Proofing");
	Dialog.addMessage("Is the skeleton produced acceptable? Click OK if so.");
	Dialog.show()

	//Analyze the skeleton using the Analyze Skeleton plugin.
	showStatus("MiNA: Processing skeleton...");
	selectWindow("TestSkeleton");
	run("Analyze Skeleton (2D/3D)", "prune=none show display");
    close("Outline");
	close("Tagged skeleton");
	close("TestSkeleton");
	close("TestSkeleton-labeled-skeletons");

	//Collect relevant output from the tables and close these tables.
	selectWindow("Results"); rows = nResults;
	BranchCounts = newArray(rows);
	for (i=0; i<rows; i++) {
		BranchCounts[i] = getResult("# Branches", i);
	}
	selectWindow("Results"); run("Close");

	IJ.renameResults("Branch information", "Results");
	selectWindow("Results"); rows = nResults;
	BranchLengths = newArray(rows);
	for (i=0; i<rows; i++) {
		BranchLengths[i] = getResult("Branch length", i);
	}
	run("Close");

	//Feature counts
	individuals = parseFloat(countIndividuals(BranchCounts));
	networks = parseFloat(countNetworks(BranchCounts));

	//Size descriptors for lengths
	meanLength = mean(BranchLengths);
	medianLength = median(BranchLengths);
	sdLength = sd(BranchLengths);

	//Strip non networked branches
	networkBranchCounts = newArray(0);
	for (i=0; i<BranchCounts.length; i++) {
		if (BranchCounts[i]>1) {
			networkBranchCounts = Array.concat(networkBranchCounts, BranchCounts[i]);
		}
	}

	meanBranches = mean(networkBranchCounts);
	medianBranches = median(networkBranchCounts);
	sdBranches = sd(networkBranchCounts);

	Measurement = newArray("Individuals",
			       "Networks",
			       "Mean Branch Length",
			       "Median Branch Length",
			       "Length Standard Deviation",
			       "Mean Network Size (Branches)",
			       "Median Network Size (Branches)",
			       "Network Size Standard Deviation",
			       "Mitochondrial Footprint");

	Value = newArray(individuals,
			 networks,
			 meanLength,
			 medianLength,
			 sdLength,
			 meanBranches,
			 medianBranches,
			 sdBranches,
			 mitoArea);

	Units = newArray("Counts",
			 "Counts",
			 unit,
			 unit,
			 unit,
			 "Counts",
			 "Counts",
			 "Counts",
			 unit+" squared");

	Array.show("MiNA Output", Measurement, Value, Units);

}

//Count Individuals...
function countIndividuals(data) {
	entries = data.length;
	total = 0.0;
	for (i=0; i<entries; i++) {
		if (data[i] <= 1) {
			total = total + 1;
		}
		else {
		}
	}
	return(total);
}

//Count Networks...
function countNetworks(data) {
	entries = data.length;
	total = 0.0;
	for (i=0; i<entries; i++) {
		if (data[i] > 1) {
			total = total + 1;
		}
		else {
		}
	}
	return(total);
}

//Count Branches in Networks...
function countNetworkBranches(data) {
	entries = data.length;
	total = 0.0;
	for (i=0; i<entries; i++) {
		if (data[i] > 1) {
			total = total + data[i];
		}
		else {
		}
	}
	return(total);
}

//Mean...
function mean(data) {
	entries = data.length;
	total = 0.0;
	for (i=0; i<entries; i++) {
		total = total + data[i];
	}
	ave = total/parseFloat(entries);
	return(ave);
}

//Median...
function median(data) {
	entries = data.length;
	sorted = Array.sort(data);
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

//Standard deviation...
function sd(data) {
	entries = data.length;
	N = parseFloat(entries);
	u = mean(data);
	sse = 0.0;
	for (i=0; i<entries; i++) {
		sse = sse + (pow((data[i] - u),2)/N);
	}
	std = sqrt(sse);
	return(std);
}

//Preprocessing set up GUI...
function setUp() {
	//Produce GUI to set preprocessing preferences
    Dialog.create("Preprocessing");
    Dialog.addMessage("Processing to Apply");
    Dialog.addCheckbox("CLAHE", false);
	Dialog.addSlider("Blocksize: ", 1, 256, 127);
	Dialog.addSlider("Histogram Bins: ", 1, 256, 256);
	Dialog.addSlider("Maximum Slope: ", 0, 10, 3);
	Dialog.addCheckbox("Median Filter", false);
	Dialog.addSlider("Radius: ", 0, 20, 2);
	Dialog.addCheckbox("Unsharp Mask", false);
	Dialog.addSlider("Radius: ", 0, 20, 2);
	Dialog.addSlider("Mask Strength: ", 0, 0.9, 0.6);
	Dialog.addCheckbox("Tophat (Iannetti et al., 2016)" , false);

    Dialog.show();

	CLAHE = Dialog.getCheckbox();
	CLAHE_BLOCKSIZE = Dialog.getNumber();
	CLAHE_HISTOGRAM = Dialog.getNumber();
	CLAHE_MAXSLOPE = Dialog.getNumber();

	MED = Dialog.getCheckbox();
	MED_RADIUS = Dialog.getNumber();

	UNSHARP = Dialog.getCheckbox();
	UNSHARP_RADIUS = Dialog.getNumber();
	UNSHARP_STRENGTH = Dialog.getNumber();
	TOPHAT = Dialog.getCheckbox();

}

//Preprocessing...
function preprocessing() {

	//Apply unsharp mask to image if selected
	selectWindow("Original");
	if (UNSHARP == true) {
		run("Unsharp Mask...", "radius="+toString(UNSHARP_RADIUS)+" mask="+toString(UNSHARP_STRENGTH));
	}

    //Apply contrast limited adaptive histogram equalization if selected
	if (CLAHE == true) {
		run("Enhance Local Contrast (CLAHE)",
                    "blocksize="+toString(CLAHE_BLOCKSIZE)+" histogram="+toString(CLAHE_HISTOGRAM)+" maximum="+toString(CLAHE_MAXSLOPE)+" mask=*None* fast_(less_accurate)");
	}

    //Apply median filtering if selected
	if (MED == true) {
		run("Median...", "radius="+toString(MED_RADIUS));
	}

	//Apply tophat filter if selected
	if (TOPHAT == true) {
		run("Convolve...", "text1=[0 0 -1 -1 -1 0 0 \n0 -1 -1 -1 -1 -1 0\n-1 -1 3 3 3 -1 -1\n-1 -1 3 4 3 -1 -1\n-1 -1 3 3 3 -1 -1\n0 -1 -1 -1 -1 -1 0\n0 0 -1 -1 -1 0 0 \n] normalize");
	}
}
