import subprocess
import time
from datetime import datetime
import logging
import os
import argparse

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

def launch_instances(num_instances, onelv_spot_base):
    logger = setup_launcher_logger()
    logger.info(f"启动器开始运行，计划启动 {num_instances} 个实例")
    logger.info(f"使用 onelv_spot 基础参数: {onelv_spot_base}")
    
    processes = []
    
    try:
        for i in range(num_instances):
            # 为每个实例生成唯一的 onelv_spot 参数
            instance_onelv_spot = f"{onelv_spot_base}{i+1}"
            logger.info(f"正在启动第 {i+1} 个实例 (onelv_spot: {instance_onelv_spot})")
            
            # 将唯一的 onelv_spot 参数传递给 auto_refresh.py
            process = subprocess.Popen(['python', 'auto_refresh.py', '--onelv_spot', instance_onelv_spot])
            processes.append(process)
            logger.info(f"实例 {i+1} 启动成功，进程ID: {process.pid}")
            time.sleep(5)
        
        logger.info(f"所有 {num_instances} 个实例已启动")
        
        # 监控所有进程
        while True:
            for i, process in enumerate(processes):
                if process.poll() is not None:
                    # 重启时使用相同的实例ID
                    instance_onelv_spot = f"{onelv_spot_base}{i+1}"
                    logger.warning(f"实例 {i+1} (PID: {process.pid}, onelv_spot: {instance_onelv_spot}) 已终止，正在重新启动")
                    process = subprocess.Popen(['python', 'auto_refresh.py', '--onelv_spot', instance_onelv_spot])
                    processes[i] = process
                    logger.info(f"实例 {i+1} 已重新启动，新进程ID: {process.pid}")
            
            time.sleep(60)
            
    except KeyboardInterrupt:
        logger.info("收到终止信号，正在关闭所有实例...")
        for i, process in enumerate(processes):
            try:
                instance_onelv_spot = f"{onelv_spot_base}{i+1}"
                logger.info(f"正在终止实例 {i+1} (PID: {process.pid}, onelv_spot: {instance_onelv_spot})")
                process.terminate()
            except:
                logger.error(f"终止实例 {i+1} (PID: {process.pid}) 时出错")
        
        logger.info("所有实例已关闭")
    except Exception as e:
        logger.error(f"启动器运行出错: {e}")
    finally:
        logger.info("启动器程序结束")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='启动多个自动刷新实例')
    parser.add_argument('--instances', type=int, default=3,
                      help='要启动的实例数量 (默认: 3)')
    parser.add_argument('--onelv_spot', type=str, required=True,
                      help='onelv_spot 基础参数值 (例如: bj)')
    
    args = parser.parse_args()
    
    launch_instances(args.instances, args.onelv_spot) 