import pandas as pd
import mysql.connector

conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='toor',
    database='furniture_company',
    charset='utf8mb4'
)

cursor = conn.cursor()

def import_material_types(Material_type_import):

    df = pd.read_excel(Material_type_import, sheet_name='Material_type_import')
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO materials_type (material_type, loss_percentage)
            VALUES (%s, %s)
        """, (row['Тип материала'].strip(), row['Процент потерь сырья'] * 100 ))
    conn.commit()

def import_materials(Product_type_import):

    cursor.execute("SELECT id_material_type, material_type FROM Material_type_import")
    type_map = {name: mid for mid, name in cursor.fetchall()}

    df = pd.read_excel(Product_type_import, sheet_name='Product_type_import')
    df['Тип продукции'] = df['Тип продукции'].str.strip()
    df['id_product_type'] = df['Тип продукции'].map(type_map)
    df = df.rename(columns={
        'Наименование материала': 'name',
        'Цена единицы материала': 'unit_price',
        'Количество на складе': 'in_stock',
        'Минимальное количество': 'min_stock',
        'Количество в упаковке': 'pack_size',
        'Единица измерения': 'unit'
    })
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO materials
            (name, id_material_type, unit_price, in_stock, min_stock, pack_size, unit)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            row['name'], row['id_material_type'], row['unit_price'],
            row['in_stock'], row['min_stock'], row['pack_size'], row['unit']
        ))
    conn.commit()

def import_product_types(Product_type_import):
    df = pd.read_excel(Product_type_import, sheet_name='Product_type_import')
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO products_type (product_type, type_coefficient)
            VALUES (%s, %s)
        """, (row['Тип продукции'].strip(), row['Коэффициент типа продукции']))
    conn.commit()

def import_products(Products_import):
    cursor.execute("SELECT id_product_type, product_type FROM products_type")
    type_map = {name: pid for pid, name in cursor.fetchall()}

    df = pd.read_excel(Products_import, sheet_name='Products_import')
    df['id_product_type'] = df['Тип продукции'].str.strip().map(type_map)
    df = df.rename(columns={
        'Наименование продукции': 'name',
        'Артикул': 'article',
        'Минимальная стоимость для партнера': 'min_partner_price'
    })
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO products
            (id_product_type, name, article, min_partner_price)
            VALUES (%s, %s, %s, %s)
        """, (row['id_product_type'], row['name'], row['article'], row['min_partner_price']))
    conn.commit()


def import_partners(Partners_import):
    type_map = {name: pid for pid, name in cursor.fetchall()}

    df = pd.read_excel(Partners_import, sheet_name='partners_import')
    df['id_partners_type'] = df['Тип партнера'].str.strip().map(type_map)
    df = df.rename(columns={
        'Наименование партнера': 'name_partner',
        'Директор': 'director',
        'Электронная почта партнера': 'mail_partners',
        'Телефон партнера': 'phone_number',
        'Юридический адрес партнера': 'adres',
        'ИНН': 'inn',
        'Рейтинг': 'reiting'
    })
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO partners
            (id_partners_type, name_partner, director, mail_partners, phone_number, adres, inn, reiting)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (row['id_partners_type'], row['name'], row['directir'], row['mail_partners'], row['phone_number'], row['adres'], row['inn'], row['reiting']))
    conn.commit()

def import_partners_request(Partner_products_request_import):
    cursor.execute("SELECT id_products, products FROM Products_import")
    type_map = {name: pid for pid, name in cursor.fetchall()}

    df = pd.read_excel(Partner_products_request_import, sheet_name='Partners_products_request_import')
    df['id_products'] = df['Продукция'].str.strip().map(type_map)
    df = df.rename(columns={
        'Наименование партнера': 'name_partner',
        'Количество продукции': 'products_quantity',
    })
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO products
            (id_products, name_partner, products_quantity)
            VALUES (%s, %s, %s)
        """, (row['id_products'], row['name_partner'], row['products_quantity']))
    conn.commit()

import_material_types('C:\\Users\\admin\\Desktop\\№6-ДЭМ 25\\1 смена\\Прил_В3_КОД 09.02.07-2-2025-ПУ (3)\\Прил_В3_КОД 09.02.07-2-2025-ПУ\\Ресурсы\\Material_type_import.xlsx')
import_product_types('C:\\Users\\admin\\Desktop\\№6-ДЭМ 25\\1 смена\\Прил_В3_КОД 09.02.07-2-2025-ПУ (3)\\Прил_В3_КОД 09.02.07-2-2025-ПУ\\Ресурсы\\Products_type_import.xlsx')
import_products('C:\\Users\\admin\\Desktop\\№6-ДЭМ 25\\1 смена\\Прил_В3_КОД 09.02.07-2-2025-ПУ (3)\\Прил_В3_КОД 09.02.07-2-2025-ПУ\\Ресурсы\\Products_import.xlsx')
import_partners('C:\\Users\\admin\\Desktop\\№6-ДЭМ 25\\1 смена\\Прил_В3_КОД 09.02.07-2-2025-ПУ (3)\\Прил_В3_КОД 09.02.07-2-2025-ПУ\\Ресурсы\\Partners_import.xlsx')
import_partners_request('C:\\Users\\admin\\Desktop\\№6-ДЭМ 25\\1 смена\\Прил_В3_КОД 09.02.07-2-2025-ПУ (3)\\Прил_В3_КОД 09.02.07-2-2025-ПУ\\Ресурсы\\Partners_product_request_import.xlsx')
cursor.close()
conn.close()
