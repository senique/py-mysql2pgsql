from __future__ import absolute_import

import codecs
import time
import os

from .lib import print_red
from .lib.mysql_reader import MysqlReader
from .lib.postgres_file_writer import PostgresFileWriter
from .lib.postgres_db_writer import PostgresDbWriter
from .lib.converter import Converter
from .lib.config import Config
from .lib.errors import ConfigurationFileInitialized


class Mysql2Pgsql(object):
    def __init__(self, options):
        self.run_options = options
        self.total_rows = 0
        self.satistics_info = ""
        self.log_detail = ""
        self.execute_error_log = ""
        self.log_head = "##########################%s\n##TOTAL Database Rows:[%s]##\n%s##########################"
        try:
            self.file_options = Config(options.file, True).options
        except ConfigurationFileInitialized, e:
            print_red(e.message)
            raise e

    def convert(self):
        postgres_options = self.file_options['destination']['postgres']
        postgres_database = postgres_options['database']
        if not ':' in str(postgres_database):
            print("\nIMPORT DESTINATION:%s:public\n"%(postgres_options['database']))
        else:
            postgres_database = postgres_database.split(':')[0]

        start_time = time.time()
        get_dbinfo = self.file_options['mysql']['getdbinfo']
        same_schame = postgres_options['sameschame']
        for database in self.file_options['mysql']['database'].split(','):
            self.file_options['mysql']['database'] = database
            if same_schame:
                self.file_options['destination']['postgres']['database'] = postgres_database+':'+database

            if get_dbinfo:
                self.getMysqlReader()
            else:
                self.convert_db()
        end_time = time.time()

        """DATABASE SATISTICS INFO OUTPUT INTO FILE [START]"""
        pound_sign = '#'*len(str(self.total_rows))

        path_log_file = os.getcwd()+os.sep+"%s_database_sync_info.txt"%(self._get_time_str())
        print('DATABASE SATISTICS INFO OUTPUT INTO: \n%s\n'%(path_log_file))
        logFile = self._get_file(path_log_file)

        logFile.write(self.log_head%(pound_sign,str(self.total_rows),pound_sign))
        logFile.write("\n##Process Time:%s s.##"%(round(end_time-start_time, 2)))
        logFile.write('\n\nDATABASE SATISTICS INFO:'+self.satistics_info)
        if not get_dbinfo:
            logFile.write('\nINDEXES, CONSTRAINTS, AND TRIGGERS DETAIL:'+self.log_detail)

        if self.execute_error_log:
            print("\nPOSTGRES EXECUTE ERROR LOG: \n"+self.execute_error_log)
        else:
            print("POSTGRES EXECUTE ERROR LOG: OH YEAH~ NO ERRORS!")

        logFile.close()
        """DATABASE SATISTICS INFO OUTPUT INTO FILE [FINISH]"""

    def getMysqlReader(self):
        reader = MysqlReader(self.file_options['mysql'])

        """"Deal data satistics info:"""
        satistics_rows_info = "\n"+self.file_options['mysql'].get('database')+":%s|TOTAL\n"
        total_rows = 0
        for table in reader.tables:
            total_rows += table.rows
            satistics_rows_info += '    '+table.name+":%s\n"%(table.rows)
        self.satistics_info += satistics_rows_info%(total_rows)
        self.total_rows += total_rows

        return reader

    def convert_db(self):
        reader = self.getMysqlReader()

        if self.file_options['destination']['file']:
            filename = self.file_options['destination']['file']
            if filename.endswith('.sql'):
                filename = filename[0:-4]+'-'+reader.db.options['db']+'.sql'
            else:
                filename += '-'+reader.db.options['db']+'.sql'

            writer = PostgresFileWriter(self._get_file(filename), 
                                        self.run_options.verbose, 
                                        self.file_options,
                                        tz=self.file_options.get('timezone'))
        else:
            writer = PostgresDbWriter(self.file_options['destination']['postgres'], 
                                      self.run_options.verbose, 
                                      self.file_options,
                                      tz=self.file_options.get('timezone'))

        Converter(reader, writer, self.file_options, self.run_options.verbose).convert()
        self.log_detail += writer.log_detail
        
        if not self.file_options['destination']['file']:
            self.execute_error_log += writer.execute_error_log
        else:
            print('SQLs SCRIPTS OUTPUT INTO: \n%s\%s\n'%(os.getcwd(),filename))

    def _get_file(self, file_path):
        return codecs.open(file_path, 'wb', 'utf-8')

    def _get_time_str(self):
        now = int(time.time()) 
        timeStruct = time.localtime(now) 
        strTime = time.strftime("%Y-%m-%d_%H%M%S", timeStruct) 
        return strTime
