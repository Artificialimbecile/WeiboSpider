import networkx as nx
from weibo_follow import Follow
import matplotlib.pyplot as plt


def write_network(user_id, cookie, file_path):
    # 将爬取的关注列表写入network.txt
    fw = Follow(user_id, cookie)    # 调用Weibo类，创建微博实例wb
    fw.get_follow_list()            # 获取关注列表的uid和昵称
    print(fw.follow_list)           # 输出关注列表的uid
    print(fw.follow_name_list)      # 输出关注列表的昵称
    f = open(file_path, 'a')
    f.writelines(' '.join(fw.follow_name_list)+'\n')
    f.close()

    for i in range(1, len(fw.follow_list)):     # 获取关注列表的关注列表
        new_fw = Follow(int(fw.follow_list[i]), cookie)
        new_fw.get_follow_list()
        print(new_fw.follow_list)               # 输出关注列表的uid
        print(new_fw.follow_name_list)          # 输出关注列表的昵称
        f = open(file_path, 'a')
        f.writelines(' '.join(new_fw.follow_name_list) + '\n')
        f.close()


def draw_graph(file_path):
    # 绘制关系网
    G = nx.Graph()
    new_G = nx.Graph()
    f = open(file_path, 'r')
    lines = f.readlines()
    for line in lines:
        name_list = line[:-1].split(' ')
        print(name_list)
        for i in range(1, len(name_list)):
            G.add_edge(name_list[0], name_list[i])
            new_G.add_edge(name_list[0], name_list[i])

    for node in G.nodes:        # 删除没有共同关注的微博昵称
        if len(G[node]) == 1:
            new_G.remove_node(node)

    nx.draw(new_G, node_color='w', with_labels=True, font_size=7, node_size=2000)
    plt.rcParams['font.sans-serif'] = ['SimHei']    # 节点显示中文
    plt.rcParams['font.family'] = 'sans-serif'
    plt.show()


def main():
    user_id = int('Your id')  # 你的的user_id
    cookie = {'Cookie': 'Your cookie'}
    file_path = 'network.txt'
    write_network(user_id, cookie, file_path)
    draw_graph(file_path)


if __name__ == '__main__':
    main()
