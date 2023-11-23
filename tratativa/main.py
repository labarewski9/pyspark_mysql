# script_principal.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, trim,lit, upper
from pyspark.sql.types import StringType
from pyspark.sql import Row

# No arquivo main.py
# No arquivo main.py
from config import mysql_config_stage_compras, mysql_config_projeto_financeiro_compras
from schema import *
from fug import cnpj_valido

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

# COMPRAS --------------------------------------------------------------------------------------------------------------------------------------------------------

tb_compras = spark.read.options(header='True', delimiter=',').schema(schemaCompras).csv('/home/labarewski/Documents/pyspark_mysql/compras_teste_13_11.csv')

# Gravando a tabela compras no banco 
'''
tb_compras.write \
    .format("jdbc") \
    .option("url", mysql_url_stage_compras) \
    .option("dbtable", 'COMPRAS') \
    .option("user", mysql_properties["user"]) \
    .option("password", mysql_properties["password"]) \
    .option("driver", mysql_properties["driver"]) \
    .mode("append") \
    .save()
'''
# Lendo a tabela compras do banco 

df_compras = spark.read \
    .format("jdbc") \
    .option("url", mysql_url_stage_compras) \
    .option("dbtable", 'COMPRAS') \
    .option("user", mysql_properties["user"]) \
    .option("password", mysql_properties["password"]) \
    .option("driver", mysql_properties["driver"]) \
    .load()

# lendo tabela de cep 

df_cep = spark.read \
    .format("jdbc") \
    .option("url", mysql_url_stage_compras) \
    .option("dbtable", 'CEP') \
    .option("user", mysql_properties["user"]) \
    .option("password", mysql_properties["password"]) \
    .option("driver", mysql_properties["driver"]) \
    .load()


# tratamento do complemento 

tb_compras1 = df_compras.withColumn("COMPLEMENTO", when(col("COMPLEMENTO").isNull(),"N/A").otherwise(col("COMPLEMENTO")))

# tratamento dos espacos em vazios a direita e a aesquerda 

colunas = tb_compras1.columns

for coluna in colunas:
    df_compras2 = tb_compras1.withColumn(coluna, trim(col(coluna)))

# tratamento dos nulls

df_compras3 = df_compras2.na.drop()

# tratamento dos duplicados 

df_compras4 = df_compras3.dropDuplicates()

# df_compras_duplicadas

df_compras_duplicadas = tb_compras1.subtract(df_compras4).withColumn("MOTIVO_REJEITADO", lit("Dado Repetido"))

# df_compras_nulas

df_compras_nulls = tb_compras1.subtract(df_compras4).withColumn("MOTIVO_REJEITADO", lit("Alguma coluna possui null"))


# validando o CNPJ

df_compras_cnpj = df_compras4.withColumn("CNPJ_STATUS", cnpj_valido("CNPJ_FORNECEDOR"))

# df CNPJ ivalido 

df_compras_rejeitados_CNPJ = df_compras_cnpj.filter(col("CNPJ_STATUS") == False).withColumn("MOTIVO_REJEITADO", lit("CNPJ INVALIDO")).drop('CNPJ_STATUS')

# df CNP valido 

df_compras5 = df_compras_cnpj.filter(col("CNPJ_STATUS") == True).drop('CNPJ_STATUS').withColumn("NOME_FORNECEDOR", upper("NOME_FORNECEDOR"))

# tratativa do CEP

colunas_ordenadas = ['NOME_FORNECEDOR', 'CNPJ_FORNECEDOR', 'EMAIL_FORNECEDOR', 'TELEFONE_FORNECEDOR',
                     'NUMERO_NF', 'DATA_EMISSAO', 'VALOR_NET', 'VALOR_TRIBUTO', 'VALOR_TOTAL',
                     'NOME_ITEM', 'QTD_ITEM', 'CONDICAO_PAGAMENTO', 'CEP' , 'NUM_ENDERECO', 'COMPLEMENTO',
                     'TIPO_ENDERECO', 'DATA_PROCESSAMENTO']

df_compras_rejeitadas_CEP = df_compras5.join(df_cep, "CEP", how="left_anti").select(colunas_ordenadas).withColumn("MOTIVO_REJEITADO", lit("CEP INVALIDO"))


# df compras validas sem cep errado

df_compras6 = df_compras5.subtract(df_compras_rejeitadas_CEP.drop("MOTIVO_REJEITADO"))



# df Compras final 


# Tratamento condicao

df_compras7 = (df_compras6
    .withColumn("CONDICAO_PAGAMENTO", when(col("CONDICAO_PAGAMENTO").substr(2, 4).like("%ntra%"), col("CONDICAO_PAGAMENTO"))
        .otherwise(when(col("CONDICAO_PAGAMENTO").like("%90 dias") | col("CONDICAO_PAGAMENTO").like("%noventa dias"), "30/60/90 dias")
            .when(col("CONDICAO_PAGAMENTO").like("%60 dias"), "30/60 dias")
            .when(col("CONDICAO_PAGAMENTO").like("%vista"), "A vista")
            .otherwise(col("CONDICAO_PAGAMENTO")))
    ))


# Lendo a tabela  condicao

df_condicao_pagamento = spark.read \
    .format("jdbc") \
    .option("url", mysql_url_projeto_financeiro_compras) \
    .option("dbtable", 'CONDICAO_PAGAMENTO') \
    .option("user", mysql_properties["user"]) \
    .option("password", mysql_properties["password"]) \
    .option("driver", mysql_properties["driver"]) \
    .load()

df_compras8 = df_compras7.join(df_condicao_pagamento, col("DESCRICAO") == col("CONDICAO_PAGAMENTO"), "inner") \
    .select(df_compras6["NOME_FORNECEDOR"], df_compras6["CNPJ_FORNECEDOR"], df_compras6["EMAIL_FORNECEDOR"],
        df_compras6["TELEFONE_FORNECEDOR"], df_compras6["NUMERO_NF"], df_compras6["DATA_EMISSAO"],
        df_compras6["VALOR_NET"], df_compras6["VALOR_TRIBUTO"], df_compras6["VALOR_TOTAL"], df_compras6["NOME_ITEM"],
        df_compras6["QTD_ITEM"], df_condicao_pagamento["ID_CONDICAO"], df_compras6["CEP"], df_compras6["NUM_ENDERECO"],
        df_compras6["COMPLEMENTO"], df_compras6["TIPO_ENDERECO"], df_compras6["DATA_PROCESSAMENTO"]).withColumnRenamed("ID_CONDICAO", "ID_CONDICAO_PAGAMENTO")



# Unindo os rejitados

df_compras_rejeitados = df_compras_duplicadas.union(df_compras_nulls.union(df_compras_rejeitados_CNPJ.union(df_compras_rejeitadas_CEP)))

df_compras_rejeitados.show()
'''
df_compras8.write \
    .format("jdbc") \
    .option("url", mysql_url_stage_compras) \
    .option("dbtable", 'TRATAMENTO_COMPRAS_FINAL') \
    .option("user", mysql_properties["user"]) \
    .option("password", mysql_properties["password"]) \
    .option("driver", mysql_properties["driver"]) \
    .mode("append") \
    .save()

df_compras_rejeitados.write \
    .format("jdbc") \
    .option("url", mysql_url_stage_compras) \
    .option("dbtable", 'VALIDACAO_COMPRAS_REJEITADOS') \
    .option("user", mysql_properties["user"]) \
    .option("password", mysql_properties["password"]) \
    .option("driver", mysql_properties["driver"]) \
    .mode("append") \
    .save()
'''
# COMPRAS VALIDADAS

df_compras_validadas = df_compras8.select("DATA_PROCESSAMENTO", "DATA_EMISSAO", "NUMERO_NF", "CNPJ_FORNECEDOR")

df_compras_validadas.printSchema()
df_compras_validadas.write \
    .format("jdbc") \
    .option("url", mysql_url_stage_compras) \
    .option("dbtable", 'VALIDACAO_COMPRAS') \
    .option("user", mysql_properties["user"]) \
    .option("password", mysql_properties["password"]) \
    .option("driver", mysql_properties["driver"]) \
    .mode("append") \
    .save()
df_compras_validadas.show()

#df_compras_rejeitadas_CEP.show()
#novos_condicao_pagamento = condicao_pagamento.join(condicao_pagamento_bd, on=list(condicao_pagamento.columns), how="left_anti")
#df_compras_duplicadas.show()
#df_compras_nulls.show()
#df_compras_rejeitados.show()
#df_compras_cnpj.show()
#df_compras_rejeitados_CNPJ.show()
#df_compras5.show()
'''
tb_compras1.write \
    .format("jdbc") \
    .option("url", mysql_url_stage_compras) \
    .option("dbtable", 'COMPRAS') \
    .option("user", mysql_properties["user"]) \
    .option("password", mysql_properties["password"]) \
    .option("driver", mysql_properties["driver"]) \
    .mode("append") \
    .save()



df_compras = spark.read \
    .format("jdbc") \
    .option("url", mysql_url_stage_compras) \
    .option("dbtable", 'COMPRAS') \
    .option("user", mysql_properties["user"]) \
    .option("password", mysql_properties["password"]) \
    .option("driver", mysql_properties["driver"]) \
    .load()




df_compras_limpo, df_compras_rejeitados = limpar_tabela(tb_compras1)

df_compras_rejeitados.limit(10).show()




df_compras_limpo.write \
    .format("jdbc") \
    .option("url", mysql_url_stage_compras) \
    .option("dbtable", 'TRATAMENTO_COMPRAS_FINAL') \
    .option("user", mysql_properties["user"]) \
    .option("password", mysql_properties["password"]) \
    .option("driver", mysql_properties["driver"]) \
    .mode("append") \
    .save()

'''

spark.stop()
