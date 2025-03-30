# 导入logging模块，用于记录程序运行过程中的信息，方便调试和监控
import logging
# 导入traci模块，它是SUMO（Simulation of Urban MObility）的一个接口，用于与SUMO仿真环境进行交互
import traci
# 从sumolib模块中导入checkBinary函数，该函数用于检查SUMO相关的二进制可执行文件是否可用
from sumolib import checkBinary

def flatten(l):
    # 定义一个名为flatten的函数，它接受一个列表l作为参数
    # 该函数的作用是将嵌套列表展开成一个一维列表
    # 具体实现是使用列表推导式，遍历嵌套列表中的每个子列表，再遍历子列表中的每个元素并添加到新列表中
    return [item for sublist in l for item in sublist]

def setUpSimulation(configFile, trafficScale = 1, outputFileLocation="output/additional.xml"):
    # 定义一个名为setUpSimulation的函数，用于设置并启动SUMO仿真
    # configFile是SUMO的配置文件路径，是必传参数
    # trafficScale是交通流量的缩放比例，默认为1
    # outputFileLocation是额外输出文件的位置，默认为"output/additional.xml"

    # 调用checkBinary函数检查sumo-gui这个可执行文件是否可用，并将结果赋值给sumoBinary变量
    # sumo-gui是SUMO的图形化界面版本
    sumoBinary = checkBinary("sumo-gui")

    # 配置日志记录的格式，使用当前时间和日志信息组合的格式
    # 这样在记录日志时，每条日志前都会显示记录的时间
    logging.basicConfig(format='%(asctime)s %(message)s')
    # 获取根日志记录器
    root = logging.getLogger()
    # 设置根日志记录器的日志级别为DEBUG
    # 这样可以记录包括调试信息在内的所有级别的日志
    root.setLevel(logging.DEBUG)

    # 使用traci.start函数启动SUMO仿真
    # 传入的参数是一个列表，包含了启动SUMO所需的各种配置信息
    # sumoBinary指定使用的SUMO可执行文件
    # "-c"表示指定配置文件，后面跟着configFile变量的值
    # "--step-length"指定仿真的时间步长为0.1秒
    # "--collision.action"设置碰撞发生时的处理动作，这里设置为不做任何处理
    # "--start"表示立即开始仿真
    # "--additional-files"指定额外的输出文件位置
    # "--duration-log.statistics"表示记录仿真的持续时间统计信息
    # "--scale"指定交通流量的缩放比例，将其转换为字符串传入
    traci.start([sumoBinary, "-c", configFile, "--step-length", "0.1", "--collision.action", "none", "--start",
                 "--additional-files", outputFileLocation, "--duration-log.statistics", "--scale", str(trafficScale)])