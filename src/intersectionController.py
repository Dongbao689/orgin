import traci  # 导入SUMO的TraCI库，用于与SUMO仿真进行交互
import logging  # 导入日志模块，用于记录日志信息
from simlib import flatten  # 从simlib模块导入flatten函数，用于展平列表

class IntersectionController():
    def __init__(self, intersection, zip=True):
        """
        初始化交叉口控制器。
        :param intersection: 交叉口的名称或ID
        :param zip: 是否启用车辆“压缩”功能（即车辆在交叉口处合并通过）
        """
        lanes = traci.trafficlight.getControlledLanes(intersection)  # 获取该交叉口控制的所有车道
        self.lanesServed = set(lanes)  # 将车道转换为集合，方便后续操作
        self.name = intersection  # 交叉口名称
        self.platoons = []  # 存储当前管理的车队列表
        self.platoonsZipped = set()  # 存储已经“压缩”过的车队
        self.platoonZips = []  # 存储“压缩”车队的列表
        self.zip = zip  # 是否启用“压缩”功能
        self._a_max = 2.0  # 最大允许加速度

    def can_pass_green_light(self, platoon, t_green):
        """
        检查车队是否可以在绿灯时间内通过交叉口。
        :param platoon: 车队
        :param t_green: 绿灯剩余时间
        :return: 如果可以通过，返回True，否则返回False
        """


    def addPlatoon(self, platoon):
        """
        将车队添加到交叉口控制器中。
        :param platoon: 要添加的车队对象
        """


    def calculateNewReservedTime(self, pv, reservedTime):
        """
        计算为给定车队或车辆（pv）预留的时间。
        :param pv: 车队或车辆对象
        :param reservedTime: 已经预留的时间
        :return: 新的预留时间
        """
        # 如果该车队是第一个提出预留请求的，则需要包括到交叉口的距离
        # 计算新的预留时间

    def _eligibleZippings(self, platoon):
        """
        检查是否有符合条件的“压缩”车队。
        :param platoon: 要检查的车队
        :return: 符合条件的“压缩”车队列表
        """


    def removeIrreleventPlatoons(self):
        """
        移除不再受交叉口控制器管理的车队（例如已经离开影响范围或离开地图的车队）。
        """


    def findAndAddReleventPlatoons(self, platoons):
        """
        在给定的车队列表中找到可以由该控制器管理的车队，并将其添加到控制器中。
        :param platoons: 要检查的车队列表
        """


    def getVehicleZipOrderThroughJunc(self):
        """
        获取启用“压缩”功能时，车队通过交叉口的顺序。
        :return: 车队通过交叉口的顺序列表
        """


    def _generatePlatoonZips(self):
        """
        生成所有车队的“压缩”组合。
        """


    def _getLanePosition(self, v):
        """
        获取车队或车辆在交叉口控制车道上的位置。
        :param v: 车队或车辆对象
        :return: 车队或车辆的位置，如果不在控制车道上则返回1000
        """
        if v.isActive():
            if v.getLane() in self.lanesServed:
                return v.getLanePositionFromFront()  # 返回车队前端的位置
        return 1000  # 如果不在控制车道上，返回1000

    def getNewSpeed(self, pv, reservedTime):
        """
        获取车队或车辆应遵守的速度，以便安全通过交叉口。
        :param pv: 车队或车辆对象
        :param reservedTime: 预留的时间
        :return: 新的速度
        """



    def removePlatoon(self, platoon):
        """
        从控制器中移除车队，并重置其行为为默认状态。
        :param platoon: 要移除的车队
        """
        self.platoons.remove(platoon)  # 从列表中移除车队
        # 恢复默认速度行为
        platoon.removeTargetSpeed()  # 移除目标速度
        platoon.setSpeedMode(31)  # 设置速度模式为默认
        if self.zip:
            platoon.removeControlledLanes(self.lanesServed)  # 如果启用“压缩”功能，移除控制的车道信息

    def update(self):
        """
        更新交叉口的状态。
        1. 确保所有由交叉口管理的车辆自动停止行为被禁用（否则它们在交叉口处会过于谨慎）
        2. 移除不再受交叉口影响的车队
        3. 更新所有由控制器管理的车队的速度
        """
        reservedTime = 0
        if self.zip:
            self._generatePlatoonZips()
            for v in self.getVehicleZipOrderThroughJunc():
                if v.isActive() and v.getLane() in self.lanesServed:
                    if self.can_pass_green_light(v, reservedTime):
                        v.setSpeed(v.getMaxSpeed())
                    else:
                        v.setSpeed(0)
                    reservedTime = self.calculateNewReservedTime(v, reservedTime)
        else:
            for p in self.platoons:
                # 如果车队未通过交叉口，则更新其速度
                if p.getLane() in self.lanesServed:
                    speed = self.getNewSpeed(p, reservedTime)
                    if speed == -1:
                        p.removeTargetSpeed()  # 如果速度为-1，则移除目标速度
                    else:
                        p.setTargetSpeed(speed)  # 否则设置目标速度
                    reservedTime = self.calculateNewReservedTime(p, reservedTime)  # 计算新的预留时间
        self._logIntersectionStatus(reservedTime)  # 记录交叉口状态

    def _logIntersectionStatus(self, reservation=None):
        """
        记录交叉口的状态。
        :param reservation: 预留的时间
        """


    def _zipPlatoons(self, platoons):
        """
        将给定车队中的所有车辆“压缩”成一个连续的集合。
        :param platoons: 要“压缩”的车队列表
        :return: “压缩”后的车辆列表
        """
