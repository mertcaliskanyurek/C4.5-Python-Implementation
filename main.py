import csv
import math
import copy


class DataSet:
    headers = []
    rows = []

    def get_width(self):
        return self.headers.__len__()

    def get_size(self):
        return self.rows.__len__()

    def get_class_index(self):
        return self.headers.__len__() - 1


class Tree(object):
    def __init__(self, name='root', children=None):
        self.name = name
        self.value = ''
        self.children = []
        if children is not None:
            for child in children:
                self.add_child(child)

    def __repr__(self):
        return self.name

    def add_child(self, node):
        assert isinstance(node, Tree)
        self.children.append(node)

    def is_pure(self):
        return self.children.__len__() == 0


def read_data(filename='') -> DataSet:
    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        headers = []
        rows = []
        for row in csv_reader:
            if line_count == 0:
                headers += row
                line_count += 1
            else:
                rows.append(row)
                line_count += 1

    data = DataSet()
    data.headers = headers
    data.rows = rows

    return data


def remove_attr(dataset: DataSet, index: int) -> DataSet:
    new_headers = dataset.headers[:index] + dataset.headers[index + 1:]
    new_rows = []
    for row in dataset.rows:
        new_rows.append(row[:index] + row[index + 1:])

    new_dataset = DataSet()
    new_dataset.headers = new_headers
    new_dataset.rows = new_rows
    return new_dataset


def extract_feature(dataset: DataSet, col_index: int, future='') -> DataSet:
    new_rows = []
    for row in dataset.rows:
        if row[col_index] == future:
            new_rows.append(copy.copy(row))

    new_dataset = DataSet()
    new_dataset.headers = copy.copy(dataset.headers)
    new_dataset.rows = new_rows
    return new_dataset


def calc_attribute_info(dataset: DataSet, col_index: int):
    diff_features = []
    info = 0
    for row in dataset.rows:
        if row[col_index] not in diff_features:
            diff_features.append(row[col_index])
            subset = extract_feature(dataset, col_index, row[col_index])
            info += calc_info(subset) * (subset.get_size() / dataset.get_size())
            # print_dataset(subset)

    return {'info': info, 'features': diff_features}


def calc_info(dataset: DataSet) -> float:
    rows = dataset.rows
    class1label = rows[0][dataset.get_class_index()]
    class1count = 0
    class2count = 0

    for i in range(dataset.get_size()):
        if rows[i][dataset.get_class_index()] == class1label:
            class1count += 1
        else:
            class2count += 1

    pclass1 = class1count / dataset.get_size()
    pclass2 = class2count / dataset.get_size()

    if pclass2 == 0:
        return 0.0

    info = (-pclass1 * math.log(pclass1, 2)) + (-pclass2 * math.log(pclass2, 2))
    return info


def c45(dataset: DataSet, org_dataset_info: float,root: Tree):
    best_gain = 0.0
    best_col_index = 0
    features = []
    for col_index in range(dataset.get_width() - 1):  # ignore class attr
        res = calc_attribute_info(dataset, col_index)
        gain = org_dataset_info - res['info']
        if gain > best_gain:
            best_gain = gain
            best_col_index = col_index
            features = res['features']

    for feature in features:
        new_node = Tree()
        new_node.name = dataset.headers[best_col_index]
        new_node.value = feature

        new_subset = extract_feature(dataset,best_col_index,feature)
        new_subset = remove_attr(new_subset, best_col_index)
        info = calc_info(new_subset)
        if info == 0:
            pure_node = Tree(new_subset.headers[new_subset.get_class_index()])
            pure_node.value = new_subset.rows[0][new_subset.get_class_index()]
            new_node.add_child(pure_node)
            pure_node = None
        else:
            c45(new_subset, org_dataset_info,new_node)  # call function recursive

        root.add_child(new_node)


def print_dataset(dataset: DataSet):
    print()
    print(dataset.headers)
    for row in dataset.rows:
        print(row)


def print_tree(root: Tree):

    if root.is_pure():
        print(' THAN ' + root.name + ' ' + root.value)
    else:
        if root.name != 'root':
            print(' IF ' + root.name + ' IS ' + root.value, end='')
            print(' AND ', end='')
        for child in root.children:
            print_tree(child)


def pprint_tree(node: Tree, file=None, _prefix="", _last=True):
    print(_prefix, "`- " if _last else "|- ", node.name +' - '+node.value, sep="", file=file)
    _prefix += "   " if _last else "|  "
    child_count = len(node.children)
    for i, child in enumerate(node.children):
        _last = i == (child_count - 1)
        pprint_tree(child, file, _prefix, _last)


def main():
    data = read_data('tennis.csv')
    info = calc_info(data)
    root = Tree()
    c45(data, info,root)
    pprint_tree(root)


main()
