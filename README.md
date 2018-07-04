# MiNA - ImageJ Tools for Mitochondrial Morphology Research

--------------------------------------------------------------------------------
## The TODO List :wrench: :computer: :coffee:
To give you an idea of what I am working on and what you will see next from MiNA, take  a peak at my TODO list. Do you have an idea for added functionality or a way to improve the analysis routine? Feel free to open an [issue](https://github.com/ScienceToolkit/MiNA/issues) to let me know, or add it yourself and make a [pull request](https://yangsu.github.io/pull-request-tutorial/). :octocat:

- [x] Create a clean release of the original macros.
- [x] Complete the README file.
- [ ] Rewrite as IJ2 Jython parameterized script.
- [ ] Extend for 3D analysis.
- [ ] Extend for time series analysis.
- [ ] Extend for multiple ROI support.
- [ ] Add workspace style functionality for concatenating consecutive outputs.
- [ ] Move to SciJava plugin framework.
- [ ] Create a Fiji update site for the project.

--------------------------------------------------------------------------------

## Introduction
MiNA (Mitochondrial Network Analysis) is a project aimed at making the analysis and characterization of mitochondrial network morphology more accurate, faster, and less subjective. It consists of a set of ImageJ macros that are used to measure meaningful morphological parameters from fluorescence micrographs of labelled mitochondria. The first macro was published early in 2017, the article for which can be found  [here](https://doi.org/10.1016/j.acthis.2017.03.001).

The project began as a result of extensive work with adherent mammalian cell cultures in the laboratory of [Dr. Jeff Stuart](https://brocku.ca/mathematics-science/biology/directory/jeff-stuart/) at Brock University. As others adopt the macros for additional applications and cell lines, we use the feedback from these users to extend and further generalize the tools.

## Releases
Releases are available from the [releases page](https://github.com/ScienceToolkit/MiNA/releases) of the repository. You can download the release that suits your fancy, but I recommend always grabbing the latest as it will have the most recent bug fixes and more features.


## Suitability and Weaknesses

:exclamation: __PLEASE READ THIS SECTION BEFORE USING THE MACROS__ :exclamation:

Is this set of macros suitable for your data? MiNA relies on fluorescence microscopy, binarized signals, and morphological skeletons to provide several parameters describing the mitochondrial morphology captured in a micrograph. These parameters can be helpful, but the user must ensure the analysis was accurate for their case before going further. It is important to understand the limitations of the analysis and where you may run into more or less accurate depictions of the true mitochondrial structure. This analysis aims to estimate topological relationships and mitochondrial dimensions, but its accuracy is primarily dependent on data being appropriate. Ultimately, the user is responsible for validating their analysis. However, some general pointers are provided here.

The analysis makes a few assumptions regarding the shapes of mitochondria, the properties of the dataset, and the sample preparation itself. While it is unlikely to fully meet all requirements completely, the closer the data is to the requirements, the more faithful the  analysis will be. The assumptions are:

* [x] Physically independent mitochondria are resolved.
* [x] Mitochondria are tube-like or ellipsoidal.
* [x] Structures are well resolved.
* [x] Signal is homegenous within the bounds of the mitochondria
* [x] Signal of label is clearly detectable at the voxel/pixel level.

If the images are noisy, blurry, not at taken with sufficient resolution, then the analysis will not provide faithful results. The sample characteristics are also important. MiNA is suitable for non-aggregated, largely filamentous mitochondrial morphologies. Tightly packed mitochondria, non-tubular or non-spherical morphologies, and uneven labelling of the mitochondria can all lead to eroneous analysis. It is the vital the user thoroughly validate their analysis to ensure it is a faithful representation of the mitochondrial morphologies.

## Overview
### Measured Parameters
A description is provided for each of the parameters provided by the macros. Additionally, how you would perform the process to obtain the value manually is provided. We use the manual process to compare the output results on a reference dataset as a way of checking for issues with the macros themselves. However, it also provides a good overview as to how the macros work and what the parameters physically mean rather than just what they are trying to capture in a biological sense. The [synthetic demo](/doc/test_image.tif) data provides an example of the different morphologies MiNA tries to capture.

![Demo data.](/doc/test_image.png)

The simplified morphologies depicted here from left to right are punctate, rod-like or elongated, and network. MiNA lumps punctate and rod-like structures into a single category - _individuals_. These different structures can be represented by different morphological skeletons, which provides a means to categorize structures automatically. In practice, generating an accurate skeleton can be difficult and preprocessing may be necessary. The figure below shows the skeleton for the 3 objects and where some of the measurements come from.

![Skeletal representation of mitochondria.](/doc/skeleton_representation.png)

#### Individuals and Networks
An individual or network is defined using information generated by analyzing a morphological skeleton. This analysis is done using the [AnalyzeSkeleton plugin](https://imagej.net/AnalyzeSkeleton). A section of code runs through the _# Branches_ column and bins each graph as being an individual or a skeleton. A network simply has more than one branch, while an individual is counted if it does not have more than one branch. The table for the demo data is shown below. For this case there is one network and two individuals.

![Branch counts results table.](/doc/skeleton_branches.png)

#### Mean, Median, and Standard Deviation of Branch Lengths
The mean, median, and standard deviation of branch lengths is calculated from the Branch Length column of the results table generated by the [AnalyzeSkeleton plugin](https://imagej.net/AnalyzeSkeleton). To do this by clicking around Fiji, you would do the following:
1. Binarize the image.
2. Then generate a morphological skeleton with _Plugins &rarr; Skeleton &rarr; Skeletonize 2D/3D_.
3. Analyze the skeleton using _Analyze &rarr; Skeleton &rarr; AnalyzeSkeleton_. Running the analysis will generate the results table shown below.

    ![Branch lengths column.](/doc/skeleton_branch_lengths.png)

5. Calculate the mean, median, and standard deviation of the column values.

#### Mean, Median, and Standard Deviation of Network Size
The mean, median, and standard deviation of network size is calculated from the _# Branches_ column of the results table generated by the [AnalyzeSkeleton plugin](https://imagej.net/AnalyzeSkeleton) plugin after stripping results for puncta (single pixel graphs). For the example image the mean and median will both be 3 as there is only one network. To do this by clicking around Fiji, you would do the following:

1. Binarize the image.
2. Then generate a morphological skeleton with _Plugins &rarr; Skeleton &rarr; Skeletonize 2D/3D_.
3. Analyze the skeleton using _Analyze &rarr; Skeleton &rarr; AnalyzeSkeleton_. Running the analysis will generate the results table shown below.

    ![Branch lengths column.](/doc/skeleton_branches.png)

4. Remove entries where the branch counts is not greater than 1 (not a network).
5. Calculate the mean, median, and standard deviation of the remaining values.

#### Footprint (Area)
Area is simply the number of non-zero pixels in a binarized copy of the image multiplied by the area of each pixel. There are other nicer ways to do this, but the technique here mimics what the macro does. The equivalent way of determining this value without the macro is as follows:

1. Generate a binary image such that background is 0 and foreground is 255. This can be done by going through _Image &rarr; Adjust &rarr; Threshold..._ and hitting _Apply_. Note MiNA version 1 macros use the last selected thresholding method. On a fresh instance of Fiji this will be "Default." Future versions will allow selecting the algorithm to use as well as local thresholding routines.

    ![Binarize the image.](/doc/binary_footprint_1.png)

2. Determine the number of signal positive pixels. Easy way to do this is to multiply the mean of the binary by the count and divide by the maximum.

    ![Binarize the image.](/doc/binary_footprint_2.png)

3. Once you have the number of positive pixels, multiply it by the pixel width squared to get the total area. The pixel width can be found by navigating to _Image &rarr; Properties_.

--------------------------------------------------------------------------------
## User Guide :rocket:
### Installation
:warning: __Have you already read the Suitability, Benefits, and Weaknesses section?__ :warning:

1. First, if you do not already have it installed on your computer, install [Fiji](https://fiji.sc/). It is a wonderful distribution of ImageJ containing many additional useful plugins and ImageJ2 at its core.
2. Download the latest release of MiNA from the [releases](https://github.com/ScienceToolkit/MiNA/releases) page. New releases with bug fixes will be made available there.
3. Unzip the archive to an appropriate location on your computer.
4. Open Fiji and install the macros by clicking __Plugins__ -> __Macros__ -> __Install...__ and navigate to the file MiNA.ijm. The file is in the src folder of the archive you unzipped. Now the tools are installed and you may begin! Note that this will need to be done each time you use the macros (in the future it will be a one time plugin install).

### Loading an Image
First you will want to load an image and ensure you have any calibration information correctly set for the image. For loading scientific formats, we recommend using the [Bioformats Importer](https://imagej.net/Bio-Formats#Bio-Formats_Importer) directly. To load your image with the importer plugin, navigate to Plugins &rarr; Bioformats &rarr; Bioformats importer as shown below.

![Bioformats importer screenshot.](/doc/bioformats_importer.png)

Once you have an image loaded, check the calibration information were loaded correctly using Image &rarr; Properties. This will open a dialog as shown below with the pixel spacing information and units.

![Image properties screenshot.](/doc/image_properties.png)
### Running the Analysis
To run the analysis simple navigate to the macro through Plugins &rarr; Macros &rarr; MiNA - Analyze Mitochondrial Morphology. A prompt will appear as shown below. By default, no options are selected. You can proceed to run it without any preprocessing options to start. Preprocessing can help with getting the skeleton representation closer to the topology you see visually, but it can also introduce bias so it should be used cautiously.

![MiNA dialog screenshot.](/doc/MiNA_dialog.png)

In the future, preprocessing will be separated from running and fully extensible to allow for running custom scripts as part of the analysis. It is being separated because what works best can be highly variable and it is not sensible to try and incorporate every option users may want in MiNA itself. To proceed with the options selected, clock OK. This will begin the analysis.

### Checking for Errors
Once the analysis has begun, a pop up will appear after a skeleton is generated and overlaid upon the preprocessed image. Green is the skeleton and magenta is the  outline of the binarized area. A second pop up dialog will ask the user if the skeleton is suitable. At this point you will want to look for poorly resolved areas that may be erroneously connected by the skeleton, or artificial breaks where there is inhomegenous fluorescent intensity. If everything looks good, you can proceed and click OK. The dialog is shown below.

![MiNA dialog screenshot.](/doc/skeleton_quality_control.png)

### Working with the Results
If the user clicks OK and proceeds, the skeleton will be analyzed using the  [AnalyzeSkeleton plugin](https://imagej.net/AnalyzeSkeleton) and some additional code in the macro itself. The results of the analysis are summarized into a number of parameters and displayed in a table as shown below.

![MiNA dialog screenshot.](/doc/results_dialog.png)
