from stable_baselines3 import PPO
from sumo_env import SumoEnvWithPlatoon
from stable_baselines3.common.callbacks import BaseCallback
import matplotlib.pyplot as plt
import os
import torch
from tqdm import tqdm
import time
from torch.utils.tensorboard import SummaryWriter
import datetime

# 自定义回调函数，用于在训练过程中跟踪每个episode的总奖励
class RewardTrackingCallback(BaseCallback):
    def __init__(self, verbose=0):
        super(RewardTrackingCallback, self).__init__(verbose)
        self.episode_rewards = []  # 用于存储每个 episode 的总奖励
        self.episode_reward = 0  # 当前 episode 的奖励

    def _on_step(self):
        reward = self.locals["rewards"][0]  # 获取当前步的奖励
        self.episode_reward += reward  # 累加当前 episode 的奖励
        done = self.locals["dones"][0]  # 检查是否 episode 结束
        if done:
            self.episode_rewards.append(self.episode_reward)  # 保存当前 episode 的总奖励
            self.episode_reward = 0  # 重置当前 episode 的奖励
        return True




    def _on_step(self):
        # 检查是否 episode 结束
        done = self.locals.get("dones", [False])[0]
        if done:
            # 确保当前 episode 的奖励已经被存储
            if len(self.reward_callback.episode_rewards) > self.episode_count:
                episode_reward = self.reward_callback.episode_rewards[self.episode_count]  # 获取当前 episode 的总奖励
                # 将当前 episode 的总奖励写入 TensorBoard
                self.writer.add_scalar("Reward/episode", episode_reward, self.episode_count)
                # 打印当前 episode 的总奖励
                print(f"Episode {self.episode_count + 1}: Total Reward = {episode_reward}")
                self.episode_count += 1  # 更新 episode 计数器

        # 记录每一步的奖励
        if "rewards" in self.locals:
            self.writer.add_scalar("Reward/step", self.locals["rewards"][0], self.num_timesteps)

        # 记录损失值（如果模型已经初始化）
        if self.model is not None:
            # 获取模型的损失值
            loss_dict = self.model.logger.name_to_value  # 获取日志中的损失值
            for key, value in loss_dict.items():
                if "loss" in key:  # 只记录与损失相关的值
                    self.writer.add_scalar(f"Loss/{key}", value, self.num_timesteps)

        return True

    def _on_training_end(self):
        self.writer.close()  # 训练结束时关闭 TensorBoard writer



# 运行PPO算法的函数，支持不同的超参数配置
def run_experiment(batch_size, gamma, clip_range, n_steps, model_save_path, learning_rate=0.0003, total_timesteps=5000):
    env = SumoEnvWithPlatoon(config_file="../maps/s.sumocfg", max_steps=500)  # 初始化SUMO环境

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    model = PPO(
        "MlpPolicy",  # 使用多层感知机策略
        env,
        batch_size=batch_size,  # 设置批量大小
        gamma=gamma,  # 设置折扣因子
        clip_range=clip_range,  # 设置截断范围
        n_steps=n_steps,  # 设置每个episode的步数
        learning_rate=learning_rate,  # 设置学习率
        verbose=1,  # 设置日志级别
        device=device  # 指定使用GPU
    )

    # 获取当前日期和时间
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # 生成唯一的实验名称，包含日期和时间
    experiment_name = f"{current_datetime}_batch_size_{batch_size}_gamma_{gamma}_clip_range_{clip_range}_n_steps_{n_steps}_lr_{learning_rate}"

    reward_callback = RewardTrackingCallback()  # 创建奖励跟踪回调函数实例
    tqdm_callback = TQDMProgressCallback(total_timesteps=total_timesteps)  # 创建 tqdm 进度条回调函数实例
    tensorboard_callback = TensorboardCallback(reward_callback, experiment_name=experiment_name)  # 创建 TensorBoard 回调函数实例

    model.learn(total_timesteps=total_timesteps,
                callback=[reward_callback, tqdm_callback, tensorboard_callback])  # 训练模型
    model.save(model_save_path)  # 训练完成后保存模型
    env.close()  # 关闭环境
    return reward_callback.episode_rewards  # 返回每个episode的总奖励


# 超参数配置
batch_sizes = []  # 批量大小列表
gammas = []  # 折扣因子列表
clip_ranges = []  # 截断范围列表
n_steps_list = []  # 每个episode的步数列表
learning_rates = []  # 学习率列表
total_timesteps =   # 总训练步数



# 绘制不同批量大小和学习率下的总奖励曲线
plt.figure(figsize=(10, 6))
for batch_size in batch_sizes:
    for learning_rate in learning_rates:
         # 生成模型保存路径，包含 timesteps、batch_size 和 learning_rate
        model_save_path = os.path.join(
            "PPO_Platoon/model",
            f"{current_datetime}_PPO_MODEL_timesteps_{total_timesteps}_batch_size_{batch_size}_lr_{learning_rate}.zip"
        )
        rewards = run_experiment(
            batch_size=batch_size,
            gamma=,
            clip_range=,
            n_steps=256,
            model_save_path=model_save_path,
            learning_rate=learning_rate,
            total_timesteps=total_timesteps
        )
        plt.plot(rewards, label=f"batch_size={batch_size}, lr={learning_rate}")
plt.xlabel("Episode")
plt.ylabel("Total reward")
plt.title("Total Reward Curves for Different Batch Sizes, Learning Rates, and n_steps")
plt.legend()
plt.show()