# GitHub: https://github.com/naotaka1128/llm_app_codes/chapter_011/part2/tools/bigquery.py


import pandas as pd
import streamlit as st
from typing import Optional
from google.cloud import bigquery
from google.oauth2 import service_account
from langchain_core.tools import Tool, StructuredTool
from langchain_core.pydantic_v1 import (BaseModel, Field)
from src.code_interpreter import CodeInterpreterClient


class SqlTableInfoInput(BaseModel):
    table_name: str = Field()


class ExecSqlInput(BaseModel):
    query: str = Field()
    limit: Optional[int] = Field(default=None)


class BigQueryClient():
    def __init__(
        self,
        code_interpreter: CodeInterpreterClient,
        project_id: str = 'ai-app-book-bq',
        dataset_project_id: str = 'bigquery-public-data',
        dataset_id: str = 'google_trends',
    ) -> None:
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"])
        self.client = bigquery.Client(
            credentials=credentials, project=project_id)
        self.dataset_project_id = dataset_project_id
        self.dataset_id = dataset_id
        self.table_names_str = self._fetch_table_names()
        self.code_interpreter = code_interpreter

    def _fetch_table_names(self) -> str:
        """
        利用可能なテーブル名をBigQueryから取得
        カンマ区切りの文字列として返却
        """
        query = f"""
        SELECT table_name
        FROM `{self.dataset_project_id}.{self.dataset_id}.INFORMATION_SCHEMA.TABLES`
        """
        table_names = self._exec_query(query).table_name.tolist()
        return ', '.join(table_names)

    def _exec_query(self, query: str, limit: int = None) -> pd.DataFrame:
        """ SQLを実行し Pandas Dataframe として返却 """
        if limit is not None:
            query += f"\nLIMIT {limit}"
        query_job = self.client.query(query)
        return query_job.result().to_dataframe(
            create_bqstorage_client=True
        )

    def exec_query_and_upload(self, query: str, limit: int = None) -> str:
        """Execute given SQL query and return result as a formatted string or path to a saved file."""
        try:
            df = self._exec_query(query, limit)
            csv_data = df.to_csv().encode('utf-8')
            assistant_api_path = self.code_interpreter.upload_file(csv_data)
            return f"sql:\n```\n{query}\n```\n\nsample results:\n{df.head()}\n\nfull result was uploaded to /mnt/{assistant_api_path} (Assistants API File)"
        except Exception as e:
            return f"SQL execution failed. Error message is as follows:\n```\n{e}\n```"

    def _generate_sql_for_table_info(self, table_name: str) -> tuple:
        """ 指定されたテーブルのスキーマとサンプルデータを取得するSQLを生成 """
        get_schema_sql = f"""
        SELECT 
            TO_JSON_STRING(
                ARRAY_AGG(
                    STRUCT(
                        IF(is_nullable = 'YES', 'NULLABLE', 'REQUIRED'
                    ) AS mode,
                    column_name AS name,
                    data_type AS type
                )
                ORDER BY ordinal_position
            ), TRUE) AS schema
        FROM
            `{self.dataset_project_id}.{self.dataset_id}.INFORMATION_SCHEMA.COLUMNS`
        WHERE
            table_name = "{table_name}"
        """

        sample_data_sql = f"""
        SELECT
            *
        FROM
            `{self.dataset_project_id}.{self.dataset_id}.{table_name}`
        LIMIT
            3
        """
        return get_schema_sql, sample_data_sql

    def get_table_info(self, table_name: str) -> str:
        """ テーブルスキーマとサンプルデータを返す """
        get_schema_sql, sample_data_sql = \
            self._generate_sql_for_table_info(table_name)
        schema = self._exec_query(get_schema_sql) \
                     .to_string(index=False)
        sample_data = self._exec_query(sample_data_sql)\
                          .to_string(index=False)
        table_info = f"""
        ### schema
        ```
        {schema}
        ```

        ### sample_data
        ```
        {sample_data}
        ```
        """
        return table_info
        

    def exec_query_tool(self):
        exec_query_tool_description = f"""
        BigQueryでSQLクエリを実行するツールです。
        SQLクエリを入力すると、BigQueryで実行されます。

        このツールを利用する前に `get_table_info_tool` ツールで
        テーブルスキーマを確認することを **強く** お勧めします。

        BigQuery用のクエリを書く際は、
        project_id、dataset_id、table_idを必ず指定してください。

        使用しているBigQueryは以下の通りです:
        - project_id: {self.dataset_project_id}
        - dataset_id: {self.dataset_id}
        - table_id: {self.table_names_str}

        SQLは可読性を考慮して記述してください（例: 改行を入れるなど）。
        最頻値を求める際は「Mod」関数を使用してください。

        サンプル以外の結果はCode InterpreterにCSVファイルで保存されます。
        Code InterpreterでPythonを実行してアクセスしてください。
        """
        return StructuredTool.from_function(
            name='exec_query',
            func=self.exec_query_and_upload,
            description=exec_query_tool_description,
            args_schema=ExecSqlInput
        )

    def get_table_info_tool(self):
        sql_table_info_tool_description = f"""
        BigQueryテーブルのスキーマとサンプルデータ（3行）を取得するツール
        SQLクエリを構築する際にテーブルスキーマを参照できる

        利用可能なテーブルは以下の通りです: {self.table_names_str}
        """
        return Tool.from_function(
            name='sql_table_info',
            func=self.get_table_info,
            description=sql_table_info_tool_description,
            args_schema=SqlTableInfoInput
        )
