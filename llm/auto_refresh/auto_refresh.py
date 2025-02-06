from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime, timedelta
import logging
import os
import argparse
from config import CONFIG

def setup_logger():
    # 创建logs目录（如果不存在）
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # 生成日志文件名（包含时间戳）
    log_filename = f"logs/auto_click_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # 配置日志记录器
    logger = logging.getLogger('auto_click')
    logger.setLevel(logging.INFO)
    
    # 创建文件处理器
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 创建格式化器
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # 添加处理器到记录器
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def get_current_config():
    """获取当前配置"""
    current_config = {}
    for key, value in CONFIG.items():
        if key == 'get_target_numbers':  # 跳过这个特殊的函数配置项
            current_config[key] = value
            continue
            
        if callable(value):
            current_config[key] = value()
        elif isinstance(value, dict):
            current_config[key] = {}
            for sub_key, sub_value in value.items():
                if callable(sub_value):
                    current_config[key][sub_key] = sub_value()
                else:
                    current_config[key][sub_key] = sub_value
        else:
            current_config[key] = value
    return current_config

def auto_click_h5(onelv_spot):
    # 设置日志记录器
    logger = setup_logger()
    
    # 记录开始时间和参数
    start_time = datetime.now()
    logger.info(f"程序开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"使用 onelv_spot 参数: {onelv_spot}")
    
    # 获取当前配置
    current_config = get_current_config()
    
    # 添加执行次数计数器
    execution_count = 0
    driver = None
    
    while True:  # 外层循环，用于浏览器重启
        try:
            if driver is None:
                # 设置 Chrome 选项
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_argument('--disable-gpu')
                chrome_options.add_argument('--no-sandbox')
                chrome_options.add_argument('--disable-dev-shm-usage')
                chrome_options.add_argument(f'--window-size={current_config["browser"]["window_width"]},{current_config["browser"]["window_height"]}')
                
                # 禁用后台运行
                chrome_options.add_argument('--disable-background-mode')
                # 禁用无头模式
                chrome_options.add_argument('--disable-headless')
                # 设置窗口位置（居中显示）
                screen_width = 1920  # 假设屏幕宽度
                screen_height = 1080  # 假设屏幕高度
                window_x = (screen_width - current_config["browser"]["window_width"]) // 2
                window_y = (screen_height - current_config["browser"]["window_height"]) // 2
                chrome_options.add_argument(f'--window-position={window_x},{window_y}')
                
                # 添加移动设备模拟
                mobile_emulation = {
                    "deviceMetrics": {
                        "width": current_config["browser"]["window_width"],
                        "height": current_config["browser"]["window_height"],
                        "pixelRatio": current_config["browser"]["pixel_ratio"]
                    },
                    "userAgent": current_config["browser"]["user_agent"]
                }
                chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
                
                # 禁用自动化控制提示
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                
                # 使用 webdriver_manager 自动安装和管理 ChromeDriver
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                
                # 设置窗口始终在最前
                if os.name == 'nt':  # Windows
                    try:
                        import win32gui
                        import win32con
                        hwnd = win32gui.GetForegroundWindow()
                        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, 
                                           win32con.SWP_NOMOVE | win32con.SWP_NOSIZE)
                    except:
                        logger.warning("无法设置窗口置顶（仅支持Windows）")
                
                logger.info("浏览器已启动")
                
                # 强制激活窗口
                driver.switch_to.window(driver.current_window_handle)
            
            # 内层循环，用于页面刷新
            while True:
                try:
                    execution_count += 1
                    # 每次循环获取最新配置
                    current_config = get_current_config()
                    target_numbers = CONFIG['get_target_numbers']()
                    
                    # 记录本次执行开始时间
                    iteration_start = datetime.now()
                    logger.info(f"\n=== 第 {execution_count} 次执行 === {iteration_start.strftime('%H:%M:%S')}")
                    
                    # 检查浏览器是否还在运行
                    try:
                        # 尝试获取当前窗口句柄，如果失败说明浏览器已关闭
                        driver.current_window_handle
                    except:
                        logger.warning("检测到浏览器已关闭，准备重启...")
                        driver = None
                        time.sleep(5)  # 等待一段时间后重启
                        break  # 跳出内层循环，重新启动浏览器
                    
                    # 使用传入的 onelv_spot 参数构建 URL
                    url = f"https://avatar.migudm.cn/h5/newyear2025/index.html?onelv_chl=hound&onelv_spot={onelv_spot}&sec_chl=spot&sec_spot="
                    driver.get(url)
                    logger.info(f"页面已打开: {url}")
                    
                    # 初始化按钮点击状态
                    button_clicked = False
                    
                    # 使用配置的时间间隔
                    time.sleep(current_config['intervals']['page_load'])
                    
                    # 更新选择器列表，专门针对抽签按钮
                    selectors = [
                        # 精确匹配抽签按钮
                        (By.CSS_SELECTOR, "div[style*='btn_chouqian']"),
                        (By.CSS_SELECTOR, "div[style*='btn_lianchou']"),
                        # 匹配按钮的内部div
                        (By.CSS_SELECTOR, "div.w-280px.h-104px.mb-16px"),
                        (By.CSS_SELECTOR, "div.w-280px.h-104px.mb-16px.ml-16px"),
                    ]
                    
                    # 等待页面加载完成
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    
                    # 修改 JavaScript 检测脚本
                    js_script = """
                    return Array.from(document.querySelectorAll('*')).filter(el => {
                        const style = window.getComputedStyle(el);
                        const backgroundImage = el.style.backgroundImage || '';
                        return (
                            backgroundImage.includes('btn_chouqian') ||
                            backgroundImage.includes('btn_lianchou') ||
                            (el.className && (
                                (el.className.includes('w-280px') && el.className.includes('h-104px')) ||
                                (el.className.includes('w-308px') && el.className.includes('h-122px'))
                            ))
                        );
                    });
                    """
                    
                    try:
                        clickable_elements = driver.execute_script(js_script)
                        if clickable_elements:
                            logger.info(f"找到 {len(clickable_elements)} 个可能可点击的元素")
                            for element in clickable_elements:
                                logger.info(f"尝试点击元素: {element.get_attribute('outerHTML')}")
                                try:
                                    if element.is_displayed():
                                        # 获取元素的背景图片URL
                                        bg_image = element.value_of_css_property('background-image')
                                        logger.info(f"按钮背景图片: {bg_image}")
                                        
                                        # 尝试滚动到元素位置
                                        driver.execute_script("arguments[0].scrollIntoView(true);", element)
                                        time.sleep(1)
                                        
                                        # 获取元素位置和大小
                                        location = element.location
                                        size = element.size
                                        logger.info(f"元素位置: {location}, 大小: {size}")
                                        
                                        # 点击元素中心位置
                                        action = webdriver.ActionChains(driver)
                                        action.move_to_element(element).click().perform()
                                        logger.info("成功点击按钮")
                                        button_clicked = True  # 设置点击状态
                                        time.sleep(2)  # 等待点击效果
                                        
                                        # 继续查找下一个按钮，不要break
                                except Exception as e:
                                    logger.error(f"点击元素失败: {e}")
                                    # 尝试使用JavaScript点击
                                    try:
                                        driver.execute_script("arguments[0].click();", element)
                                        logger.info("通过JavaScript成功点击按钮")
                                        time.sleep(2)
                                    except Exception as js_e:
                                        logger.error(f"JavaScript点击也失败: {js_e}")
                                    continue
                    except Exception as e:
                        logger.error(f"执行 JavaScript 检测失败: {e}")
                    
                    # 原有的选择器循环逻辑
                    if not button_clicked:
                        for selector in selectors:
                            try:
                                logger.info(f"尝试查找按钮: {selector}")
                                # 使用 presence_of_element_located 而不是 element_to_be_clickable
                                elements = driver.find_elements(*selector)
                                for element in elements:
                                    try:
                                        if element.is_displayed():
                                            # 使用 JavaScript 点击按钮
                                            driver.execute_script("arguments[0].click();", element)
                                            logger.info(f"成功点击按钮: {selector}")
                                            button_clicked = True
                                            break
                                    except Exception as e:
                                        logger.error(f"点击元素失败: {e}")
                                        continue
                                if button_clicked:
                                    break
                            except Exception as e:
                                logger.error(f"查找元素失败: {e}")
                                continue
                    
                    if not button_clicked:
                        logger.info(f"第 {execution_count} 次执行未找到可点击的按钮")
                    else:
                        logger.info(f"第 {execution_count} 次执行成功点击按钮")
                    
                    # 计算本次执行时间
                    iteration_end = datetime.now()
                    iteration_duration = iteration_end - iteration_start
                    # 计算总运行时间
                    total_duration = iteration_end - start_time
                    
                    logger.info(f"=== 第 {execution_count} 次执行完成 ===")
                    logger.info(f"本次执行用时: {iteration_duration.seconds}秒")
                    logger.info(f"总运行时间: {str(total_duration).split('.')[0]}\n")
                    
                    logger.info("等待3秒后重试...")
                    
                    # 清理浏览器缓存
                    try:
                        driver.execute_script("window.localStorage.clear();")
                        driver.execute_script("window.sessionStorage.clear();")
                        driver.delete_all_cookies()
                        logger.info("已清理浏览器缓存")
                    except Exception as e:
                        logger.error(f"清理缓存失败: {e}")
                    
                    # 使用配置的时间间隔
                    time.sleep(current_config['intervals']['retry'])
                    
                except Exception as e:
                    logger.error(f"第 {execution_count} 次执行过程中发生错误: {e}")
                    # 检查是否是浏览器关闭导致的错误
                    if "invalid session id" in str(e).lower() or "no such window" in str(e).lower():
                        logger.warning("检测到浏览器已关闭，准备重启...")
                        driver = None
                        time.sleep(5)
                        break  # 跳出内层循环，重新启动浏览器
                    time.sleep(5)
                    continue
                    
        except Exception as e:
            logger.error(f"浏览器启动错误: {e}")
            time.sleep(10)  # 启动失败后等待较长时间再重试
            continue
        finally:
            if driver is not None:
                try:
                    driver.quit()
                except:
                    pass
                driver = None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='自动刷新页面')
    parser.add_argument('--onelv_spot', type=str, required=True,
                      help='onelv_spot 参数值 (例如: bj1)')
    
    args = parser.parse_args()
    auto_click_h5(args.onelv_spot)

