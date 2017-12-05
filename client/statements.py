import enum


class Mode(enum.IntEnum):
    COMMAND = 1
    CHAT = 2
    QUERY = 3

# Mode : Statement > Action


def process_statements(client, statement):

    @statement_register(Mode.COMMAND)
    def login(username, password):
        pass


def _process_statement(self, str_input):
        ''' 处理用户输入 '''
        if self.mode == Mode.COMMAND:  # 命令模式
            if str_input == 'quit':
                quit()
            elif str_input == 'help':
                help()
            elif str_input == 'query':
                query_mode()
            elif str_input == 'chat':
                chat_mode()
            elif str_input == 'server time':
                query_server_time()
            else:
                unkown()
            # input_slice=str_input.split(':', 1)
            # if not input_slice or len(input_slice) < 2:
            #     pass
        elif self.mode == Mode.CHAT:  # 聊天模式
            pass
        elif self.mode == Mode.QUERY:  # 查询模式
            if str_input == 'server time':
                query_server_time()
