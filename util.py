import random
import string
from datetime import datetime 

def get_current_date():
    date_and_time_without_seconds = str(datetime.now())[0:16]
    return date_and_time_without_seconds

def get_unique_file_name():
    current_date = datetime.now()
    letters = string.ascii_lowercase
    
    file_name_base =  int(datetime.timestamp(current_date))
    random_file_name_ending = ''.join(random.choice(letters) for _ in range(6))
    
    unique_file_name = str(file_name_base) + "-" + random_file_name_ending
    
    return unique_file_name