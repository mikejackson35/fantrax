import numpy as np

team_color={
     "Philly919": 'rgb(14,195,210)',
     "unit_circle": 'rgb(194,139,221)',
     "AlphaWired": 'rgb(247,160,93)',
     "Snead's Foot": 'rgb(70,214,113)',
     "New Team 4": 'rgb(247,94,56)',
     "Team Gamble": 'rgb(38,147,190)',
     "txmoonshine": 'rgb(219,197,48)',
     "Putt Pirates": 'rgb(115,112,106)'
     }

# color dictionary
active_color={
    "ACTIVE":'rgb(146,146,143)',
    "RESERVE":'rgb(220,222,202)'
    }

team_abbrev_dict = {
        '919':'Philly919',
        'u_c':'unit_circle',
        'NT 4':'New Team 4',
        'NT 8':"Snead's Foot",
        'txms':'txmoonshine',
        'MG':'Team Gamble',
        'grrr':'Putt Pirates',
        '[AW]':'AlphaWired'
        }

stats_dict = {
    'bb_ratio':'Birdie Bogey Ratio',
    'bird_num':'Birdies/wk',
    'median_delta':'+/- Weekly Median',
    'total_pts':'Fantasy Points',
    'plc_pts':'Place Points/wk',
    'cuts_made':'Cuts Made/Wk',
    'pp_hole':'Points/Hole Played',
    'pars_num':'Pars/wk',
    'eag_num':'Eagles/wk',
    'dbog_num':'Double Bogeys/wk',
    'bog_num':'Bogeys/wk'
}

names_dict = {'Matt Fitzpatrick': 'Matthew Fitzpatrick',
    'Si Kim': 'Si Woo Kim',
    'Min Lee': 'Min Woo Lee',
    'Byeong An': 'Byeong Hun An',
    'Rooyen Van': 'Erik Van Rooyen',
    'Vince Whaley': 'Vincent Whaley',
    'kevin Yu': 'Kevin Yu',
    'Kyounghoon Lee': 'Kyoung-Hoon Lee',
    'Jr Hale': 'Blane Hale Jr',
    'de Dumont': 'Adrien Dumont de Chassart'
             }

def fix_names(dg):

    """
    Input: dataframe with player_name as last_name,first_name

    Output: list of player names as first_name, last_name
    """

    names = dg['player_name_rev'].str.split(expand=True)                  
    names[0] = names[0].str.rstrip(",")
    names[1] = names[1].str.rstrip(",")
    names['player_name_rev'] = names[1] + " " + names[0]

    # manually correct known problem names (ie "Jr" or "Si Woo Kim")
    for incorrect_name, correct_name in names_dict.items():
        names['player_name_rev'] = np.where(names['player_name_rev'] == incorrect_name, correct_name, names['player_name_rev'])

    return names.player_name_rev