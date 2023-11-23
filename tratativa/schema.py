from pyspark.sql.types import StructType, StructField, StringType, IntegerType, LongType, DateType , DecimalType, BooleanType, ShortType 

schemaCompras = StructType([
    StructField("NOME_FORNECEDOR", StringType(), True),
    StructField("CNPJ_FORNECEDOR", StringType(), True),
    StructField("EMAIL_FORNECEDOR", StringType(), True),
    StructField("TELEFONE_FORNECEDOR", StringType(), True),
    StructField("NUMERO_NF", LongType(), True),
    StructField("DATA_EMISSAO", DateType(), True),
    StructField("VALOR_NET", DecimalType(8,2), True),
    StructField("VALOR_TRIBUTO", DecimalType(8,2), True),
    StructField("VALOR_TOTAL", DecimalType(8,2), True),
    StructField("NOME_ITEM", StringType(), True),
    StructField("QTD_ITEM", IntegerType(), True),
    StructField("CONDICAO_PAGAMENTO", StringType(), True),
    StructField("CEP", IntegerType(), True),
    StructField("NUM_ENDERECO", IntegerType(), True),
    StructField("COMPLEMENTO", StringType(), True),
    StructField("TIPO_ENDERECO", StringType(), True),
    StructField("DATA_PROCESSAMENTO", DateType(), True)
])
