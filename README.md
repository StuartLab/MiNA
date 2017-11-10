# MiNA - A Tool for Mitochondrial Research
## Introduction
MiNA (Mitochondrial Network Analysis) is a project aimed at making the analysis and characterization of mitochondrial network morphology more accurate, faster, and less subjective. The first macro was published early in 2017, the article for which can be found  [here](https://doi.org/10.1016/j.acthis.2017.03.001). The project began as a result of extensive work with adherent mammalian cell cultures in the laboratory of [Dr. Jeff Stuart](https://brocku.ca/mathematics-science/biology/directory/jeff-stuart/) at Brock University. As others adopt the macro and we push its usage under different experimental scenarios, we aim to generalize its usability and improve its accuracy fostering objective morphologic analysis in mitochondria research.

This project is under continuous development and this README file will be used to communicate the status and advancements being made. In version 1's development, changes were originally made directly to the file. For version 2, the macro will still remain a single file, but the changes will be made as new file uploads named according to the magnitude of changes made. MiNA_V200 is version 2.0.0, where the numbering is [version].[functional update].[bug fix]. Older copies of the file will remain in the repo and new ones will be added when changes are made. This numbering convention will be used from here on out unless otherwise stated. A version change indicates a loss of backwards compatibility, a functional update may add functionality without removing anything, and a bug fix simply fixes any errors in the macro.

## Status
Currently the project has entered development of the second version of the tool. The most recent copy of the 2.0.0 macro is available, but not fully functional. The version 2 macro pack aims to 3D and time series functionality. It removes the pre-processing options from the macro, but allows the user to specify an IJ1 style macro to run before executing the analysis. Also, batch processing has been removed to facilitate more thorough curation of the analysis output. In total, there are 4 macros in the file.
1. __MiNA - Analyze__
>_Provides the functionality to perform the analysis on a single image, stack, or time series._
2. __MiNA - View Results__
>_Allows user to view the data generated from the Analyze Skeleton 2D/3D plugin for their analysis. There is also an option to generate a summary table providing MiNA V1 parameters for each file and timepoint in the results and branch information tables._
3. __MiNA - Clear Results__
>_Clears the results arrays._
4. __MiNA - Settings__
>_Provides an interface to altering the settings used by the "MiNA - Analyze" macros, such as binarization method, and whether or not to run a pre-processing script before analysis._

## MiNA Version 1


## MiNA Version 2
