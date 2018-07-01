package easyDiagnose;

import java.awt.EventQueue;

import javax.swing.JFrame;
import javax.swing.JTextField;
import java.awt.Font;
import java.awt.Image;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.AdjustmentEvent;
import java.awt.event.AdjustmentListener;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Scanner;

import javax.swing.JLabel;
import javax.swing.JButton;
import javax.swing.JScrollBar;
import java.awt.Color;
import javax.swing.SwingConstants;
import java.awt.Toolkit;

import javax.swing.*;

public class UserInterface {

	public static String preProcessPath ;
	
	private final String secondaryDir = "TEMP_DATA" ;
	private final String thirdlyDir = "figure" ;
//	private final String MODEL_PATH = "E:\"
	
	private JFrame frmEasydiagnose;
	private JLabel lbl_id_1;
	private JLabel lbl_id_2;
	private JLabel lbl_imageSwitch;
	private JLabel lbl_predictResult_1;
	private JLabel lbl_predictResult_2;
	private JLabel lbl_confidence_1;
	private JLabel lbl_confidence_2;
	private JButton btn_import ;
	private JButton btn_checkInfo ;
	private JButton btn_startProcess ;
	private JScrollBar scb_imageSwitch ;
	private JLabel lbl_imageDisplay ;
	private ImageIcon dcmImage ;
	private JLabel lbl_logoDisplay ;
	private ImageIcon logoImage ;
	
	private boolean dcmReady = false ;
	private JFileChooser jfc = new JFileChooser();
	private String inPath ;
//	private String sendPath ;
	private String currentRootPath ;
	private String imagePath ;
	private String id ;
    private BufferedReader br ;
    private String[] names ;
    private String[] dumplicate ;
	private ArrayList<String> imageDir ;
	private String temp ;
	private String resultCondition ;
	private String resultConfidence ;
	/**
	 * Launch the application.
	 */
	public static void main(String[] args) {
		EventQueue.invokeLater(new Runnable() {
			public void run() {
				try {
					UserInterface window = new UserInterface();
					window.frmEasydiagnose.setVisible(true);
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		});
	}

	/**
	 * Create the application.
	 */
	public UserInterface() {
		initialize();
	}

	/**
	 * Initialize the contents of the frame.
	 */
	private void initialize() {
		frmEasydiagnose = new JFrame();
		frmEasydiagnose.setIconImage( Toolkit.getDefaultToolkit().getImage("logo" + File.separator + "logo_v2.png"));
		frmEasydiagnose.setResizable(false);
		frmEasydiagnose.setTitle("Easy Diagnose");
		frmEasydiagnose.setBounds(100, 100, 817, 712);
		frmEasydiagnose.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
		frmEasydiagnose.getContentPane().setLayout(null);
		
		lbl_id_1 = new JLabel();
		lbl_id_1.setFont(new Font("Microsoft JhengHei", Font.BOLD, 20));
		lbl_id_1.setText("\u6570\u636E ID ");
		lbl_id_1.setBounds(45, 20, 71, 36);
		frmEasydiagnose.getContentPane().add(lbl_id_1);
		
		lbl_id_2 = new JLabel();
		lbl_id_2.setFont(new Font("Microsoft JhengHei", Font.PLAIN ,20));
		lbl_id_2.setBounds(130, 20, 410, 36);
		frmEasydiagnose.getContentPane().add(lbl_id_2);
		
		lbl_imageDisplay = new JLabel();
		lbl_imageDisplay.setBounds(47, 98, 512, 512);
		frmEasydiagnose.getContentPane().add(lbl_imageDisplay);
		
		btn_import = new JButton("\u5BFC\u5165\u6587\u4EF6");
		btn_import.setFont(new Font("Microsoft JhengHei", Font.BOLD, 20));
		btn_import.setBounds(627, 98, 130, 60);
		frmEasydiagnose.getContentPane().add(btn_import);
		btn_import.addActionListener(new ActionListener() 
			{
				public void actionPerformed(ActionEvent arg0)
				{		
					jfc.setFileSelectionMode(1);
		            int state = jfc.showOpenDialog(null);
		            if ( state == 1 ) 
		            {  
		                return;  
		            } 
		            else 
		            {  
		                File f = jfc.getSelectedFile();
		                inPath = f.getAbsolutePath() ;
//		                sendPath = "r'" + inPath + "'" ;
		                File validCheck = new File ( inPath ) ;
		                names = validCheck.list() ;
		                boolean isValid = false ;
		                for ( String s : names )
		                {
		                	if ( s.endsWith ( ".dcm" ) )
		                	{
		                		isValid = true ;
		                		break ;
		                	}
		                }
		                if ( isValid == true )
		                {
		                	btn_checkInfo.setEnabled ( true ) ;
		                	btn_startProcess.setText("\u5F00\u59CB\u68C0\u6D4B") ;
		                	btn_startProcess.setEnabled ( true ) ;
		                	scb_imageSwitch.setEnabled ( true ) ;
		                	JOptionPane.showMessageDialog(null, "加载路径成功", "",JOptionPane.WARNING_MESSAGE);
		                	currentRootPath = System.getProperty ( "user.dir" ) ;
		                	Process proc = null ;
							try 
							{
//								System.out.println("python " + "\"" + currentRootPath + File.separator + "Python_Scripts" + File.separator + "preprocess-analysis.py" + "\"" +  " " + "\"" + inPath + "\"" );
								proc = Runtime.getRuntime().exec("python " + "\"" + currentRootPath + File.separator + "Python_Scripts" + File.separator + "preprocess-analysis.py" + "\"" +  " " + "\"" + inPath + "\"" );
							}
							catch (IOException e1)
							{
								e1.printStackTrace();
							}  
		                	try 
		                	{
								proc.waitFor();
							} 
		                	catch (InterruptedException e1) 
		                	{
								e1.printStackTrace();
							} 
		                	preProcessPath = inPath + File.separator + secondaryDir ;
		                	try 
		                	{
								br = new BufferedReader ( new FileReader ( preProcessPath + File.separator + "info_basic.txt" ) ) ;
							} 
		                	catch (FileNotFoundException e) 
		                	{
		                		e.printStackTrace();
							}
		                	try 
		                	{
								id = br.readLine() ;
							} 
		                	catch (IOException e) 
		                	{
		                		e.printStackTrace();
							}
		                	lbl_id_2.setText( id );
		                	frmEasydiagnose.getContentPane().add(lbl_id_2);
		                	//打开另一个窗口并处理详细信息
		                	imagePath = preProcessPath + File.separator + thirdlyDir ;
		                	File getImage = new File ( imagePath ) ;
			                names = getImage.list() ;
			                imageDir = new ArrayList<String> () ;
			                for ( String s : names )
			                {
			                	if ( s.endsWith ( ".png" ) )
			                	{
			                		imageDir.add( imagePath + File.separator + s ) ;
			                	}
			                }
			                Collections.sort( imageDir ) ;
			                scb_imageSwitch.setMinimum( 0 ) ;
			                scb_imageSwitch.setMaximum( imageDir.size() ) ;
			                scb_imageSwitch.setValue ( 0 ) ;
			                dcmImage = new ImageIcon ( imageDir.get ( 0 ) ) ;
							lbl_imageDisplay.setIcon ( dcmImage ) ;
							frmEasydiagnose.getContentPane().add(lbl_imageDisplay);
		                }
		                else
		                {
		                	JOptionPane.showMessageDialog(null, "找不到DCM文件,请确认路径是否正确", "",JOptionPane.ERROR_MESSAGE);
		                }
		            }
				}
			});
		
		btn_checkInfo = new JButton("\u67E5\u770B\u4FE1\u606F");
		btn_checkInfo.setFont(new Font("Microsoft JhengHei", Font.BOLD, 20));
		btn_checkInfo.setBounds(627, 171, 130, 60);
		frmEasydiagnose.getContentPane().add(btn_checkInfo);
		if ( dcmReady == false )
			btn_checkInfo.setEnabled ( false ) ;
		btn_checkInfo.addActionListener(new ActionListener() 
		{
			
			public void actionPerformed(ActionEvent arg0)
			{	
				InfoDisplay infoDisplay = new InfoDisplay () ;
				infoDisplay.main( dumplicate );
			}
		});
		
		btn_startProcess = new JButton("\u5F00\u59CB\u68C0\u6D4B");//\u5F00\u59CB\u68C0\u6D4B 开始检测
		btn_startProcess.setFont(new Font("Microsoft JhengHei", Font.BOLD, 20));
		btn_startProcess.setBounds(627, 244, 130, 60);
		frmEasydiagnose.getContentPane().add(btn_startProcess);
		if ( dcmReady == false )
			btn_startProcess.setEnabled ( false ) ;
		btn_startProcess.addActionListener(new ActionListener ()
		{
			public void actionPerformed(ActionEvent arg0)
			{
				btn_import.setEnabled ( false );
				frmEasydiagnose.getContentPane().add(btn_import);
				btn_startProcess.setText("\u68C0\u6D4B\u4E2D...");//\u68C0\u6D4B\u4E2D... 检测中
				btn_startProcess.setEnabled ( false ) ;
				frmEasydiagnose.getContentPane().add(btn_startProcess);
				Process proc = null ;
				try 
				{
	//				System.out.println("python " + "\"" + currentRootPath + File.separator + "Python_Scripts" + File.separator + "predict.py" + "\"" +  " " + "\"" + inPath + "\"" + " " + "\"" + currentRootPath + File.separator + "Python_Scripts" + File.separator + "my_model.h5" + "\"" );
					proc = Runtime.getRuntime().exec("python " + "\"" + currentRootPath + File.separator + "Python_Scripts" + File.separator + "predict.py" + "\"" +  " " + "\"" + inPath + "\"" + " " + "\"" + currentRootPath + File.separator + "Python_Scripts" + File.separator + "my_model.h5" + "\"" );
//					proc = Runtime.getRuntime().exec( "python E:\\predict.py E:\\00cba091fa4ad62cc3200a657aeb957e" );
				}
				catch (IOException e1)
				{
					e1.printStackTrace();
				}  
            	try 
            	{
					proc.waitFor();
				} 
            	catch (InterruptedException e1) 
            	{
					e1.printStackTrace();
				} 
				btn_startProcess.setText("\u68C0\u6D4B\u5B8C\u6210");//\u68C0\u6D4B\u5B8C\u6210 检测完成
            	btn_import.setEnabled ( true );
            	frmEasydiagnose.getContentPane().add(btn_import);
            	frmEasydiagnose.getContentPane().add(btn_startProcess);
				try 
            	{
					br = new BufferedReader ( new FileReader ( preProcessPath + File.separator + "result.txt" ) ) ;
				} 
            	catch (FileNotFoundException e) 
            	{
            		e.printStackTrace();
				}
            	try 
            	{
					resultCondition = br.readLine() ;
					resultConfidence = br.readLine() ;
				} 
            	catch (IOException e) 
            	{
            		e.printStackTrace();
				}
            	if ( resultCondition.contains("0") )
            	{
            		lbl_predictResult_2.setText("阴性");
            	}
            	else
            	{
            		lbl_predictResult_2.setText("阳性");
            	}
            	lbl_confidence_2.setText(resultConfidence);
            	frmEasydiagnose.getContentPane().add(lbl_confidence_2);
            	frmEasydiagnose.getContentPane().add(lbl_confidence_2);
			}
			
		});
		
		scb_imageSwitch = new JScrollBar();
		scb_imageSwitch.setForeground(Color.BLACK);
		scb_imageSwitch.setBackground(Color.WHITE);
		scb_imageSwitch.setOrientation(JScrollBar.HORIZONTAL);
		scb_imageSwitch.setBounds(627, 366, 130, 21);
		frmEasydiagnose.getContentPane().add(scb_imageSwitch);
		if ( dcmReady == false )
			scb_imageSwitch.setEnabled ( false ) ;
		scb_imageSwitch.addAdjustmentListener( new AdjustmentListener()
				{
					public void adjustmentValueChanged(AdjustmentEvent evt)
					{
						dcmImage = new ImageIcon ( imageDir.get( scb_imageSwitch.getValue() ) ) ;
						lbl_imageDisplay.setIcon ( dcmImage ) ;
						frmEasydiagnose.getContentPane().add(lbl_imageDisplay);
					}
				});
		
		lbl_imageSwitch = new JLabel();
		lbl_imageSwitch.setHorizontalAlignment(SwingConstants.CENTER);
		lbl_imageSwitch.setText("\u56FE\u50CF\u5207\u6362");
		lbl_imageSwitch.setFont(new Font("Microsoft JhengHei", Font.BOLD, 20));
		lbl_imageSwitch.setBounds(627, 317, 130, 36);
		frmEasydiagnose.getContentPane().add(lbl_imageSwitch);
		
		lbl_predictResult_1 = new JLabel();
		lbl_predictResult_1.setFont(new Font("Microsoft JhengHei", Font.BOLD, 20));
		lbl_predictResult_1.setText("\u9884\u6D4B\u7ED3\u679C ");
		lbl_predictResult_1.setBounds(650, 411, 92, 43);
		frmEasydiagnose.getContentPane().add(lbl_predictResult_1);
		
		lbl_predictResult_2 = new JLabel();
		lbl_predictResult_2.setFont(new Font("Microsoft JhengHei", Font.PLAIN, 20));
		lbl_predictResult_2.setBounds(650, 467, 86, 36);
		frmEasydiagnose.getContentPane().add(lbl_predictResult_2);
		
		lbl_confidence_1 = new JLabel();
		lbl_confidence_1.setText("\u7F6E\u4FE1\u7A0B\u5EA6 ");
		lbl_confidence_1.setFont(new Font("Microsoft JhengHei", Font.BOLD, 20));
		lbl_confidence_1.setBounds(650, 516, 92, 43);
		frmEasydiagnose.getContentPane().add(lbl_confidence_1);
		
		lbl_confidence_2 = new JLabel();
		lbl_confidence_2.setFont(new Font("Microsoft JhengHei", Font.PLAIN, 20));
		lbl_confidence_2.setBounds(650, 572, 86, 38);
		frmEasydiagnose.getContentPane().add(lbl_confidence_2);
		
		lbl_logoDisplay = new JLabel("logo");
		lbl_logoDisplay.setBounds(587, 13, 200, 50);
		logoImage = new ImageIcon ( "logo" + File.separator + "Easy_Diagnose.png" ) ;
		logoImage.setImage(logoImage.getImage().getScaledInstance(200,50,Image.SCALE_DEFAULT));
		lbl_logoDisplay.setIcon ( logoImage ) ;
		frmEasydiagnose.getContentPane().add(lbl_logoDisplay);
	}
}
