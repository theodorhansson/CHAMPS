﻿using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Windows.Forms;
using System.Runtime.InteropServices;

using System.Threading;
using System.Drawing.Imaging;

using Hamamatsu.DCAM4;
using Hamamatsu.subacq4;

namespace csAcq4
{
    public partial class FormMain : Form
    {
        private enum FormStatus
        {
            Startup,                // After startup or camapi_uninit()
            Initialized,            // After dcamapi_init() or dcamdev_close()
            Opened,                 // After dcamdev_open() or dcamcap_stop() without any image
            Acquiring,              // After dcamcap_start()
            AcquiringSoftwareTrigger,
            Acquired                // After dcamcap_stop() with image
        }

        private MyDcam mydcam;
        private MyDcamWait mydcamwait;
        private MyImage m_image;
        private MyLut m_lut;
        private readonly object BitmapLock;

        private struct MyLut
        {
            public int camerabpp;          // camera bit per pixel.  This sample code only support MONO.
            public int cameramax;

            public int inmax;
            public int inmin;
        };

        private int m_indexCamera = 0;          // index of DCAM device.  This is used at allocating mydcam instance.
        private int m_nFrameCount;              // frame count of allocation buffer for DCAM capturing
        private FormStatus m_formstatus;        // Indicate current Form status. For setting, Use MyFormStatus() functions
        private Thread m_threadCapture;         // System.Threading.  Assigned for monitoring updated frames during capturing
        private Bitmap m_bitmap;                // bitmap data for displaying in this Windows Form
        private bool m_cap_stopping = false;    // reset to false when starting capture and set to true if stopping capture

        private FormProperties formProperties;  // Properties Form

        // ---------------- private class MyImage ----------------

        private class MyImage
        {
            public DCAMBUF_FRAME bufframe;
            public MyImage()
            {
                bufframe = new DCAMBUF_FRAME(0);
            }
            public int width { get { return bufframe.width; } }
            public int height { get { return bufframe.height; } }
            public DCAM_PIXELTYPE pixeltype { get { return bufframe.type; } }
            public bool isValid()
            {
                if (width <= 0 || height <= 0 || pixeltype == DCAM_PIXELTYPE.NONE)
                {
                    return false;
                }
                else
                {
                    return true;
                }
            }
            public void clear()
            {
                bufframe.width = 0;
                bufframe.height = 0;
                bufframe.type = DCAM_PIXELTYPE.NONE;
            }
            public void set_iFrame(int index)
            {
                bufframe.iFrame = index;
            }
        }

        // ---------------- Local functions ----------------

        // My Form Status helper
        private void MyFormStatus(FormStatus status)
        {
            Boolean isStartup = (status == FormStatus.Startup);
            Boolean isInitialized = (status == FormStatus.Initialized);
            Boolean isOpened = (status == FormStatus.Opened);
            Boolean isAcquiring = (status == FormStatus.Acquiring) || (status == FormStatus.AcquiringSoftwareTrigger);
            Boolean isAcquired = (status == FormStatus.Acquired);
            Boolean isAcquiringSoftwareTrigger = (status == FormStatus.AcquiringSoftwareTrigger);
            PushInit.Enabled = isStartup;
            PushOpen.Enabled = isInitialized;
            PushInfo.Enabled = (isOpened || isAcquired || isAcquiring);
            PushSnap.Enabled = (isOpened || isAcquired);
            PushLive.Enabled = (isOpened || isAcquired);
            PushFireTrigger.Enabled = isAcquiringSoftwareTrigger;
            PushIdle.Enabled = isAcquiring;
            PushBufRelease.Enabled = isAcquired;
            PushClose.Enabled = (isOpened || isAcquired);
            PushUninit.Enabled = isInitialized;

            PushProperties.Enabled = (isOpened || isAcquired);

            if (isInitialized || isOpened)
            {
                // acquisition is not starting
                MyThreadCapture_Abort();
            }

            m_formstatus = status;
        }
        private void MyFormStatus_Startup() { MyFormStatus(FormStatus.Startup); }
        private void MyFormStatus_Initialized() { MyFormStatus(FormStatus.Initialized); }
        private void MyFormStatus_Opened() { MyFormStatus(FormStatus.Opened); }
        private void MyFormStatus_Acquiring() { MyFormStatus(FormStatus.Acquiring); }
        private void MyFormStatus_AcquiringSoftwareTrigger() { MyFormStatus(FormStatus.AcquiringSoftwareTrigger); }
        private void MyFormStatus_Acquired() { MyFormStatus(FormStatus.Acquired); }

        private Boolean IsMyFormStatus_Startup() { return (m_formstatus == FormStatus.Startup); }
        private Boolean IsMyFormStatus_Initialized() { return (m_formstatus == FormStatus.Initialized); }
        private Boolean IsMyFormStatus_Opened() { return (m_formstatus == FormStatus.Opened); }
        private Boolean IsMyFormStatus_Acquiring() { return (m_formstatus == FormStatus.Acquiring) || (m_formstatus == FormStatus.AcquiringSoftwareTrigger); }
        private Boolean IsMyFormStatus_Acquired() { return (m_formstatus == FormStatus.Acquired); }

        // Display status
        private void MyShowStatus(string text) { LabelStatus.Text = text; }
        private void MyShowStatusOK(string text) { MyShowStatus("OK: " + text); }
        private void MyShowStatusNG(string text, DCAMERR err)
        {
            MyShowStatus(String.Format("NG: 0x{0:X8}:{1}", (int)err, text));
        }

        // update LUT condition
        private void update_lut(bool bUpdatePicture)
        {
            if (mydcam != null)
            {
                MyDcamProp prop = new MyDcamProp(mydcam, DCAMIDPROP.BITSPERCHANNEL);

                double v = 0;
                prop.getvalue(ref v);
                bool reset = false;
                if (m_lut.camerabpp > 0 && m_lut.camerabpp != (int)v)
                {
                    reset = true;
                }
                m_lut.camerabpp = (int)v;
                m_lut.cameramax = (1 << m_lut.camerabpp) - 1;

                m_lut.inmax = HScrollLutMax.Value;
                m_lut.inmin = HScrollLutMin.Value;

                HScrollLutMax.Maximum = m_lut.cameramax;
                HScrollLutMin.Maximum = m_lut.cameramax;

                if (reset)
                {
                    HScrollLutMax.Value = m_lut.cameramax;
                    HScrollLutMin.Value = 0;
                    bUpdatePicture = true;
                }
 
                if (bUpdatePicture)
                    MyUpdatePicture();
            }
        }

        // auto LUT condition
        private void auto_lut()
        {
            bool bUpdatePicture = false;
            int min = m_lut.cameramax;
            int max = 0;
            if (m_image.isValid())
            {
                int w = PicDisplay.Size.Width;
                int h = PicDisplay.Size.Height;
                if (w > m_image.width) w = m_image.width;
                if (h > m_image.height) h = m_image.height;

                Int16[] s = new Int16[w];

                // Displaying center of the image
                Int32 y0 = (m_image.height - h) / 2;
                Int32 x0 = (m_image.width - w) / 2;

                Int32 y;
                for (y = 0; y < h; y++)
                {
                    Int32 offset;

                    offset = m_image.bufframe.rowbytes * (y + y0) + (x0 * 2);// In bytes, so multiply by bpp
                    Marshal.Copy((IntPtr)(m_image.bufframe.buf.ToInt64() + offset), s, 0, w);

                    Int32 x;
                    for (x = 0; x < w; x++)
                    {
                        UInt16 u = (UInt16)s[x];
                        if (u > max)
                            max = u;
                        else if (u < min)
                            min = u;
                    }
                }
            }

            if (m_lut.inmax != max)
            {
                m_lut.inmax = max;
                HScrollLutMax.Value = m_lut.inmax;
                EditLutMax.Text = m_lut.inmax.ToString();
                bUpdatePicture = true;
            }

            if (m_lut.inmin != min)
            {
                m_lut.inmin = min;
                HScrollLutMin.Value = m_lut.inmin;
                EditLutMin.Text = m_lut.inmin.ToString();
                bUpdatePicture = true;
            }
            
            if (bUpdatePicture)
                MyUpdatePicture();
        }

        // Updating myimage by DCAM frame
        private void MyUpdateImage(int iFrame)
        {
            // lock selected frame by iFrame
            m_image.set_iFrame(iFrame);
            if (!mydcam.buf_lockframe(ref m_image.bufframe))
            {
                // Fail: dcambuf_lockframe()
                m_image.clear();
            }

            MyUpdatePicture();

        }

        // Draw Bitmap in the PictureBox 
        private delegate void MyDelegate_UpdateDisplay();

        private void MyUpdateDisplay()
        {
            Image oldImg = PicDisplay.Image;
            if (m_bitmap != null)
            {
                m_lut.inmax = HScrollLutMax.Value;
                m_lut.inmin = HScrollLutMin.Value;

                // Show center of image
                Int32 y0 =  (m_image.height - PicDisplay.Height) / 2;
                Int32 x0 =  (m_image.width - PicDisplay.Width) / 2;

                Rectangle rc = new Rectangle(x0, y0, PicDisplay.Width, PicDisplay.Height);
                Bitmap bmp = new Bitmap(PicDisplay.Width, PicDisplay.Height, PixelFormat.Format24bppRgb);
                using (var gr = Graphics.FromImage(bmp))
                {
                    gr.DrawImage(m_bitmap, 0, 0, rc, GraphicsUnit.Pixel);
                }
            
                PicDisplay.Image = bmp;
                PicDisplay.Refresh();
             
            }
            else
            {
                PicDisplay.Image = null;
            }

            if (oldImg != null)
                oldImg.Dispose();

        }

        // Updating Bitmap and Display
        private void MyUpdatePicture()
        {
            if (m_image.isValid())
            {
                m_lut.inmax = HScrollLutMax.Value;
                m_lut.inmin = HScrollLutMin.Value;

                Rectangle rc = new Rectangle(0, 0, m_image.width, m_image.height);
                lock (BitmapLock)
                {
                    Bitmap oldBitmap = m_bitmap;
                    m_bitmap = new Bitmap(m_image.width, m_image.height, PixelFormat.Format24bppRgb);

                    SUBACQERR err = subacq.copydib(ref m_bitmap, m_image.bufframe, ref rc, m_lut.inmax, m_lut.inmin, m_lut.camerabpp);

                    if (oldBitmap != null)
                        oldBitmap.Dispose();
                }

            }
          
            if (InvokeRequired)
            {
                // worker thread calls this function
                // only display drawing needs to be called from Main Thread
                Invoke(new MyDelegate_UpdateDisplay(MyUpdateDisplay));
                return;
            }

            MyUpdateDisplay();

        }

        // Capturing Thread helper functions
        private void MyThreadCapture_Start()
        {
            m_threadCapture = new Thread(new ThreadStart(OnThreadCapture));

            m_threadCapture.IsBackground = true;
            m_threadCapture.Start();
        }
        void MyThreadCapture_Abort()
        {
            if (m_threadCapture != null)
            {
                if (mydcamwait != null)
                    mydcamwait.abort();

                m_threadCapture.Abort();
            }
        }

        // Updating myimage by DCAM frame
        private delegate void MyDelegate_SnapCaptureFinished();
        private void MySnapCaptureFinished()
        {
            if (InvokeRequired)
            {
                // worker thread calls this function
                Invoke(new MyDelegate_SnapCaptureFinished(MySnapCaptureFinished), null);
                return;
            }

            MyShowStatusOK("mydcamwait.start(eventhappened && DCAMWAIT.CAPEVENT.STOPPED) &&&& DCAMCAP_START.SNAP");
            MyFormStatus_Acquired();            // change dialog FormStatus to Acquired
        }

        private void OnThreadCapture()
        {
            bool bContinue = true;

            using (mydcamwait = new MyDcamWait(ref mydcam))
            {
                while (bContinue)
                {
                    DCAMWAIT eventmask = DCAMWAIT.CAPEVENT.FRAMEREADY | DCAMWAIT.CAPEVENT.STOPPED;
                    DCAMWAIT eventhappened = DCAMWAIT.NONE;
                    if (mydcamwait.start(eventmask, ref eventhappened))
                    {
                        if (eventhappened & DCAMWAIT.CAPEVENT.FRAMEREADY)
                        {
                            int iNewestFrame = 0;
                            int iFrameCount = 0;

                            if (mydcam.cap_transferinfo(ref iNewestFrame, ref iFrameCount))
                            {
                                MyUpdateImage(iNewestFrame);
                            }
                        }

                        if (eventhappened & DCAMWAIT.CAPEVENT.STOPPED)
                        {
                            bContinue = false;
                            if (m_cap_stopping == false && mydcam.m_capmode == DCAMCAP_START.SNAP)
                            {
                                // in this condition, cap_stop() happens automatically, so update the main dialog
                                MySnapCaptureFinished();
                            }
                        }
                    }
                    else
                    {
                        if (mydcamwait.m_lasterr == DCAMERR.TIMEOUT)
                        {
                            // nothing to do
                        }
                        else
                        if (mydcamwait.m_lasterr == DCAMERR.ABORT)
                        {
                            bContinue = false;
                        }
                    }
                }
            }
        }

        // ---------------- constructor of FormMain ----------------

        public FormMain()
        {
            InitializeComponent();
            m_image = new MyImage();
            m_lut = new MyLut();
            BitmapLock = new object();
        }

        // ---------------- Windows Form Command Handler ----------------
        private void FormMain_Load(object sender, EventArgs e)
        {
            // Initialize form status
            MyFormStatus_Startup();
            m_nFrameCount = 3;

            // Update window title
            if (IntPtr.Size == 4)
            {
                Text = "csAcq4 (32 bit)";
            }
            else
            if (IntPtr.Size == 8)
            {
                Text = "csAcq4 (64 bit)";
            }
        }

        private void FormMain_FormClosing(object sender, FormClosingEventArgs e)
        {
            MyThreadCapture_Abort();                // abort capturing thread if exist

            if (mydcam != null)                     // close device if exist
            {
                mydcam.dev_close();
                mydcam = null;
            }

            if (!IsMyFormStatus_Startup())          // uninitialize if necessary
            {
                MyDcamApi.uninit();
            }
        }
        // ---------------- DCAM-API related command handler ----------------

        private void PushInit_Click(object sender, EventArgs e)
        {
            // dcamapi_init() may takes for a few seconds
            Cursor.Current = Cursors.WaitCursor;

            if (!MyDcamApi.init())
            {
                MyShowStatusNG("dcamapi_init()", MyDcamApi.m_lasterr);
                Cursor.Current = Cursors.Default;
                return;                         // Fail: dcamapi_init()
            }

            // Success: dcamapi_init()

            MyShowStatusOK("dcamapi_init()");
            MyFormStatus_Initialized();
            Cursor.Current = Cursors.Default;
        }
        private void PushUninit_Click(object sender, EventArgs e)
        {
            if (!MyDcamApi.uninit())
            {
                MyShowStatusNG("dcamapi_uninit()", MyDcamApi.m_lasterr);
                return;                         // Fail: dcamapi_uninit()
            }

            // Success: dcamapi_uninit()

            MyShowStatusOK("dcamapi_uninit()");
            MyFormStatus_Startup();             // change dialog FormStatus to Startup
        }
        private void PushOpen_Click(object sender, EventArgs e)
        {
            if (mydcam != null)
            {
                MyShowStatus("Internal Error: mydcam is already set");
                MyFormStatus_Initialized();     // FormStatus should be Initialized.
                return;                         // internal error
            }

            // dcamdev_open() may takes for a few seconds
            Cursor.Current = Cursors.WaitCursor;

            MyDcam aMyDcam = new MyDcam();
            if (!aMyDcam.dev_open(m_indexCamera))
            {
                MyShowStatusNG("dcamdev_open()", aMyDcam.m_lasterr);
                aMyDcam = null;
                Cursor.Current = Cursors.Default;
                return;                         // Fail: dcamdev_open()
            }

            // Success: dcamdev_open()

            mydcam = aMyDcam;					// store MyDcam instance

            MyShowStatusOK("dcamdev_open()");
            MyFormStatus_Opened();              // change dialog FormStatus to Opened
            Cursor.Current = Cursors.Default;
        }
        private void PushClose_Click(object sender, EventArgs e)
        {
            if (mydcam == null)
            {
                MyShowStatus("Internal Error: mydcam is null");
                MyFormStatus_Initialized();     // FormStatus should be Initialized.
                return;                         // internal error
            }

            MyThreadCapture_Abort();            // abort capturing thread if exist

            if (!mydcam.dev_close())
            {
                MyShowStatusNG("dcamdev_close()", mydcam.m_lasterr);
                return;                         // Fail: dcamdev_close()
            }

            // Success: dcamdev_close()

            mydcam = null;

            MyShowStatusOK("dcamdev_close()");
            MyFormStatus_Initialized();         // change dialog FormStatus to Initialized
        }
        private void PushInfo_Click(object sender, EventArgs e)
        {
            FormInfo formInfo = new FormInfo();

            formInfo.set_mydcam(ref mydcam);
            formInfo.Show();                    // show FormProperties dialog as modeless
        }
        private void PushProperties_Click(object sender, EventArgs e)
        {
            if (formProperties == null)
            {
                formProperties = new FormProperties();
            }
            else if (formProperties.IsDisposed)
            {
                formProperties = new FormProperties();
            }

            formProperties.set_mydcam(ref mydcam);
            formProperties.Show();          // show FormProperties dialog as modeless
            formProperties.update_properties();
        }
        private void PushSnap_Click(object sender, EventArgs e)
        {
            if (mydcam == null)
            {
                MyShowStatus("Internal Error: mydcam is null");
                MyFormStatus_Initialized();     // FormStatus should be Initialized.
                return;                         // internal error
            }

            string text = "";

            if (IsMyFormStatus_Opened())
            {
                // if FormStatus is Opened, DCAM buffer is not allocated.
                // So call dcambuf_alloc() to prepare capturing.

                text = string.Format("dcambuf_alloc({0})", m_nFrameCount);

                // allocate frame buffer
                if (!mydcam.buf_alloc(m_nFrameCount))
                {
                    // allocation was failed
                    MyShowStatusNG(text, mydcam.m_lasterr);
                    return;                     // Fail: dcambuf_alloc()
                }

                // Success: dcambuf_alloc()

                update_lut(false);
            }

            // start acquisition
            m_cap_stopping = false;
            mydcam.m_capmode = DCAMCAP_START.SNAP;    // one time capturing.  acqusition will stop after capturing m_nFrameCount frames
            if (!mydcam.cap_start())
            {
                // acquisition was failed. In this sample, frame buffer is also released.
                MyShowStatusNG("dcamcap_start()", mydcam.m_lasterr);

                mydcam.buf_release();           // release unnecessary buffer in DCAM
                MyFormStatus_Opened();          // change dialog FormStatus to Opened
                return;                         // Fail: dcamcap_start()
            }

            // Success: dcamcap_start()
            // acquisition has started

            if (text.Length > 0)
            {
                text += " && ";
            }
            MyShowStatusOK(text + "dcamcap_start()");

            MyDcamProp prop = new MyDcamProp(mydcam, DCAMIDPROP.TRIGGERSOURCE);

            double v = 0;
            prop.getvalue(ref v);

            if (v == DCAMPROP.TRIGGERSOURCE.SOFTWARE)
            {
                MyFormStatus_AcquiringSoftwareTrigger(); // change dialog FormStatus to AcquiringSoftwareTrigger
            }
            else
            {
                MyFormStatus_Acquiring();           // change dialog FormStatus to Acquiring
            }

            MyThreadCapture_Start();            // start monitoring thread
        }
        private void PushLive_Click(object sender, EventArgs e)
        {
            if (mydcam == null)
            {
                MyShowStatus("Internal Error: mydcam is null");
                MyFormStatus_Initialized();     // FormStatus should be Initialized.
                return;                         // internal error
            }

            string text = "";

            if (IsMyFormStatus_Opened())
            {
                // if FormStatus is Opened, DCAM buffer is not allocated.
                // So call dcambuf_alloc() to prepare capturing.

                text = string.Format("dcambuf_alloc({0})", m_nFrameCount);

                // allocate frame buffer
                if (!mydcam.buf_alloc(m_nFrameCount))
                {
                    // allocation was failed
                    MyShowStatusNG(text, mydcam.m_lasterr);
                    return;                     // Fail: dcambuf_alloc()
                }

                // Success: dcambuf_alloc()

                update_lut(false);
            }

            // start acquisition
            m_cap_stopping = false;
            mydcam.m_capmode = DCAMCAP_START.SEQUENCE;    // continuous capturing.  continuously acqusition will be done
            if (!mydcam.cap_start())
            {
                // acquisition was failed. In this sample, frame buffer is also released.
                MyShowStatusNG("dcamcap_start()", mydcam.m_lasterr);

                mydcam.buf_release();           // release unnecessary buffer in DCAM
                MyFormStatus_Opened();          // change dialog FormStatus to Opened
                return;                         // Fail: dcamcap_start()
            }

            // Success: dcamcap_start()
            // acquisition has started

            if (text.Length > 0)
            {
                text += " && ";
            }
            MyShowStatusOK(text + "dcamcap_start()");

            MyDcamProp prop = new MyDcamProp(mydcam, DCAMIDPROP.TRIGGERSOURCE);
            double v = 0;
            prop.getvalue(ref v);

            if (v == DCAMPROP.TRIGGERSOURCE.SOFTWARE)
            {
                MyFormStatus_AcquiringSoftwareTrigger(); // change dialog FormStatus to AcquiringSoftwareTrigger
            }
            else
            {
                MyFormStatus_Acquiring();           // change dialog FormStatus to Acquiring
            }
            MyThreadCapture_Start();            // start monitoring thread
        }
        private void PushIdle_Click(object sender, EventArgs e)
        {
            if (mydcam == null)
            {
                MyShowStatus("Internal Error: mydcam is null");
                MyFormStatus_Initialized();     // FormStatus should be Initialized.
                return;                         // internal error
            }

            if (!IsMyFormStatus_Acquiring())
            {
                MyShowStatus("Internal Error: Idle button is only available when FormStatus is Acquiring");
                return;                         // internal error
            }

            // stop acquisition
            m_cap_stopping = true;
            if (!mydcam.cap_stop())
            {
                MyShowStatusNG("dcamcap_stop()", mydcam.m_lasterr);
                return;                         // Fail: dcamcap_stop()
            }

            // Success: dcamcap_stop()

            MyShowStatusOK("dcamcap_stop()");
            MyFormStatus_Acquired();            // change dialog FormStatus to Acquired
        }
        private void PushFireTrigger_Click(object sender, EventArgs e)
        {
            if (mydcam == null)
            {
                MyShowStatus("Internal Error: mydcam is null");
                MyFormStatus_Initialized();     // FormStatus should be Initialized.
                return;                         // internal error
            }

            if (!IsMyFormStatus_Acquiring())
            {
                MyShowStatus("Internal Error: FireTrigger button is only available when FormStatus is Acquiring");
                return;                         // internal error
            }

            // fire software trigger
            if (!mydcam.cap_firetrigger())
            {
                MyShowStatusNG("dcamcap_firetrigger()", mydcam.m_lasterr);
                return;                         // Fail: dcamcap_firetrigger()
            }

            // Success: dcamcap_firetrigger()

            MyShowStatusOK("dcamcap_firetrigger()");

            // FormStatus is not changed here
        }
        private void PushBufRelease_Click(object sender, EventArgs e)
        {
            if (mydcam == null)
            {
                MyShowStatus("Internal Error: mydcam is null");
                MyFormStatus_Initialized();     // FormStatus should be Initialized.
                return;                         // internal error
            }

            if (!IsMyFormStatus_Acquired())
            {
                MyShowStatus("Internal Error: BufRelease is only available when FormStatus is Acquired");
                return;                         // internal error
            }

            // release buffer
            if (!mydcam.buf_release())
            {
                MyShowStatusNG("dcambuf_release()", mydcam.m_lasterr);
                return;                         // Fail: dcambuf_release()
            }

            // Success: dcambuf_release()

            MyShowStatusOK("dcambuf_release()");
            MyFormStatus_Opened();              // change dialog FormStatus to Opened

            m_image.clear();
        }

        private void EditLutMax_TextChanged(object sender, EventArgs e)
        {
            try
            {
                m_lut.inmax = int.Parse(EditLutMax.Text);
                if (HScrollLutMax.Value != m_lut.inmax && 0 <= m_lut.inmax && m_lut.inmax <= m_lut.cameramax)
                {
                    HScrollLutMax.Value = m_lut.inmax;
                    MyUpdatePicture();
                }
            }
            catch
            {
                m_lut.inmax = 0;
            }
        }

        private void EditLutMin_TextChanged(object sender, EventArgs e)
        {
            try
            {
                m_lut.inmin = int.Parse(EditLutMin.Text);
                if (HScrollLutMin.Value != m_lut.inmin && 0 <= m_lut.inmin && m_lut.inmin <= m_lut.cameramax)
                {
                    HScrollLutMin.Value = m_lut.inmin;
                    MyUpdatePicture();
                }
            }
            catch
            {
                m_lut.inmin = 0;
            }
        }

        private void HScrollLutMax_ValueChanged(object sender, EventArgs e)
        {
            if (m_lut.inmax != HScrollLutMax.Value)
            {
                m_lut.inmax = HScrollLutMax.Value;
                EditLutMax.Text = m_lut.inmax.ToString();
                MyUpdatePicture();
            }
        }

        private void HScrollLutMin_ValueChanged(object sender, EventArgs e)
        {
            if (m_lut.inmin != HScrollLutMin.Value)
            {
                m_lut.inmin = HScrollLutMin.Value;
                EditLutMin.Text = m_lut.inmin.ToString();
                MyUpdatePicture();
            }
        }

        private void PushAsterisk_Click(object sender, EventArgs e)
        {
            auto_lut();
        }

        private void toolTip1_Popup(object sender, PopupEventArgs e)
        {

        }
    }
}
