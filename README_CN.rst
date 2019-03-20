==============================
全量数据迁移_MySQL_2_PostgreSQL
==============================

支持版本: MySQL 5.x 迁移到PostgresSQL 8.2 or higher(含Greenplum Database base on PSQL) 

致谢： `py-mysql2pgsql <https://github.com/philipsoutham/py-mysql2pgsql>`_ 所有的贡献者

版本修改简述：

1. 修改对表注释和表字段注释的处理，已经支持中文注释迁移；  

2. 增加配置参数is_gpdb，设置对GPDB的特殊处理忽略（INDEXES(not PRIMARY KEY INDEXE), CONSTRAINTS, AND TRIGGERS）；

3. 增加配置参数destination.postgres.sameschame，设置导入GPDB的schema与mysql.database设置相同（需提前创建）；

4. 增加配置参数mysql.getdbinfo，如果为true，则只读取MySQL的数据库统计信息，不执行数据迁移操作；

5. 修改逻辑为单独处理comment，增加try/exception/else防止execute()异常导致后续脚本执行被终止；

6. 优化脚本文件输出(通过destination.file指定)：表名和字段去除双引号(不带双引号，会自动转换为小写)及转换为小写，脚本名称和格式；

.. attention::
   README_CN.rst(本中文说明)非英文原版说明的翻译(详细请参考 README.rst)，只是使用简述。_


Linux环境下安装说明：见README.rst
====================

Windows环境下安装和使用说明：
============================

1. 安装Python 2.7 和如下依赖：
-----------------------------

* `psycopg2 for Windows <http://www.stickpeople.com/projects/python/win-psycopg/>`_
* `MySQL-python for Windows <http://www.codegood.com/archives/129>`_


2. clone代码到本地，比如D:\python\py-mysql2pgsql，执行如下命令安装和测试：
-------------------------------------------------------------------------

::

    > cd D:\python\py-mysql2pgsql
    > python setup.py install
    > cd D:\python\py-mysql2pgsql\bin
    > python py-mysql2pgsql -h


3. 参照说明编写'.yml'文件，或者直接执行[4.]命令，如指定文件不存在则可创建指定名字的初始化配置文件，再作修改；
--------------------------------------------------------------------------------------------------

a .执行命令创建指定名字的初始化配置文件:
::

     bin> python py-mysql2pgsql -v -f mysql2pgsql.yml
     No configuration file found.
     A new file has been initialized at: mysql2pgsql.yml
     Please review the configuration and retry...

b .由于数据库结构差异：MySQL（**database**->table）与PostgreSQL（**database->schema**->table），配置database字段时，PostgreSQL需要通过 **冒号** 指定schema（**database:schema**），否则会迁移到public模式下；

c .迁移前需要在新库（PostgreSQL）创建冒号指定的模式（schema），否则会报不存在；

d .读取MySQL表结构，当注释有乱码时，可能导致报错，需要将报错的表注释更新正确，然后再迁移数据；

e .其他参数配置：

  - destination.file: 指定输出的postgres脚本文件，如设置则只生成脚本，不执行数据迁移操作；
  - destination.postgres.sameschame: true-导入GPDB的schema指定为mysql.database；
  - mysql.getdbinfo: true-只读取MySQL的数据库统计信息，不执行数据迁移操作；
  - only_tables: 指定迁移的table（必须换行减号加空格缩进列出表名），不指定则迁移全部；
  - exclude_tables:指定排除的table(必须换行减号加空格缩进列出表名)，不指定则不排除；
  - supress_data: true-只迁移模式（包含表结构），默认false；
  - supress_ddl: true-只迁移数据，默认false；如果只全量同步数据，同时force_truncate也应该需要为true；
  - force_truncate: true-迁移数据前，对目标表执行truncate操作，默认false；
  - timezone: true-转换时间，默认false；
  - index_prefix: 指定索引前缀，默认为空；
  - is_gpdb: true-GPDB的特殊性，需要忽略INDEXES(not PRIMARY KEY INDEXE), CONSTRAINTS, AND TRIGGERS，默认false；

f .使用drop+data(即supress_data: false;supress_ddl: false;)，会删除引用的视图：

  如不删除视图，则考虑使用其他方式处理【表结构变化】，然后使用truncate+only data同步数据；  

g .使用truncate+only data(即force_truncate: true;supress_ddl: true;)，可能会报错(如下)：**事务提交逻辑更新(见 postgres_writer.py 函数 execute)**  

  File "/usr/lib/python2.7/site-packages/py_mysql2pgsql-0.1.6-py2.7.egg/mysql2pgsql/lib/postgres_db_writer.py", line 216, in write_contents
    self.copy_from(f, '"%s"' % table.name, ['"%s"' % c['name'] for c in table.columns])
  File "/usr/lib/python2.7/site-packages/py_mysql2pgsql-0.1.6-py2.7.egg/mysql2pgsql/lib/postgres_db_writer.py", line 121, in copy_from
    columns=columns
  psycopg2.InternalError: current transaction is aborted, commands ignored until end of transaction block

4. 执行命令迁移数据：
--------------------

::

    > cd D:\python\py-mysql2pgsql\bin
    > python py-mysql2pgsql -v -f mysql2pgsql.yml

5. 数据库统计信息说明（输出到文件：_database_sync_info.txt）：
--------

::

    > ########################################
    > ##TOTAL Database Rows:[迁移的总数据量]##
    > ########################################
    > ##Process Time:迁移数据执行时间 s.##
    > 
    > DATABASE SATISTICS INFO:
    > 数据库名(或模式):单个库总数据量|TOTAL
    >     表名:单个表数据量
    > 
    > test_db:8|TOTAL
    >     test_inc:6
    >     test_primary_error:2
    > 
    > INDEXES, CONSTRAINTS, AND TRIGGERS DETAIL:
    > 导入数据库名:导入模式名
    >     操作信息(create/ignore): 表名|字段名(备注信息)
    > 
    > mydb:test_db
    >     create index: test_inc|id|PRIMARY
    >     create index: test_primary_error|code|PRIMARY
    >     ignore index: test_primary_error|code

6. 注意：
--------

* 不支持MySQL空间数据类型（**Spatial Data Types**）；

* 由于Greenplum Database(base on PSQL)对 **UNIQUE Index** 的特殊处理，迁移unique index可能会报错。介于GPDB特殊性，迁移时建议忽略除主键外的其他约束（主键，约束和触发器）。即 *不创建任何索引的情况下测试下性能，而后再做出正确的决定。* 详情如下：

  * `Greenplum Database does not allow having both PRIMARY KEY and UNIQUE constraints <https://stackoverflow.com/questions/40987460/how-should-i-deal-with-my-unique-constraints-during-my-data-migration-from-postg>`_
  * `EXCERPT：CREATE_INDEX <http://gpdb.docs.pivotal.io/4320/ref_guide/sql_commands/CREATE_INDEX.html>`_

::

  In Greenplum Database, unique indexes are allowed only if the columns of the index key are the same as 
  (or a superset of) the Greenplum distribution key. On partitioned tables, a unique index is only supported
  within an individual partition - not across all partitions

* **SHOW TABLE STATUS;** 结果说明：Rows-行数：对于非事务性表（如MyISAM），这个值是精确的；但对于事务性引擎（如InnoDB），这个值通常是估算的，与实际值相差可达40到50％。对于INFORMATION_SCHEMA中的表，Rows值为NULL。所以替换方案是使用 **SELECT COUNT(\*)** 获取准确的数据。详情如下：

  * `why-is-innodbs-show-table-status-so-unreliable <https://stackoverflow.com/questions/8624408/why-is-innodbs-show-table-status-so-unreliable>`_
  * `EXCERPT：INNODB-RESTRICTIONS <https://dev.mysql.com/doc/refman/5.7/en/innodb-restrictions.html>`_

::

  The official MySQL 5.1 documentation acknowledges that InnoDB does not give accurate statistics with SHOW 
    TABLE STATUS. Whereas MYISAM tables specifically keep an internal cache of meta-data such as number of rows
    etc, the InnoDB engine stores both table data and indexes in */var/lib/mysql/ibdata**

  Inconsistent table row numbers are reported by SHOW TABLE STATUS because InnoDB dynamically estimates the 
    'Rows' value by sampling a range of the table data (in */var/lib/mysql/ibdata**) and then extrapolates the
    approximate number of rows.So much so that the InnoDB documentation acknowledges row number inaccuracy of 
    up to 50% when using SHOW TABLE STATUS.
  So use SELECT COUNT(*) FROM TABLE_NAME.