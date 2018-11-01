#@ Boolean(label="Unsharp Mask: ", value=false) unsharp_check
#@ BigDecimal(label="Radius: ", value=2) unsharp_radius
#@ BigDecimal(label="Mask Strength: ", value=0.6) unsharp_strength
#@ Boolean(label="CLAHE: ", value=false) CLAHE_check
#@ BigDecimal(label="Blocksize: ", value=127) CLAHE_blocksize
#@ BigDecimal(label="Histogram Bins: ", value=256) CLAHE_bins
#@ BigDecimal("Maximum Slope: ", value=3) CLAHE_slope
#@ Boolean(label="Median Filter: ", value=false) median_check
#@ BigDecimal(label="Radius: ", value=2) median_radius
#@ Boolean(label="Tophat (Iannetti et al., 2016)", value=false) tophat_check

#@ UIService ui

import java.awt.Color
import ij.IJ
import ij.gui.ImageRoi
import ij.gui.Overlay
import ij.macro.MacroRunner
import ij.plugin.Duplicator

duplicator = ij.plugin.Duplicator()
built_macro = '// Start of Generated Macro Code... \n'

# Convert BigDecimals floats ...
unsharp_radius = unsharp_radius.floatValue()
unsharp_strength = unsharp_strength.floatValue()
CLAHE_blocksize = CLAHE_blocksize.floatValue()
CLAHE_bins = CLAHE_bins.floatValue()
CLAHE_slope = CLAHE_slope.floatValue()
median_radius = median_radius.floatValue()

# Build the IJ1 macro ...
if unsharp_check == True:
	built_macro += 'run("Unsharp Mask...", "radius=%d mask=%.2f");\n'%(unsharp_radius,unsharp_strength)
if CLAHE_check == True:
    built_macro += 'run("Enhance Local Contrast (CLAHE)", "blocksize=%d histogram=%d maximum=%.2f mask=*None* fast_(less_accurate)");\n'%(CLAHE_blocksize, CLAHE_bins, CLAHE_slope)
if median_check == True:
    built_macro += 'run("Median...", "radius=%d");\n' % median_radius
if tophat_check == True:
    built_macro += 'run("Convolve...", "text1=[0 0 -1 -1 -1 0 0 \\n0 -1 -1 -1 -1 -1 0\\n-1 -1 3 3 3 -1 -1\\n-1 -1 3 4 3 -1 -1\\n-1 -1 3 3 3 -1 -1\\n0 -1 -1 -1 -1 -1 0\\n0 0 -1 -1 -1 0 0 \\n] normalize");\n'

built_macro += '// End of Generated Macro Code! \n'

# Display the IJ1 macro code
ui.show("Generated Macro Code", built_macro)
