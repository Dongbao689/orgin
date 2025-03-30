from intersectionController import IntersectionController
from platoon import Platoon
from vehicle import Vehicle
from simlib import flatten

import traci

class SimulationManager():
    """
    模拟管理器类，用于管理交通模拟中的各种元素，如交叉口、车队和车辆等。
    """

    def __init__(self, pCreation=True, iCoordination=True, iZipping=True, maxVehiclesPerPlatoon=0):
        """
        初始化模拟管理器。

        Args:
            pCreation (bool): 是否允许创建车队，默认为True。
            iCoordination (bool): 是否进行交叉口协调，默认为True。
            iZipping (bool): 是否启用交织功能，默认为True。
            maxVehiclesPerPlatoon (int): 每个车队的最大车辆数，默认为0。
        """
        self.intersections = []  # 存储所有交叉口控制器的列表
        self.platoons = list()  # 存储所有车队的列表
        self.platoonCreation = pCreation  # 是否允许创建车队的标志
        self.vehicles = list()  # 存储所有车辆的列表
        self.maxStoppedVehicles = dict()  # 存储每个车道上最多停止车辆数的字典
        self.maxVehiclesPerPlatoon = maxVehiclesPerPlatoon  # 每个车队的最大车辆数
        if iCoordination:
            # 如果需要进行交叉口协调，则为每个交通灯创建一个交叉口控制器并添加到列表中
            for intersection in traci.trafficlight.getIDList():
                controller = IntersectionController(intersection, iZipping)
                self.intersections.append(controller)

    def createPlatoon(self, vehicles):
        """
        使用给定的车辆列表创建一个车队。

        Args:
            vehicles (list): 用于创建车队的车辆列表。
        """
        # 创建一个新的车队，最大车辆数为self.maxVehiclesPerPlatoon
        platoon = Platoon(vehicles, maxVehicles=self.maxVehiclesPerPlatoon)
        self.platoons.append(platoon)  # 将新创建的车队添加到车队列表中

    def getActivePlatoons(self):
        """
        获取所有活跃的车队。

        Returns:
            list: 活跃车队的列表。
        """
        # 过滤出所有活跃的车队
        return [p for p in self.platoons if p.isActive()]

    def getAllVehiclesInPlatoons(self):
        """
        获取所有活跃车队中的所有车辆。

        Returns:
            list: 所有活跃车队中车辆的列表。
        """
        # 先获取所有活跃车队，然后将每个车队中的车辆名称列表合并并扁平化
        return flatten(p.getAllVehiclesByName() for p in self.getActivePlatoons())

    def getAverageLengthOfAllPlatoons(self):
        """
        计算所有车队的平均长度。

        Returns:
            float: 所有车队的平均长度。
        """
        if self.platoons:  # 如果存在车队
            count = 0  # 用于累加车队中车辆的总数
            length = len(self.platoons)  # 车队的数量
            for platoon in self.platoons:
                # 如果车队的解散原因不是“Merged”和“Reform required due to new leader”
                if platoon._disbandReason != "Merged" and platoon._disbandReason != "Reform required due to new leader":
                    count = count + platoon.getNumberOfVehicles()  # 累加该车队的车辆数
                else:
                    length = length - 1  # 排除不符合条件的车队
            return count/length  # 计算平均长度

    def getPlatoonByLane(self, lane):
        """
        获取指定车道上的所有车队。

        Args:
            lane (str): 车道名称。

        Returns:
            list: 指定车道上的车队列表。
        """
        # 过滤出所有活跃车队中位于指定车道的车队
        return [p for p in self.getActivePlatoons() if lane == p.getLane()]

    def getPlatoonByVehicle(self, v):
        """
        获取包含指定车辆的所有车队。

        Args:
            v (str): 车辆名称。

        Returns:
            list: 包含指定车辆的车队列表。
        """
        return [p for p in self.getActivePlatoons() if v in p.getAllVehiclesByName()]

    def getReleventPlatoon(self, vehicle):
        """
        返回与指定车辆最相关的单个车队。
        通过查看前方车辆是否属于某个车队，并检查车队的行驶方向是否正确。

        Args:
            vehicle (Vehicle): 车辆对象。

        Returns:
            Platoon or None: 与指定车辆最相关的车队，如果没有则返回None。
        """


    def handleSimulationStep(self):
        """
        处理模拟的单个步骤。
        """

