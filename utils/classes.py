from dataclasses import dataclass


###############################################################################


class SQLiteTable:
    # override in the child class
    def __init__(self):
        self._table_name = 'base'
        self._dataclass = BaseDataClass

    
    #------------------------------------------------------# 


    # override in the child class
    def init_db(self):
        pass


    #::::::::::::::::::::::::::::::::::::::::::::::::::::::# 


    def _dataclass_row_factory(self, cur, row):
        fields = [column[0] for column in cur.description]
        as_dict = {key: value for key, value in zip(fields, row)}
        return self._dataclass(**as_dict)


    def _reset_table(self):
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            sql = f'DROP TABLE {self._table_name}'
            cur.execute(sql)

        self.init_db()


    def _compare_data(self, results, data_list, objects_list):
        for i, tup in enumerate(zip(data_list, objects_list)):
            data, obj = tup
            obj = obj.as_dict
            self._compare_items(results, data, obj, i)


    @staticmethod
    def _compare_items(results, data, obj, i=None):
        for key, value in data.items():
            if value != obj[key]:
                error_message = f'''
                    (~)ERROR in test object {i}: key {key}
                        (~~)request value: {value}
                        (~~)type: {type(value)}
                        (~~)object value: {obj[key]}
                        (~~)type: {type(obj[key])}
                '''
                error_message =error_message.replace("    ", "")
                error_message = error_message.replace("(~)", "\t\t")
                error_message = error_message.replace("(~~)", "\t\t\t")
                results.write(error_message)


#-----------------------------------------------------------------------------#


@dataclass(slots=True)
class BaseDataClass:
    members: None


###############################################################################
