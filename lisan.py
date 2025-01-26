from flask import Flask, request, jsonify, abort
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

app = Flask(__name__)

# 设置你的API密钥
API_KEY = "yuzhengyu131426"


def validate_api_key(api_key):
    return api_key == API_KEY


def fetch_hot_news_with_selenium(url):
    # 设置无头模式（可选）
    edge_options = webdriver.EdgeOptions()
    edge_options.add_argument("--headless")

    # 设置WebDriver路径，使用原始字符串避免转义问题
    service = Service(r"F:\Edgedown\edgedriver_win64\msedgedriver.exe")

    # 创建WebDriver对象
    driver = webdriver.Edge(service=service, options=edge_options)

    news_data = []
    try:
        # 访问目标网址
        driver.get(url)

        # 等待页面加载完成，确保所有新闻项都已加载
        wait = WebDriverWait(driver, 10)  # 等待最多10秒
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'li.n-list-item')))

        # 查找所有新闻项
        news_items = driver.find_elements(By.CSS_SELECTOR, 'li.n-list-item')

        for item in news_items:
            # 查找新闻标题
            title_tag = item.find_element(By.CSS_SELECTOR, '.n-text.title')
            if title_tag:
                title = title_tag.text.strip()

                # 查找热度值
                hotness_tag = item.find_element(By.CSS_SELECTOR, '.n-text.hot-text')
                hotness = hotness_tag.text.strip() if hotness_tag else "Hotness not found"

                # 模拟点击新闻项以获取链接
                original_window = driver.current_window_handle
                item.click()

                # 等待新窗口或标签页打开，并切换到新窗口
                wait.until(EC.number_of_windows_to_be(2))
                for window_handle in driver.window_handles:
                    if window_handle != original_window:
                        driver.switch_to.window(window_handle)
                        break

                # 获取当前页面的URL作为新闻链接
                link = driver.current_url

                # 关闭新窗口并切换回原窗口
                driver.close()
                driver.switch_to.window(original_window)

                news_data.append({
                    "title": title,
                    "link": link,
                    "hotness": hotness
                })

    finally:
        # 关闭浏览器
        driver.quit()

    return news_data


@app.route('/')
def index():
    return "Hello, this is the Flask server!"


@app.route('/fetch-news', methods=['POST'])
def fetch_news():
    # 获取请求中的 API 密钥
    provided_api_key = request.headers.get('X-API-KEY')

    if not validate_api_key(provided_api_key):
        abort(403)  # 返回 403 Forbidden 状态码

    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({"error": "URL is required"}), 400

    try:
        news_data = fetch_hot_news_with_selenium(url)
        return jsonify(news_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)