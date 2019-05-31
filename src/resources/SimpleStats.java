/**
 * 
 */
package resources;

/**
 * A utility class for basic statistical functions.
 * 
 * @author Rodrigo
 * @author Andrew
 */
public class SimpleStats<T extends Number> {
	
	static public <T extends Number> Double mean(T[] data) {
		Double total = 0.0;
		Double mean = 0.0;
		Long counts = 0l;
		
		for (T value : data) {
			total += value.doubleValue();
			counts += 1;
		}
		mean = total / counts;
		
		return(mean);
	}
	
}
