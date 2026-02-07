using OpenQA.Selenium;
using OpenQA.Selenium.Chrome;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.IO;
using System.Threading;

static class Selenium_ext
{
    private static IWebElement M_FindAnElement(
        Func<By, ReadOnlyCollection<IWebElement>> findElements,
        By by, Predicate<IWebElement> predicate)
    {
        by ??= By.XPath(".//*");
        var elements = findElements(by);
        foreach (var element in elements)
        {
            if (predicate is null)
                return element;
            if (predicate(element))
                return element;
        }
        return null;
    }

    private static IWebElement M_WaitForElement<TSrc>(
        TSrc source,
        Func<TSrc, By, Predicate<IWebElement>, IWebElement> findAnElement,
        By by, Predicate<IWebElement> predicate,
        int wait)
    {
        IWebElement element = null;
        while (element is null)
        {
            Thread.Sleep(wait);
            element = findAnElement(source, by, predicate);
        }
        return element;
    }

    #region IWebDriver

    /// <summary>
    /// Searches for a web element
    /// </summary>
    /// <param name="driver">Driver</param>
    /// <param name="by">What to look for</param>
    /// <param name="predicate">Predicate</param>
    /// <returns>Found element (or null if element could not be found)</returns>
    /// <exception cref="ArgumentNullException"><paramref name="driver"/> is null</exception>
    public static IWebElement FindAnElement(this IWebDriver driver,
        By by = null, Predicate<IWebElement> predicate = null)
    {
        try { return M_FindAnElement(driver.FindElements, by, predicate); }
        catch when (driver is null) { throw new ArgumentNullException(nameof(driver)); }
    }

    /// <summary>
    /// Waits until a certain web element is found
    /// </summary>
    /// <param name="driver">Driver</param>
    /// <param name="by">What to look for</param>
    /// <param name="predicate">Predicate</param>
    /// <param name="wait">Length of wait intervals (in milliseconds)</param>
    /// <returns>Found element</returns>
    /// <exception cref="ArgumentNullException"><paramref name="driver"/> is null</exception>
    /// <exception cref="ArgumentOutOfRangeException"><paramref name="wait"/> is less than zero</exception>
    public static IWebElement WaitForElement(this IWebDriver driver,
        By by = null, Predicate<IWebElement> predicate = null,
        int wait = 1000)
    {
        try
        {
            if (wait < 0)
                throw new ArgumentOutOfRangeException(nameof(wait), "Wait must be greater than or equal to zero.");
            return M_WaitForElement(driver, FindAnElement, by, predicate, wait);
        }
        catch when (driver is null) { throw new ArgumentNullException(nameof(driver)); }
    }

    #endregion

    #region IWebElement

    /// <summary>
    /// Searches for a web element
    /// </summary>
    /// <param name="root">"Root" element</param>
    /// <param name="by">What to look for</param>
    /// <param name="predicate">Predicate</param>
    /// <returns>Found element (or null if element could not be found)</returns>
    /// <exception cref="ArgumentNullException"><paramref name="root"/> is null</exception>
    public static IWebElement FindAnElement(this IWebElement root,
        By by = null, Predicate<IWebElement> predicate = null)
    {
        try { return M_FindAnElement(root.FindElements, by, predicate); }
        catch when (root is null) { throw new ArgumentNullException(nameof(root)); }
    }

    /// <summary>
    /// Waits until a certain web element is found
    /// </summary>
    /// <param name="root">"Root" element</param>
    /// <param name="by">What to look for</param>
    /// <param name="predicate">Predicate</param>
    /// <param name="wait">Length of wait intervals (in milliseconds)</param>
    /// <returns>Found element</returns>
    /// <exception cref="ArgumentNullException"><paramref name="root"/> is null</exception>
    /// <exception cref="ArgumentOutOfRangeException"><paramref name="wait"/> is less than zero</exception>
    public static IWebElement WaitForElement(this IWebElement root,
        By by = null, Predicate<IWebElement> predicate = null,
        int wait = 1000)
    {
        try
        {
            if (wait < 0)
                throw new ArgumentOutOfRangeException(nameof(wait), "Wait must be greater than or equal to zero.");
            return M_WaitForElement(root, FindAnElement, by, predicate, wait);
        }
        catch when (root is null) { throw new ArgumentNullException(nameof(root)); }
    }

    #endregion


}