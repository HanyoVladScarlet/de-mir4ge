import os


P_DATASET = r'C:\Users\hanyo\Desktop\yolo-data\yolo-data\val'


def pair_check(p_dataset):
    path = os.path.join(p_dataset, 'images')
    p_images = set([p.split('.png')[0] for p in os.listdir(path)])
    path = os.path.join(p_dataset, 'labels')
    p_labels = set([p.split('.txt')[0] for p in os.listdir(path)])
    ex_images = set.difference(p_images, p_labels)
    ex_labels = set.difference(p_labels, p_images)
    return ex_images, ex_labels

def main(p_dataset):
    ex_images, ex_labels = pair_check(p_dataset)
    print(list(ex_images))
    print(list(ex_labels))
    return


if __name__ == '__main__':
    main(P_DATASET)