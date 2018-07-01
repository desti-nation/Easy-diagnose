package easyDiagnose;

import java.awt.EventQueue;
import java.awt.Image;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;

import javax.swing.Icon;
import javax.swing.ImageIcon;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JScrollBar;
import javax.swing.JScrollPane;
import javax.swing.JTextArea;

public class InfoDisplay {

	private JFrame frame;
	private JLabel huGraph ;
	private JTextArea infoArea ;
	private ImageIcon huG ;
	private BufferedReader br ;
	private String input ;
	private JScrollPane infoPane ;
	private JScrollBar infoPaneBar ;
	
//	private final String preProcessPath = "E:" + File.separator + "00cba091fa4ad62cc3200a657aeb957e - ¸±±¾" + File.separator + "TEMP_DATA";
	/**
	 * Launch the application.
	 */
	public static void main(String[] args) {
		EventQueue.invokeLater(new Runnable() {
			public void run() {
				try {
					InfoDisplay window = new InfoDisplay();
					window.frame.setVisible(true);
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		});
	}

	/**
	 * Create the application.
	 */
	public InfoDisplay() {
		frame = new JFrame();
		frame.setBounds(100, 100, 801, 795);
		frame.setDefaultCloseOperation(JFrame.DISPOSE_ON_CLOSE);
		frame.getContentPane().setLayout(null);
		
		huGraph = new JLabel("New label");
		huGraph.setBounds(182, 13, 432, 288);
		huG = new ImageIcon ( UserInterface.preProcessPath + File.separator + "hu_hist.png") ;
//		huG = new ImageIcon ( preProcessPath + File.separator + "hu_hist.png") ;
		huG.setImage(huG.getImage().getScaledInstance(640,480,Image.SCALE_DEFAULT));
		huGraph.setIcon ( huG ) ;
		frame.getContentPane().add(huGraph);
		
		infoArea = new JTextArea () ;
		infoArea.setBounds(14, 314, 755, 404);
		infoArea.setAutoscrolls ( true ) ;
		infoArea.setLineWrap ( true ) ;
		infoArea.setWrapStyleWord ( true ) ;
		infoPane = new JScrollPane ( infoArea ) ;
		infoPane.setVerticalScrollBarPolicy( JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED); 
		infoPane.setHorizontalScrollBarPolicy ( JScrollPane.HORIZONTAL_SCROLLBAR_NEVER ) ;
		infoPane.setBounds(14, 314 , 755, 404 );
		frame.getContentPane().add(infoPane);
		try 
		{
			br = new BufferedReader ( new FileReader ( UserInterface.preProcessPath + File.separator + "info_DICOM.txt" ) ) ;
//			br = new BufferedReader ( new FileReader ( preProcessPath + File.separator + "info_DICOM.txt" ) ) ;
		} 
		catch (FileNotFoundException e) 
		{
			e.printStackTrace();
		}
		while ( true )
		{
			try 
			{
				input = br.readLine() ;
			} 
			catch (IOException e) 
			{
				e.printStackTrace();
			}
			if ( input == null )
				break ;
			infoArea.append ( input + "\n" ) ;
		}
		infoArea.setEditable ( false ) ;
//		infoPaneBar = infoPane.getVerticalScrollBar() ;
//		infoPaneBar.setValue ( infoPaneBar.getMinimum() ) ;
	}
}