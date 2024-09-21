from pypokerengine.api.game import setup_config, start_poker
from my_players.DQNPlayer1 import DQNPlayer1
from my_players.DQNPlayer2 import DQNPlayer2
from my_players.DQNPlayer3 import DQNPlayer3
from my_players.DQNPlayer4 import DQNPlayer4
from my_players.DQNPlayer5 import DQNPlayer5
from my_players.DQNPlayer6 import DQNPlayer6
from my_players.HonestPlayer import HonestPlayer
import os
import matplotlib.pyplot as plt
import gc
import pandas as pd
import numpy as np

# User's Input
num_episode = 10000000
win = 0
sample_mean = 0
SXX = 0
sample_std = 0
count = 0
log_interval = 100
log = []
confidence_level = 0.05
Num_of_agents = 6

def moving_average(data, window_size=10):
    """Calculate the moving average manually."""
    if len(data) < window_size:
        return data  # Not enough data to smooth
    averages = []
    for i in range(len(data) - window_size + 1):
        avg = sum(data[i:i + window_size]) / window_size
        averages.append(avg)
    return averages

def plotting_VPIP(vpip_df):
    plt.figure(figsize=(12, 6))
    for j in range(6):
        plt.plot(vpip_df.iloc[:, j], label=f'Player {j+1} VPIP')
        # Smoothing with a moving average
    plt.title('VPIP History of All Agents')
    plt.xlabel('Episodes (every 100 episodes)')
    plt.ylabel('VPIP (%)')
    plt.legend()
    plt.grid()
    plt.savefig('images/vpip_history.png')
    plt.close()

    plt.figure(figsize=(12, 6))
    for j in range(6):
        smoothed_vpip = moving_average(vpip_df.iloc[:, j])
        plt.plot(range(len(smoothed_vpip)), smoothed_vpip, linestyle='--', 
                label=f'Player {j+1} Smoothed VPIP', alpha=0.7)
    plt.title('VPIP History of All Agents')
    plt.xlabel('Episodes (every 100 episodes)')
    plt.ylabel('VPIP (%)')
    plt.legend()
    plt.grid()
    plt.savefig('images/vpip_history_smoothed.png')
    plt.close()
        
def plotting_PFR(pfr_df):
    plt.figure(figsize=(12, 6))
    for j in range(6):
        plt.plot(pfr_df.iloc[:, j], label=f'Player {j+1} PFR')
    
    plt.title('PFR History of All Agents')
    plt.xlabel('Episodes (every 100 episodes)')
    plt.ylabel('PFR (%)')
    plt.legend()
    plt.grid()
    plt.savefig('images/pfr_history.png')
    plt.close()

    plt.figure(figsize=(12, 6))
    for j in range(6):
        # Smoothing with a moving average
        smoothed_pfr = moving_average(pfr_df.iloc[:, j])
        plt.plot(range(len(smoothed_pfr)), smoothed_pfr, linestyle='--', 
                 label=f'Player {j+1} Smoothed PFR', alpha=0.7)
    
    plt.title('PFR History of All Agents')
    plt.xlabel('Episodes (every 100 episodes)')
    plt.ylabel('PFR (%)')
    plt.legend()
    plt.grid()
    plt.savefig('images/pfr_history_smoothed.png')
    plt.close()

def plotting_3bet(three_bet_df):
    plt.figure(figsize=(12, 6))
    for j in range(6):
        plt.plot(three_bet_df.iloc[:, j], label=f'Player {j+1} 3-Bet %')
    plt.title('3-Bet Percentage History of All Agents')
    plt.xlabel('Episodes (every 100 episodes)')
    plt.ylabel('3-Bet %')
    plt.legend()
    plt.grid()
    plt.savefig('images/three_bet_history.png')
    plt.close()

    plt.figure(figsize=(12, 6))
    for j in range(6):
        # Smoothing with a moving average
        smoothed_3bet = moving_average(three_bet_df.iloc[:, j])
        plt.plot(range(len(smoothed_3bet)), smoothed_3bet, linestyle='--', 
                 label=f'Player {j+1} Smoothed 3-Bet %', alpha=0.7)
    plt.title('3-Bet Percentage History of All Agents')
    plt.xlabel('Episodes (every 100 episodes)')
    plt.ylabel('3-Bet %')
    plt.legend()
    plt.grid()
    plt.savefig('images/three_bet_history_Smoothed.png')
    plt.close()

# Declaration
vpip_history = []
pfr_history = []
three_bet_history = []

vpip_df = pd.DataFrame()
pfr_df = pd.DataFrame()
three_bet_df = pd.DataFrame()

if os.path.exists("DQN_Stat/vpip_history.csv"):
    vpip_df = pd.read_csv("DQN_Stat/vpip_history.csv")
if os.path.exists("DQN_Stat/pfr_history.csv"):
    pfr_df = pd.read_csv("DQN_Stat/pfr_history.csv")
if os.path.exists("DQN_Stat/three_bet_history.csv"):
    three_bet_df = pd.read_csv("DQN_Stat/three_bet_history.csv")

dqn_paths = {}
for i in range(Num_of_agents):
    dqn_paths[i] = {
        'model': os.getcwd() + f'/model/dqn{i+1}.dump',
        'optimizer': os.getcwd() + f'/model/dqn{i+1}_optim.dump'
    }

training_agents =  [DQNPlayer1(dqn_paths[0]['model'], dqn_paths[0]['optimizer'], True),
                    DQNPlayer2(dqn_paths[1]['model'], dqn_paths[1]['optimizer'], True),
                    DQNPlayer3(dqn_paths[2]['model'], dqn_paths[2]['optimizer'], True),
                    DQNPlayer4(dqn_paths[3]['model'], dqn_paths[3]['optimizer'], True),
                    DQNPlayer5(dqn_paths[4]['model'], dqn_paths[4]['optimizer'], True),
                    DQNPlayer6(dqn_paths[5]['model'], dqn_paths[5]['optimizer'], True)]

# Set up configuration
config = setup_config(max_round=36, initial_stack=100, small_blind_amount=5)

# Register each player with their respective DQNPlayer instance
for i in range(Num_of_agents):
    config.register_player(name=f"p{i+1}", algorithm=training_agents[i])

for i in range(Num_of_agents+1, 7):
    config.register_player(name=f"p{i+1}", algorithm=HonestPlayer())

# Game_Simulation
for i in range(0, num_episode):
    count += 1
    game_result = start_poker(config, verbose=0)

    if count % log_interval == 0:
        print(count)
        for j in range(Num_of_agents):

            vpip_rate = training_agents[j].VPIP / training_agents[j].hand_count * 100 
            vpip_history.append(vpip_rate)
            print(f"VPIP over each episode: {vpip_rate:.2f}%")

            # Calculate and log PFR
            pfr_rate = training_agents[j].PFR / training_agents[j].hand_count * 100 
            pfr_history.append(pfr_rate)
            print(f"PFR over each episode: {pfr_rate:.2f}%")

            # Calculate and log 3-Bet Percentage
            three_bet_rate = training_agents[j].three_bet / training_agents[j].hand_count * 100
            three_bet_history.append(three_bet_rate)
            print(f"3-Bet Percentage over each episode: {three_bet_rate:.2f}%")

            # Resetting the counts for the next episode
            training_agents[j].VPIP, training_agents[j].PFR, training_agents[j].three_bet, training_agents[j].hand_count = 0, 0, 0, 0
            config.players_info[j]['algorithm'].save_model()

        vip_history = np.array(vpip_history)

        new_vpip = pd.DataFrame([vpip_history])
        new_pfr = pd.DataFrame([pfr_history])
        new_three_bet = pd.DataFrame([three_bet_history])

        if not vpip_df.empty:
            new_vpip.columns = vpip_df.columns
        
        if not pfr_df.empty:
            new_pfr.columns = pfr_df.columns

        if not three_bet_df.empty:
            new_three_bet.columns = three_bet_df.columns

        # Reset index before concatenation
        vpip_df = pd.concat([vpip_df, new_vpip], ignore_index=True)  # No ignore_index here
        pfr_df = pd.concat([pfr_df, new_pfr], ignore_index=True)      # No ignore_index here
        three_bet_df = pd.concat([three_bet_df, new_three_bet],ignore_index=True)

        vpip_df.to_csv("DQN_Stat/vpip_history.csv", index=False)
        pfr_df.to_csv("DQN_Stat/pfr_history.csv", index=False)
        three_bet_df.to_csv("DQN_Stat/three_bet_history.csv", index=False)

        vpip_history = []
        pfr_history = []
        three_bet_history = []

        plotting_VPIP(vpip_df)
        plotting_PFR(pfr_df)
        plotting_3bet(three_bet_df)

        if count % 10000 == 0:
            gc.collect()
        

