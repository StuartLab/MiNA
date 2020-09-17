import ij.ImagePlus;
import ij.WindowManager;
import ij.plugin.Duplicator;

import net.imagej.ImageJ;
import org.scijava.command.Command;
import org.scijava.plugin.Parameter;
import org.scijava.plugin.Plugin;
import org.scijava.script.ScriptService;

import javax.imageio.ImageIO;
import javax.script.ScriptException;
import javax.swing.*;
import java.awt.*;
import java.awt.event.ItemEvent;
import java.awt.image.BufferedImage;
import java.io.File;
import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

@Plugin(type = Command.class, menuPath = "Plugins>StuartLab>MiNA Analyze Morphology")

/**
 * Main user interface for MiNA
 */
public class MiNAgui implements Command {
    @Parameter
    private ScriptService scriptS;

    // The font of different operating systems can be longer/shorter. Mac's and linux's font is longer than
    // Window's font. Therefore a buffer is needed to space out the GUI elements depending on the OS.
    String OS = System.getProperty("os.name").toLowerCase();
    private int spaceBuffer = OS.contains("win")?0:30;
    private int linuxBuffer = 7;

    JFrame window;
    Duplicator duplicator = new Duplicator();
    ImagePlus imp;
    ImagePlus imp_preview;
    private final int WINDOW_WIDTH = 750+spaceBuffer*2,  WINDOW_HEIGHT= 440;
    public int window_height = WINDOW_HEIGHT;
    public int bottomPanel_height = 200;
    public JTextField preProcText, postProcText;
    public Boolean useRidgeD = false;
    public Boolean useMedian = false;
    public Boolean useUnsharp = false;
    public Boolean useClahe = false;
    public JTextField commentText;
    public JComboBox threshBox;
    public JComboBox claheMask;
    public JComboBox orderMedian;
    public JComboBox orderUnsharp;
    public JComboBox orderClahe;
    public JSpinner medianRadSpin;
    public JSpinner unsharpRadSpin;
    public JSpinner unsharpWeightSpin;
    public JSpinner claheBlockSpin;
    public JSpinner claheHisSpin;
    public JSpinner claheSlopSpin;
    // ridge detection options
    public JSpinner highCs;
    public JSpinner lowCs;
    public JSpinner lineWs;
    public JSpinner lineLs;

    /**
     * Collect parameter settings and feed them to MiNA or for preview
     *
     * @param preview Boolean run MiNA or preview preprocessing
     */
    public void runMiNA(boolean preview){
        Map<String, Object> parameters =  new HashMap<String, Object>();

        parameters.put("use_ridge_detection", useRidgeD);
        parameters.put("rd_max", highCs.getValue());
        parameters.put("rd_min", lowCs.getValue());
        parameters.put("rd_width", lineWs.getValue());
        parameters.put("rd_length", lineWs.getValue());

        parameters.put("use_median", useMedian);
        parameters.put("order_median", String.valueOf(orderMedian.getSelectedIndex()));
        parameters.put("median_radius", medianRadSpin.getValue());

        parameters.put("use_unsharp", useUnsharp);
        parameters.put("order_unsharp", String.valueOf(orderUnsharp.getSelectedIndex()));
        parameters.put("unsharp_radius", unsharpRadSpin.getValue());
        parameters.put("unsharp_weight", unsharpWeightSpin.getValue());

        parameters.put("use_clahe", useClahe);
        parameters.put("order_clahe", String.valueOf(orderClahe.getSelectedIndex()));
        parameters.put("clahe_block", claheBlockSpin.getValue());
        parameters.put("clahe_bins", claheHisSpin.getValue());
        parameters.put("clahe_slope", claheSlopSpin.getValue());
        parameters.put("clahe_mask", claheMask.getSelectedItem());

        parameters.put("preprocessor_path", preProcText.getText());
        parameters.put("postprocessor_path", postProcText.getText());
        parameters.put("threshold_method", String.valueOf(threshBox.getSelectedItem()));
        parameters.put("user_comment", commentText.getText());

        parameters.put("preview_preprocessing", preview);

        for(String[] param : parametersToString()) parameters.put(param[0], param[1]);

        try{
            imp_preview.changes = false;
            imp_preview.close();
        }catch (NullPointerException e){}

        try {
            imp = WindowManager.getCurrentImage();
            if (imp == null){
                JOptionPane.showMessageDialog(window, "Please Select an Image");
                return;
            }
            if (preview){
                imp_preview = duplicator.run(imp, imp.getChannel(), imp.getChannel(),
                        1, imp.getNSlices(), 1, imp.getNFrames());
                imp_preview.setTitle("Preview_"+imp.getTitle());
                parameters.put("imp", imp_preview);
            }

            warnOnImageType();
            String minaFile = new File("scripts/MiNA_Analyze_Morphology.py").getCanonicalPath();
            scriptS.run(new File(minaFile),true, parameters);

        } catch (ScriptException | IOException e) {
            e.printStackTrace();
        }

    }

    /**
     * place all the gui elements along with their actions listeners
     */
    public void run(){
        window = new JFrame("MiNA Analyze Morphology");
        window.setSize(WINDOW_WIDTH, WINDOW_HEIGHT);
        if (OS.contains("win") | OS.contains("mac")) linuxBuffer = 0;

        //Limitations
        Icon warnIcon = UIManager.getIcon("OptionPane.warningIcon");
        // Rescale info icon image
        BufferedImage warnBI = new BufferedImage(warnIcon.getIconWidth(), warnIcon.getIconHeight(), BufferedImage.TYPE_INT_ARGB);
        Graphics2D warnG = warnBI.createGraphics();
        warnIcon.paintIcon(null, warnG, 0, 0);
        warnG.dispose();
        ImageIcon warnIconResized = new ImageIcon(warnBI.getScaledInstance(30, 30, Image.SCALE_SMOOTH));

        JButton warningBttn = new JButton(warnIconResized);
        warningBttn.setBounds(0,0,30,30);
        String warningMssg =
                "Analysis of large stacks and rendering can be very slow and the computation time is" +
                        "\n        dependent on how many structures are in the image. Other methods that have been reported " +
                        "\n        and function on 3D stacks with many structures and may operate substantially faster." +
                        "\n\nIf background noise is above the threshold determined, the analysis may freeze as noise " +
                        "\n        pixels all become analyzed as structures." +
                        "\n\nTime series images are not handled, nor are multi-channel images. The input images MUST" +
                        "\n        be a 2D or 3D grey-scale image";
        warningBttn.addActionListener(e ->{
            JOptionPane.showMessageDialog(window, warningMssg, "Warning note",2);
        });

        // processing labels
        JLabel preProcLabel = new JLabel("Pre-processor path: ");
        JLabel postProcLabel = new JLabel("Post-processing path: ");
        preProcText = new JTextField();
        postProcText = new JTextField();
        preProcLabel.setBounds(40, 52, 150, 20);
        postProcLabel.setBounds(40, 77, 150+linuxBuffer*3, 20);
        preProcText.setBounds(190+linuxBuffer*3, 50, 300, 25);
        postProcText.setBounds(190+linuxBuffer*3, 77, 300, 25);

        JButton browseButtonPre = new JButton("Choose File");
        JButton browseButtonPost = new JButton("Choose File");
        browseButtonPre.setBounds(495+linuxBuffer*3, 50, 110+linuxBuffer*3, 25);
        browseButtonPost.setBounds(495+linuxBuffer*3, 77, 110+linuxBuffer*3, 25);

        browseButtonPre.addActionListener(e -> {
            JFileChooser fc=new JFileChooser();
            int i = fc.showOpenDialog(window);
            if (i == JFileChooser.APPROVE_OPTION){
                File f = fc.getSelectedFile();
                String filepath = f.getPath();
                preProcText.setText(filepath);
            }
        });

        browseButtonPost.addActionListener(e -> {
            JFileChooser fc=new JFileChooser();
            int i = fc.showOpenDialog(window);
            if (i == JFileChooser.APPROVE_OPTION){
                File f = fc.getSelectedFile();
                String filepath = f.getPath();
                postProcText.setText(filepath);
            }
        });

        // Preview preprocessing button
        JButton preview = new JButton("Preview Preprocessing");
        preview.setBounds(WINDOW_WIDTH/2 - 100, 10, 200, 25);

        preview.addActionListener(e -> {
            runMiNA(true);
        });

        // threshold options
        JLabel threshLabel = new JLabel("Thresholding Op: ");
        String[] thresholds = {"huang", "ij1", "intermodes", "isoData", "li", "maxEntropy", "maxLikelihood", "mean",
                "minError", "minimum", "moments", "otsu", "percentile",
                "renyiEntropy", "rosin", "shanbhag", "triangle", "yen"};
        threshBox = new JComboBox(thresholds);
        threshBox.setSelectedItem(thresholds[11]);
        threshLabel.setBounds(45, 50, 130, 20);
        threshBox.setBounds(190, 54, 250, 25);

        // User comments
        int commentL_X = 50, commentL_Y = 130, commentT_X = 190;
        JLabel commentLabel = new JLabel("User Comments: ");
        commentText = new JTextField();
        commentLabel.setBounds(commentL_X, commentL_Y, 100+spaceBuffer/2+linuxBuffer, 20);
        commentText.setBounds(commentT_X, commentL_Y, 350, 25);

        // OK and Cancel buttons
        int okCancel_Y = 160;
        JButton ok = new JButton("OK");
        JButton cancel = new JButton("Cancel");
        ok.setBounds(WINDOW_WIDTH/2 - 80,   okCancel_Y, 100, 30);
        cancel.setBounds(WINDOW_WIDTH/2 + 30, okCancel_Y, 100, 30);

        ok.addActionListener(e -> {
            runMiNA(false);
        });

        cancel.addActionListener(e -> {
            window.setVisible(true);
            window.dispose();
        });

        // Information Buttons
        Icon infoIcon = new ImageIcon();
        BufferedImage infoBI = null;
        try {
            String infoIconFile = new File("images/mina_icons/infoIcon.png").getCanonicalPath();
            infoBI = ImageIO.read(new File(infoIconFile));
        } catch (IOException e) {
            e.printStackTrace();
        }
        Graphics2D infoG = infoBI.createGraphics();
        infoIcon.paintIcon(null, infoG, 0, 0);
        infoG.dispose();
        ImageIcon infoIconResized = new ImageIcon(infoBI.getScaledInstance(21,21,Image.SCALE_SMOOTH));

        JButton infoMedian = new JButton(infoIconResized);
        JButton infoUnsharp = new JButton(infoIconResized);
        JButton infoClahe = new JButton(infoIconResized);
        JButton infoRidgeD = new JButton(infoIconResized);
        JButton preProcInfo = new JButton(infoIconResized);
        JButton posProcInfo = new JButton(infoIconResized);
        JButton commentsInfo = new JButton(infoIconResized);
        JButton[] infoButton = {infoMedian,infoUnsharp,infoClahe,infoRidgeD, preProcInfo, posProcInfo, commentsInfo};

        infoMedian.setBounds(193+spaceBuffer/2+linuxBuffer,150,22,22);
        infoUnsharp.setBounds(385+spaceBuffer+(spaceBuffer/3)+linuxBuffer,150,22,22);
        infoClahe.setBounds(680+(spaceBuffer*2)+(spaceBuffer/3)+linuxBuffer*2,150,22,22);
        infoRidgeD.setBounds(242+spaceBuffer+linuxBuffer+(linuxBuffer/2),90,22,22);
        preProcInfo.setBounds(610+linuxBuffer*6, 50, 22, 22);
        posProcInfo.setBounds(610+linuxBuffer*6, 77, 22, 22);
        commentsInfo.setBounds(commentT_X+355, commentL_Y, 22, 22);


        String[][] infoMssgs = getInfoMessages();
        int i = 0;
        for (JButton b : infoButton){
            b.setOpaque(false);
            b.setContentAreaFilled(false);
            b.setBorderPainted(false);
            String infoTitle = infoMssgs[i][0];
            String mssg = infoMssgs[i][1];
            b.addActionListener(e ->{
                JOptionPane.showMessageDialog(window, mssg, infoTitle,1);
            });
            i++;
        }

        // Ridge detection options
        int ridgeCB_Y = 92;
        JCheckBox ridgeDetection = new JCheckBox("Use Ridge Detection (2D) only");
        ridgeDetection.setBounds(45, ridgeCB_Y, 195+spaceBuffer+(spaceBuffer/5)+linuxBuffer, 20);

        int ridgePanelY = ridgeCB_Y + 10;
        JPanel ridgeDetectionParam = new JPanel();
        ridgeDetectionParam.setVisible(false);
        ridgeDetectionParam.setBounds(30, ridgePanelY+10, 242+linuxBuffer*2, 150);
        JLabel highC = new JLabel("High Contrast");
        JLabel lowC = new JLabel("Low Contrast");
        JLabel lineW = new JLabel("Line Width");
        JLabel lineL = new JLabel("Min Line Length");
        int labelWidth = 100;
        highC.setBounds(40, 15, labelWidth, 15);
        lowC.setBounds(40, 45, labelWidth, 15);
        lineW.setBounds(40, 75, labelWidth, 15);
        lineL.setBounds(40, 105, labelWidth*2, 15);
        highCs = new JSpinner();
        lowCs = new JSpinner();
        lineWs = new JSpinner();
        lineLs = new JSpinner();
        highCs.setBounds(labelWidth+35+linuxBuffer*3, 15, labelWidth, 20);
        lowCs.setBounds(labelWidth+35+linuxBuffer*3, 45, labelWidth, 20);
        lineWs.setBounds(labelWidth+35+linuxBuffer*3, 75, labelWidth, 20);
        lineLs.setBounds(labelWidth+35+linuxBuffer*3, 105, labelWidth, 20);

        ridgeDetectionParam.setLayout(null);
        ridgeDetectionParam.add(highC);ridgeDetectionParam.add(lowC);ridgeDetectionParam.add(lineW);
        ridgeDetectionParam.add(lineL);
        ridgeDetectionParam.add(highCs);ridgeDetectionParam.add(lowCs);ridgeDetectionParam.add(lineWs);
        ridgeDetectionParam.add(lineLs);


        // add action to allow the ridge detection chechbox to expand and contract the window
        ridgeDetection.addItemListener(e -> {
            if (e.getStateChange() == ItemEvent.DESELECTED){
                window_height -= 153;
                window.setSize(WINDOW_WIDTH, window_height);
                commentsInfo.setBounds(commentT_X+355, commentL_Y, 23, 23);
                commentLabel.setBounds(commentL_X, commentL_Y, 100+spaceBuffer/2+linuxBuffer, 20);
                commentText.setBounds(commentT_X, commentL_Y, 350, 25);
                ok.setBounds(WINDOW_WIDTH/2 - 80,   okCancel_Y, 100, 30);
                cancel.setBounds(WINDOW_WIDTH/2 + 30, okCancel_Y, 100, 30);
                ridgeDetectionParam.setVisible(false);
                useRidgeD = false;

            }
            else if (e.getStateChange() ==  ItemEvent.SELECTED){
                window_height += 153;
                window.setSize(WINDOW_WIDTH, window_height);
                commentsInfo.setBounds(commentT_X+355, commentL_Y+150, 23, 23);
                commentLabel.setBounds(commentL_X, commentL_Y+ 150, 100+spaceBuffer/2+linuxBuffer, 20);
                commentText.setBounds(commentT_X, commentL_Y+ 150, 350, 25);
                ok.setBounds(WINDOW_WIDTH/2 - 80,   okCancel_Y + 150, 100, 30);
                cancel.setBounds(WINDOW_WIDTH/2 + 30, okCancel_Y + 150, 100, 30);
                ridgeDetectionParam.setVisible(true);
                useRidgeD = true;
            }
        });

        // panel to contain bottom half of GUI components
        JPanel bottomHalfPanel = new JPanel();
        bottomHalfPanel.setBounds(0, bottomPanel_height,WINDOW_WIDTH, WINDOW_HEIGHT/2 + 130);
        bottomHalfPanel.setLayout(null);
        bottomHalfPanel.add(threshLabel);bottomHalfPanel.add(threshBox);
        bottomHalfPanel.add(ridgeDetection);bottomHalfPanel.add(ridgeDetectionParam);
        bottomHalfPanel.add(commentLabel);bottomHalfPanel.add(commentText);
        bottomHalfPanel.add(ok);bottomHalfPanel.add(cancel);bottomHalfPanel.add(preview);
        bottomHalfPanel.add(infoRidgeD);bottomHalfPanel.add(commentsInfo);

        // Filter options
        JLabel filterTitle = new JLabel("Other Preprocessing Options:");
        filterTitle.setBounds(40, 130,350, 20);
        String[] filterOrder = {"1st", "2nd", "3rd"};

        // Median filter
        JCheckBox medianCB = new JCheckBox("Median Filter");
        orderMedian = new JComboBox(filterOrder);
        orderMedian.setSelectedItem(filterOrder[0]);
        JLabel medianRadLabel = new JLabel("Radius");
        medianRadSpin = new JSpinner();
        medianCB.setBounds(95, 150, 97+(spaceBuffer/2)+(spaceBuffer/3), 20);
        orderMedian.setBounds(49-(spaceBuffer)+linuxBuffer*2, 150,
                46+spaceBuffer+(spaceBuffer/8)-(linuxBuffer*3), 18+spaceBuffer/5);
        medianRadLabel.setBounds(55, 170, 50, 20);
        medianRadSpin.setBounds(97+linuxBuffer, 170, 50, 20);
        orderMedian.setVisible(false);
        medianRadLabel.setVisible(false);
        medianRadSpin.setVisible(false);

        // Unsharp Mask
        JCheckBox unsharpCB = new JCheckBox("Unsharp Mask");
        orderUnsharp = new JComboBox(filterOrder);
        orderUnsharp.setSelectedItem(filterOrder[1]);
        JLabel unsharpRadLabel = new JLabel("Radius (sigma)");
        unsharpRadSpin = new JSpinner();
        JLabel unsharpWeightLabel = new JLabel("Mask Weight");
        unsharpWeightSpin = new JSpinner(new SpinnerNumberModel(0.1, 0.1, 0.9, 0.1));
        unsharpCB.setBounds(275+spaceBuffer, 150, 111+spaceBuffer/2, 20);
        orderUnsharp.setBounds(227+spaceBuffer/3+linuxBuffer, 150,
                46+spaceBuffer+(spaceBuffer/8)-(linuxBuffer*3), 18+spaceBuffer/5);
        unsharpRadLabel.setBounds(230+spaceBuffer, 170, 100+linuxBuffer, 20);
        unsharpRadSpin.setBounds(320+spaceBuffer+linuxBuffer*2, 170, 50, 20);
        unsharpWeightLabel.setBounds(230+spaceBuffer, 190, 100, 20);
        unsharpWeightSpin.setBounds(320+spaceBuffer+linuxBuffer*2, 190, 50, 20);
        orderUnsharp.setVisible(false);
        unsharpRadLabel.setVisible(false);
        unsharpRadSpin.setVisible(false);
        unsharpWeightLabel.setVisible(false);
        unsharpWeightSpin.setVisible(false);
        JFormattedTextField tf = ((JSpinner.DefaultEditor)unsharpWeightSpin.getEditor()).getTextField();
        tf.setEditable(false);

        //CLAHE
        int claheYbound = 172;
        JPanel clahePanel = new JPanel();
        JCheckBox claheCB = new JCheckBox("Enhance Local Contrast CLAHE");
        orderClahe = new JComboBox(filterOrder);
        orderClahe.setSelectedItem(filterOrder[2]);
        JLabel claheBlockLabel = new JLabel("blocksize");
        claheBlockSpin = new JSpinner();
        JLabel claheHisLabel = new JLabel("histogram bins");
        claheHisSpin = new JSpinner(new SpinnerNumberModel(1, 1, 100000,1));
        JLabel claheSlopLabel = new JLabel("max slope");
        claheSlopSpin = new JSpinner();
        JLabel maskLabel = new JLabel("Mask");

        claheMask = new JComboBox(WindowManager.getImageTitles());
        clahePanel.setLayout(null);
        clahePanel.add(claheBlockLabel); clahePanel.add(claheBlockSpin);
        clahePanel.add(claheHisLabel);clahePanel.add(claheHisSpin); clahePanel.add(claheSlopLabel); clahePanel.add(claheSlopSpin);
        clahePanel.add(maskLabel);clahePanel.add(claheMask);
        claheCB.setBounds(475+spaceBuffer+(spaceBuffer/2)+(spaceBuffer/8), 150,
                205+spaceBuffer+(spaceBuffer/14)+linuxBuffer/2, 20);
        orderClahe.setBounds(425+spaceBuffer+linuxBuffer,
                150, 46+spaceBuffer+(spaceBuffer/8)-(linuxBuffer*3), 18+spaceBuffer/5);
        clahePanel.setBounds(410+spaceBuffer, claheYbound, 300, 80);
        claheBlockLabel.setBounds(10+spaceBuffer, 0, 100, 20);
        claheBlockSpin.setBounds(110+spaceBuffer+linuxBuffer, 0, 100, 20);
        claheHisLabel.setBounds(10+spaceBuffer, 20, 100+linuxBuffer, 20);
        claheHisSpin.setBounds(110+spaceBuffer+linuxBuffer, 20, 100, 20);
        claheSlopLabel.setBounds(10+spaceBuffer, 40, 100, 20);
        claheSlopSpin.setBounds(110+spaceBuffer+linuxBuffer, 40, 100, 20);
        maskLabel.setBounds(10+spaceBuffer, 60, 50, 20);
        claheMask.setBounds(110+spaceBuffer, 60, 125, 20);
        claheMask.addItem("*None*");
        claheMask.addItem("Update Menu..");
        orderClahe.setVisible(false);
        clahePanel.setVisible(false);

        orderMedian.addItemListener(e -> {
            if(e.getStateChange() == ItemEvent.SELECTED){
                changeFilterOrder(filterOrder, orderMedian, orderClahe, orderUnsharp);
            }
        });

        orderUnsharp.addItemListener(e -> {
            if(e.getStateChange() == ItemEvent.SELECTED){
                changeFilterOrder(filterOrder, orderUnsharp, orderClahe, orderMedian);
            }
        });

        orderClahe.addItemListener(e -> {
            if(e.getStateChange() == ItemEvent.SELECTED){
                changeFilterOrder(filterOrder, orderClahe, orderMedian, orderUnsharp);
            }
        });

        medianCB.addItemListener(e -> {
            if (e.getStateChange() == ItemEvent.DESELECTED){
                orderMedian.setVisible(false);
                medianRadLabel.setVisible(false);
                medianRadSpin.setVisible(false);
                useMedian = false;
            }
            else if (e.getStateChange() ==  ItemEvent.SELECTED){
                orderMedian.setVisible(true);
                medianRadLabel.setVisible(true);
                medianRadSpin.setVisible(true);
                useMedian = true;
            }
        });

        unsharpCB.addItemListener(e -> {
            if (e.getStateChange() == ItemEvent.DESELECTED){
                orderUnsharp.setVisible(false);
                unsharpRadLabel.setVisible(false);
                unsharpRadSpin.setVisible(false);
                unsharpWeightLabel.setVisible(false);
                unsharpWeightSpin.setVisible(false);
                window_height -= 14;
                bottomPanel_height -= 14;
                window.setSize(WINDOW_WIDTH, window_height);
                bottomHalfPanel.setBounds(0, bottomPanel_height, WINDOW_WIDTH, WINDOW_HEIGHT/2 + 170);
                useUnsharp = false;
            }
            else if (e.getStateChange() ==  ItemEvent.SELECTED){
                orderUnsharp.setVisible(true);
                unsharpRadLabel.setVisible(true);
                unsharpRadSpin.setVisible(true);
                unsharpWeightLabel.setVisible(true);
                unsharpWeightSpin.setVisible(true);
                window_height += 14;
                bottomPanel_height += 14;
                window.setSize(WINDOW_WIDTH, window_height);
                bottomHalfPanel.setBounds(0, bottomPanel_height, WINDOW_WIDTH, WINDOW_HEIGHT/2 + 170);
                useUnsharp = true;
            }
        });

        claheCB.addItemListener(e -> {
            if (e.getStateChange() == ItemEvent.DESELECTED){
                orderClahe.setVisible(false);
                clahePanel.setVisible(false);
                window_height -= 43;
                bottomPanel_height -= 43;
                window.setSize(WINDOW_WIDTH, window_height);
                bottomHalfPanel.setBounds(0, bottomPanel_height, WINDOW_WIDTH, WINDOW_HEIGHT/2 + 170);
                useClahe = false;
            }
            else if (e.getStateChange() ==  ItemEvent.SELECTED){
                orderClahe.setVisible(true);
                clahePanel.setVisible(true);
                window_height += 43;
                bottomPanel_height += 43;
                window.setSize(WINDOW_WIDTH, window_height);
                bottomHalfPanel.setBounds(0, bottomPanel_height, WINDOW_WIDTH, WINDOW_HEIGHT/2 + 170);
                useClahe = true;
            }
        });

        claheMask.addItemListener(e -> {
                    if (e.getStateChange() == ItemEvent.SELECTED){
                        if (claheMask.getSelectedItem() == "Update Menu.."){
                            claheMask.removeAllItems();
                            int imgplW = 0;
                            int imgplH = 0;
                            ImagePlus imgpl = WindowManager.getCurrentImage();
                            if (imgpl != null){
                                imgplW = imgpl.getWidth();
                                imgplH = imgpl.getHeight();
                            }

                            claheMask.addItem("*None*");
                            for (String image : WindowManager.getImageTitles()){
                                ImagePlus tmp_image = WindowManager.getImage(image);
                                // mask has to have same height and width as the image it is being applied to
                                if (tmp_image.getWidth() == imgplW && tmp_image.getHeight() == imgplH){
                                    claheMask.addItem(image);
                                }
                            }
                            claheMask.addItem("Update Menu..");
                        }
                    }
                }
        );

        window.setLayout(null);
        window.setResizable(false);
        window.add(warningBttn);
        window.add(preProcLabel);window.add(postProcLabel);window.add(preProcText);window.add(postProcText);
        window.add(browseButtonPre);window.add(browseButtonPost);

        window.add(filterTitle);
        window.add(medianCB);window.add(orderMedian);window.add(medianRadLabel);window.add(medianRadSpin);
        window.add(unsharpCB);window.add(orderUnsharp);window.add(unsharpRadLabel);window.add(unsharpRadSpin);
        window.add(unsharpWeightLabel);window.add(unsharpWeightSpin);
        window.add(claheCB); window.add(orderClahe);window.add(clahePanel);
        window.add(infoMedian);window.add(infoUnsharp);window.add(infoClahe);
        window.add(preProcInfo);window.add(posProcInfo);
        window.add(postProcLabel);

        window.add(bottomHalfPanel);

        window.setVisible(true);
    }

    /**
     * Makes sure only one order label can be used at a time by changing box's labels if they are the same.
     *
     * @param filterOrder array containing order labels
     * @param current JComboBox whose state has changed
     * @param other1 JComboBox
     * @param other2 JComboBox
     */
    public void changeFilterOrder(String[] filterOrder, JComboBox current, JComboBox other1, JComboBox other2){
        if(current.getSelectedItem() == other1.getSelectedItem()){
            int oldOrder = other1.getSelectedIndex();
            int newOrder = 0;
            while (newOrder == oldOrder || newOrder == other2.getSelectedIndex()){
                newOrder += 1;
            }
            other1.setSelectedItem(filterOrder[newOrder]);
        }

        if(current.getSelectedItem() == other2.getSelectedItem()){
            int oldOrder = other2.getSelectedIndex();
            int newOrder = 0;
            while (newOrder == oldOrder || newOrder == other1.getSelectedIndex()){
                newOrder += 1;
            }
            other2.setSelectedItem(filterOrder[newOrder]);
        }
    }

    /**
     * Get the messages and titles to be displayed when the information buttons are clicked
     * @return array of arrays with titles and messages
     */
    public String[][] getInfoMessages(){
        String[] infoMedianMsg = {"Median Filter",
                "Smooths image by replacing each pixel with the neighborhood median" +
                        "\n\n radius:  The size of the neighborhood"};

        //https://imagejdocu.tudor.lu/gui/process/filters
        String[] infoUnsharpMsg = {"Unsharp Mask",
                "Sharpens and enhances edges by subtracting a blurred version of the" +
                        " image (the unsharp mask) from the original.\n The unsharp mask is created by Gaussian" +
                        " blurring the original image and then multiplying by the “Mask Weight”\n parameter.\n" +
                        "\nRadius (sgima):  Increase it to increase the contrast.\n" +
                        "\nMask Weight:  Increase it for additional edge enhancement.\n"};

        String[] infoClaheMsg = {"Enhance Local Contrast (CLAHE)",
                "Enhances the local contrast of an image." +
                        "\n\nblock size:  The size of the local region around a pixel for which the histogram is equalized. " +
                        "\n                       This size should be larger than the size of features to be preserved." +
                        "\n\nhistogram bins:  The number of histogram bins used for histogram equalization. Values larger" +
                        "\n                        than 256 are not meaningful. This value also limits the quantification" +
                        "\n                       of the output when processing 8bit gray or 24bit RGB images." +
                        "\n                       The number of histogram bins should be smaller than the number of pixels" +
                        "\n                       in a block." +
                        "\n\nmax slope:  Limits the contrast stretch in the intensity transfer function. Very large values" +
                        "\n                       will let the histogram equalization do whatever it wants to do, that " +
                        "\n                       is result in maximal local contrast. The value 1 will result in the " +
                        "\n                       original image." +
                        "\n\nmask:  Choose, from the currently opened images, one that should be used as a mask for the " +
                        "\n                       filter application. The Mask should have the same size as the image it" +
                        "\n                       is being applied to."};
        // https://imagej.net/Enhance_Local_Contrast_(CLAHE)
        String[] infoRidgeDMsg = {"Ridge Detection",
                "Detects Ridges" +
                        "\n\nHigh contrast:  Highest grayscale value of the line." +
                        "\n\nLow contrast:  Lowest grayscale value of the line." +
                        "\n\nLine Width:  The line diameter in pixels." +
                        "\n\nMin Line Length:  Smallest line length expected.\n"};
        String[] infoPreProc = {"Preprocessing Path",
                "The path to an ImageJ script or macro to run before the analysis is run. This is typically used to run"+
                        "\n user defined preprocessing operations on the image before it is analyzed, such as " +
                        "\nexpanding the histogram range, reducing noise by filtering, or deconvolving the image. " +
                        "\nIt is optional.\n"};
        String[] infoPostProc = {"Postprocessing Path", "The path to an ImageJ compatible script or macro to be run " +
                "when the analysis completes.\n This can be used to trigger saving a copy of the data, plotting the " +
                "\ncurrent data stored in the ResultsTable window, and much more. It is optional.\n"};
        String[] infoComments = {"User Comments", "A user comment to store in the table. " +
                "\n\nThis supports key-value pairs, which is useful for storing condition information." +
                "\n\nFor example, if you wanted a column \"oxygen\" and a column \"glucose\" to store the culture " +
                "conditions, " +
                "\nYou could use the comment \"oxygen=18,glucose=high\" to add the value 18 to a column titled oxygen and " +
                "\nthe value high to another column titled glucose.\n"};
        String[][] messages = {infoMedianMsg, infoUnsharpMsg, infoClaheMsg, infoRidgeDMsg, infoPreProc, infoPostProc,
                infoComments};
        return messages;
    }

    /**
     * Return the parameter options in a String format
     * @return array of arrays with paramater options
     */
    public String[][] parametersToString(){
        String medianString = "";
        String unsharpString = "";
        String claheString = "";
        String ridgeString = "";
        String threshString = "Thresholding Op:"+String.valueOf(threshBox.getSelectedItem());

        if (useMedian) medianString = "Median Filter\nRadius: "+medianRadSpin.getValue()+"\norder: "+orderMedian.getSelectedItem();
        if (useUnsharp){
            unsharpString = "Unsharp Mask\n"+"radius(sigma): "+
                    unsharpRadSpin.getValue()+"\nMask Weight: "+unsharpWeightSpin.getValue()+"\norder: "+
                    orderUnsharp.getSelectedItem();
        }
        if (useClahe){
            claheString = "CLAHE\nblocksize: "+claheBlockSpin.getValue()+"\nhist bins: "+
                    claheHisSpin.getValue() + "\nmax slope: " + claheSlopSpin.getValue() + "\nmask: " +
                    claheMask.getSelectedItem() + "\norder: "+orderClahe.getSelectedItem();
        }
        if (useRidgeD){
            ridgeString = "Ridge Detection\nHigh Contrast: "+highCs.getValue()+"\nLow Contrast: "+lowCs.getValue()+
                    "\nLine Width: "+lineWs.getValue()+"\nMin Line Length: "+lineWs.getValue();
        }

        String[][] parameterString ={{"median_string", medianString}, {"unsharp_string", unsharpString},
                {"clahe_string",claheString}, {"ridge_string", ridgeString}, {"thresh_string",threshString}};
        return parameterString;
    }

    /**
     * Warn the user if the image is RGB or if it's not calibrated
     */
    public void warnOnImageType(){
        if (imp.getType() == ImagePlus.COLOR_RGB) JOptionPane.showMessageDialog(window,
                "Image MUST not be RGB. Analysis will not be completed.");
        if (imp.getCalibration().getUnit() == "pixel") JOptionPane.showMessageDialog(window,
                "Units are in pixels, please make sure you convert the output measurements" +
                        "\nappropriately or calibrate the image with appropriate units.");
    }

    public static void main(final String... args){
        final ImageJ ij = new ImageJ();
        ij.launch(args);
        new MiNAgui().run();
    }
}

