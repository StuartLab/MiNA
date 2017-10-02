////////////////////////////////////////////////////////////////////////
//	TITLE: MiNA - Macro Pack 2D/3D/4D + Batch Process Folder
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
// Output Arrays...
var FILENAME = newArray();
var FILEPATH = newArray();
var FRAME = newArray();
var TIMESTAMP = newArray();
var INDIVIDUALS = newArray();
var NETWORKS = newArray();
var MEAN_BRANCH_LENGTH = newArray();
var MEDIAN_BRANCH_LENGTH = newArray();
var SD_BRANCH_LENGTH = newArray();
var MEAN_BRANCHES = newArray();
var MEDIAN_BRANCHES = newArray();
var SD_BRANCHES = newArray();
var MITO_COVERAGE = newArray();
var LENGTH_UNITS = newArray();
var COVERAGE_UNITS = newArray();

// Preprocessing Constants...
var CLAHE = false;
var CLAHE_BLOCKSIZE = 127;
var CLAHE_HISTOGRAM = 256;
var CLAHE_MAXSLOPE = 3;

var MED = false;
var MED_RADIUS = 2;

var MEXICAN_HAT = false;
var MEXICAN_HAT_RADIUS = 5;

var UNSHARP = false;
var UNSHARP_RADIUS = 2;
var UNSHARP_STRENGTH = 0.6;

// PREPROCESSING MACRO ---------------------------------------------------------
macro "MiNA - Preprocessing Helper" {

}

// SINGLE IMAGE ANALYSIS MACRO -------------------------------------------------
macro "MiNA - Single Image" {

}

// BATCH PROCESS FOLDER --------------------------------------------------------
macro "MiNA - Process Folder" {

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
	entries = data.length;
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
        return();
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
		sse = sse + (pow((data[i] - u),2)/N);
	}
	std = sqrt(sse);
	return(std);
}

/*
*   Analyze mitochondrial network morphology. Operates on a single image or
*   stack. For time series analysis, the function is called on each frame.
*/
function analyzeMitos() {

    // Check that an image is open.
    if (nImages == 0) {
        showMessage("No images are open.");
        exit();
    }

    // Enter silent execution.
    setBatchMode(true);



}
