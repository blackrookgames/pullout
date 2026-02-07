using OpenQA.Selenium;
using OpenQA.Selenium.Chrome;
using System;
using System.Collections.Generic;
using System.IO;
using System.Reflection;
using System.Threading;
using System.Threading.Tasks;

class Program
{
    const int LONGWAIT = 1000;
    const int EXTRAWAIT = 1000;

    class Observation
    {
        public Observation(ChromeDriver driver,
            string url,
            string buyURL,
            string sellURL,
            float newInvest)
        {
            _Driver = driver;
            _URL = url;
            _BuyURL = buyURL;
            _SellURL = sellURL;
            _Invest = newInvest;
            // Sell initial investment
            if (Pr_GetInvestment() > 0)
            {
                Console.WriteLine("Selling existing invetment.");
                Pr_Sell();
            }
            // Get initial value
            _Value = Pr_GetValue();
            // Initialize status
            _MoneyIn = false;
        }

        #region fields
    
        ChromeDriver _Driver;
        string _URL;
        string _BuyURL;
        string _SellURL;

        float _Invest;
        float _Value;
        bool _MoneyIn;

        #endregion

        #region properties

        public float Invest => _Invest;

        public float Value => _Value;

        public bool MoneyIn => _MoneyIn;

        #endregion

        #region helper methods

        private float Pr_GetInvestment()
        {
            _Driver.Navigate().GoToUrl(_URL);
            IWebElement element = _Driver.WaitForElement(
                by: By.TagName("div"),
                predicate: e => 
                {
                    try
                    {
                        string value = e.GetAttribute("aria-label");
                        if (value is null) return false;
                        return value.Contains("available value");
                    }
                    catch (StaleElementReferenceException) { return false; }
                },
                wait: LONGWAIT);
            string rawtext = element.GetAttribute("aria-label");
            return rawtext[(rawtext.IndexOf('$') + 1)..].ToPrice();
        }

        private float Pr_GetValue()
        {
            _Driver.Navigate().GoToUrl(_URL);
            IWebElement e_Price = _Driver.WaitForElement(
                by: By.Id("currentAssetPrice_coachTip_headingText"),
                wait: LONGWAIT);
            return e_Price.Text.ToPrice();
        }

        private float Pr_Sell(float amount = -1)
        {
            _Driver.Navigate().GoToUrl(_SellURL);
            // Form 1
            float maxAmount;
            {
                // Check how much there is to sell
                IWebElement e_amount = _Driver.WaitForElement(
                    by: By.TagName("div"),
                    predicate: e => 
                    {
                        try { return e.Text.Contains("You can sell up to "); }
                        catch (StaleElementReferenceException) { return false; }
                    }, 
                    wait: LONGWAIT);
                maxAmount = e_amount.Text[(e_amount.Text.IndexOf('$') + 1)..].ToPrice();
                if (amount < 0 || amount > maxAmount)
                    amount = maxAmount;
                // If amount is zero, don't continue
                if (amount == 0) return amount;
                // Get input field
                IWebElement e_field = _Driver.WaitForElement(
                    by: By.TagName("input"),
                    predicate: e => 
                    {
                        try { return e.GetAttribute("data-testid") == "amountField"; }
                        catch (StaleElementReferenceException) { return false; }
                    });
                e_field.SendKeys(amount.ToString());
                // Get submit
                IWebElement e_submit = _Driver.WaitForElement(
                    by: By.TagName("button"),
                    predicate: e => 
                    {
                        try { return e.Text.Trim() == "Next"; }
                        catch (StaleElementReferenceException) { return false; }
                    });
                e_submit.Click();
            }
            // Form Confirm
            if (amount == maxAmount)
            {
                // Get submit
                IWebElement e_submit = _Driver.WaitForElement(
                    by: By.TagName("button"),
                    predicate: e => 
                    {
                        try { return e.Text.Trim() == "Yes"; }
                        catch (StaleElementReferenceException) { return false; }
                    }, 
                    wait: LONGWAIT);
                e_submit.Click();
            }
            // Form 2
            {
                // 
                for (int i = 0; i < 10; ++i)
                {
                    Thread.Sleep(1000);
                    IWebElement e_balance = _Driver.FindAnElement(
                        by: By.CssSelector("button.sell-to-paypal-balance-card"));
                    if (e_balance is null)
                        continue;
                    e_balance.Click();
                    break;
                }
                // Get submit
                IWebElement e_submit = _Driver.WaitForElement(
                    by: By.TagName("button"),
                    predicate: e => 
                    {
                        try { return e.Text.Trim() == "Sell Now"; }
                        catch (StaleElementReferenceException) { return false; }
                    });
                e_submit.Click();
            }
            // Success!!!
            return amount;
        }

        private void Pr_Buy(float amount)
        {
            _Driver.Navigate().GoToUrl(_BuyURL);
            // Form 1
            {
                // Get input field
                IWebElement e_field = _Driver.WaitForElement(
                    by: By.TagName("input"),
                    predicate: e => 
                    {
                        try { return e.GetAttribute("data-testid") == "amountField"; }
                        catch (StaleElementReferenceException) { return false; }
                    }, 
                    wait: LONGWAIT);
                e_field.SendKeys(amount.ToString());
                // Get submit
                IWebElement e_submit = _Driver.WaitForElement(
                    by: By.TagName("button"),
                    predicate: e => 
                    {
                        try { return e.Text.Trim() == "Next"; }
                        catch (StaleElementReferenceException) { return false; }
                    });
                e_submit.Click();
            }
            // Form 2
            {
                // Get radio button
                IWebElement e_radio = _Driver.WaitForElement(
                    by: By.TagName("input"),
                    predicate: e => 
                    {
                        try { return e.GetAttribute("type") == "radio"; }
                        catch (StaleElementReferenceException) { return false; }
                    }, 
                    wait: LONGWAIT);
                IWebElement e_label = e_radio.FindAnElement(
                    by: By.XPath("../label"));
                e_label.Click();
                // Get submit
                IWebElement e_submit = _Driver.WaitForElement(
                    by: By.TagName("button"),
                    predicate: e => 
                    {
                        try { return e.Text.Trim() == "Next"; }
                        catch (StaleElementReferenceException) { return false; }
                    });
                e_submit.Click();
            }
            // Form 3
            {
                // Get submit
                IWebElement e_submit = _Driver.WaitForElement(
                    by: By.TagName("button"),
                    predicate: e => 
                    {
                        try { return e.Text.Trim() == "Buy Now"; }
                        catch (StaleElementReferenceException) { return false; }
                    }, 
                    wait: LONGWAIT);
                e_submit.Click();
            }
        }

        #endregion

        #region methods

        public void Update()
        {
            // Update value
            float oldValue = _Value;
            _Value = Pr_GetValue();
            // Buy or sell
            if (_Value > oldValue)
            {
                if (!_MoneyIn)
                {
                    Pr_Buy(_Invest);
                    _MoneyIn = true;
                }
            }
            else
            {
                if (_MoneyIn)
                {
                    _Invest = Pr_Sell();
                    _MoneyIn = false;
                }
            }
        }

        #endregion
    }

    static bool TryReadKey(long timeout, out ConsoleKeyInfo result)
    {
        var readKeyTask = Task.Run(() =>
        {
            ConsoleKeyInfo keyInfo = Console.ReadKey(true);
            return keyInfo;
        });
        bool keyHandled = readKeyTask.Wait(TimeSpan.FromSeconds(timeout));
        if (keyHandled)
        {
            result = readKeyTask.Result;
            return true;
        }
        else
        {
            result = default;
            return false;
        }
    }

    static int Main(string[] args)
    {
        string exeDir = Path.GetFullPath(Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location));
        string logPath = Path.Join(exeDir, "chromedriver.log");
        string chromeProfile = Path.Join(exeDir, "SeleniumProfile");
        Directory.CreateDirectory(chromeProfile);

        ChromeOptions options = new ChromeOptions();
        options.AddArgument("--remote-allow-origins=*");

        if (chromeProfile[0] == '/') // Check if linux
        {
            options.AddArgument("--ozone-platform=x11");
            options.AddArgument("--disable-gpu");
            options.AddArgument("--disable-software-rasterizer");
            options.AddArgument("--disable-gpu-compositing");
            options.AddArgument("--disable-vulkan");
            options.AddArgument("--no-sandbox");
            options.AddArgument("--disable-dev-shm-usage");
        }

        options.AddExcludedArgument("enable-automation");
        options.AddAdditionalChromeOption("useAutomationExtension", false);
        options.AddArgument("--disable-blink-features=AutomationControlled");
        options.AddArgument($"--user-data-dir={chromeProfile}");
        options.AddArgument("--disable-disable-rasterizer");

        options.AddArgument("--window-size=800,600");


        ChromeDriverService service = ChromeDriverService.CreateDefaultService();
        service.LogPath = logPath;
        service.EnableVerboseLogging = true;

        Console.WriteLine("Opening browser");
        ChromeDriver driver = new ChromeDriver(service, options);
        try
        {
            // Goto paypal
            driver.Navigate().GoToUrl("https://www.paypal.com");
            Thread.Sleep(1000);
            // Wait for user to login
            Console.WriteLine("Please login to paypal.");
            while (!driver.Url.StartsWith("https://www.paypal.com/myaccount/summary"))
                Thread.Sleep(1000);
            // Run loop
            float initalInvest = 20;
            Observation observe_BTC = new Observation(driver,
                "https://www.paypal.com/myaccount/crypto/BTC",
                "https://www.paypal.com/myaccount/crypto/BTC/buy/amount",
                "https://www.paypal.com/myaccount/crypto/BTC/sell/amount",
                initalInvest);
            Console.WriteLine("Press Esc to quit");
            Console.WriteLine($"${observe_BTC.Value} ${observe_BTC.Invest}");
            while (true)
            {
                // Wait
                if (TryReadKey(60, out var keyInfo))
                {
                    if (keyInfo.Key == ConsoleKey.Escape)
                    {
                        Console.WriteLine("Quitting");
                        break;
                    }
                }
                // Update
                observe_BTC.Update();
                // Print
                Console.WriteLine($"${observe_BTC.Value} ${observe_BTC.Invest} {observe_BTC.MoneyIn}");
            }
        }
#if DEBUG
#else
        catch (Exception ex)
        {
            Console.Error.WriteLine($"ERROR: {ex.Message}");
            return 1;
        }
#endif
        finally
        {
            driver.Quit();
        }

        return 0;
    }
}