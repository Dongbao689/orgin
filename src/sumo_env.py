import gym
import numpy as np
import traci
from gym import spaces
from simulationmanager import SimulationManager
from scenario_manager import SCENARIO_NUMBER_CONFIGS


class SumoEnvWithPlatoon(gym.Env):
    def __init__(self, config_file, max_steps=3600, use_gui=False, scenario_num=1,
                 tripinfo_file=None):
        super(SumoEnvWithPlatoon, self).__init__()
        self.config_file = config_file  # SUMO 配置文件路径
        self.max_steps = max_steps  # 每个 episode 的最大步数
        self.current_step = 0  # 当前步数计数
        self.use_gui = use_gui  # 是否使用 GUI 模式
        self.switch_time = switch_time  # 初始化信号灯切换时间
        self.last_change_time = 0  # 初始化信号灯切换时间
        self.scenario_num = scenario_num  # 场景编号
        self.tripinfo_file = tripinfo_file  # TripInfo 输出文件路径

        # 选择 SUMO 模式（GUI 或无 GUI）
        self.sumo_cmd = ["sumo-gui" if use_gui else "sumo", "-c", self.config_file]

        # 如果指定了 TripInfo 文件，则添加到 sumo_cmd 中
        if self.tripinfo_file:
            self.sumo_cmd.extend(["--tripinfo-output", self.tripinfo_file])

        # 定义动作空间（8 种信号灯相位）
        self.action_space = spaces.Discrete(8)
        # 定义观测空间，包含 20 维特征
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(20,), dtype=np.float32)

        # 存储受控车道 ID
        self.lane_ids = []
        self.manager = None  # SimulationManager 实例
        self.current_phase = 0  # 当前信号灯相位

    def reset(self):
        """重置环境"""
        try:
            traci.close()
        except traci.exceptions.FatalTraCIError:
            pass

        traci.start(self.sumo_cmd)
        self.current_step = 0
        self.last_change_time = 0  # 重置上次切换时间
        self.current_phase = 0  # 重置当前信号灯相位

        # 获取受控车道列表
        self.lane_ids = traci.trafficlight.getControlledLanes("junction")

        # 初始化 SimulationManager
        scenario_config = SCENARIO_NUMBER_CONFIGS.get(self.scenario_num)
        if scenario_config:
            self.manager = SimulationManager(
                pCreation=scenario_config.enablePlatoons,
                iCoordination=scenario_config.enableCoordination,
                iZipping=scenario_config.enableZipping,
                maxVehiclesPerPlatoon=scenario_config.maxVehiclesPerPlatoon
            )

        return self._get_observation()

    def step(self, action):
        """执行一个动作并返回新的状态、奖励和终止标志"""
        try:
            current_time = traci.simulation.getTime()

            # 设置信号灯相位
            traci.trafficlight.setPhase("junction", int(action))
            self.current_phase = int(action)  # 更新当前信号灯相位
            self.last_change_time = current_time  # 更新上次切换时间

            # 运行一步仿真
            traci.simulationStep()
            self.current_step += 1

            # 处理车辆编队逻辑
            if self.manager:
                self.manager.handleSimulationStep()

            # 获取新的观测值
            obs = self._get_observation()
            # 计算奖励
            reward, total_waiting_time = self._calculate_reward()

            # 终止条件：达到最大步数或没有车辆
            done = self.current_step >= self.max_steps or traci.simulation.getMinExpectedNumber() == 0
            return obs, reward, done, {'total_waiting_time': total_waiting_time}
        except traci.exceptions.FatalTraCIError as e:
            print(f"TraCI Error: {e}")
            self.close()
            raise e

    def _get_observation(self):
        """获取当前环境的观测值"""
        obs = []
        total_waiting = 0  # 总等待车辆数
        total_speed = 0  # 车辆总速度
        vehicle_count = 0  # 统计车辆总数

        for lane_id in self.lane_ids:
            num_vehicles = traci.lane.getLastStepVehicleNumber(lane_id)  # 该车道上的车辆数
            avg_speed = traci.lane.getLastStepMeanSpeed(lane_id)  # 该车道的平均速度
            queue_length = traci.lane.getLastStepHaltingNumber(lane_id)  # 该车道上的排队车辆数

            obs.extend([num_vehicles, avg_speed, queue_length])
            total_waiting += queue_length
            total_speed += avg_speed * num_vehicles
            vehicle_count += num_vehicles

        # 计算平均等待时间和平均速度
        avg_waiting_time = total_waiting / len(self.lane_ids) if self.lane_ids else 0
        avg_speed = total_speed / vehicle_count if vehicle_count > 0 else 0

        # 获取信号灯状态和剩余时间
        tls_state = traci.trafficlight.getRedYellowGreenState("junction")
        tls_remaining_time = traci.trafficlight.getPhaseDuration("junction") - traci.trafficlight.getNextSwitch(
            "junction")
        obs.extend([tls_state == 'G', tls_remaining_time, avg_waiting_time, avg_speed])

        # 保持观测向量长度为 20
        obs = np.pad(obs, (0, 20 - len(obs)), mode='constant') if len(obs) < 20 else np.array(obs[:20],
                                                                                              dtype=np.float32)
        return obs

    def get_platoon_by_vehicle_id(self, vehicle_id):
        """
        根据车辆ID获取其所属的车队。
        :param vehicle_id: 车辆ID
        :return: 车辆所属的车队对象，如果找不到则返回None
        """
        if self.manager:
            # 使用 SimulationManager 的 getPlatoonByVehicle 方法获取车辆所属的车队
            platoons = self.manager.getPlatoonByVehicle(vehicle_id)
            if platoons:
                return platoons[0]  # 返回第一个匹配的车队
        return None

    def _calculate_reward(self):
        """计算奖励函数（负数处理）"""
        # 获取所有车辆 ID
        vehicle_ids = traci.vehicle.getIDList()
        num_vehicles = len(vehicle_ids) if vehicle_ids else 1  # 避免除以零

        # 计算总等待时间和平均等待时间
        total_waiting_time = sum(traci.vehicle.getWaitingTime(veh_id) for veh_id in vehicle_ids)
        avg_waiting_time = total_waiting_time / num_vehicles

        # 计算平均速度
        avg_speed = np.mean([traci.vehicle.getSpeed(veh_id) for veh_id in vehicle_ids]) if vehicle_ids else 0

        # 统计已经通过交叉口的车辆


        # 计算每个车道上离交叉口最近的车队的等待时间
        closest_platoon_waiting_times = []
        closest_platoon_vehicle_counts = []  # 存储最近车队的车辆数

        # 计算最接近交叉口的车队的加权平均等待时间


        # 对频繁切换交通灯的行为进行惩罚


        # 后续考虑更新奖励函数：switch_penalty = - (15 / (self.current_step - self.last_change_time + 1))  # 惩罚值随切换频率递增

        # 定义奖励的各个组成部分


        # 计算总奖励
        reward = throughput_reward + speed_bonus + closest_platoon_penalty + switch_penalty

        return reward, total_waiting_time

    def close(self):
        """关闭 SUMO 环境"""
        try:
            traci.close()
        except traci.exceptions.FatalTraCIError:
            pass