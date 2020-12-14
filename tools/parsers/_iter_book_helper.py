#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'ipetrash'


from itertools import tee

# import matplotlib.pyplot as plt
import networkx as nx

from bot.book_helper import BookHelper
from config import DIR_BOOKS

# from parsers.generate_graph_html import generate

# G = nx.DiGraph()
#
# G.add_edge('3', '4')
# G.add_edge('4', '5')
# G.add_edge('3', '8')
# G.add_edge('8', '5')
#
# for paths in nx.all_simple_paths(G, '3', '5'):
#     print(paths)
#
# quit()


for file_name in DIR_BOOKS.rglob('book.json'):
    book = BookHelper.from_file(file_name)

    if book.title != 'Берегись Лиловой Пасты!':
        continue

    # print(book)
    # print(book.title)
    # print(book.sections)
    # print(book.end_pages)
    # print(book.total_pages)
    # print()
    # print(book.G)

    # print(repr(book.title_html))
    # print(book.title_html)

    cycles = list(nx.simple_cycles(book.G))
    print(cycles)

    # print(nx.recursive_simple_cycles(book.G))
    cycles_nodes = {item for sublist in cycles for item in sublist}
    # print(cycles_nodes)

    # Попробуем определить какие страницы в цикле шли раньше других, чтобы
    # правильно удалить зациклинность
    for edge in cycles:
        new_edge = None
        node_1, node_2 = edge

        for paths in nx.all_simple_paths(book.G, book.first_page, node_1):
            if node_2 not in paths:
                new_edge = node_2, node_1
                break

        for paths in nx.all_simple_paths(book.G, book.first_page, node_2):
            if node_1 not in paths:
                new_edge = node_1, node_2
                break

        if new_edge:
            book.G.remove_edge(*new_edge)
    quit()
    #
    # print(len(book.G.edges), [edge for edge in book.G.edges if edge[0] in cycles_nodes or edge[1] in cycles_nodes])
    # book.G.remove_edges_from(cycles)
    # print(len(book.G.edges), [edge for edge in book.G.edges if edge[0] in cycles_nodes or edge[1] in cycles_nodes])
    #
    # print(list(nx.simple_cycles(book.G)))

    # for paths in nx.all_simple_paths(book.G, '3', '13'):
    #     print(paths)
    #     print(list(pairwise(paths)))
    #
    #     print()

    # visited_pages = []
    # print(book.check_path('3', visited_pages))

    # for end_page in book.end_pages:
    #     for paths in nx.all_simple_paths(book.G, book.first_page, end_page):
    #         print(end_page, paths)

    print()

    # links = []
    # for page, section in book.sections.items():
    #     for to_page in section['transitions']:
    #         links.append((page, to_page))
    # generate('1.html', links)

    # G = nx.DiGraph()
    #
    # for page, section in book.sections.items():
    #     for to_page in section['transitions']:
    #         G.add_edge(page, to_page)
    #
    # pos = nx.spring_layout(G)  # positions for all nodes
    # nx.draw_networkx_nodes(G, pos)
    # nx.draw_networkx_edges(G, pos, edgelist=G.edges())
    # nx.draw_networkx_labels(G, pos)
    # # nx.draw_networkx_nodes(G, pos, node_size=700)
    # # nx.draw_networkx_edges(G, pos, edgelist=G.edges(), width=6)
    # # nx.draw_networkx_labels(G, pos, font_size=20, font_family='sans-serif')
    #
    # plt.axis('off')
    # # plt.savefig("custom_graph.png")  # save as png
    # plt.show()  # display

    break
