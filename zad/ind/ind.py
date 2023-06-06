#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import json
import os
import sqlite3


def create_tables(conn):
    """
    Создает таблицы в базе данных, если они еще не существуют
    """
    cursor = conn.cursor()
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS shops (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            UNIQUE(name)
        )
        '''
    )
    cursor.execute(
        '''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shop_id INTEGER,
            product TEXT,
            price INTEGER,
            FOREIGN KEY (shop_id) REFERENCES shops (id)
        )
        '''
    )
    conn.commit()


def get_shop(conn, name, product, price):
    """
    Добавляет информацию о магазине и товаре в базу данных
    """
    cursor = conn.cursor()
    cursor.execute(
        '''
        INSERT INTO shops (name) VALUES (?)
        ON CONFLICT(name) DO NOTHING
        ''',
        (name,)
    )
    cursor.execute(
        '''
        SELECT id FROM shops WHERE name=?
        ''',
        (name,)
    )
    shop_id = cursor.fetchone()[0]
    cursor.execute(
        '''
        INSERT INTO products (shop_id, product, price) VALUES (?, ?, ?)
        ''',
        (shop_id, product, price)
    )
    conn.commit()


def display_shops(conn):
    """
    Отображает данные о магазинах и товарах в виде таблицы
    """
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT s.name, p.product, p.price FROM shops AS s
        JOIN products AS p ON s.id = p.shop_id
        ORDER BY s.name
        '''
    )
    rows = cursor.fetchall()
    if rows:
        line = '+-{}-+-{}-+-{}-+'.format(
            '-' * 30,
            '-' * 20,
            '-' * 8
        )
        print(line)
        print(
            '| {:^30} | {:^20} | {:^8} |'.format(
                "Название",
                "Товар",
                "Цена"
            )
        )
        print(line)
        for row in rows:
            print(
                '| {:<30} | {:<20} | {:>8} |'.format(
                    row[0],
                    row[1],
                    row[2]
                )
            )
        print(line)


def select_shops(conn, name):
    """
    По заданному магазину находит товары, находящиеся в нем,
    если магазина нет - показывает соответствующее сообщение
    """
    cursor = conn.cursor()
    cursor.execute(
        '''
        SELECT s.name, p.product, p.price FROM shops AS s
        JOIN products AS p ON s.id = p.shop_id
        WHERE s.name=?
        ''',
        (name,)
    )
    rows = cursor.fetchall()
    if rows:
        line = '+-{}-+-{}-+-{}-+'.format(
            '-' * 30,
            '-' * 20,
            '-' * 8
        )
        print(line)
        print(
            '| {:^30} | {:^20} | {:^8} |'.format(
                "Название",
                "Товар",
                "Цена"
            )
        )
        print(line)
        for row in rows:
            print(
                '| {:<30} | {:<20} | {:>8} |'.format(
                    row[0],
                    row[1],
                    row[2]
                )
            )
        print(line)
    else:
        print("Такого магазина нет")


def main(command_line=None):
    """
    Главная функция программы
    """
    # Создать родительский парсер для определения имени файла.
    file_parser = argparse.ArgumentParser(add_help=False)
    file_parser.add_argument(
        "--filename",
        action="store",
        required=True,
        help="The data file name"
    )
    # Создать основной парсер командной строки.
    parser = argparse.ArgumentParser("shops")
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )
    subparsers = parser.add_subparsers(dest="command")
    # Создать субпарсер для добавления магазина.
    add = subparsers.add_parser(
        "add",
        parents=[file_parser],
        help="Add a new product"
    )
    add.add_argument(
        "-n",
        "--name",
        action="store",
        required=True,
        help="The shop's name"
    )
    add.add_argument(
        "-p",
        "--product",
        action="store",
        help="The shop's product"
    )
    add.add_argument(
        "-pr",
        "--price",
        action="store",
        type=int,
        required=True,
        help="The price of product"
    )
    display = subparsers.add_parser(
        "display",
        parents=[file_parser],
        help="Display all products"
    )
    # Создать субпарсер для выбора магазина.
    select = subparsers.add_parser(
        "select",
        parents=[file_parser],
        help="Select the shops"
    )
    select.add_argument(
        "-s",
        "--selected_shop",
        required=True,
        help="The selected shop name"
    )

    args = parser.parse_args(command_line)

    conn = sqlite3.connect(args.filename)
    create_tables(conn)

    if args.command == "add":
        get_shop(
            conn,
            args.name,
            args.product,
            args.price
        )
    elif args.command == 'display':
        display_shops(conn)
    elif args.command == 'select':
        select_shops(conn, args.selected_shop)

    conn.close()


if __name__ == '__main__':
    main()
