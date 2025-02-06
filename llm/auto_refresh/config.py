from datetime import datetime, time
import json
import os

CONFIG_FILE = 'runtime_config.json'

def get_auto_config():
    """根据当前日期时间自动生成配置"""
    current_date = datetime.now().strftime('%m%d')
    current_hour = datetime.now().hour
    
    # 基础访问量配置（按日期）
    date_config = {
        '0131': {'visits': 28275, 'actions': 6972},
        '0201': {'visits': 66249, 'actions': 9925},
        '0202': {'visits': 20367, 'actions': 22234},
        '0203': {'visits': 71413, 'actions': 19477},
        '0204': {'visits': 100000, 'actions': 25000},
        '0205': {'visits': 120000, 'actions': 40000},
        '0206': {'visits': 100000, 'actions': 25000},
        '0207': {'visits': 80000, 'actions': 25000},
        '0208': {'visits': 70000, 'actions': 20000},
        '0209': {'visits': 70000, 'actions': 20000},
        '0210': {'visits': 80000, 'actions': 25000},
        '0211': {'visits': 100000, 'actions': 30000},
        '0212': {'visits': 140000, 'actions': 50000},  # 峰值
        '0213': {'visits': 100000, 'actions': 40000},
        '0214': {'visits': 80000, 'actions': 30000},
        '0215': {'visits': 60000, 'actions': 20000},
        '0216': {'visits': 50000, 'actions': 15000},
    }
    
    # 时间段系数（相对于基础值的倍率）
    hour_factors = {
        (0, 6): 0.7,   # 深夜到凌晨
        (6, 9): 0.8,   # 早晨
        (9, 12): 0.9,  # 上午
        (12, 14): 1.0, # 中午高峰
        (14, 17): 0.9, # 下午
        (17, 20): 0.8, # 傍晚
        (20, 24): 0.7, # 晚上
    }
    
    # 获取当天的基础配置
    base_config = date_config.get(current_date, {'visits': 70000, 'actions': 20000})  # 默认值
    
    # 获取当前时间段的系数
    hour_factor = 0.7  # 默认系数
    for (start, end), factor in hour_factors.items():
        if start <= current_hour < end:
            hour_factor = factor
            break
    
    # 计算实际目标值
    target_visits = int(base_config['visits'] * hour_factor)
    target_actions = int(base_config['actions'] * hour_factor)
    
    # 计算所需实例数（每个实例处理约5万次访问）
    instances = max(1, target_visits // 50000)
    
    # 计算时间间隔
    page_load_interval = max(1, 3600 / (target_visits / instances))
    retry_interval = max(1, 3600 / (target_actions / instances))
    
    return {
        'target_visits': target_visits,
        'target_actions': target_actions,
        'instances': instances,
        'intervals': {
            'instance_start': 5,    # 添加实例启动间隔
            'process_check': 60,    # 添加进程检查间隔
            'page_load': page_load_interval,
            'retry': retry_interval
        },
        'date_factor': base_config['visits'] / 140000,
        'hour_factor': hour_factor,
        'current_date': current_date,
        'current_hour': current_hour
    }

def load_runtime_config():
    """加载运行时配置，如果没有手动配置则使用自动配置"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                manual_config = json.load(f)
                if manual_config:  # 如果有手动配置，使用手动配置
                    return manual_config
        except:
            pass
    
    # 如果没有手动配置或加载失败，使用自动配置
    return get_auto_config()

def save_runtime_config(config):
    """保存运行时配置"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

def get_date_factor():
    """根据日期获取基础倍率因子"""
    runtime_config = load_runtime_config()
    if 'date_factor' in runtime_config:
        return float(runtime_config['date_factor'])
        
    date_factors = {
        # 1月31日到2月16日的数据
        '0131': 0.2,  # 28275
        '0201': 0.45, # 66249
        '0202': 0.15, # 20367
        '0203': 0.5,  # 71413
        '0204': 0.7,  # 100000
        '0205': 0.85, # 120000
        '0206': 0.7,  # 100000
        '0207': 0.57, # 80000
        '0208': 0.5,  # 70000
        '0209': 0.5,  # 70000
        '0210': 0.57, # 80000
        '0211': 0.7,  # 100000
        '0212': 1.0,  # 140000 (峰值)
        '0213': 0.7,  # 100000
        '0214': 0.57, # 80000
        '0215': 0.43, # 60000
        '0216': 0.36, # 50000
    }
    
    current_date = datetime.now().strftime('%m%d')
    return date_factors.get(current_date, 0.5)

def get_hour_factor():
    """根据小时获取时间倍率因子"""
    runtime_config = load_runtime_config()
    if 'hour_factor' in runtime_config:
        return float(runtime_config['hour_factor'])
        
    current_hour = datetime.now().hour
    
    # 每个时间段的基础倍率
    if 0 <= current_hour < 6:
        return 0.7  # 深夜到凌晨
    elif 6 <= current_hour < 9:
        return 0.8  # 早晨
    elif 9 <= current_hour < 12:
        return 0.9  # 上午
    elif 12 <= current_hour < 14:
        return 1.0  # 中午高峰
    elif 14 <= current_hour < 17:
        return 0.9  # 下午
    elif 17 <= current_hour < 20:
        return 0.8  # 傍晚
    else:
        return 0.7  # 晚上

def get_target_numbers():
    """获取目标数值"""
    runtime_config = load_runtime_config()
    
    # 如果运行时配置中有直接指定的目标值，使用它们
    if 'target_visits' in runtime_config and 'target_actions' in runtime_config:
        return {
            'target_visits': int(runtime_config['target_visits']),
            'target_actions': int(runtime_config['target_actions']),
            'date_factor': float(runtime_config.get('date_factor', 1.0)),
            'hour_factor': float(runtime_config.get('hour_factor', 1.0))
        }
    
    # 否则使用计算值
    BASE_VISITS = 140000
    BASE_ACTIONS = 50000
    
    date_factor = get_date_factor()
    hour_factor = get_hour_factor()
    
    return {
        'target_visits': int(BASE_VISITS * date_factor * hour_factor),
        'target_actions': int(BASE_ACTIONS * date_factor * hour_factor),
        'date_factor': date_factor,
        'hour_factor': hour_factor
    }

# 基础配置
CONFIG = {
    # 实例数量动态配置
    'instances': lambda: load_runtime_config().get('instances', 1),
    
    # onelv_spot 基础参数
    'onelv_spot': 'bj',
    
    # 浏览器配置
    'browser': {
        'window_width': 375,
        'window_height': 812,
        'pixel_ratio': 3.0,
        'user_agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
    },
    
    # 时间间隔配置（秒）
    'intervals': {
        'instance_start': 5,    # 启动实例间隔
        'process_check': 60,    # 进程检查间隔
        'page_load': lambda: load_runtime_config()['intervals']['page_load'],
        'retry': lambda: load_runtime_config()['intervals']['retry'],
    },
    
    # 目标数据获取函数
    'get_target_numbers': get_target_numbers
} 