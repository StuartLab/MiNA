
**IMPORTANT**  
GitHub does not support directly downloading single files. To "download" the scripts for use click on the script, open the file in browser and click the RAW button to view the script as plain text. You may then right click, select save as, and save the file with the filename as shown in the GitHub folder.


#Table of Contents
1. [Introduction](#introduction)  
2. [System Requirements](#system-requirements)  
3. [Installing the Software](#installing-the-software)  
4.[About the Macros](#about-the-macros)  
4.1. [Terminology Used](#terminology-used)  
4.2. [Output Parameters](#output-parameters)  
4.3. [Optional Preprocessing](#optional-preprocessing)  
5. [Macro Usage](#macro-usage)  
5.1. [MiNA Single Image](#mina-single-image)  
5.2. [MiNA Batch Analysis](#mina-batch-analysis)  
6. [Limitations](#limitations)  
7. [Bibliography](#bibliography)  

#Introduction
The Mitochondrial Network Analysis (MiNA) macro tools were developed for ImageJ to provide biologists studying mitochondrial network morphology and dynamics with a simple, effective method of quantifying mitochondrial network morphology in images of cultured adherent animal cells. Mitochondrial network morphology is a dynamic characteristic of cells that is related to the efficiency of oxidative phosphorylation, cell cycle phase, apoptotic cell death, and other important aspects of normal and aberrant cell physiology. MiNA is based on a foundation of analytical techniques that have been developed by  various authors.  The work is largely inspired by previous work conducted by Nikolaisen _et al_ (2014).

MiNA uses existing ImageJ plugins and additional processing to provide a rapid method for measuring parameters related to mitochondrial network morphology. This documentation describes the measurements made using MiNA, how the measurements are made, and the limitations of the measurements. The basic algorithm used by the plugin for preprocessing the images and analyzing the mitochondrial network morphology is described in detail and the reasoning for each step explained.

#System Requirements
MiNA was produced for use in [ImageJ](https://imagej.nih.gov/ij/index.html) and [FIJI](https://fiji.sc/) software platforms. If using FIJI, all necessary plugins are present for using the tool and MiNA may simply be installed and used. Both of these image processing packages will run on Windows, Mac OS, and Linux operating systems. For use with ImageJ, additional plugins are required and are listed below.  

1. [AnalyzeSkeleton - 	Ignacio Arganda-Carreras](http://imagej.net/AnalyzeSkeleton)  
2. [Bio-Formats - Open Microscopy Environment](http://imagej.net/Bio-Formats)  
3. [Enhance Local Contrast (CLAHE) - Stephen Saalfeld](http://imagej.net/Enhance_Local_Contrast_(CLAHE))  

#Installing the Software
1. Download and install FIJI according to the documentation on the software web page.  
2. Download the MiNA Single Image or Batch Analysis macros.  
3. Install the macro tool by opening FIJI, then _clicking Plugins -> Macros -> Install_. Select the appropriate downloaded file (either MiNA Single Image.ijm or MiNA Batch Analysis.ijm) and click OK to proceed. A new icon will appear in the toolbar if it successfully installs as shown below in figure 1.  

![Figure 1](https://github.com/ScienceToolkit/MiNA/blob/master/Documentation%20Images/F1.png)

#About the Macros
The macro tools operate to summarize the morphological characteristics of the mitochondrial material using a morphological skeleton and binary image. The morphological skeleton is a copy of the image after it has been converted to a binary (black and white only) and thinned such that the structures are represented by lines 1 pixel wide. A summative flowchart depicting how the plugin operates is shown in figure 2.  

![Figure 2](https://github.com/ScienceToolkit/MiNA/blob/master/Documentation%20Images/F2.png)

##Terminology Used
Nomenclature used to describe the morphological properties of the mitochondrial networks is adopted and modified from Leonard *et al* (2015). The terms used and their definitions are listed below and visually demonstrated in figure 3.   
* **End-Point Pixel** - A pixel having one or no neighbouring pixels that are a part of the skeleton. These mark the terminus of rods and network branches, as well as represent small punctate objects.  
* **Junction Pixel** - A pixel having three or more neighbouring pixels that are a part of the skeleton.These mark the intersection points of branches in networks.  
* **Slab Pixel** - A pixel having exactly two neighbouring pixels that are a part of the skeleton. 
* **Individual** - a mitochondrial feature that does not contain any branch pixels in its representation. This category would include puncta, rods, and large/round mitochondria. 
* **Network** - a mitochondrial feature containing at least one branch pixel in its representation.
* **Branch** - the stretch of slab pixels connecting one end point pixel or junction pixel to the next. An individual is a single branch while a network is composed of multiple branches.  

![Figure 3](https://github.com/ScienceToolkit/MiNA/blob/master/Documentation%20Images/F3.png)

##Output Parameters  
The parameters computed by MiNA are summarized as follows: 

**Filepath:** This is the complete filepath for the image processed by the *Batch Analysis* macro. It is not included in the *Single Image output.*

**Individuals:** This is the number of objects in the image that do not contain a junction pixel. 

**Networks:** This is the number of objects in the image that contain at least 1 junction pixel.  

**Mean Branch Length:** The average length of all branches (distances between connected end point or junction pixels). This is calculated using branches that would be categorized as belonging to either individuals OR networks. The variable is called meanLength in the *Batch Analysis* output table.  

**Median Branch Length:** The median length of all branches (distances between connected end point or junction pixels). This is calculated using branches that would be categorized as belonging to either individuals OR networks. The variable is called medianLength in the *Batch Analysis* output table.  

**Length Standard Deviation:** This is the standard deviation of all branches lengths treated as a population. It is called lengthStandardDeviation in the *Batch Analysis* output table.  

**Mean Network Size (Branches):** This is the mean number of branches per network. The variable is called medianNetworkSize in the *Batch Analysis* output table.    

**Median Network Size (Branches):** This is the median number of branches per network. The variable is called medianNetworkSize in the *Batch Analysis* output table.      

**Network Size Standard Deviation:** This is the standard deviation of the number of branches in each independent network as calculated using the formula for the population standard deviation. The variable is called medianNetworkSize in the *Batch Analysis* output table  

**Mitochondrial Footprint:**This is the total area in the image consumed by signal after being separated from the background. It is the number of pixels in the binary image containing signal multiplied by the area of a pixel if the calibration information is present.  

##Optional Preprocessing
MiNA offers three options for preprocessing conveniently, though users can choose to preprocess the images separately as they wish and then analyse the image with the macro. The options available are **Unsharp Mask, CLAHE, and Median filter**. These options help to sharpen edge details and discontinuities in the mitochondrial network, enhance contrast locally throughout the image, and reduce the negative effects of salt and pepper noise. The sequential use of these in producing an accurate skeleton is demonstrated in figure 4.  

![Figure 4](https://github.com/ScienceToolkit/MiNA/blob/master/Documentation%20Images/F4.png)  

**Unsharp Mask:** Subtracts a blurred image using a gaussian blur of radius 2. This step helps to sharpen the image producing a visual change similar to deconvolution. This is useful on most images, especially those that appear blurry.  
**CLAHE:** Contrast limited adaptive histogram equalization helps to maximize the use of the available dynamic range locally. It is applied in the macro with an arbitrary neighbourhood block size of 127 pixels. This is useful if the image is not particularly bright and there is poor contrast between the signal and background.  
**Median Filtering:** Median filtering uses a 2 pixel radius to remove spurious signals (such as noise) from the image. This is useful if you find the skeleton produced is overly fragmented or irregular, which may result if the image is noisy. It should also be used when unsharp masking or CLAHE is used as these both amplify noise significantly.  

#Usage
**IMPORTANT**  
GitHub does not support directly downloading single files. To "download" the scripts for use click on the script, open the file in browser and click the RAW button to view the script as plain text. You may then right click, select save as, and save the file with the filename as shown in the GitHub folder.

##MiNA Single Image
To process a single image file or ROI, first download and install [MiNA Single Image.ijm](https://github.com/ScienceToolkit/MiNA/blob/master/MiNA%20ImageJ%20Macros/MiNA%20Batch%20Analysis.ijm). Once the macro is installed simply open the image you wish to process, choose any of the preprocessing steps you wish to apply when prompted, and click OK. The use of the macro is demonstrated in figure 5.  

![Figure 5](https://github.com/ScienceToolkit/MiNA/blob/master/Documentation%20Images/F5.png) 

##MiNA Batch Analysis
To process a folder full of image files, first download and install [MiNA Batch Analysis.ijm](https://github.com/ScienceToolkit/MiNA/blob/master/MiNA%20ImageJ%20Macros/MiNA%20Batch%20Analysis.ijm). Once the macro is installed simply click the MiNA icon and follow the on screen instructions, filling out what preprocessing you wish to apply, what folder is to be processed, and proofing the skeletons produced to let the program know whether they are to be included in the analysis or skipped.  

#Limitations
MiNA effectively processes two dimensional images of fluorescently labelled mitochondrial networks. However, the analysis relies on the production of an accurate skeleton to faithfully report parameters representing measurements of the mitochondrial features. Blurry or noisy images can produce poor results, where non-connected regions are represented as connected or connected regions are represented with discontinuities. Further more, the images currently must be two dimensional, which limits its usage to thin adherant cultured mammalian cells. Extensive three dimensional can not be captured by the macro as the structured are all projected into two dimensions. This problem has been noted and the methods to deal with thick cells have been investigated and reported upon by others (Nikolaisen, 2015). The artifacts that may be produced in the analysis are summarized in figure 6.  

![Figure 6](https://github.com/ScienceToolkit/MiNA/blob/master/Documentation%20Images/F6.png) 

#Bibliography
Leonard, A.P. et al., 2015. Quantitative analysis of mitochondrial morphology and membrane potential in living cells using high-content imaging, machine learning, and morphological binning. Biochimica et Biophysica Acta - Molecular Cell Research, 1853(2), pp.348–360. Available at: http://dx.doi.org/10.1016/j.bbamcr.2014.11.002.  

Nikolaisen, J. et al., 2014. Automated quantification and integrative analysis of 2D and 3D mitochondrial shape and network properties. PLoS ONE, 9(7), pp.1–16.  







