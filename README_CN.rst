==============================
全量数据迁移_MySQL_2_PostgreSQL
==============================

支持版本: MySQL 5.x 迁移到PostgresSQL 8.2 or higher(含Greenplum Database base on PSQL) 

致谢： `py-mysql2pgsql <https://github.com/philipsoutham/py-mysql2pgsql>`_ 所有的贡献者

版本修改简述：

1. 修改对表注释和表字段注释的处理，已经支持中文注释迁移；  

2. 增加配置参数is_gpdb，设置对GPDB的特殊处理忽略（INDEXES(not PRIMARY KEY INDEXE), CONSTRAINTS, AND TRIGGERS）；

.. attention::
   README_CN.rst(本中文说明)非英文原版说明的翻译(详细请参考 `README.rst <https://github.com/philipsoutham/py-mysql2pgsql/blob/master/README.rst>`_)，只是使用简述。_


Windows环境下使用说明：
======================

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

d .其他参数配置：

  - only_tables: 指定迁移的table（换行缩进列出表名），不指定则迁移全部；
  - exclude_tables:指定排除的table，不指定则不排除；
  - supress_data: true-只迁移模式（包含表结构），默认false；
  - supress_ddl: true-只迁移数据，默认false；
  - timezone: true-转换时间，默认false；
  - index_prefix: 指定索引前缀，默认为空；
  - is_gpdb: true-GPDB的特殊性，需要忽略INDEXES(not PRIMARY KEY INDEXE), CONSTRAINTS, AND TRIGGERS，默认false；


4. 执行命令迁移数据：
--------------------

::

    > cd D:\python\py-mysql2pgsql\bin
    > python py-mysql2pgsql -v -f mysql2pgsql.yml


5. 注意：
--------

不支持MySQL空间数据类型（**Spatial Data Types**）；

由于Greenplum Database(base on PSQL)对 **UNIQUE Index** 的特殊处理，迁移unique index可能会报错。介于GPDB特殊性，迁移时建议忽略除主键外的其他约束（主键，约束和触发器）。即 *不创建任何索引的情况下测试下性能，而后再做出正确的决定。* 详情如下：

* `Greenplum Database does not allow having both PRIMARY KEY and UNIQUE constraints <https://stackoverflow.com/questions/40987460/how-should-i-deal-with-my-unique-constraints-during-my-data-migration-from-postg>`_
* `EXCERPT：CREATE_INDEX <http://gpdb.docs.pivotal.io/4320/ref_guide/sql_commands/CREATE_INDEX.html>`_

::

  In Greenplum Database, unique indexes are allowed only if the columns of the index key are the same as 
  (or a superset of) the Greenplum distribution key. On partitioned tables, a unique index is only supported
  within an individual partition - not across all partitions