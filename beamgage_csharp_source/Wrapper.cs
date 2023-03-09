using Spiricon.Automation;
using System.Collections.Generic;

namespace Beamgage_python_wrapper
{
    public class Beamgage
    {

        public AutomatedBeamGage bg;

        public Beamgage(string title, bool show)
        {
            bg = new AutomatedBeamGage(title, show);
        }

        public AutomatedBeamGage get_AutomatedBeamGage()
        {
            return bg;
        }

        public double[] get_Data_Double()
        {
            return bg.ResultsPriorityFrame.DoubleData;
        }
    }
}