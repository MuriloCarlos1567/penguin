class Tundra:
    def __init__(self, adapter, **kwargs):
        self.adapter = adapter
        if self.adapter == 'mysql':
            import pymysql
            self.connection = pymysql.connect(**kwargs)
        elif self.adapter == 'postgresql':
            import psycopg2
            self.connection = psycopg2.connect(**kwargs)
        else:
            raise ValueError(f"Database '{self.adapter}' not supported.")

    def row_lock_query(self, table_name, condition, update_values):
        try:
            with self.connection.cursor() as cursor:
                cursor.execute('BEGIN TRANSACTION;')
                select_query = f'SELECT * FROM {table_name} WHERE {condition} FOR UPDATE;'

                cursor.execute(select_query)
                row_to_update = cursor.fetchone()

                if row_to_update:
                    update_query = f'UPDATE {table_name} SET {", ".join(f"{col} = %s" for col in update_values.keys())} WHERE {condition};'
                    update_params = tuple(update_values.values())
                    cursor.execute(update_query, update_params)

                    self.connection.commit()
                    print("Transação confirmada.")
                else:
                    print("Nenhuma linha encontrada para atualização.")

        except Exception as e:
            self.connection.rollback()
            print(f"Erro: {str(e)}")
        finally:
            self.connection.close()
