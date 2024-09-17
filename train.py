from pypokerengine.api.game import setup_config, start_poker
from my_players.RandomPlayer import RandomPlayer
from my_players.AllCall import AllCallPlayer
from my_players.QLearningPlayer import QLearningPlayer
from my_players.HumanPlayer import ConsolePlayer
from my_players.DQNPlayer1 import DQNPlayer1
from my_players.DQNPlayer2 import DQNPlayer2
from my_players.DQNPlayer3 import DQNPlayer3
from my_players.DQNPlayer4 import DQNPlayer4
from my_players.DQNPlayer5 import DQNPlayer5
from my_players.DQNPlayer6 import DQNPlayer6
from my_players.cardplayer import cardplayer
from my_players.A2CPlayer import A2CPlayer
from my_players.HonestPlayer import HonestPlayer
from scipy.stats import t
import math
import os
import matplotlib.pyplot as plt

num_episode = 10000
win = 0
sample_mean = 0
SXX = 0
sample_std = 0
count = 0
log_interval = 1000
log = []
confidence_level = 0.05
Num_of_agents = 6


vpip_history = {i: [] for i in range(1, Num_of_agents+1)}

dqn_paths = {}
for i in range(1, Num_of_agents+1):
    dqn_paths[i] = {
        'model': os.getcwd() + f'/model/dqn{i}.dump',
        'optimizer': os.getcwd() + f'/model/dqn{i}_optim.dump'
    }


training_agents = []
training_agents.append("")
training_agents.append(DQNPlayer1(dqn_paths[1]['model'], dqn_paths[1]['optimizer'], True))
training_agents.append(DQNPlayer2(dqn_paths[2]['model'], dqn_paths[2]['optimizer'], True))
training_agents.append(DQNPlayer3(dqn_paths[3]['model'], dqn_paths[3]['optimizer'], True))
training_agents.append(DQNPlayer4(dqn_paths[4]['model'], dqn_paths[4]['optimizer'], True))
training_agents.append(DQNPlayer5(dqn_paths[5]['model'], dqn_paths[5]['optimizer'], True))
training_agents.append(DQNPlayer6(dqn_paths[6]['model'], dqn_paths[6]['optimizer'], True))

# Set up configuration
config = setup_config(max_round=1, initial_stack=100, small_blind_amount=5)

# Register each player with their respective DQNPlayer instance
for i in range(1, Num_of_agents+1):
    config.register_player(name=f"p{i}", algorithm=training_agents[i])

for i in range(Num_of_agents+1, 7):
    config.register_player(name=f"p{i}", algorithm=HonestPlayer())

for i in range(0, num_episode):
    count += 1
    game_result = start_poker(config, verbose=0)

    if count % log_interval == 0:
        for j in range(1, Num_of_agents+1):
            vpip_rate = training_agents[j].VPIP / training_agents[j].hand_count * 100 
            vpip_history[j].append(vpip_rate)
            print(f"VPIP over each episode: {vpip_rate:.2f}%")
            training_agents[j].VPIP , training_agents[j].hand_count = 0, 0
            config.players_info[j-1]['algorithm'].save_model()

# Plotting the VPIP history
plt.figure(figsize=(12, 6))
for j in range(1, 7):
    plt.plot(vpip_history[j], label=f'Player {j} VPIP')
    
plt.title('VPIP History of All Agents')
plt.xlabel('Episodes (every 10 episodes)')
plt.ylabel('VPIP (%)')
plt.legend()
plt.grid()
plt.show()