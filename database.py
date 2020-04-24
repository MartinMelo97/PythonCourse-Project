import sqlite3

class Database:

    def __init__(self):
        self.conn = self.create_connection()
        self.create_tables(self.conn)
        self.tables = self.get_table_dict()

    # Validations

    def validate_not_error(self, value):
        return not isinstance(value, dict) or not 'error' in value

    def validate_get_all_result(self, rows):
        return len(rows) > 0

    def validate_get_one_result(self, row):
        return row is not None

    def validate_create_update_result(self, value):
        return value is not None and value > 0

    def validate_table_exist(self, table_name):
        return table_name in self.get_tables_names()

    def validate_column_exist(self, columns, column_name):
        return column_name in columns

    # Getters

    def get_tables_names(self):
        return [key for key, value in self.tables.items()]

    def get_table_columns(self, table_name):
        if self.validate_table_exist(table_name):
            return self.tables[table_name]
        return {
            'error': True,
            'message': 'No existe la tabla especificada en la base de datos'
        }

    def get_columns_by_table(self, table_name):
        table = self.get_table_columns(table_name)
        if self.validate_not_error(table):
            return [key for key, value in table.items()]
        return table

    def get_value_from_column(self, table_name, column_name):
        columns = self.get_table_columns(table_name)
        if self.validate_not_error(columns):
            if self.validate_column_exist(columns, column_name):
                return columns[column_name]
            return {
                'error': True,
                'message': f'No existe la columna {column_name} en la tabla {table_name}'
            }
        return columns

    def get_all(self, table_name):
        table_columns = self.get_columns_by_table(table_name)
        if self.validate_not_error(table_columns):
            sql = f'''
                SELECT
                    {','.join(table_columns)}
                FROM
                    {table_name}
            '''
            cursor = self.conn.execute(sql)
            return cursor.fetchall()
        return {
            'error': True,
            'message': f'Algo falló al intentar traer la lista de {table_name}'
        }

    def get_one(self, table_name, value, column_name='rowid'):
        table_columns = self.get_columns_by_table(table_name)
        column = self.get_value_from_column(table_name, column_name)
        if self.validate_not_error(table_columns) and self.validate_not_error(column):
            sql = f'''
                SELECT
                    {','.join(table_columns)}
                FROM
                    {table_name}
                WHERE
                    {column} = ?
            '''
            values = (value,)
            cursor = self.conn.execute(sql, values)
            return cursor.fetchone()
        return {
            'error': True,
            'message': f'Algo falló al traer al {table_name} con el {value} {id}'
        }

    def create(self, table_name, data):
        table_columns = self.get_columns_by_table(table_name)
        if self.validate_not_error(table_columns):
            del table_columns[0]
            del table_columns[-1]
            sql = f'''
                INSERT INTO {table_name} (
                    {','. join(table_columns)}
                ) VALUES (
                        {','.join(["?" for i in range(len(table_columns))])}
                )
            '''
            cursor = self.conn.cursor()
            cursor.execute(sql, data)
            self.conn.commit()
            return cursor.lastrowid
        return {
            'error': True,
            'message': f'Algo falló al tratar de crear un {table_name}'
        }

    def update(self, table_name, column_name, value, id):
        column = self.get_value_from_column(table_name, column_name)
        id_column = self.get_value_from_column(table_name, 'rowid')
        if self.validate_not_error(column):
            sql = f'''
                UPDATE
                    {table_name}
                SET
                    {column} = ?
                WHERE
                    {id_column} = ?
            '''
            data = (value, id)
            cursor = self.conn.cursor()
            cursor.execute(sql, data)
            self.conn.commit()
            return cursor.rowcount
        return {
            'error': True,
            'message': f'Algo falló al traer de editar el {table_name} con el ID {id}'
        }

    def delete(self, table_name, id):
        id_column = self.get_value_from_column(table_name, 'rowid')
        if self.validate_not_error(id_column):
            sql = f'''
                DELETE FROM
                    {table_name}
                WHERE
                    {id_column} = ?
            '''
            data = (id,)
            self.conn.execute(sql, data)
            self.conn.commit()
            return f'{table_name} con el ID: {id} fue eliminado con éxito'
        return {
            'error': True,
            'message': f'Algo falló al tratar de eliminar {table_name} con el ID {id}'
        }

    # Database methods
    def create_connection(self):
        print("Database connected")
        return sqlite3.connect('restaurant.db')

    def create_tables(self, conn):
        user_create_table_sql = '''
            CREATE TABLE IF NOT EXISTS user (
                first_name VARCHAR NOT NULL,
                last_name VARCHAR NOT NULL,
                email VARCHAR NOT NULL UNIQUE,
                phone VARCHAR NOT NULL,
                password VARCHAR NOT NULL,
                is_logged INT NOT NULL DEFAULT 0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        '''

        dish_create_table_sql = '''
            CREATE TABLE IF NOT EXISTS dish (
                name VARCHAR NOT NULL,
                description TEXT NOT NULL,
                price DOUBLE NOT NULL DEFAULT 0,
                ingredients TEXT NULL,
                preparation_time INT NOT NULL DEFAULT 1,
                is_available INT NOT NULL DEFAULT 1,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        '''

        order_create_table_sql = '''
            CREATE TABLE IF NOT EXISTS order_ (
                user_id INT NOT NULL,
                notes TEXT NULL,
                preparation_time INT NOT NULL,
                total DOUBLE NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user (rowid)
            )
        '''

        order_dish_create_table_sql = '''
            CREATE TABLE IF NOT EXISTS order_dish (
                order_id INT NOT NULL,
                dish_id INT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (order_id) REFERENCES order_ (rowid),
                FOREIGN KEY (dish_id) REFERENCES dish (rowid)
            )
        '''

        conn.execute(user_create_table_sql)
        print('User table created')
        conn.execute(dish_create_table_sql)
        print('Dish table created')
        conn.execute(order_create_table_sql)
        print('Order table created')
        conn.execute(order_dish_create_table_sql)
        print('Order-Dish table created')

    # Database tables and columns structure
    def get_table_dict(self):
        tables = {
            'user': {
                'rowid': 'rowid',
                'first_name': 'first_name',
                'last_name': 'last_name',
                'email': 'email',
                'phone': 'phone',
                'password': 'password',
                'is_logged': 'is_logged'
            },
            'dish': {
                'rowid': 'rowid',
                'name': 'name',
                'description': 'description',
                'price': 'price',
                'ingredients': 'ingredients',
                'preparation_time': 'preparation_time',
                'is_available': 'is_available'
            },
            'order': {
                'rowid': 'rowid',
                'user_id': 'user_id',
                'notes': 'notes',
                'preparation_time': 'preparation_time',
                'total': 'total'
            },
            'order_dish': {
                'rowid': 'rowid',
                'order_id': 'order_id',
                'dish_id': 'dish_id'
            }
        }
        return tables