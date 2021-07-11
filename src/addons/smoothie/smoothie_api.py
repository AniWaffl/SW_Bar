import numpy as np
import itertools

# Генерация списка всех рецептов
def all_recipe():
    rng = range(1,6)
    l = [f'{a}{b}{c}{d}{e}' for a, b, c, d, e in itertools.product(rng, rng, rng, rng, rng)]
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


def true_position_is_0(new_recipe, posible_recipe_array):
    temp = []
    for rp, pos1, pos2 in itertools.product(posible_recipe_array, range(5), range(5)):
        if pos2 == pos1:
            continue
        elif new_recipe[pos1] != rp[pos1]:
            continue
        elif new_recipe[pos2] != rp[pos2]:
            continue
        temp.append(rp)
    return list(set(posible_recipe_array) ^ set(temp))


def true_position_is_2(new_recipe):
    temp = []
    for i_1 in range(5):
        for i_2 in range(5):
            for i_3 in range(5):
                if i_1 != (i_2 and i_3) and i_2 != (i_1 and i_3) and i_3 != (i_1 and i_2):
                    for l_1 in "12345":
                        if l_1 != list(new_recipe)[i_1]:
                            for l_2 in "12345":
                                if l_2 != list(new_recipe)[i_2]:
                                    for l_3 in "12345":
                                        if l_3 != list(new_recipe)[i_3]:
                                            a = pos_exchange(new_recipe, i_1, l_1)
                                            b = pos_exchange(a, i_2, l_2)
                                            c = pos_exchange(b, i_3, l_3)                           
                                            temp.append(c)
    return temp


def true_position_is_3(new_recipe):
    temp = []
    for pos1, pos2, to_1, to_2 in itertools.product(range(5), range(5), "12345", "12345"):
        if (pos2 != pos1) and (to_1 != list(new_recipe)[pos1]) or (to_2 != list(new_recipe)[pos2]):
            a = pos_exchange(new_recipe, pos1, to_1)
            b = pos_exchange(a, pos2, to_2)
            temp.append(b)
    return temp


def true_position_is_4(new_recipe):
    temp = []
    for positions, change_to in itertools.product(range(5), "12345"):
        if change_to != new_recipe[positions]:
            a = pos_exchange(new_recipe, positions, change_to)
            temp.append(a)
    return temp


# Основная хуйня
def generate_list_to_remove(posible_recipe_array:np.array, new_recipe:str, count_find_pos:int):    
    if count_find_pos == 0:
        all_posible:list = true_position_is_0(new_recipe, posible_recipe_array)

    elif count_find_pos == 2:  
        all_posible:list = true_position_is_2(new_recipe)

    elif count_find_pos == 3:
        all_posible:list = true_position_is_3(new_recipe)

    elif count_find_pos == 4:
        all_posible:list = true_position_is_4(new_recipe)

    elif count_find_pos == 5:
        return []
    
    new_posible_recipe_list = list(set(posible_recipe_array) & set(all_posible))
    return np.array(new_posible_recipe_list)
