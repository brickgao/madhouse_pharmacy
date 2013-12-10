// mwic_rdDlg.cpp : implementation file
//

#include "stdafx.h"
#include "mwic_rd.h"
#include "mwic_rdDlg.h"
#include "mwic_32.h"

#ifdef _DEBUG
#define new DEBUG_NEW
#undef THIS_FILE
static char THIS_FILE[] = __FILE__;
#endif

/////////////////////////////////////////////////////////////////////////////
// CAboutDlg dialog used for App About

class CAboutDlg : public CDialog
{
public:
	CAboutDlg();

// Dialog Data
	//{{AFX_DATA(CAboutDlg)
	enum { IDD = IDD_ABOUTBOX };
	//}}AFX_DATA

	// ClassWizard generated virtual function overrides
	//{{AFX_VIRTUAL(CAboutDlg)
	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV support
	//}}AFX_VIRTUAL

// Implementation
protected:
	//{{AFX_MSG(CAboutDlg)
	//}}AFX_MSG
	DECLARE_MESSAGE_MAP()
};

CAboutDlg::CAboutDlg() : CDialog(CAboutDlg::IDD)
{
	//{{AFX_DATA_INIT(CAboutDlg)
	//}}AFX_DATA_INIT
}

void CAboutDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CAboutDlg)
	//}}AFX_DATA_MAP
}

BEGIN_MESSAGE_MAP(CAboutDlg, CDialog)
	//{{AFX_MSG_MAP(CAboutDlg)
		// No message handlers
	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CMwic_rdDlg dialog

CMwic_rdDlg::CMwic_rdDlg(CWnd* pParent /*=NULL*/)
	: CDialog(CMwic_rdDlg::IDD, pParent)
{
	//{{AFX_DATA_INIT(CMwic_rdDlg)
		// NOTE: the ClassWizard will add member initialization here
	//}}AFX_DATA_INIT
	// Note that LoadIcon does not require a subsequent DestroyIcon in Win32
	m_hIcon = AfxGetApp()->LoadIcon(IDR_MAINFRAME);
}

CMwic_rdDlg::~CMwic_rdDlg ()
{
	st=ic_exit(icdev);
}

void CMwic_rdDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialog::DoDataExchange(pDX);
	//{{AFX_DATA_MAP(CMwic_rdDlg)
	DDX_Control(pDX, IDC_LIST1, m_list);
	//}}AFX_DATA_MAP
}

BEGIN_MESSAGE_MAP(CMwic_rdDlg, CDialog)
	//{{AFX_MSG_MAP(CMwic_rdDlg)
	ON_WM_SYSCOMMAND()
	ON_WM_PAINT()
	ON_WM_QUERYDRAGICON()
	ON_COMMAND(ID_MENUITEMEXIT, OnMenuitemexit)
	ON_COMMAND(ID_MENUITEMCONN, OnMenuitemconn)
	ON_COMMAND(ID_MENUITEM4442, OnMenuitem4442)


	//}}AFX_MSG_MAP
END_MESSAGE_MAP()

/////////////////////////////////////////////////////////////////////////////
// CMwic_rdDlg message handlers

BOOL CMwic_rdDlg::OnInitDialog()
{
	CDialog::OnInitDialog();

	// Add "About..." menu item to system menu.

	// IDM_ABOUTBOX must be in the system command range.
	ASSERT((IDM_ABOUTBOX & 0xFFF0) == IDM_ABOUTBOX);
	ASSERT(IDM_ABOUTBOX < 0xF000);

	CMenu* pSysMenu = GetSystemMenu(FALSE);
	if (pSysMenu != NULL)
	{
		CString strAboutMenu;
		strAboutMenu.LoadString(IDS_ABOUTBOX);
		if (!strAboutMenu.IsEmpty())
		{
			pSysMenu->AppendMenu(MF_SEPARATOR);
			pSysMenu->AppendMenu(MF_STRING, IDM_ABOUTBOX, strAboutMenu);
		}
	}

	// Set the icon for this dialog.  The framework does this automatically
	//  when the application's main window is not a dialog
	SetIcon(m_hIcon, TRUE);			// Set big icon
	SetIcon(m_hIcon, FALSE);		// Set small icon
	
	// TODO: Add extra initialization here
    HMENU hmnu;
	hmnu=LoadMenu(AfxGetInstanceHandle(),MAKEINTRESOURCE(IDR_MENU1));
	::SetMenu(m_hWnd,hmnu);
	return TRUE;  // return TRUE  unless you set the focus to a control
}

void CMwic_rdDlg::OnSysCommand(UINT nID, LPARAM lParam)
{
	if ((nID & 0xFFF0) == IDM_ABOUTBOX)
	{
		CAboutDlg dlgAbout;
		dlgAbout.DoModal();
	}
	else
	{
		CDialog::OnSysCommand(nID, lParam);
	}
}

// If you add a minimize button to your dialog, you will need the code below
//  to draw the icon.  For MFC applications using the document/view model,
//  this is automatically done for you by the framework.

void CMwic_rdDlg::OnPaint() 
{
	if (IsIconic())
	{
		CPaintDC dc(this); // device context for painting

		SendMessage(WM_ICONERASEBKGND, (WPARAM) dc.GetSafeHdc(), 0);

		// Center icon in client rectangle
		int cxIcon = GetSystemMetrics(SM_CXICON);
		int cyIcon = GetSystemMetrics(SM_CYICON);
		CRect rect;
		GetClientRect(&rect);
		int x = (rect.Width() - cxIcon + 1) / 2;
		int y = (rect.Height() - cyIcon + 1) / 2;

		// Draw the icon
		dc.DrawIcon(x, y, m_hIcon);
	}
	else
	{
		CDialog::OnPaint();
	}
}

// The system calls this to obtain the cursor to display while the user drags
//  the minimized window.
HCURSOR CMwic_rdDlg::OnQueryDragIcon()
{
	return (HCURSOR) m_hIcon;
}

void CMwic_rdDlg::OnMenuitemexit() 
{
	// TODO: Add your command handler code here
   st=ic_exit(icdev);
   OnOK();
}







void CMwic_rdDlg::OnMenuitemconn() 
{
	// TODO: Add your command handler code here
 l=0;
 m_list.ResetContent();
 port=1;    //COM2
 baud=9600;//115200;
 status=0;
 l=0;
 icdev=ic_init(port,baud);
 if (icdev<0)
 {
   m_list.InsertString(l,"ic_init() error!");
   l++;
   goto end;
 }
 else
 {
   m_list.InsertString(l,"ic_init() ok");
   l++;
 }

 st=get_status(icdev,&status);
 if (st<0) 
 {
	m_list.InsertString(l,"get_status() error!");
    l++;
	goto end;
 }
 else
 {
	m_list.InsertString(l,"get_status() ok!");
    l++;
 }
end: ;		
}

void CMwic_rdDlg::OnMenuitem4442() 
{
	// TODO: Add your command handler code here
	l=0;
	m_list.ResetContent ();
	st=chk_4442(icdev);//检查卡
	if (st!=0) 
	{
       m_list.InsertString(l,"chk_4442() error!");
	   l++;
	   goto end;
	}
	else
	{
		m_list.InsertString(l,"chk_4442() ok!");
        l++;
	}
	key[0]=0xff;
    key[1]=0xff;
	key[2]=0xff;
	st=csc_4442(icdev,3,key);//核对卡密码
	if (st!=0) 
	{
		m_list.InsertString (l,"csc_4442() error!");
        l++;
		goto end;
	}
	else
	{
		m_list.InsertString (l,"csc_4442() ok!");
        l++;
    }
	
    st = rsct_4442(icdev,&counter);//读出卡密码计数器 
    if (st!= 0)
    {
		m_list.InsertString (l,"rsct_4442() error");
        l++;
	    goto end;
	}
    else
	{
		
        memset(c3,0x20,200);
		memcpy(c3,"rsct_4442() ok! The counter is:",31);
		_itoa(counter,c3+31,2);
		m_list.InsertString (l,c3);
		l++;
    }
        
	
    offset = 40;
    lenth = 10;
    memcpy(data1, "1234567890",10);
    st = swr_4442(icdev, offset, lenth, data1);//向 从40开始的地址 写入“1234567890”数据
    if (st != 0) 
    {     
	   m_list.InsertString (l,"swr_4442() error!");
        l++;
	   goto end;
	}
	else 
	{
	    m_list.InsertString (l,"swr_4442() ok! Write 1234567890");
        l++;
    }
 
    st = srd_4442(icdev, offset, lenth, data2);//读出数据
    if (st !=0) 
    {
        m_list.InsertString (l,"srd_4442() error! Read ");
        l++;
        goto end;
	}
    else
	{
        memset(c3,0x20,200);
		memcpy(c3,"srd_4442() ok! Read:",20);
		memcpy(c3+21,data2,10);
		m_list.InsertString (l,c3);
        l++;
    }


  
end:;
	
}




