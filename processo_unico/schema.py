from pyspark.sql.types import StructType, StructField, StringType, IntegerType, LongType, DateType , DecimalType, BooleanType, ShortType 

schemaCEP = StructType([
    StructField("CEP", IntegerType(), True),
    StructField("UF", StringType(), True),
    StructField("CIDADE", StringType(), True),
    StructField("BAIRRO", StringType(), True),
    StructField("LOGRADOURO", StringType(), True)
])

schemaTipoEndereco = StructType([
    StructField("ID_TIPO_ENDERECO", StringType(), False),
    StructField("DESCRICAO", StringType(), False),
    StructField("SIGLA", StringType(), False)
])

schemaCondicaoPagamento = StructType([
    StructField("ID_CONDICAO", IntegerType(), False),
    StructField("DESCRICAO", StringType(), False),
    StructField("QTD_PARCELAS", IntegerType(), False),
    StructField("ENTRADA", ShortType(), False)
])