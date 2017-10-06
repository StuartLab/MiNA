# MiNA - A Tool for Mitochondrial Research
## Introduction
MiNA (Mitochondrial Network Analysis) is a project aimed at making the analysis and characterization of mitochondrial network morphology more accurate, faster, and objective. This project is under development and this README file will be used to communicate the status and advancements being made. In version 1's development, changes were made directly to the file. For version 2, the macro will still remain a single file, but the changes will be made as new file uploads named according to the magnitude of changes made. MiNA_V200 is version 2.0.0, where the numbering is [version].[functional update].[bug fix]. Older copies of the file will remain in the repo and new ones will be added when changes are made. This numbering convention will be used from here on out unless otherwise stated.

## Status
Currently the project has entered development of the second version of the tool. It is still being developed as an IJ1 macro, but the workflow is being changed significantly. The workflow will now treated as a "session." The analysis routine is being extended to support 2D, 3D, and 4D (time series stacks) datasets. Batch processing capability has been removed and preprocessing separated from the analysis macro. The removal of this functionality aims to push users to visually inspect all results and ensure that skeleton and binary representation of the mitochondria is faithful. 

The changes hope to reduce the likelyhood of flawed analyses being pushed through and to make further analysis with other software packages easier. If the analysis appears visually accurate, the results can be appended to a running table stored as a CSV file. All output of the Analyze Skeleton 2D/3D plugin are also stored if users wish to perform further analysis outside of the summary information provided by MiNA.

## MiNA Version 1


## MiNA Version 2
