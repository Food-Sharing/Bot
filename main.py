from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from vk_api.utils import get_random_id
import random
import datetime


all_participants = {}
vka = VkApi(token='')
longpoll = VkLongPoll(vka)
vk_session = VkApi('', '', auth_handler=True)
vk_session.auth()
vk = vk_session.get_api()
keyboard = VkKeyboard(one_time=True)
list_urls = ['https://vk.com/sharingfood', 'https://vk.com/foodptz', 'https://vk.com/chelny_eda_darom', 'https://vk.com/otdam_edy_darom',
             'https://vk.com/nsk_foodsharing', 'https://vk.com/sharingfood_irk', 'https://vk.com/sharingfoodperm', 'https://vk.com/foodsharing48']


def read_db():
    d = {}
    with open('database.txt') as f:
        data = f.read()
    for i in data.split('\n'):
        if not i or 'Продукты' in i:
            continue
        else:
            d[int(i.split(' - ')[0])] = i.split(' - ')[1]
    return d


def read_prods():
    d1 = {}
    with open('database.txt') as f:
        data = f.read()
    for i in data.split('\n'):
        if not i:
            continue
        elif 'Продукты' in i:
            d1[i.split(' - Продукты: ')[0]] = i.split(' - Продукты: ')[1]
    return d1


def detect_adress(string):
    adress = ''
    for i in string.split():
        if i.istitle():
            adress = i + string[string.index(i) - 1]
    return f'{string}\nАдрес: {adress}'


def write_db(id1, city):
    f = open('database.txt', 'a')
    f.write(f'{id1} - {city}\n')


def write_db_prods(id1, prods):
    f = open('database.txt', 'a')
    f.write(f'{id1} - Продукты: {prods}\n')


def groups(city):
    offset, count, groups1 = 1, 10, ''
    while True:
        groups1 = vk.groups.search(
            q=f'фудшеринг {city.lower().title()}', offset=offset, count=count)
        offset += 1
        if groups1:
            break
    try:
        group = groups1['items'][0]['id']
    except IndexError:
        return 'В вашем городе не найдено групп фудшеринга.'
    return group


def parse(city):
    a = []
    posts_strings = ''
    try:
        posts = vk.wall.get(owner_id=float(f"-{groups(city)}"),count=5)['items']
        print(posts)
    except ValueError:
        return False
    timestamp = posts[0]['date']
    value = datetime.datetime.fromtimestamp(timestamp)
    td = datetime.date.today()
    posts_strings = [post['text'] for post in posts]
    for p in posts_strings:
        if 'примем' in p or 'приму' in p or 'возьму' in p or 'возьмём' in p or 'админ' in p or 'помоги' in p or 'прошу' in p\
            or 'ECO' in p:
            continue
        else:
            a.append(p)
            break
    if a:
        return ''.join(a), f'\nСообщество: vk.com/club{groups(city)}\nАвтор: vk.com/id{posts[0]["from_id"]}'
    return False


def write_m(user_id, message, keyboard1=False):
    if keyboard1:
        vka.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': random.randint(0, 2 ** 64),
                                     'keyboard': keyboard1.get_keyboard()})
    else:
        vka.method('messages.send', {
            'user_id': user_id, 'message': message, 'random_id': random.randint(0, 2 ** 64)})


def send_help(user_id):
    write_m(user_id,
            'Доброго времени суток!\nВот, что я могу:\n1.Город <город> - изменить место поиска\n2.Время <кол-во ' +
            'минут> - установить интервалы оффлайн-поиска\n3.Продукты - задать список интересующих продуктов и что в них включается.\n' +
            '4.Помощь - список доступных команд')


all_participants, favorites = read_db(), read_prods()
print(all_participants, favorites)


def bot():
    user_id = ''
    global all_participants
    prods = []
    for event in longpoll.listen():
        keyboard = VkKeyboard(one_time=False)
        keyboard2 = VkKeyboard(one_time=True)
        keyboard.add_button('Поиск продуктов в моем городе',color=VkKeyboardColor.POSITIVE)
        keyboard.add_line()
        keyboard.add_button('Задать интересные продукты', color=VkKeyboardColor.PRIMARY)
        keyboard.add_line()
        keyboard.add_button('Расширенный поиск', color=VkKeyboardColor.PRIMARY)
        # Если пришло новое сообщение
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                request = event.text.lower()
                user_id = event.user_id
                if user_id in all_participants.keys():
                    if request.split()[0] == 'отзыв':
                        
                    if request.split('\n')[0] == 'нужное':
                        for i in request.split('), ')[1:]:
                            prods.append(f'{i}), ')
                        write_db_prods(user_id, ''.join(prods))
                    if request == 'начать' or request == 'помощь' or request == 'привет':
                        send_help(user_id)
                    elif request.split()[0] == 'город' and len(request.split()) == 2:
                        write_db(user_id, request.split()[1])
                    elif request.split()[0] == 'поиск' or request == 'поиск продуктов в моем городе':
                        if not parse(all_participants[user_id]):
                            write_m(user_id, 'Нет свежих предложений')
                        else:
                            write_m(event.user_id, parse(all_participants[user_id])[0])
                            write_m(user_id, parse(all_participants[user_id])[1])
                    elif request.split()[0] == 'продукты' or 'задать интересные продукты' in request:
                        write_m(user_id, 'Напиши в следующем сообщении список, как указано в примере с пометкой "Нужное" в начале.Пример: Нужное\nхлебопродукты(хлеб, торт), супы(борщ, гороховый)')
                if user_id not in all_participants.keys():
                    print(user_id)
                    keyboard2.add_location_button()
                    result = vka.method("messages.getById", {"message_ids": event.message_id})
                    if 'geo'not in result['items'][0].keys():
                        write_m(event.user_id, 'Вы новый пользователь.\nДобавьте Ваше местоположение(нажатие на кнопку):', keyboard2)
                    else:
                        geo = result['items'][0]['geo']['place']['city']
                        write_db(user_id, geo)
                        write_m(user_id, 'Поздравляем! Вы авторизованы.', keyboard)
        all_participants = read_db()


try:
    bot()
except ConnectionError:
    bot()
