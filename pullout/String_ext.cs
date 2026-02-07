using OpenQA.Selenium;
using OpenQA.Selenium.Chrome;
using System;
using System.Collections.Generic;
using System.IO;
using System.Threading;

static class String_ext
{
    /// <summary>
    /// Parses the string as a price value
    /// </summary>
    /// <param name="s">Input string</param>
    /// <returns>Price value</returns>
    /// <exception cref="ArgumentNullException"><paramref name="s"/> is null</exception>
    public static float ToPrice(this string s)
    {
        try
        {
            using (StringWriter str = new StringWriter())
            {
                // Remove non-number characters
                bool cents = false;
                foreach (char c in s)
                {
                    if (c >= '0' && c <= '9')
                        str.Write(c);
                    else if ((!cents) && c == '.')
                    {
                        str.Write(c);
                        cents = true;
                    }
                }
                // Parse
                return float.Parse(str.ToString());
            }
        }
        catch when (s is null)
        {
            throw new ArgumentNullException(nameof(s));
        }
    }

}