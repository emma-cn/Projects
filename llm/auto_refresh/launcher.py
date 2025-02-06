import subprocess
import time
from datetime import datetime
import logging
import os
from config import CONFIG, get_auto_config

def setup_launcher_logger():
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    log_filename = f"logs/launcher_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    logger = logging.getLogger('launcher')
    logger.setLevel(logging.INFO)
    
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    console_handler = logging.StreamHandler()
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def cleanup_processes(logger, processes):
    """清理所有进程和浏览器"""
    for i, process in enumerate(processes):
        try:
            logger.info(f"正在终止实例 {i+1} (PID: {process.pid})")
            process.terminate()
            process.wait(timeout=5)  # 等待进程终止
        except subprocess.TimeoutExpired:
            logger.warning(f"实例 {i+1} (PID: {process.pid}) 终止超时，尝试强制终止")
            try:
                process.kill()  # 强制终止
            except:
                logger.error(f"强制终止实例 {i+1} (PID: {process.pid}) 失败")
        except Exception as e:
            logger.error(f"终止实例 {i+1} (PID: {process.pid}) 时出错: {e}")
    
    # 清理可能残留的 Chrome 进程
    try:
        if os.name == 'nt':  # Windows
            os.system('taskkill /f /im chrome.exe /t')
            os.system('taskkill /f /im chromedriver.exe /t')
        else:  # Linux/Mac
            os.system('pkill -f chrome')
            os.system('pkill -f chromedriver')
    except Exception as e:
        logger.error(f"清理残留Chrome进程时出错: {e}")
    
    return []  # 返回空列表表示所有进程已清理

def update_instances(logger, current_processes, current_config, onelv_spot_base):
    """更新实例数量和配置"""
    try:
        target_instances = current_config['instances']
        current_instance_count = len(current_processes)
        instance_start_interval = current_config.get('intervals', {}).get('instance_start', 5)
        
        # 如果需要调整实例数量，先清理所有现有实例
        if current_instance_count != target_instances:
            logger.info(f"需要调整实例数量: {current_instance_count} -> {target_instances}")
            logger.info("清理所有现有实例...")
            current_processes = cleanup_processes(logger, current_processes)
            current_instance_count = 0
        
        # 启动新实例
        while current_instance_count < target_instances:
            instance_onelv_spot = f"{onelv_spot_base}{current_instance_count+1}"
            logger.info(f"正在启动新实例 {current_instance_count+1} (onelv_spot: {instance_onelv_spot})")
            
            process = subprocess.Popen(['python', 'auto_refresh.py', '--onelv_spot', instance_onelv_spot])
            current_processes.append(process)
            logger.info(f"新实例启动成功，进程ID: {process.pid}")
            time.sleep(instance_start_interval)
            current_instance_count += 1
        
        return current_processes
    except Exception as e:
        logger.error(f"更新实例时出错: {e}")
        return current_processes

def launch_instances():
    logger = setup_launcher_logger()
    processes = []
    last_config_check = 0
    
    try:
        while True:
            try:
                current_time = time.time()
                
                # 每分钟检查一次配置
                if current_time - last_config_check >= 60:
                    # 获取最新配置
                    current_config = get_auto_config()
                    onelv_spot_base = CONFIG['onelv_spot']
                    
                    logger.info("\n=== 配置检查 ===")
                    logger.info(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    logger.info(f"目标访问量: {current_config['target_visits']}")
                    logger.info(f"目标操作量: {current_config['target_actions']}")
                    logger.info(f"日期因子: {current_config['date_factor']:.2f}")
                    logger.info(f"时间因子: {current_config['hour_factor']:.2f}")
                    logger.info(f"需要实例数: {current_config['instances']}")
                    logger.info(f"当前实例数: {len(processes)}")
                    
                    # 更新实例数量
                    processes = update_instances(logger, processes, current_config, onelv_spot_base)
                    last_config_check = current_time
                
                # 检查进程状态
                for i, process in enumerate(processes):
                    if process.poll() is not None:
                        instance_onelv_spot = f"{CONFIG['onelv_spot']}{i+1}"
                        logger.warning(f"实例 {i+1} (PID: {process.pid}, onelv_spot: {instance_onelv_spot}) 已终止，正在重新启动")
                        # 清理可能的残留进程
                        cleanup_processes(logger, [process])
                        # 启动新实例
                        process = subprocess.Popen(['python', 'auto_refresh.py', '--onelv_spot', instance_onelv_spot])
                        processes[i] = process
                        logger.info(f"实例 {i+1} 已重新启动，新进程ID: {process.pid}")
                
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"主循环中出错: {e}")
                time.sleep(5)
                continue
            
    except KeyboardInterrupt:
        logger.info("收到终止信号，正在关闭所有实例...")
        cleanup_processes(logger, processes)
        logger.info("所有实例已关闭")
    finally:
        logger.info("启动器程序结束")

if __name__ == "__main__":
    launch_instances() 