////////////////////////////////////////////////////////////////////////////////
//                                                                            //
//      MACRO: Mitochondrial Network Analysis (MiNA) - Batch Analysis         //
//      AUTHOR: Andrew Valente                                                // 
//      EMAIL: valentaj94@gmail.com                                           //
//      LAST EDITED: October 31st, 2016                                       //
//                                                                            //  
////////////////////////////////////////////////////////////////////////////////

//Global Variables--------------------------------------------------------------
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

// Macro Main-------------------------------------------------------------------
macro "MiNA Batch Analysis Action Tool - C000C111C222C333C444C555C666C777D00D01D02D03D04D05D06D07D08D09D0aD0bD0cD0dD0eD0fD12D14D17D1bD1eC777C888C999D10D11D13D15D16D18D19D1aD1cD1dD1fD20D21D22D23D24D25D26D27D28D29D2aD2bD2cD2dD2eD2fD30D31D32D33D34D35D36D37D38D39D3aD3bD3cD3dD3eD3fD40D41D42D43D44D45D46D47D48D49D4aD4bD4eD4fD50D51D52D53D54D55D56D57D58D59D5aD5bD5eD5fD60D61D62D63D64D65D66D67D68D69D6bD6eD6fD70D71D72D73D74D75D76D77D78D79D7bD7eD7fD80D81D82D83D84D85D89D8bD8eD8fD90D91D92D93D94D99D9bD9eD9fDa0Da1Da2Da3Da8Da9DabDaeDafDb0Db1Db2DbeDbfDc0Dc1DceDcfDd0Dd1Dd6Dd7Dd8Dd9DdaDdbDdcDddDdeDdfDe0De1De2De3De4De5De6De7De8De9DeaDebDecDedDeeDefDf0Df1Df2Df3Df4Df5Df6Df7Df8Df9DfaDfbDfcDfdDfeDff" {

    //Produce GUI to set preprocessing preferences
    Dialog.create("Preprocessing");
    Dialog.addMessage("Processing to Apply");
    Dialog.addCheckboxGroup(3,1, 
                            newArray("Unsharp Mask", "CLAHE", "Median Filtering"), 
                            newArray(false, false, false));
    Dialog.show();
        
    //Collect values selected by user.
	UNSHARP = Dialog.getCheckbox();
	CLAHE = Dialog.getCheckbox();
	MED = Dialog.getCheckbox();
	imageCount = nImages(); 
    
    //Select a Directory to Process
	dir = getDirectory("Choose a Directory ");
	
	//Process all files
	processFiles(dir);
	
	//Rename to readable column names for user
    filepaths = filenameARRAY;
    individuals = individualsARRAY;
    networks = networksARRAY;
    meanLength = meanLengthARRAY;
    medianLength = medianLengthARRAY;
    lengthStandardDeviation = sdLengthARRAY;
    meanNetworkSize = meanBranchesARRAY;
    medianNetworkSize = medianBranchesARRAY;
    networkSizeStandardDeviation = sdBranchesARRAY;
    mitochondrialFootprint = mitoAreaARRAY;
	
	//Display table of results
	Array.show("MiNA Output",
	           filepaths,
	           individuals,
	           networks,
	           meanLength,
	           medianLength,
	           lengthStandardDeviation,
	           meanNetworkSize,
	           medianNetworkSize,
	           networkSizeStandardDeviation,
	           mitochondrialFootprint);
	           
}

//Functions I need--------------------------------------------------------------
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

//Process Files...
function processFiles(dir) {
  list = getFileList(dir);
  for (i=0; i<list.length; i++) {
      if (endsWith(list[i], "/"))
          processFiles(""+dir+list[i]);
      else {
         path = dir+list[i];
         processFile(UNSHARP, CLAHE, MED, path);
      }
  }
}
  
//Process file...
function processFile(UNSHARP, CLAHE, MED, path) {

    //Open the image
    run("Bio-Formats Macro Extensions");
    Ext.setId(path);
    Ext.openImage(path,0);

    //Duplicate region of interest and collect general information
    showStatus("MiNA: Getting image information...");
	run("Duplicate...", "title=Original");
	selectWindow("Original");
	run("Grays");
	getDimensions(width, height, channels, slices, frames);
	getPixelSize(unit, pixelWidth, pixelHeight);
        
    //Apply unsharp mask to image if selected
	selectWindow("Original");
	if (UNSHARP == true) {
		run("Unsharp Mask...", "radius=2 mask=0.60");
	}
        
    //Apply contrast limited adaptive histogram equalization if selected
	if (CLAHE == true) {
		run("Enhance Local Contrast (CLAHE)", 
                    "blocksize=127 histogram=256 maximum=3 mask=*None* fast_(less_accurate)");
	}

    //Apply median filtering if selected
	if (MED == true) {
		run("Median...", "radius=2");
	}

	//Produce binary duplicate image for skeleton
	showStatus("MiNA: Producing test skeleton...");
	run("Duplicate...", "title=TestSkeleton");
	selectWindow("TestSkeleton");
	run("32-bit");
	run("Make Binary");
	run("8-bit");
	
    //Calculate the mitochondrial footprint
	getStatistics(area, Mean, min, max);
	mitoArea = pow(pixelWidth, 2.0) * parseFloat(width) * parseFloat(height) * (Mean / parseFloat(max)) ;
	
    //Skeletonize the binary image and overlay it onto the original
	run("Skeletonize");
	run("Red");
	selectWindow("Original");
	run("Add Image...", "image=TestSkeleton x=0 y=0 opacity=100 zero");

	//Add a scale bar to it.
	size = toString(round(0.25*parseFloat(width)*parseFloat(pixelWidth)));
	run("Scale Bar...", "width=" + size + " height=4 font=14 color=White background=Black location=[Lower Right] bold overlay");
        
        QC=true;
	
	if (QC == true) {

		//Analyze the skeleton using the Analyze Skeleton plugin.
		selectWindow("TestSkeleton");
		run("Analyze Skeleton (2D/3D)", "prune=none show display");
		close("Tagged skeleton");
		close("TestSkeleton"); 
		close("TestSkeleton-labeled-skeletons");
		
		//Collect relevant output from the tables, procede to close these tables.
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
		networkBranchCounts = newArray();
		for (i=0; i<BranchCounts.length; i++) {
			if (BranchCounts[i]>1) {
				networkBranchCounts = Array.concat(networkBranchCounts, BranchCounts[i]);
			}
		}
		
		meanBranches = mean(networkBranchCounts);
		medianBranches = median(networkBranchCounts);
		sdBranches = sd(networkBranchCounts);
	
        //Update column vectors
        filenameARRAY = Array.concat(filenameARRAY, path);
        individualsARRAY = Array.concat(individualsARRAY, individuals);
        networksARRAY = Array.concat(networksARRAY, networks);
        meanLengthARRAY = Array.concat(meanLengthARRAY, meanLength);
        medianLengthARRAY = Array.concat(medianLengthARRAY, medianLength);
        sdLengthARRAY = Array.concat(sdLengthARRAY, sdLength);
        meanBranchesARRAY = Array.concat(meanBranchesARRAY, meanBranches);
        medianBranchesARRAY = Array.concat(medianBranchesARRAY, medianBranches);
        sdBranchesARRAY = Array.concat(sdBranchesARRAY, sdBranches);
        mitoAreaARRAY = Array.concat(mitoAreaARRAY, mitoArea);

		//close images
		titles = getList("image.titles");
		for (i=0; i<titles.length; i++) {
			selectWindow(titles[i]);
			close();
		}
	}

	else {
		//Fill row with no data cells
        filenameARRAY = Array.concat(filenameARRAY, path);
        individualsARRAY = Array.concat(individualsARRAY, "");
        networksARRAY = Array.concat(networksARRAY, "");
        meanLengthARRAY = Array.concat(meanLengthARRAY, "");
        medianLengthARRAY = Array.concat(medianLengthARRAY, "");
        sdLengthARRAY = Array.concat(sdLengthARRAY, "");
        meanBranchesARRAY = Array.concat(meanBranchesARRAY, "");
        medianBranchesARRAY = Array.concat(medianBranchesARRAY, "");
        sdBranchesARRAY = Array.concat(sdBranchesARRAY, "");
        mitoAreaARRAY = Array.concat(mitoAreaARRAY, "");

		//close images
		titles = getList("image.titles");
		for (i=0; i<titles.length; i++) {
			selectWindow(titles[i]);
			close();
		}
	}
}

