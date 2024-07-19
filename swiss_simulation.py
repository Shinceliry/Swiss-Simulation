import random
from collections import defaultdict, Counter
import argparse
import numpy as np

def swiss_draw_simulation(p, r, q):
    # 各チームの初期勝敗数を0に設定し、負けたラウンドを記録するフィールドを追加
    records = [{'wins': 0, 'losses': 0, 'loss_rounds': [], 'opponents': []} for _ in range(p)]

    for round_num in range(1, r + 1):
        # 2敗したチームはリタイアさせる
        records = [record for record in records if record['losses'] < 2]
        
        # チームを勝ち数でソート
        records.sort(key=lambda x: (-x['wins'], x['losses']))

        # 勝利数ごとにチームを分ける
        grouped_records = defaultdict(list)
        for record in records:
            grouped_records[record['wins']].append(record)
        
        new_records = []
        one_loss_records = []
        for wins, group in grouped_records.items():
            random.shuffle(group)  # シャッフルしてランダムにマッチング

            if len(group) % 2 == 1:
                # 奇数の場合
                extra_team = group.pop()
                if extra_team['losses'] == 0:
                    # 無敗の選手の場合、1敗の選手とマッチング
                    one_loss_records.append(extra_team)
                else:
                    # 1敗の選手の場合、不戦勝
                    extra_team['wins'] += 1
                    new_records.append(extra_team)

            # 残りのチームをマッチング
            for i in range(0, len(group), 2):
                team1, team2 = group[i], group[i + 1]
                winner = random.choice([0, 1])
                if winner == 0:
                    team1['wins'] += 1
                    team2['losses'] += 1
                    team2['loss_rounds'].append(round_num)
                else:
                    team2['wins'] += 1
                    team1['losses'] += 1
                    team1['loss_rounds'].append(round_num)
                team1['opponents'].append(team2)
                team2['opponents'].append(team1)
                new_records.append(team1)
                new_records.append(team2)

        # 無敗の選手を1敗の選手とマッチング
        for extra_team in one_loss_records:
            matched = False
            for i in range(len(new_records)):
                if new_records[i]['losses'] == 1:
                    winner = random.choice([0, 1])
                    if winner == 0:
                        new_records[i]['wins'] += 1
                        extra_team['losses'] += 1
                        extra_team['loss_rounds'].append(round_num)
                    else:
                        new_records[i]['losses'] += 1
                        new_records[i]['loss_rounds'].append(round_num)
                        extra_team['wins'] += 1
                    new_records[i]['opponents'].append(extra_team)
                    extra_team['opponents'].append(new_records[i])
                    new_records.append(extra_team)
                    matched = True
                    break
            if not matched:
                # もし1敗の選手が見つからなかった場合
                extra_team['wins'] += 1
                new_records.append(extra_team)

        records = new_records

    # 全ラウンド終了後にオポネント%を計算
    for player in records:
        total_opponent_wins = sum(opp['wins'] for opp in player['opponents'])
        total_opponent_matches = len(player['opponents'])
        opponent_win_percentage = (total_opponent_wins / total_opponent_matches) if total_opponent_matches > 0 else 0
        player['opponent_win_percentage'] = max(opponent_win_percentage, 0.33)  # 33%未満の場合は33%にする
    
    # オポネント%に基づいて再度ソート
    records.sort(key=lambda p: (p['wins'], p['opponent_win_percentage']), reverse=True)
    
    results = defaultdict(lambda: defaultdict(int))
    m_wins_0_losses = sum(1 for record in records if record['wins'] == r and record['losses'] == 0)
    m_minus_1_wins_1_loss = sum(1 for record in records if record['wins'] == r - 1 and record['losses'] == 1)
    
    for rank, record in enumerate(records):
        if record['wins'] == r - 1 and record['losses'] == 1:
            for loss_round in record['loss_rounds']:
                results[loss_round]['total'] += 1
                if rank < q:
                    results[loss_round]['qualified'] += 1

    return results, m_wins_0_losses, m_minus_1_wins_1_loss

def calculate_qualification_rates(p, r, q, num_simulations):
    aggregate_results = {x: {'total': 0, 'qualified': 0} for x in range(1, r + 1)}
    total_m_wins_0_losses = 0
    total_m_minus_1_wins_1_loss = 0

    for _ in range(num_simulations):
        simulation_results, m_wins_0_losses, m_minus_1_wins_1_loss = swiss_draw_simulation(p, r, q)
        for x in range(1, r + 1):
            aggregate_results[x]['total'] += simulation_results[x]['total']
            aggregate_results[x]['qualified'] += simulation_results[x]['qualified']
        
        total_m_wins_0_losses += m_wins_0_losses
        total_m_minus_1_wins_1_loss += m_minus_1_wins_1_loss
    
    qualification_rates = {x: (aggregate_results[x]['qualified'] / aggregate_results[x]['total']) if aggregate_results[x]['total'] > 0 else 0 for x in range(1, r + 1)}
    avg_m_wins_0_losses = total_m_wins_0_losses / num_simulations
    avg_m_minus_1_wins_1_loss = total_m_minus_1_wins_1_loss / num_simulations
    return qualification_rates, avg_m_wins_0_losses, avg_m_minus_1_wins_1_loss

def main(args):
    p = args.players
    r = args.rounds
    q = args.qualify
    num_simulations = args.simulations

    qualification_rates, avg_m_wins_0_losses, avg_m_minus_1_wins_1_loss = calculate_qualification_rates(p, r, q, num_simulations)
    for round_num, rate in qualification_rates.items():
        print(f"{round_num}回戦で負けかつ最終1敗の選手の予選通過率は{rate:.2%}")
    print(f"{r}勝0敗の選手の平均人数: {avg_m_wins_0_losses:.2f}")
    print(f"{r-1}勝1敗の選手の平均人数: {avg_m_minus_1_wins_1_loss:.2f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="スイスドロー予選通過シミュレーション")
    parser.add_argument("--players", type=int, help="プレイヤー数")
    parser.add_argument("--rounds", type=int, help="ラウンド数")
    parser.add_argument("--qualify", type=int, help="予選通過人数")
    parser.add_argument("--simulations", type=int, help="シミュレーション回数")
    args = parser.parse_args()
    
    main(args)