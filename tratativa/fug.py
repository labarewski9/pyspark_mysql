from pyspark.sql.functions import col, trim, when, upper, regexp_extract, lit, udf, current_timestamp
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, LongType, DateType , DecimalType, BooleanType, ShortType 
import re

def cnpj_valido(cnpj):
    cnpj = re.sub(r'[^0-9]', '', cnpj)
    if len(cnpj) !=14:
        return False
    
    total = 0 
    resto = 0 
    digito_verificador_1 = 0
    digito_verificador_2 = 0
    multiplicadores1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    multiplicadores2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]

    for i in range(0,12,1):
        total += int(cnpj[i]) * int(multiplicadores1[i])
    resto = total % 11
    
    if resto < 2:
        digito_verificador_1 = 0
    else:
        digito_verificador_1 = 11 - resto

    total = 0
    resto = 0

    for i in range(0,13,1):
        total += int(cnpj[i]) * int(multiplicadores2[i])

    resto = total % 11
    if resto < 2:
        digito_verificador_2 = 0 
    else:
        digito_verificador_2 = 11 - resto

    return cnpj[-2:] == str(digito_verificador_1) + str(digito_verificador_2)   
cnpj_valido = udf(cnpj_valido, BooleanType())
