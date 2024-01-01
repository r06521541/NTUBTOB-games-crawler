import functions_framework
from flask import jsonify, abort
import json

from variables import get_schedule_website_url, get_team_name
from crawler import get_games_from_schedules

@functions_framework.http
def get_games(request):
    
    if not (request.method == "GET"):
        return abort(405)
    
    try:
        games = get_games_from_schedules(get_schedule_website_url(), get_team_name())
        # 使用列表推導式將每個物件轉換為字典
        game_list = [game.as_dict() for game in games]

        # 使用 json.dumps 將整個列表轉換為 JSON 字串
        json_string = json.dumps(game_list, indent=2, ensure_ascii=False)        
        return jsonify({'status': 'success', 'games': json_string})

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'status': 'error', 'message': f'Failed to search games: {e}'}), 500
    