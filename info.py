import json
import datetime
import time

test = 'okok'
if test == 'y':
    print('\033[1m'+'\nThis is a test run. Items will' +
          '\033[91m'+' not be added to cart\n'+'\033[0m')

data = json.load(open(r'json_data\data.json'))

search_list = []
search_id = []

while len(search_list) == 0:
    location = str(input('Search Location: '))
    booking_date = datetime.date.today() + datetime.timedelta(days=14)
    date_selected = booking_date.strftime('%Y-%m-%d')
    booking_timestamp = int(time.mktime(booking_date.timetuple()))

    for loc in data['Data']:
        if location.title() in loc['facilityAddress']:

            search_list.append(loc['facilityName'])
            search_id.append(loc['facilityID'])

        elif location.title() in loc['facilityName']:

            search_list.append(loc['facilityName'])
            search_id.append(loc['facilityID'])

    if len(search_list) == 0:
        print('Check inputs and try again. ')


if booking_date.weekday() <= 3:
    list_remove = [i for i, x in enumerate(search_list) if 'School' in x]
    for i in reversed(list_remove):
        search_id.pop(i)
        search_list.pop(i)


id_remove = [i for i, x in enumerate(search_id) if 'Error' in x]
for i in reversed(id_remove):
    search_id.pop(i)
    search_list.pop(i)


morning = 'n'

delay = 'n'

pre_selection = list(input(
    '\nPre-select your court timing (Eg. 12,18) \nPress "n" to search for any timing: ').split(","))
if pre_selection != ['n']:
    pre_selection = [i.zfill(2) for i in pre_selection]


if __name__ == '__main__':
    print(search_list, search_id)
    print(morning)
    print(date_selected)
    print(booking_date.strftime("%a, %#d %b %Y"))
    print(pre_selection)
