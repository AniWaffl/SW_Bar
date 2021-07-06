from typing import Text
import numpy as np
import itertools
from time import process_time
# Генерация списка всех рецептов
def all_recipe():
    rng = range(1,6)
    l = [f'{a}{b}{c}{d}{e}' for a, b, c, d, e in itertools.product(rng, rng, rng, rng, rng)]
    print(f"Список создан\nЗначений: {len(l)}\n")
    return np.array(l)


# Удаление 100% невалидных рецептов
def remove(l, list_invalid_recipe):
    l = np.setdiff1d(l, np.array(list_invalid_recipe))
    return l


# Заменяет значение в строке 
def pos_exchange(string, positions, change_to):
    str_list = list(string)
    str_list[positions] = change_to    
    string = ''.join(str_list)
    return string

# на основании возможных рецептов, создает список которые точно не подходят => передаёт на удаление
def invert_list(l, potential_recipe):
    list_for_remove = list(set(l)-set(potential_recipe))
    return remove(l, list_for_remove)

def true_position_is_0(key, l, temp):
    for rp, pos1, pos2 in itertools.product(l, range(5), range(5)):
        if pos2 == pos1:
            continue
        elif key[pos1] != rp[pos1]:
            continue
        elif key[pos2] != rp[pos2]:
            continue
        temp.append(rp)
    return remove(l, temp)

def true_position_is_2(key, l, temp):
    for i_1 in range(5):
        for i_2 in range(5):
            for i_3 in range(5):
                if i_1 != (i_2 and i_3) and i_2 != (i_1 and i_3) and i_3 != (i_1 and i_2):
                    for l_1 in "01234":
                        if l_1 != list(key)[i_1]:
                            for l_2 in "01234":
                                if l_2 != list(key)[i_2]:
                                    for l_3 in "01234":
                                        if l_3 != list(key)[i_3]:
                                            a = pos_exchange(key, i_1, l_1)
                                            b = pos_exchange(a, i_2, l_2)
                                            c = pos_exchange(b, i_3, l_3)                           
                                            temp.append(c)
    return invert_list(l, temp)

def true_position_is_3(key, l, temp):
    for pos1, pos2, to_1, to_2 in itertools.product(range(5), range(5), "12345", "12345"):
        if (pos2 != pos1) and (to_1 != list(key)[pos1]) and (to_2 != list(key)[pos2]):
            pass
            a = pos_exchange(key, pos1, to_1)
            b = pos_exchange(a, pos2, to_2)
            temp.append(b)
    return invert_list(l, temp)



def true_position_is_4(key, l, temp):
    for positions, change_to in itertools.product(range(5), "12345"):
        if change_to != key[positions]:
            a = pos_exchange(key, positions, change_to)
            temp.append(a)
    return invert_list(l, temp)

# Основная хуйня
def generate_list_to_remove(posible_recipe_array:np.array, new_recipe:str, count_find_pos:int):
    temp = []

    if count_find_pos == 0:
        return true_position_is_0(new_recipe, posible_recipe_array, temp)

    elif count_find_pos == 2:  
        return true_position_is_2(new_recipe, posible_recipe_array, temp)

    elif count_find_pos == 3:
        return true_position_is_3(new_recipe, posible_recipe_array, temp)

    elif count_find_pos == 4:
        return true_position_is_4(new_recipe, posible_recipe_array, temp)

    elif count_find_pos is 5:
        return []
    

# def _main(recipe_list):
#     l = all_recipe()
#     for recipe in recipe_list:
#         recipe, pos_find = recipe
#         generate_list_to_remove(l, recipe, pos_find)
#     return l
