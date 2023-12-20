import datetime

from bs4 import BeautifulSoup
from pyspark.sql import SparkSession, DataFrame
import sparknlp
from sparknlp.base import *
from sparknlp.annotator import *
from pyspark.ml import Pipeline
import pyspark.sql.functions as F 
from utils import *

import os
import logging


class FilterRawdata():
    
    def __init__(self, 
                 spark:SparkSession,
                 target_date:str, 
                 target_sitename:str, 
                 dest_dir:str,
                 data_type='html',
                 target_type='ransomware'):
        self.spark = spark
        self.target_date = target_date
        self.target_sitename = target_sitename
        self.dest_dir = dest_dir
        self.target_type = target_type


    def run(self) -> DataFrame:
        try:
            df = None
            df = self.load()
            if df is None:
                logging.warning('No raw data to filter')
            else: 
                df = self.filter(df)
                if df is None:
                    logging.error('filter error')
        except Exception as e:
            logging.error('Exception: ' + e)
            raise e
        # end try
        return df

    def load(self) -> DataFrame:
        path = 'webcrawler/data/raw/'
        websitename = self.sitename
        df = None
        file_path = os.path.join(
                    path, 
                    self.target_date, 
                    self.target_type, 
                    websitename, 
                    '*')
        data = self.spark.sparkContext.wholeTextFiles(file_path)
        df = data.toDF(schema=["filename", "value"])

        if df is not None:
           df = (
                df
                .withColumn('filedir', F.split(F.col('filename'), '/', limit=-1))
                .select(F.element_at('filedir', -1).alias("sha256"), "value")
                )
        
        return df
    
    def save(self, df:DataFrame) -> None:
        try:
            now = datetime.datetime.now() 
            df = df.withColumn('timestamp_store', F.lit(now.isoformat())) 
            (
            df.write.format("mongodb")
            .mode("append")
            .option("database", "web")
            .option("collection", self.target_type)
            .save()
            )
        except Exception as e:
            logging.error('Exception of Save: ' + e)
            raise e
        # end try



class JsonFilterRawdata(FilterRawdata):

    def load(self) -> DataFrame:
        path = 'webcrawler/data/raw/'
        websitename = self.sitename
        df = None
        file_path = os.path.join(
                    path, 
                    self.target_date, 
                    self.target_type, 
                    websitename, 
                    '*')
        df = self.spark.read.json(file_path)
        if df is not None:
           df = (
                df
                .withColumn('filedir', F.split(F.col('filename'), '/', limit=-1))
                .select(F.element_at('filedir', -1).alias("sha256"), "value")
                )
        
        return df
    
    def filter_raw(self, df:DataFrame) -> DataFrame:
        ds = df.select(
                            F.regexp_replace(F.col("name"),  '\n', '').alias('name'),
                            F.regexp_replace(F.col("title"), '\n', '').alias('title'),
                            F.regexp_replace(F.col("content"), '\n', '').alias('content'),
                            F.regexp_replace(F.col("desc"), '\n', '').alias('desc'),
                            F.regexp_replace(F.col("url"), "\\[\\[\\!;;;;", '').alias('url'),
                            'date'
                            )

        result = ds.select(
                                'sha256',
                                F.col('self.target_sitename').alias('sitename'),
                                F.when(F.col('name').isNull(), '').otherwise(F.col('name')).alias('company'),
                                F.when(F.col('title').isNull(), '').otherwise(F.col('title')).alias('title'),
                                F.when(F.col('content').isNotNull(), F.col('content')
                                       ).when(F.col('desc').isNotNull(), F.col('desc')).otherwise('').alias('contents'),
                                F.when(F.col('url').isNull(), '').otherwise(F.col('url')).alias('contents_url'),
                                F.coal('date').alias('date_upload'),
                                F.lit('').alias('contents_url'),
                                )
        return result



class HtmlFilterRawdata(FilterRawdata):

    def filter(self, df:DataFrame) -> DataFrame:
        documentAssembler = DocumentAssembler().setInputCol("value").setOutputCol("document")
        action = "clean"
        patterns = ["([^.@\\s]+)(\\.[^.@\\s]+)*@([^.@\\s]+\\.)+([^.@\\s]+)"]
        replacement = " "
        removalPolicy = "pretty_all"
        encoding = "UTF-8"

        inpuColName = "document"
        outputColName = "normalizedDocument"

        documentNormalizer = DocumentNormalizer() \
            .setInputCols(inpuColName) \
            .setOutputCol(outputColName) \
            .setAction(action) \
            .setPatterns(patterns) \
            .setReplacement(replacement) \
            .setPolicy(removalPolicy) \
            .setLowercase(False) \
            .setEncoding(encoding)

        docPatternRemoverPipeline = \
        Pipeline() \
            .setStages([
                documentAssembler,
                documentNormalizer
            ])
        df_out = docPatternRemoverPipeline.fit(df).transform(df)
        df_out = df_out.select('sha256', F.col("normalizedDocument.result")[0].alias("text"))

        get_company_udf = F.udf(get_company, F.StringType())
        get_contents_udf = F.udf(get_contents, F.StringType())
        get_cols_udf = F.udf(get_cols, F.StringType())


        result = df_out.select(
                        'sha256',
                        get_company_udf('text').alias('company'),
                        get_contents_udf('text').alias('contents'),
                        get_cols_udf('text', F.lit('website')).alias('company_url'),
                        get_cols_udf('text', F.lit("Date the files were received")).alias('date_upload'),
                        F.lit('').alias('contents_url'),
                        F.lit(self.target_sitename).alias('sitename'),
                    ) 
        result = result.withColumn('date_upload', 
                                F.when(
                                    F.col('date_upload').isNotNull(),
                                    F.date_format(F.to_date('date_upload', 'd MMMM yyyy'), 'yyyymmdd')
                                    ).otherwise(''))
        return result
    
