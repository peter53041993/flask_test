from selenium.webdriver.chrome.options import Options

# ChromeDriver 取用路徑 (若環境參數無法獲取時取用)
chromeDriver_Path = r'C:\Users\Wen\PycharmProjects\kerr_flask\chromedriver_83.exe'
# report.html 絕對路徑
reportHtml_Path = r"C:\Users\Wen\PycharmProjects\kerr_flask\templates\report.html"

# ChromeDriver 設定參數
chrome_options = Options()
chrome_options.add_argument("--headless")  # 背景執行
