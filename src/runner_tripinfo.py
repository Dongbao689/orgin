import numpy as np
import traci
from sumo_env import SumoEnvWithPlatoon
from stable_baselines3 import PPO
import os
import sumolib
import pandas as pd

# 加载训练好的 PPO 模型
model = PPO.load("../model/PPO_MODEL.zip")

# 初始化 SUMO 环境
env = SumoEnvWithPlatoon(config_file="../maps/s.sumocfg", use_gui=False)
# 用于存储每个 episode 的交通数据
episode_travel_times = []
episode_fuel_consumptions = []
episode_co2_emissions = []
episode_tripinfo_delays = []  # 基于 tripinfo 文件中的 timeLoss 计算的延误
episode_passed_vehicles = []  # 存储每个 episode 通过交叉口的车辆数量


def save_results_to_excel(excel_file, episode, episode_reward, avg_travel_time, avg_delay_tripinfo, avg_fuel_consumption, avg_co2_emission, passed_vehicle_count):
    """
    保存仿真结果到 Excel 文件
    """
    data = {
        'Episode': [episode],
        'Avg Travel Time (s)': [avg_travel_time],
        'Avg Delay (s)': [avg_delay_tripinfo],
        'Avg Fuel Consumption (L/100km)': [avg_fuel_consumption],
        'Avg CO₂ Emission (g/km)': [avg_co2_emission],
        'Passed Vehicles': [passed_vehicle_count]
    }

    # 检查 Excel 文件是否存在
    if os.path.exists(excel_file):
        df = pd.read_excel(excel_file, sheet_name="Results")
        df = pd.concat([df, pd.DataFrame(data)], ignore_index=True)
    else:
        df = pd.DataFrame(data)

    # 使用 openpyxl 以支持 Excel 格式
    with pd.ExcelWriter(excel_file, engine='openpyxl', mode='w') as writer:
        df.to_excel(writer, sheet_name="Results", index=False)


# 运行多个 episode 来验证模型效果
num_episodes = 1
for episode in range(num_episodes):
    obs = env.reset()
    done = False
    episode_reward = 0

    # 记录已通过交叉口的车辆
    passed_vehicles = set()

    # 设置仿真时间限制（500秒）
    max_simulation_time = 500

    while not done:
        # 获取当前仿真时间
        current_time = traci.simulation.getTime()

        # 如果仿真时间超过500秒，则结束当前 episode
        if current_time >= max_simulation_time:
            print(f"Episode {episode + 1} reached maximum simulation time of {max_simulation_time} seconds.")
            break

        # 使用模型进行动作预测
        action, _states = model.predict(obs, deterministic=True)

        # 执行动作并获取新的状态、奖励等信息
        obs, reward, done, info = env.step(action)
        episode_reward += reward

        # 统计已通过交叉口的车辆


    # 结束当前 episode 后，关闭 SUMO 环境，确保输出文件写入完成
    env.close()

    # 使用 sumolib 解析 tripinfo.xml 统计 Travel Time、油耗、CO₂排放及延误
    emissions_file = "../output/tripinfo.xml"
    fuel_sum, co2_sum, delay_sum, travel_time_sum, trip_count = 0, 0, 0, 0, 0
    if os.path.exists(emissions_file):
        for trip in sumolib.output.parse(emissions_file, ['tripinfo']):
            # 解析排放数据




            # 从 tripinfo 读取 Travel Time（行程时间）
            try:
                travel_time = float(getattr(trip, 'duration', 0))
            except Exception:
                travel_time = 0
            travel_time_sum += travel_time

            # 使用 tripinfo 中的 timeLoss 作为延误指标
            try:
                trip_delay = float(getattr(trip, 'timeLoss', 0))
            except Exception:
                trip_delay = 0
            delay_sum += trip_delay

            trip_count += 1



    # 存储当前 episode 的数据
    episode_travel_times.append(avg_travel_time)
    episode_fuel_consumptions.append(avg_fuel_consumption)
    episode_co2_emissions.append(avg_co2_emission)
    episode_tripinfo_delays.append(avg_delay_tripinfo)
    episode_passed_vehicles.append(len(passed_vehicles))

    print(f"Episode {episode + 1}:")
    print(f"  Reward: {episode_reward}")
    print(f"  Avg Travel Time: {avg_travel_time:.2f} s")
    print(f"  Avg Delay: {avg_delay_tripinfo:.2f} s")
    print(f"  Avg Fuel Consumption: {avg_fuel_consumption:.2f} L/100km")
    print(f"  Avg CO₂ Emission: {avg_co2_emission:.2f} g/km")
    print(f"  Passed Vehicles: {len(passed_vehicles)}")

    # 保存结果到 Excel 文件
    excel_file = "../output/results.xlsx"
    save_results_to_excel(excel_file, episode + 1, episode_reward, avg_travel_time, avg_delay_tripinfo, avg_fuel_consumption, avg_co2_emission, len(passed_vehicles))

# 输出所有 episode 的平均数据
print("\nSummary of all episodes:")
print(f"  Avg Travel Time: {np.mean(episode_travel_times):.2f} s")
print(f"  Avg Delay: {np.mean(episode_tripinfo_delays):.2f} s")
print(f"  Avg Fuel Consumption: {np.mean(episode_fuel_consumptions):.2f} L/100km")
print(f"  Avg CO₂ Emission: {np.mean(episode_co2_emissions):.2f} g/km")
print(f"  Total Passed Vehicles: {sum(episode_passed_vehicles)}")
