import traci


class Vehicle():
    # 车辆类的初始化方法，用于创建一个车辆对象
    # 参数 vehicle 是车辆的名称
    def __init__(self, vehicle):
        # 标记车辆是否处于活动状态，初始化为 True
        self._active = True
        # 获取车辆的加速度，并存储在实例变量 _acceleration 中
        self._acceleration = traci.vehicle.getAcceleration(vehicle)
        # 获取车辆的长度，并存储在实例变量 _length 中
        self._length = traci.vehicle.getLength(vehicle)
        # 获取车辆的最大速度，并存储在实例变量 _maxSpeed 中
        self._maxSpeed = traci.vehicle.getMaxSpeed(vehicle)
        # 存储车辆的名称
        self._name = vehicle
        # 获取车辆的路线，并存储在实例变量 _route 中
        self._route = traci.vehicle.getRoute(vehicle)
        # 用于存储之前设置过的属性值，初始化为一个空字典
        self._previouslySetValues = dict()
        self._position = traci.vehicle.getLanePosition(vehicle)  # 车辆位置
        self._speed = traci.vehicle.getSpeed(vehicle)  # 车辆速度
         # 车辆加速度
        # 邻居车辆列表
        # 调节系数
        # 邻居权重
        # 期望车距

    def update_dynamics(self, T):
        """
        更新车辆的位置和速度。
        :param T: 离散化时间步长
        """


    def update_acceleration(self):
        """
        基于邻居误差反馈更新车辆的加速度。
        """


    def get_state(self):
        """
        获取车辆的状态向量 [位置, 速度]。
        """
        return [self._position, self._speed]

    def add_neighbor(self, neighbor, weight):
        """
        添加邻居车辆及其权重。
        :param neighbor: 邻居车辆对象
        :param weight: 权重
        """
        self._neighbors.append(neighbor)
        self._weights[neighbor] = weight

    # 获取车辆的加速度
    def getAcceleration(self):
        return self._acceleration

    # 判断车辆是否处于活动状态


    # 获取车辆所在的道路 ID
    def getEdge(self):
        return traci.vehicle.getRoadID(self.getName())

    # 获取车辆所在的车道 ID
    def getLane(self):
        return traci.vehicle.getLaneID(self.getName())

    # 获取车辆所在车道的索引
    def getLaneIndex(self):
        return traci.vehicle.getLaneIndex(self.getName())

    # 获取车辆在车道上的位置
    def getLanePosition(self):
        return traci.vehicle.getLanePosition(self.getName())

    # 获取车辆距离车道前端的位置
    def getLanePositionFromFront(self):
        # 先获取车辆所在车道的长度
        lane_length = traci.lane.getLength(self.getLane())
        # 用车道长度减去车辆在车道上的位置，得到距离前端的位置
        return lane_length - self.getLanePosition()

    # 获取车辆前方的领头车辆
    def getLeader(self):
        # 调用 traci.vehicle.getLeader 方法，查找距离 20 米内的领头车辆
        return traci.vehicle.getLeader(self.getName(), 20)

    # 获取车辆的长度
    def getLength(self):
        return self._length

    # 获取车辆的最大速度
    def getMaxSpeed(self):
        return self._maxSpeed

    # 获取车辆的名称
    def getName(self):
        return self._name

    # 获取车辆剩余的路线
    def getRemainingRoute(self):
        # 获取车辆当前在路线中的索引
        current_index = traci.vehicle.getRouteIndex(self.getName())
        # 返回从当前索引开始的剩余路线
        return self._route[current_index:]

    # 获取车辆的完整路线
    def getRoute(self):
        return self._route

    # 获取车辆的当前速度
    def getSpeed(self):
        return traci.vehicle.getSpeed(self.getName())

    # 设置车辆的颜色
    def setColor(self, color):
        # 调用内部的 _setAttr 方法来设置颜色属性
        self._setAttr("setColor", color)

    # 将车辆标记为非活动状态
    def setInActive(self):
        self._active = False

    # 设置车辆的不完美程度（可能是一些模拟中的特殊属性）
    def setImperfection(self, imperfection):
        # 调用内部的 _setAttr 方法来设置不完美程度属性
        self._setAttr("setImperfection", imperfection)

    # 设置车辆的最小安全间距
    def setMinGap(self, minGap):
        # 调用内部的 _setAttr 方法来设置最小安全间距属性
        self._setAttr("setMinGap", minGap)

    # 设置车辆要变更到的目标车道
    def setTargetLane(self, lane):
        # 调用 traci.vehicle.changeLane 方法，让车辆以 0.5 的安全性尝试变更到指定车道
        traci.vehicle.changeLane(self.getName(), lane, 0.5)

    # 设置车辆的时间间隔参数 tau
    def setTau(self, tau):
        # 调用内部的 _setAttr 方法来设置 tau 属性
        self._setAttr("setTau", tau)

    # 设置车辆的速度
    def setSpeed(self, speed):
        # 调用内部的 _setAttr 方法来设置速度属性
        self._setAttr("setSpeed", speed)

    # 设置车辆的速度模式
    def setSpeedMode(self, speedMode):
        # 调用内部的 _setAttr 方法来设置速度模式属性
        self._setAttr("setSpeedMode", speedMode)

    # 设置车辆的速度因子
    def setSpeedFactor(self, speedFactor):
        # 调用内部的 _setAttr 方法来设置速度因子属性
        self._setAttr("setSpeedFactor", speedFactor)

    # 内部方法，用于设置车辆的属性
    def _setAttr(self, attr, arg):
        # 只有当车辆处于活动状态时才进行属性设置
        if self.isActive():
            # 检查该属性是否已经设置过
            if attr in self._previouslySetValues:
                # 如果设置过，且新值与旧值相同，则不进行设置，提高性能
                if self._previouslySetValues[attr] == arg:
                    return
            # 记录新的属性值
            self._previouslySetValues[attr] = arg
            # 使用 getattr 动态调用 traci.vehicle 模块中的相应方法来设置属性
            getattr(traci.vehicle, attr)(self.getName(), arg)