# MiNA - ImageJ Macros for Mitochondrial Morphology Research

--------------------------------------------------------------------------------
## The TODO List :wrench: :computer: :coffee:
- [x] Create a deprecated release for the old master branch.
- [ ] Add an easy way to generate a 3D rendering of the skeleton and binary.
- [x] Add ability to add comments or flags to analysis results
- [ ] Complete the documentation.

--------------------------------------------------------------------------------

## Introduction
MiNA (Mitochondrial Network Analysis) is a project aimed at making the analysis and characterization of mitochondrial network morphology more accurate, faster, and less subjective. It consists of a set of ImageJ macros that are used to measure meaningful morphological parameters from fluorescence micrographs of labelled mitochondria. The first macro was published early in 2017, the article for which can be found  [here](https://doi.org/10.1016/j.acthis.2017.03.001).

The project began as a result of extensive work with adherent mammalian cell cultures in the laboratory of [Dr. Jeff Stuart](https://brocku.ca/mathematics-science/biology/directory/jeff-stuart/) at Brock University. As others adopt the macros for additional applications and cell lines, we use the feedback from these users to extend and further generalize the tools.

## Suitability and Weaknesses

:exclamation: __PLEASE READ THIS SECTION BEFORE USING THE MACROS__ :exclamation:

Is this set of macros suitable for your data? MiNA relies fluorescence microscopy, binarized signals, and morphological skeletons to provide several parameters describing the mitochondrial morphology captured in a micrograph. These parameters can be helpful, but the user must ensure the analysis was accurate for their case before going further. It is important to understand the limitations of the analysis and where you may run into more or less accurate depictions of the true mitochondrial structure. This analysis aims to estimate topological relationships and mitochondrial dimensions, but its accuracy is primarily dependent on data being appropriate.

The analysis makes a few assumptions regarding the shapes of mitochondria, the properties of the dataset, and the sample preparation itself. While it is unlikely to fully meet all requirements completely, the closer the data is to the requirements, the more faithful the  analysis will be. The assumptions are:
* [x] Physically independent mitochondria are resolved.
* [x] Mitochondria are tube-like or ellipsoidal.
* [x] Structures are well resolved.
* [x] Signal is homegenous within the bounds of the mitochondria
* [x] Signal of label is clearly detectable at the voxel/pixel level.

If the images are noisy, blurry, at too low of a magnification, then the analysis will not provide faithful results. The sample characteristics are also important. MiNA is suitable for non-aggregated, filamentous mitochondrial morphologies. Tightly packed mitochondria, non-tubular or non-spherical morphologies, and uneven labelling of the mitochondria can all lead to eroneous analysis. It is the vital the user thoroughly test their analysis to ensure it is a faithful representation of the mitochondrial morphologies.

## Recent Changes
Users will notice that the user experience of the macros has changed from the original published version. The processing method's are still the same, but additional parameters and options have been included. The macro has also been extended to operate on 2D images, 3D stacks, and timeseries data (2D and 3D). The setup options, output paramaters, and work flow are all described in the background section of the README file.

The first release contains the original published macro as well as version 2 macros which have 3D and time series functionality, but are largely untested. Note that the versioning semantics were simplified here out to be the update date as yyyy.mm.dd and this format will continue to be used. Each patch or update will get its own release.

## Overview
### Included Macros
| MiNA Macro | Description |
|-|-|
| Settings Dialog | The _Settings Dialog_ provides an interface for setting up parameters used by the analysis macro. It is here where you can set the channel of the input image to process, the binarization method to use, and the location of a preprocessing script or macro.|
| Analyze Mitochondrial Morphology | This macro takes care of the analysis. It generates a binary representation of the image for determining the number of connected components and area/volume calculations. A morphological skeleton is in turn generated from this for capturing topological information. How each parameter is determined is described in the Measured Parameters section. |
| Add Comment | This macro prompts the user to add a comment or tag to an analysis result. It lets you select the image filename whose results should have the comment added. Uncommented results contain an empty string ("") in the comment column. |
| 3D Viewer | If a 3D stack or 3D timeseries is processed, this macro can be used to generate a 3D rendering of the skeleton and binarized mitochondria using the 3D Viewer plugin capabilities. This is intended to be used as an accuracy check for 3D analysis. Due to the time consuming process of generating the model, it is done for only the currently selected time point in the case of 3D time series analysis results. |
| Results Viewer | Opens all of the results tables to allow for saving the data. In the case of a single time series analysis, it will also plot out some line graphs of the parameters. |
| Clear Tables | Removes all results allowing you to begin analysis with fresh results tables without resetting the settings back to their defaults. |

### Measured Parameters
A description is provided for each of the parameters provided by the macros. Additionally, how you would perform the process to obtain the value manually is provided. We use the manual process to compare the output results on a reference dataset as a way of checking for issues with the macros themselves. However, it also provides a good overview as to how the macros work and what the parameters physically mean rather than just what they are trying to capture.

#### Individuals
:construction: TODO: Complete this section... :construction:

#### Networks
:construction: TODO: Complete this section... :construction:

#### Mean, Median, and Standard Deviation of Branch Lengths
:construction: TODO: Complete this section... :construction:

#### Mean, Median, and Standard Deviation of Network Size
:construction: TODO: Complete this section... :construction:

#### Mean, Median, and Standard Deviation of Thickness
:construction: TODO: Complete this section... :construction:

#### Footprint (Area or Volume)
:construction: TODO: Complete this section... :construction:


### Description of Settings Options
| __Setting__ | __Description__ |
|-|-|
| Channel | The mitochondrial labelled channel to process for a multichannel image. Defaults to 1, which works in single channel images as well.
| Thresholding Algorithm | How the threshold should be determined. Currently, only global methods are available. Information on each of the algorithms can be found at the [Auto Threshold page](https://imagej.net/Auto_Threshold). Defaults to Otsu. |
| Preprocessing Macro/Script Path _(Optional)_ |The path to a preprocessing macro to be run on the dataset prior to analysis. The macro or script should process the entire stack in place and when completed the window and ROI (if applicable) should be selected. Defaults to "None" and does not search for an existing path. |
| MiNA-3D-Viewer.py Installation Path _(Optional)_|  The location of the MiNA-3D-Viewer.py file on the computer being used for the analysis. This is only necessary if you wish to render a 3D model of a binarized and skeletonized stack. Defaults to "None" and does not search for an existing path. |

--------------------------------------------------------------------------------
## User Guide
### Installation
:warning: __Have you already read the _[Suitability, Benefits, and Weaknesses](#suitability,-benefits,-and-weaknesses)_ section?__ :warning:

1. First, if you do not already have it installed on your computer, install Fiji. It is a wonderful distribution of ImageJ containing many additional useful plugins and ImageJ2 at its core.
2. Download the latest release of MiNA from the [releases](https://github.com/ScienceToolkit/MiNA/releases) page. New releases with bug fixes will be made available there.
3. Unzip the archive to an appropriate location on your computer.
4. Open Fiji and install the macros by clicking __Plugins__ -> __Macros__ -> __Install...__ and navigate to the file MiNA-Macro-Pack.ijm. The file is in the src folder of the archive you unzipped. Now the tools are installed and you may begin! Note that this will need to be done each time you use the macro pack.

    ___Optional step...___
5. If you plan on performing 3D analysis, you will want to use the 3D Viewer script to check out how your analysis went. You need to tell MiNA where that file is. To do that, run the macro __MiNA - Settings__. In the _MiNA-3D-Viewer.py Installation Path_ field, enter the path to the MiNA-3D-Viewer.py file, which is also in the src folder of the unzipped archive (example: /home/my_name/Desktop/MiNA/src/MiNA-3D-Viewer.py).

### Analyzing an Image
#### Loading an Image
:construction: TODO: Complete this section... :construction:

#### Generating a Pre-Processing Script
:construction: TODO: Complete this section... :construction:

#### Running the Analysis
:construction: TODO: Complete this section... :construction:

#### Checking for Errors
:construction: TODO: Complete this section... :construction:

#### Analyzing 3D Stacks
:construction: TODO: Complete this section... :construction:

#### Analyzing Time Series Datasets
:construction: TODO: Complete this section... :construction:

### Working with the Results
:construction: TODO: Complete this section... :construction:

#### Adding a Comment or Flag to a Result
:construction: TODO: Complete this section... :construction:

#### Exporting the Results
:construction: TODO: Complete this section... :construction:

## Cited Material
:construction: TODO: Complete this section... :construction:

## Further Reading
:construction: TODO: Complete this section... :construction:
