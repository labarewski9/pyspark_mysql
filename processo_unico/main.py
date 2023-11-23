# script_principal.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.types import StringType
from pyspark.sql import Row
# No arquivo main.py
# No arquivo main.py
from config import mysql_config_stage_compras, mysql_config_projeto_financeiro_compras
from schema import *

# Configuração do Spark

spark = SparkSession.builder.appName("LeituraMySQL").getOrCreate()

# Configuração do MySQL 

mysql_url_stage_compras = mysql_config_stage_compras["url"]
mysql_properties = {
    "user": mysql_config_stage_compras["user"],
    "password": mysql_config_stage_compras["password"],
    "driver": mysql_config_stage_compras["driver"]
}

mysql_url_projeto_financeiro_compras = mysql_config_projeto_financeiro_compras["url"]
mysql_properties = {
    "user": mysql_config_projeto_financeiro_compras["user"],
    "password": mysql_config_projeto_financeiro_compras["password"],
    "driver": mysql_config_projeto_financeiro_compras["driver"]
}

# CEP --------------------------------------------------------------------------------------------------------------------------------------------------------

tb_cep = spark.read.options(header='True', delimiter=';').schema(schemaCEP).csv('/home/labarewski/Documents/Projeto_compras/Inputs/Csv/CEP.csv')


tb_cep1 = tb_cep.withColumnRenamed("UF","UF_ENDERECO")\
    .withColumnRenamed("CIDADE","CIDADE_ENDERECO")\
    .withColumnRenamed("BAIRRO", "BAIRRO_ENDERECO")\
    .withColumnRenamed("LOGRADOURO", "NOME_ENDERECO")


tb_cep1.write \
    .format("jdbc") \
    .option("url", mysql_url_stage_compras) \
    .option("dbtable", 'CEP') \
    .option("user", mysql_properties["user"]) \
    .option("password", mysql_properties["password"]) \
    .option("driver", mysql_properties["driver"]) \
    .mode("append") \
    .save()



##  TIPO ENDERECO ---------------------------------------------------------------------------------------------------------

tb_tipo_endereco = spark.read.options(header='True', delimiter=',').schema(schemaTipoEndereco ).csv('/home/labarewski/Documents/Projeto_compras/Inputs/Csv/TIPO_ENDERECO.csv')


tb_tipo_endereco.write \
    .format("jdbc") \
    .option("url", mysql_url_projeto_financeiro_compras) \
    .option("dbtable", 'TIPO_ENDERECO') \
    .option("user", mysql_properties["user"]) \
    .option("password", mysql_properties["password"]) \
    .option("driver", mysql_properties["driver"]) \
    .mode("append") \
    .save()

## CONDICAO PAGAMENTO -----------------------------------------------------------------------------------------------------------

tb_condicao_pagamento = spark.read.options(header='True', delimiter=',').schema(schemaCondicaoPagamento).csv('/home/labarewski/Documents/Projeto_compras/Inputs/Csv/CONDICAO_PAGAMENTO.csv')


tb_condicao_pagamento.write \
    .format("jdbc") \
    .option("url", mysql_url_projeto_financeiro_compras) \
    .option("dbtable", 'CONDICAO_PAGAMENTO') \
    .option("user", mysql_properties["user"]) \
    .option("password", mysql_properties["password"]) \
    .option("driver", mysql_properties["driver"]) \
    .mode("append") \
    .save()


spark.stop()