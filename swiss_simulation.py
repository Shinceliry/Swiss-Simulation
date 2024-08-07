import random
from collections import defaultdict, Counter
import argparse

def swiss_draw_simulation(players, rounds, qualify):
    records = [{'wins': 0, 'losses': 0, 'loss_rounds': [], 'opponents': []} for _ in range(players)]

    for round in range(1, rounds + 1):
        # Automatic retirement after two losses
        records = [record for record in records if record['losses'] < 2]
        
        records.sort(key=lambda x: (-x['wins'], x['losses']))
        grouped_records = defaultdict(list)
        
        for record in records:
            grouped_records[record['wins']].append(record)
        
        new_records = []
        one_loss_records = []
        
        for wins, group in grouped_records.items():
            random.shuffle(group)
            # When there is an odd number of undefeated players, one player plays a one-loss player
            # After that, if there is an odd number of players with one loss, one is uncontested
            if len(group) % 2 == 1:
                extra_player = group.pop()
                if extra_player['losses'] == 0:
                    one_loss_records.append(extra_player)
                else:
                    extra_player['wins'] += 1
                    new_records.append(extra_player)

            # matching simulation
            for i in range(0, len(group), 2):
                player1, player2 = group[i], group[i + 1]
                winner = random.choice([0, 1])
                if winner == 0:
                    player1['wins'] += 1
                    player2['losses'] += 1
                    player2['loss_rounds'].append(round)
                else:
                    player2['wins'] += 1
                    player1['losses'] += 1
                    player1['loss_rounds'].append(round)
                player1['opponents'].append(player2)
                player2['opponents'].append(player1)
                new_records.append(player1)
                new_records.append(player2)
        
        records = new_records

    # Opponent win rate calculated after all rounds
    for player in records:
        total_opponent_wins = sum(opp['wins'] for opp in player['opponents'])
        total_opponent_matches = len(player['opponents'])
        opponent_win_percentage = (total_opponent_wins / total_opponent_matches) if total_opponent_matches > 0 else 0
        # If opponent win rate is less than 33%, make it 33%
        player['opponent_win_percentage'] = max(opponent_win_percentage, 0.33)
    
    records.sort(key=lambda p: (p['wins'], p['opponent_win_percentage']), reverse=True)
    
    results = defaultdict(lambda: defaultdict(int))
    loss_0 = sum(1 for record in records if record['wins'] == rounds and record['losses'] == 0)
    loss_1 = sum(1 for record in records if record['wins'] == rounds - 1 and record['losses'] == 1)
    
    # Calculate the breakdown of qualifiers
    for rank, record in enumerate(records):
        if record['wins'] == rounds - 1 and record['losses'] == 1:
            for loss_round in record['loss_rounds']:
                results[loss_round]['total'] += 1
                if rank < qualify:
                    results[loss_round]['qualified'] += 1

    return results, loss_0, loss_1

def calculate_qualification_rates(players, rounds, qualify, simulations):
    aggregate_results = {x: {'total': 0, 'qualified': 0} for x in range(1, rounds + 1)}
    loss_0_players = 0
    loss_1_players = 0

    for _ in range(simulations):
        simulation_results, loss_0, loss_1 = swiss_draw_simulation(players, rounds, qualify)
        for x in range(1, rounds + 1):
            aggregate_results[x]['total'] += simulation_results[x]['total']
            aggregate_results[x]['qualified'] += simulation_results[x]['qualified']
        
        loss_0_players += loss_0
        loss_1_players += loss_1
    
    qualification_rates = {x: (aggregate_results[x]['qualified'] / aggregate_results[x]['total']) if aggregate_results[x]['total'] > 0 else 0 for x in range(1, rounds + 1)}
    avg_loss_0_players = loss_0_players / simulations
    avg_loss_1_players = loss_1_players / simulations
    return qualification_rates, avg_loss_0_players, avg_loss_1_players

def main(args):
    players = args.players
    rounds = args.rounds
    qualify = args.qualify
    simulations = args.simulations
    print(f"players={players}, rounds={rounds}, qualify={qualify}, simulations={simulations}")

    qualification_rates, avg_loss_0_players, avg_loss_1_players = calculate_qualification_rates(players, rounds, qualify, simulations)
    for round_num, rate in qualification_rates.items():
        print(f"{round_num}回戦で負けかつ最終1敗の選手の予選通過率は{rate:.2%}")
    print(f"{rounds}勝0敗の選手の平均人数: {avg_loss_0_players:.2f}")
    print(f"{rounds-1}勝1敗の選手の平均人数: {avg_loss_1_players:.2f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="スイスドロー予選通過シミュレーション")
    parser.add_argument("--players", type=int, help="プレイヤー数")
    parser.add_argument("--rounds", type=int, help="ラウンド数")
    parser.add_argument("--qualify", type=int, help="予選通過人数")
    parser.add_argument("--simulations", type=int, help="シミュレーション回数")
    args = parser.parse_args()
    
    main(args)
