/**
 * 
 */
package plugin;

import java.io.File;

import org.scijava.command.Command;
import org.scijava.plugin.Parameter;
import org.scijava.plugin.Plugin;

import resources.SimpleStats;

/**
 * A Scijava Command for analyzing mitochondrial morphology as a
 * network.
 * 
 * @author Rodrigo
 * @author Andrew
 *
 */
@Plugin(type = Command.class, menuPath = "Plugins>StuartLab>MiNA - Analyze Mitochondrial Network Morphology")
public class MiNA implements Command {

	// Required parameters (GUI will be generated if called from user interface)
	@Parameter(label="Preprocessing Script", style="file", required=false)
	private File preprocessor;
	
	@Parameter(label="Postprocessing Script", style="file", required=false)
	private File postprocessor;
	
	@Parameter(label="Thresholding Method", choices={"ij1", "li", "minimum", "otsu"})
	private String thresholding_method = "otsu";
	
	@Parameter(label="User Comment")
	private String user_comment = "";
	
	@Parameter(label="Use Ridge Detection")
	private boolean use_ridge_detection = false;
	
	@Parameter(label="Maximum Threshold")
	private double rd_max_threshold = 50;
	
	@Parameter(label="Minimum Threshold")
	private double rd_min_threshold = 50;
	
	@Parameter(label="Line Width")
	private double rd_line_width = 50;
	
	@Parameter(label="Line length")
	private double rd_line_length = 50;
	
	@Override
	public void run() {
		// TODO Auto-generated method stub

	}

	/**
	 * Start a FIJI session, open an image and run the command
	 * as a test. Feel free to use this throughout to test new
	 * things you have developed. We will put together some
	 * unit tests as proper tests later.
	 * 
	 * TODO: Remove when we are all done!
	 * @param args
	 */
	public static void main(String[] args) {
		
		Integer[] x_i = {0, 1, 2};
		Double average_i = SimpleStats.mean(x_i);
		
		Float[] x_f = {0.0f, 1.0f, 2.0f};
		Double average_f = SimpleStats.mean(x_f);
		
		Double[] x_d = {0.0d, 1.0d, 2.0d};
		Double average_d = SimpleStats.mean(x_d);
		
		System.out.println("Integer average: " + average_i.toString());
		System.out.println("Float average: " + average_f.toString());
		System.out.println("Double average: " + average_d.toString());
		
	}

}
