import torch.nn as nn
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time

def auto_click_h5():
    # 设置 Chrome 选项
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-gpu')  # 禁用GPU加速
    chrome_options.add_argument('--no-sandbox')   # 禁用沙箱模式
    chrome_options.add_argument('--disable-dev-shm-usage')  # 禁用/dev/shm使用
    chrome_options.add_argument('--window-size=375,812')    # 设置移动设备窗口大小
    
    # 添加移动设备模拟
    mobile_emulation = {
        "deviceMetrics": { "width": 375, "height": 812, "pixelRatio": 3.0 },
        "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
    }
    chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
    
    try:
        # 使用 webdriver_manager 自动安装和管理 ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("浏览器已启动")
        
        while True:
            try:
                # 打开网页
                url = "https://avatar.migudm.cn/h5/newyear2025/index.html?onelv_chl=hound&onelv_spot=bj1&sec_chl=spot&sec_spot="
                driver.get(url)
                print("页面已打开")
                
                # 增加页面加载等待时间
                time.sleep(5)  # 等待页面完全加载
                
                # 更新选择器列表，增加更多可能的按钮选择器
                selectors = [
                    (By.XPATH, "//div[contains(@class, 'button')]"),
                    (By.XPATH, "//div[contains(@class, 'btn')]"),
                    (By.XPATH, "//button"),
                    (By.XPATH, "//*[contains(text(), '开始')]"),
                    (By.XPATH, "//*[contains(text(), '点击')]"),
                    (By.XPATH, "//*[contains(text(), '启动')]"),
                    (By.CLASS_NAME, 'start-btn'),
                    (By.CLASS_NAME, 'play-btn')
                ]
                
                button_clicked = False
                for selector in selectors:
                    try:
                        print(f"尝试查找按钮: {selector}")
                        # 使用 presence_of_element_located 而不是 element_to_be_clickable
                        elements = driver.find_elements(*selector)
                        for element in elements:
                            try:
                                if element.is_displayed():
                                    # 使用 JavaScript 点击按钮
                                    driver.execute_script("arguments[0].click();", element)
                                    print(f"成功点击按钮: {selector}")
                                    button_clicked = True
                                    break
                            except Exception as e:
                                print(f"点击元素失败: {e}")
                                continue
                        if button_clicked:
                            break
                    except Exception as e:
                        print(f"查找元素失败: {e}")
                        continue
                
                if not button_clicked:
                    print("未找到可点击的按钮")
                    # 保存页面源代码以供调试
                    with open('page_source.html', 'w', encoding='utf-8') as f:
                        f.write(driver.page_source)
                    print("页面源代码已保存到 page_source.html")
                
                print("等待10秒后重试...")
                time.sleep(10)
                
            except Exception as e:
                print(f"点击过程中发生错误: {e}")
                time.sleep(5)
                continue
                
    except Exception as e:
        print(f"浏览器启动错误: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    auto_click_h5()

