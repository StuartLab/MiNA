#Table of Contents
1. [Introduction](https://github.com/ScienceToolkit/MiNA#introduction)  
2. [System Requirements](https://github.com/ScienceToolkit/MiNA#system-requirements)  
3. [Installing the Software](https://github.com/ScienceToolkit/MiNA#installing-the-software)  
4.[About the Macros](https://github.com/ScienceToolkit/MiNA#about-the-macros)  
4.1. [Terminology Used](https://github.com/ScienceToolkit/MiNA#terminology-used)  
4.2. [Output Parameters](https://github.com/ScienceToolkit/MiNA#output-parameters)  
4.3. [Optional Preprocessing](https://github.com/ScienceToolkit/MiNA#optional-preprocessing)  
5. [Macro Usage](https://github.com/ScienceToolkit/MiNA#macro-usage)  
5.1. [MiNA Single Image](https://github.com/ScienceToolkit/MiNA#mina-single-image)  
5.2. [MiNA Batch Analysis](https://github.com/ScienceToolkit/MiNA#mina-batch-analysis)  
6. [Limitations](https://github.com/ScienceToolkit/MiNA#limitations)  
7. [Bibliography](https://github.com/ScienceToolkit/MiNA#bibliography)  

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

##Optional Preprocessing

#Usage

##MiNA Single Image

##MiNA Batch Analysis

#Limitations

#Bibliography
Arganda-Carreras, I., 2016. AnalyzeSkeleton. ImageJ. Available at: http://imagej.net/AnalyzeSkeleton.  

Leonard, A.P. et al., 2015. Quantitative analysis of mitochondrial morphology and membrane potential in living cells using high-content imaging, machine learning, and morphological binning. Biochimica et Biophysica Acta - Molecular Cell Research, 1853(2), pp.348–360. Available at: http://dx.doi.org/10.1016/j.bbamcr.2014.11.002.  

Nikolaisen, J. et al., 2014. Automated quantification and integrative analysis of 2D and 3D mitochondrial shape and network properties. PLoS ONE, 9(7), pp.1–16.  

Saalfeld, S., 2010. Enhance Local Contrast (CLAHE). ImageJ. Available at: http://imagej.net/Enhance_Local_Contrast_(CLAHE).






