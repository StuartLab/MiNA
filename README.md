# MiNA - ImageJ Tools for Mitochondrial Morphology Research

## About the Project
MiNA (Mitochondrial Network Analysis) is a project aimed at making the analysis and characterization of mitochondrial network morphology more accurate, faster, and less subjective. It consists of a set of ImageJ macros that are used to measure meaningful morphological parameters from fluorescence micrographs of labelled mitochondria. Since, it has been rewritten as Python scripts adding support for 3D datasets and for using ridge detection (as suggested by one of the early reviewers of the paper we published about the macros - thank you for the suggestion!).

The project began as a result of extensive work with adherent mammalian cell cultures in the laboratory of [Dr. Jeff Stuart](https://brocku.ca/mathematics-science/biology/directory/jeff-stuart/) at Brock University. As others adopt the macros for additional applications and cell lines, we use the feedback from these users to extend and further generalize the tools.

## Project Road Map
The links listed below provide a starting point for installing, using, modifying, and discussing the project.

:microscope: [Installation and usage](https://imagej.net/MiNA_-_Mitochondrial_Network_Analysis) <br>
:book: [The macro publication](https://doi.org/10.1016/j.acthis.2017.03.001) <br>
:computer: [Source code](https://github.com/ScienceToolkit/MiNA/tree/master) <br>
:octocat: [Gitter chat room](https://gitter.im/MiNA-Suggestions/Lobby) <br>


## The TODO List :wrench: :computer: :coffee:
To give you an idea of what I am working on and what you will see next from MiNA, take  a peak at my TODO list. Do you have an idea for added functionality or a way to improve the analysis routine? Feel free to open an [issue](https://github.com/ScienceToolkit/MiNA/issues) to let me know about any software bugs, or start a discussion about additional features you would like on the [Gitter chat](). If you have forked the project and made it better, feel free to make a [pull request](https://yangsu.github.io/pull-request-tutorial/) so we all benefit. :octocat:

- [x] Create a clean release of the original macros.
- [x] Complete the README file.
- [x] Rewrite as IJ2 Jython parameterized script.
- [x] Add an option for ridge detection.
- [x] Extend for 3D analysis.
- [ ] Extend for time series analysis. :construction: [<b>IN PROGRESS</b>](https://github.com/ScienceToolkit/MiNA/tree/multi-roi) :construction:
- [ ] Extend for multiple ROI support. :construction: [<b>IN PROGRESS</b>](https://github.com/ScienceToolkit/MiNA/tree/multi-roi) :construction:
- [ ] Incorporate functional analysis options.
- [x] Concatenating consecutive outputs in a common table.
- [x] Create a Fiji update site for the project.
- [ ] Create a full manual and description as a wiki site on imagej.net. :construction: [<b>IN PROGRESS</b>](https://imagej.net/MiNA_-_Mitochondrial_Network_Analysis) :construction:
