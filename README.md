# MiNA - ImageJ Tools for Mitochondrial Morphology Research

## About the Project
MiNA (Mitochondrial Network Analysis) is a project aimed at making the analysis and characterization of mitochondrial network morphology more accurate, faster, and less subjective. It consists of a set of ImageJ macros that are used to measure meaningful morphological parameters from fluorescence micrographs of labelled mitochondria. The project began as a result of extensive work with adherent mammalian cell cultures in the laboratory of [Dr. Jeff Stuart](https://brocku.ca/mathematics-science/biology/directory/jeff-stuart/) at Brock University. Since then it has been rewritten as Python scripts adding support for 3D datasets and for using ridge detection (as suggested by one of the early reviewers of the paper we published about the macros - thank you for the suggestion!).

As others adopt the macros for additional applications and cell lines, we will continue to use the feedback from these users to extend and further generalize the tools.

## Project Road Map
The links listed below provide a starting point for installing, using, modifying, and discussing the project.

- :microscope: [**The MiNA Wiki**](https://imagej.net/MiNA_-_Mitochondrial_Network_Analysis) - A thorough description of the tools and basic usage.
- :book: [**The Publication**](https://doi.org/10.1016/j.acthis.2017.03.001) - The publication regarding the original macros. Note, the tool has changed a bit since then, so the Wiki is the most up to date source of information!
- :computer: [**Source Code**](https://github.com/StuartLab/MiNA/tree/master) - Fork the project and get hacking.
- :question: [**Issue Tracking**](https://github.com/StuartLab/MiNA/issues) - Submit bugs or feature requests here. Be sure to check the closed issues as well! We may have addressed a concern already.

## Frequently Asked Questions (FAQ)
**1. Will MiNA work for my purposes/cells/images?**<br>
This is not a question we can definitively answer or one we will try to answer. In general, try it out and see if the skeleton and binary representations are faithful to the structures you see. You may want to do some preprocessing as well, but keep in mind how the preprocessing may be altering your images and the measurements (ex. blurring to reduce noise will often increase the measured footprint). In general, the tool is typically not suitable for extremely clumped mitochondria, poorly resolved images, or images with low contrast. The accuracy of the tool will be dependent on how well resolved the mitochondrial structures are. With fluorescence microscopy for certain cell lines where mitochondria severely clump together, it may not be possible to obtain the required resolution. It is the responsibility of the researcher to understand and validate MiNA for their purposes and decide if it is suitable.

**2. Preprocessing options don't appear in the user interface anymore. How do I perform preprocessing before the analysis?**<br>
The new tool gives the user an option to provide a preprocessing and post processing script path. These paths are for a macro or script that should be run before and after analyzing the image with MiNA. We moved to this from the options in the user interface so the tool would be more flexible and allow for preprocessing in a repeatable fashion without constraints. It does require learning a bit of programming to use, but there are many resources for that online. You can use the macro language for basic processes, or dive into one of the supported scripting languages creating more elaborate pipelines. I like Python because it is a generally useful language for the sciences so learning it for ImageJ provides skills you can transfer to other tasks. Some resources are listed below:

- [ImageJ User Guide](https://imagej.nih.gov/ij/docs/guide/user-guide.pdf)
- [The Macro Recorder](https://imagej.net/Introduction_into_Macro_Programming)
- [ImageJ Macro Writing Guide](https://imagej.nih.gov/ij/developer/macro/macros.html)
- [Python Scripting Tutorials](https://imagej.net/Jython_Scripting)
- [Python Language Tutorials](https://docs.python.org/3/tutorial/)

Just as an example, we can process the image with a median filter and unsharp mask by creating a two line macro file and saving it. Here is what that file contents look like:

```javascript
run("Unsharp Mask...", "radius=3 mask=0.6"); // sharpen with an unsharp mask
run("Median...", "radius=3"); // smooth spurious noise with a median filter
```

We would then save this file with the ".ijm" extension, as it is an ImageJ macro, and then browse for it within the MiNA user interface when selecting our options. One important thing to remember is that MiNA will process the last selected image, so if your preprocessing macro/script produces a new image, you need to make sure it is the "active" image at the end. Since the above macro does not do this, we don't need to worry about it.

**3. The parameters returned by the tool are not the same as in the paper. Where are the number of individuals and number of networks?**<br>
The parameters are slightly different. Some of the additional parameters had been requested by users and interested individuals. The list of all current parameters returned and how they are calculated is provided on the [wiki](https://imagej.net/MiNA_-_Mitochondrial_Network_Analysis#Processing_Pipeline_and_Usage) (take a look at the source code too!).

Two parameters, the number of individuals and number of networks, were removed. These parameters were deduced from the number of junction points in each skeleton (or "graph"). Since the only requirement for an object to be a network was a single junction point, when larger networks break down into smaller ones, the number of networks often increases as the objects often still have at least one junction point. This could easily misinterpreted as a more "fused" structure even though it has obviously become a more "fragmented" one because of how the jargon is interpreted. To avoid such confusion, we removed it.

**4. How can I get the original macro?**<br>
Currently, you can dig through the [releases](https://github.com/StuartLab/MiNA/releases) and work on installing it manually. In the future, the releases will be cleaned up and installation instructions for each tagged release will be provided. We recommend taking a look at the most up to date version first though which can be installed using the Fiji Updater allowing for automatic updates as described on the [MiNA wiki page](https://imagej.net/MiNA_-_Mitochondrial_Network_Analysis#Installation).

**5. How can I familiarize myself with ImageJ/Fiji and image analysis first?**<br>
There are many resources in print and online to help with getting started with ImageJ and image analysis in general. Below is a list of some to get started with.

  * [ImageJ Tutorials Wiki](https://imagej.net/Category:Tutorials)
  * [Bankhead, Peter. (2014). Analyzing fluorescence microscopy images with ImageJ.](https://petebankhead.gitbooks.io/imagej-intro/content/)
  * [Vebjorn Ljosa and Anne E. Carpenter. 2009. **Introduction to the Quantitative Analysis of Two-Dimensional Fluorescence Microscopy Images for Cell-Based Screening.** PLOS Comput Biol.  doi: 10.1371/journal.pcbi.1000603.](https://dx.doi.org/10.1371%2Fjournal.pcbi.1000603)
  
 ## Installation
 **You should have [FIJI](https://fiji.sc/) installed.** </br>
 **1.** Download the contents of this repository as a zipped folder</br>
 **2.** Go to your FIJI installation and go to the "Fiji.app" folder. If you're using mac, right click on the FIJI icon and select "Show Package Contents".</br>
 **3.** Move the folder with the name "mina" located in "src" of this repository to jars>lib (create the folder lib if it does not already exist). </br>
 **4.** Move the file "MiNA_Analyze_Morphology.py" located at "src>scripts" to "scripts". </br>
 **5.** Move the folder "mina_icons" inside "images". </br>
 **6.** In the "build" folder of this repository you will see a jar file. Move it inside "plugins". </br> 
 **7.** Finally, start ImageJ and if you don't have the Biomedroup site installed then click on Help->Update...</br>
        Navigate to the update site manager (Manage update sites). Add the "Biomedgroup" site by checking the checkbox beside the site.</br>
        Close the site manager dialog (Close) and apply the changes (Apply changes)

 
