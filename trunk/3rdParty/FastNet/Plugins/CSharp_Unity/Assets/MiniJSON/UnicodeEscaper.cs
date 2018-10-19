using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;

public class UnicodeEscaper
{
    public static string Escape(string s)
    {
        StringBuilder sb = new StringBuilder();
        byte[] bytes = Encoding.Unicode.GetBytes(s);
        for (int i = 0; i < bytes.Length; i += 2)
        {
            sb.Append("\\u");
            sb.Append(bytes[i + 1].ToString("X2"));
            sb.Append(bytes[i].ToString("X2"));
        }

        return sb.ToString();
    }

    public static string UnEscape(string s)
    {
        if (s == null)
            return null;
        else if (s.Length == 0)
            return "";
        else if (s.Length % 6 != 0)
            return s;

        byte[] bytes = new byte[s.Length / 3];
        for (int i = 0; i < s.Length; i += 6)
        {
            int idx = i / 6 * 2;
            //string uniEncoded = s.Substring(i + 2, 4);
            bytes[idx] = Convert.ToByte(s.Substring(i + 4, 2), 16);
            bytes[idx + 1] = Convert.ToByte(s.Substring(i + 2, 2), 16);
        }

        return Encoding.Unicode.GetString(bytes);
    }
    public static string UnEscape2(string s)
    {
        if (s == null)
            return null;
        else if (s.Length == 0)
            return "";
        else if (s.Length % 6 != 0)
            return s;

        byte[] bytes = new byte[s.Length / 3];
        for (int i = 0; i < s.Length; i += 6)
        {
            int idx = i / 6 * 2;
            //string uniEncoded = s.Substring(i + 2, 4);
            bytes[idx] = Convert.ToByte(s.Substring(i + 4, 2), 16);
            bytes[idx + 1] = Convert.ToByte(s.Substring(i + 2, 2), 16);
        }

        return Encoding.Unicode.GetString(bytes);
    }
}

