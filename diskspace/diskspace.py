#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import os
import subprocess
import re


# ==== Arguments ====

parser = argparse.ArgumentParser(
    description='Analizes and reports the disk usage per folder'
)
parser.add_argument('directory', metavar='DIR', type=str, nargs='?',
                    default='.', help='Directory to be analized')
parser.add_argument('-o', '--order', type=str, default='desc',
                    choices=['desc', 'asc'],
                    help='The file order inside each folder')
parser.add_argument('-s', '--hide', type=int, default=0,
                    help='Hides all files that have a percentage lower than '
                         'this value')
group = parser.add_mutually_exclusive_group()
group.add_argument('-a', '--all', help='Shows the full tree',
                   action='store_true')
group.add_argument('-d', '--depth',
                   help='Specifies the folder maximum depth to be analyzed',
                   type=int, default=1)
parser.add_argument('-t', '--tree-view', action='store_true',
                    help='Display the result in a tree mode')

args = parser.parse_args()


# ==== Disk Space ====

def subprocess_check_output(command):
    return subprocess.check_output(command.strip().split(' '))


def bytes_to_readable(blocks):
    byts = blocks * 512
    readable_bytes = byts
    count = 0
    while readable_bytes / 1024:
        readable_bytes /= 1024
        count += 1

    labels = ['B', 'Kb', 'Mb', 'Gb', 'Tb']
    return '{:.2f}{}'.format(round(byts/(1024.0**count), 2), labels[count])

def print_tree(file_tree, file_tree_node, path, largest_size, total_size,
               depth=0):
    percentage = int(file_tree_node['size'] / float(total_size) * 100)

    if percentage < args.hide:
        return

    print('{:>{}s} {:>4d}%  '.format(file_tree_node['print_size'],
                                     largest_size, percentage), end='')
    if args.tree_view:
        print('{}{}'.format('   '*depth, os.path.basename(path)))
    else:
        print(path)

    if len(file_tree_node['children']) != 0:
        for child in file_tree_node['children']:
            print_tree(file_tree, file_tree[child], child, largest_size,
                       total_size, depth + 1)


def show_space_list(directory='.', depth=-1, order=True):
    abs_directory = os.path.abspath(directory)

    cmd = 'du '
    if depth != -1:
        cmd += '-d {} '.format(depth)

    cmd += abs_directory
    raw_output = subprocess_check_output(cmd)

    total_size = -1
    line_regex = r'(\d+)\s+([^\s]*|\D*)'

    file_tree = {}
    for line in re.findall(line_regex, raw_output.strip(), re.MULTILINE):
        file_path = line[-1]
        dir_path = os.path.dirname(file_path)

        file_size = int(line[0])

        if file_path == abs_directory:
            total_size = file_size

            if file_path in file_tree:
                file_tree[file_path]['size'] = file_size
            else:
                file_tree[file_path] = {
                    'children': [],
                    'size': file_size,
                }

            continue

        if file_path not in file_tree:
            file_tree[file_path] = {
                'children': [],
                'size': file_size,
            }

        if dir_path not in file_tree:
            file_tree[dir_path] = {
                'children': [],
                'size': 0,
            }

        file_tree[dir_path]['children'].append(file_path)
        file_tree[file_path]['size'] = file_size

    largest_size = 0
    for file_path in file_tree:
        file_tree_entry = file_tree[file_path]
        file_tree_entry['children'] = sorted(
            file_tree_entry['children'],
            key=lambda v: file_tree[v]['size'],
            reverse=order
        )

        file_tree_entry['print_size'] = bytes_to_readable(
            file_tree_entry['size']
        )
        largest_size = max(largest_size, len(file_tree_entry['print_size']))

    print(' ' * max(0, largest_size - len('Size')) + 'Size   (%)  File')
    print_tree(file_tree, file_tree[abs_directory], abs_directory,
               largest_size, total_size)


def main():
    if not args.all:
        show_space_list(args.directory, args.depth,
                        order=(args.order == 'desc'))
    else:
        show_space_list(args.directory, order=(args.order == 'desc'))

if __name__ == '__main__':
    main()
