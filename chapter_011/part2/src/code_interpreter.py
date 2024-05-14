# GitHub: https://github.com/naotaka1128/llm_app_codes/chapter_011/part2/src/code_interpreter.py

import os
import magic
import traceback
import mimetypes
from openai import OpenAI


class CodeInterpreterClient:
    """
    OpenAI's Assistants API の Code Interpreter Tool を使用して
    Python コードを実行したり、ファイルを読み取って分析を行うクラス

    このクラスは以下の機能を提供します：
    1. OpenAI Assistants APIを使ったPythonコードの実行
    2. ファイルのアップロードとAssistants APIへの登録
    3. アップロードしたファイルを使ったデータ分析とグラフ作成

    主要なメソッド：
    - upload_file(file_content): ファイルをアップロードしてAssistants APIに登録する
    - run(prompt): Assistants APIを使ってPythonコードを実行したり、ファイル分析を行う

    Example:
    ===============
    from src.code_interpreter import CodeInterpreterClient
    code_interpreter = CodeInterpreterClient()
    code_interpreter.upload_file(open('file.csv', 'rb').read())
    code_interpreter.run("file.csvの内容を読み取ってグラフを書いてください")
    """
    def __init__(self):
        self.file_ids = []
        self.openai_client = OpenAI()
        self.assistant_id = self._create_assistant_agent()
        self.thread_id = self._create_thread()
        self._create_file_directory()
        self.code_intepreter_instruction = """
        与えられたデータ分析用のPythonコードを実行してください。
        実行した結果を返して下さい。あなたの分析結果は不要です。
        もう一度繰り返します、実行した結果を返して下さい。
        ファイルのパスなどが少し間違っている場合は適宜修正してください。
        修正した場合は、修正内容を説明してください。
        """

    def _create_file_directory(self):
        directory = "./files/"
        os.makedirs(directory, exist_ok=True)

    def _create_assistant_agent(self):
        """
        OpenAI Assistants API Response Example:
        ===============
        Assistant(
            id='asst_hogehogehoge',
            created_at=1713525431,
            description=None,
            instructions='You are a python code runner. Write and run code to answer questions.',
            metadata={},
            model='gpt-4o',
            name='Python Code Runner',
            object='assistant',
            tools=[
                CodeInterpreterTool(type='code_interpreter')
            ],
            response_format='auto',
            temperature=1.0,
            tool_resources=ToolResources(
                code_interpreter=ToolResourcesCodeInterpreter(file_ids=[]),
                file_search=None
            ),
            top_p=1.0
        )
        """
        self.assistant = self.openai_client.beta.assistants.create(
            name="Python Code Runner",
            instructions="You are a python code runner. Write and run code to answer questions.",
            tools=[{"type": "code_interpreter"}],
            model="gpt-4o",
            tool_resources={
                "code_interpreter": {
                    "file_ids": self.file_ids
                }
            }
        )
        return self.assistant.id

    def _create_thread(self):
        """
        OpenAI Assistants API Response Example:
        Thread(
            id='thread_hoge',
            created_at=1713525580,
            metadata={},
            object='thread',
            tool_resources=ToolResources(code_interpreter=None, file_search=None))
        """
        thread = self.openai_client.beta.threads.create()
        return thread.id

    def upload_file(self, file_content):
        """
        Upload file to assistant agent

        OpenAI Assistants API Response Example:
        FileObject(
            id='file-hogehoge',
            bytes=18,
            created_at=1713525743,
            filename='test.csv',
            object='file',
            purpose='assistants',
            status='processed',
            status_details=None
        )

        Args:
            file_content (_type_): open('file.csv', 'rb').read()
        """
        file = self.openai_client.files.create(
            file=file_content,
            purpose='assistants'
        )
        self.file_ids.append(file.id)
        self._add_file_to_assistant_agent()  # Update assistant with new files
        return file.id

    def _add_file_to_assistant_agent(self):
        self.assistant = self.openai_client.beta.assistants.update(
            assistant_id=self.assistant_id,
            tool_resources={
                "code_interpreter": {
                    "file_ids": self.file_ids
                }
            }
        )

    def run(self, code):
        """
        Assistants API Response Example
        ===============
        Message(id='msg_mzx4vA5cS8kuzLfpeALC049M', assistant_id=None, attachments=[], completed_at=None, content=[TextContentBlock(text=Text(annotations=[], value='I need to solve the equation `3x + 11 = 14`. Can you help me?'), type='text')], created_at=1713526391, incomplete_at=None, incomplete_details=None, metadata={}, object='thread.message', role='user', run_id=None, status=None, thread_id='thread_dmhWy82iU3S97MMdWk5Bzkc7')
        Run(id='run_ox2vsSkPB0VMViuMOnVXGlzH', assistant_id='asst_tXog4eZKOLIal42dO5nQQISB', cancelled_at=None, completed_at=1713526496, created_at=1713526488, expires_at=None, failed_at=None, incomplete_details=None, instructions='Please address the user as Jane Doe. The user has a premium account.', last_error=None, max_completion_tokens=None, max_prompt_tokens=None, metadata={}, model='gpt-4o', object='thread.run', required_action=None, response_format='auto', started_at=1713526489, status='completed', thread_id='thread_dmhWy82iU3S97MMdWk5Bzkc7', tool_choice='auto', tools=[CodeInterpreterTool(type='code_interpreter')], truncation_strategy=TruncationStrategy(type='auto', last_messages=None), usage=Usage(completion_tokens=151, prompt_tokens=207, total_tokens=358), temperature=1.0, top_p=1.0, tool_resources={})

        
        >> message
        SyncCursorPage[Message](
            data=[
                Message(
                    id='msg_VLCN8oRK9qXoaRa41e8F9YjS',
                    assistant_id='asst_tXog4eZKOLIal42dO5nQQISB',
                    attachments=[],
                    completed_at=None,
                    content=[
                        ImageFileContentBlock(
                            image_file=ImageFile(file_id='file-oL7oQPvIcbmvD3oAqRR5eX6r'),
                            type='image_file'
                        ),
                        TextContentBlock(
                            text=Text(
                                annotations=[
                                    FilePathAnnotation(
                                        end_index=174,
                                        file_path=FilePath(file_id='file-NK7CrMtrEIZixhV6WIAiTdtk'),
                                        start_index=136,
                                        text='sandbox:/mnt/data/Fibonacci_Series.csv',
                                        type='file_path'
                                    )
                                ],
                                value="Here's the sine curve, \\( y = \\sin(x) \\), plotted over the range from \\(-2\\pi\\) to \\(2\\pi\\). The curve beautifully illustrates the periodic nature of the sine function. If you need any further analysis or another graph, feel free to let me know!"
                            ),
                            type='text'
                        )
                    ],
                    created_at=1713526821,
                    incomplete_at=None,
                    incomplete_details=None,
                    metadata={},
                    object='thread.message',
                    role='assistant',
                    run_id='run_LwPzADWdCMbwWsxB4i5VsMyu',
                    status=None,
                    thread_id='thread_dmhWy82iU3S97MMdWk5Bzkc7'
                )
            ],
            object='list',
            first_id='msg_VLCN8oRK9qXoaRa41e8F9YjS',
            last_id='msg_VLCN8oRK9qXoaRa41e8F9YjS',
            has_more=True
        )
        """

        prompt = f"""
        以下のコードを実行して結果を返して下さい。
        ファイルの読み込みなどに失敗した場合、可能な範囲で修正して再実行して下さい。
        ```python
        {code}
        ```
        あなたの見解や感想は不要なのでコードの実行結果を返して下さい
        """

        # add message to thread
        self.openai_client.beta.threads.messages.create(
            thread_id=self.thread_id,
            role="user",
            content=prompt
        )

        # run assistant to get response
        run = self.openai_client.beta.threads.runs.create_and_poll(
            thread_id=self.thread_id,
            assistant_id=self.assistant_id,
            instructions=self.code_intepreter_instruction
        )
        if run.status == 'completed': 
            message = self.openai_client.beta.threads.messages.list(
                thread_id=self.thread_id,
                limit=1  # Get the last message
            )
            try:
                file_ids = []
                for content in message.data[0].content:
                    if content.type == "text":
                        text_content = content.text.value
                        file_ids.extend([
                            annotation.file_path.file_id
                            for annotation in content.text.annotations
                        ])
                    elif content.type == "image_file":
                        file_ids.append(content.image_file.file_id)
                    else:
                        raise ValueError("Unknown content type")
            except:
                print(traceback.format_exc())
                return None, None
        else:
            raise ValueError("Run failed")

        file_names = []
        if file_ids:
            for file_id in file_ids:
                file_names.append(self._download_file(file_id))

        return text_content, file_names

    def _download_file(self, file_id):
        data = self.openai_client.files.content(file_id)
        data_bytes = data.read()

        # ファイルの内容からMIMEタイプを取得
        mime_type = magic.from_buffer(data_bytes, mime=True)

        # MIMEタイプから拡張子を取得
        extension = mimetypes.guess_extension(mime_type)

        # 拡張子が取得できない場合はデフォルトの拡張子を使用
        if not extension:
            extension = ""

        file_name = f"./files/{file_id}{extension}"
        with open(file_name, "wb") as file:
            file.write(data_bytes)

        return file_name
