import os

def get_schedule_website_url():    
    return os.environ.get("SCHEDULE_WEBSITE_URL", "Specified environment variable is not set.")
    
def get_team_name():    
    return os.environ.get("TEAM_NAME", "Specified environment variable is not set.")