from scenario_manager import runScenario, SCENARIO_NUMBER_CONFIGS, SCENARIO_LOCATION_CONFIG

import sys
import logging

# 初始化变量，用于存储步数、地图名称和场景编号，初始值都设为None
numOfSteps = None
mapName = None
scenarioNum = None

# 检查命令行是否传递了参数
if len(sys.argv) > 1:
    # 如果传递了参数，记录这些参数信息
    logging.info("Found arguments %s passed in", sys.argv)
    # 将第一个参数赋值给地图名称
    mapName = sys.argv[1]
    # 将第二个参数转换为整数并赋值给场景编号
    scenarioNum = int(sys.argv[2])
    # 如果存在第三个参数
    if sys.argv[3]:
        # 将第三个参数转换为整数并赋值给步数
        numOfSteps = int(sys.argv[3])

# 如果地图名称仍然为None，即没有从命令行获取到地图名称
if not mapName:
    # 提示用户输入地图名称，并告知可用的地图名称列表
    mapName = input("Please enter map name, available maps are: %s: " % ", ".join( SCENARIO_LOCATION_CONFIG.keys()))
# 如果场景编号仍然为None，即没有从命令行获取到场景编号
if not scenarioNum:
    # 提示用户输入场景编号，并告知可用的场景编号列表
    scenarioNum = int(input("Please enter scenario number, available numbers are: %s: " % ", ".join( str(n) for n in SCENARIO_NUMBER_CONFIGS.keys())))

# 如果步数不为None，即用户指定了步数
if numOfSteps:
    # 调用runScenario函数，传入地图名称、场景编号和步数
    runScenario(mapName, scenarioNum, numOfSteps)
# 调用runScenario函数，传入地图名称和场景编号（不传入步数）
runScenario(mapName, scenarioNum)