from operator import itemgetter


class SQLiteTable:
    # override in the child class
    def __init__(self):
        self.db_dir = 'path'
        self.dataclass = None
        self._table_name = 'base'
        self._group_keys = {}
        self._object_keys = {}
        self._test_data = {}

    
    #------------------------------------------------------# 


    # override in the child class
    def init_db(self):
        pass


    #::::::::::::::::::::::::::::::::::::::::::::::::::::::# 


    def _dataclass_row_factory(self, cur, row):
        fields = [column[0] for column in cur.description]
        as_dict = {key: value for key, value in zip(fields, row)}

        # DEBUG LOGGING
        # print(self._table_name, 'row_factory', as_dict)
        
        return self.dataclass(**as_dict)


    def _reset_table(self):
        with sqlite3.connect(self.db_dir) as con:
            cur = con.cursor()
            sql = f'DROP TABLE {self._table_name}'
            cur.execute(sql)

        self.init_db()


    def _setup_testing_data(self):
        test_encyclopedia = []

        test_encyclopedia.append(
            [
                self.dataclass(**obj)
                for obj in self._test_data
            ]
        )

        test_encyclopedia.append({})
        for key in self._group_keys:
            flag = None

            if key == 'team_rowid':
                if self._table_name == 'games':
                    flag = (self._table_name, key)
                
            if not flag:
                options = {obj[key] for obj in self._test_data}
                results = {value: [] for value in options}

                for obj in self._test_data:
                    value = obj[key]
                    results[value].append(obj)

                test_encyclopedia[1][key] = [options, results]


            match flag:
                case ('games', 'team_rowid'):
                    options_home = {
                        obj['home_team_rowid']
                        for obj in self._test_data
                    }
                    options_away = {
                        obj['away_team_rowid']
                        for obj in self._test_data
                    }
                    options = options_home | options_away
                    results = {value: [] for value in options}
                    
                    for obj in self._test_data:
                        home = obj['home_team_rowid']
                        away = obj['away_team_rowid']
                        results[home].append(obj)
                        results[away].append(obj)

                    # DEBUG LOGGING
                    # for key, value in results.items():
                        # print('\n', key, value, sep='\n')

                    test_encyclopedia[1]['team_rowid'] = [options, results]
                    
        # DEBUG LOGGING
        # print('\n\n', self._table_name, 'table test encyclo', test_encyclopedia)

        return test_encyclopedia

    
    def _test(self, results):
        results.write(f'\ntesting {self._table_name} table')
        data = self._setup_testing_data()
        
        test_objects = data[0]

        # DEBUG LOGGING
        # for key, value in data[1].items():
            # results.write(f'\n{key}:')
            # for item in value:
                # results.write(f'\n{str(item)}')

        results.write(f'\n\ttesting {self._table_name}.add(), {self._table_name}.read_all(), {self._table_name}.read_by_rowid')
        self._test_global_funcs(results, test_objects)

        for key, func in self._group_keys.items():
            if key == 'team_rowid' and self._table_name == 'games':
                results.write(f'\n\ttesting {self._table_name}.read_by_{key}()')
                self._test_games_team_rowid(func, results, *data[1][key])
            
            else:
                results.write(f'\n\ttesting {self._table_name}.read_by_{key}()')
                self._test_group_read(func, results, *data[1][key])

        for key, func in self._object_keys.items():
            results.write(f'\n\ttesting {self._table_name}.read_by_{key}()')
            self._test_obj_read(func, results, key)


    def _test_global_funcs(self, results, test_objects):

        # DEBUG LOGGING
        # for i in self._test_data:
            # for key, value in i.items():
                # print(f'{key}: {value} ({type(value)})')
            
        for obj, data in zip(test_objects, self._test_data):
            data['rowid'] = self.add(obj)
        
        db_objs = self.read_all()
        self._compare_data(results, self._test_data, db_objs)

        self._test_obj_read(self.read_by_rowid, results, 'rowid')

    
    def _test_group_read(self, func, results, options, values):
        for value in options:
            data_list = values[value]
            db_objs = func(value)
            self._compare_data(results, data_list, db_objs)
            # DEBUG LOGGING
            # if func == self.read_by_team_rowid and self._table_name == 'games':
                # print('\n\n', data_list, '\n\n')
                # print('\n\n', db_objs, '\n\n')


    # def read_by_team_rowid(self):
        # pass


    def _test_games_team_rowid(self, func, results, options, values):
        testing_list = []
        for value in options:
            data_list = values[value]
            db_objs = func(value)

            for i, obj in enumerate(db_objs):
                db_objs[i] = obj.as_dict

            db_objs = sorted(db_objs, key=itemgetter('home_team_rowid'))

            for i, obj in enumerate(db_objs):
                db_objs[i] = self.dataclass(**obj)

        self._compare_data(results, data_list, db_objs)



    def _test_obj_read(self, func, results, key):
        for obj in self._test_data:
            response = func(obj[key]).as_dict
            self._compare_items(results, obj, response)


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


###############################################################################
