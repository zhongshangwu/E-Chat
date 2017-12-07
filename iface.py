import time


# colors in console
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_help():
    ''' 打印帮助 '''
    print("Chat client commads and syntax:")
    print("-   @<user/group> \"<message>\" : Send message to user or group")
    print("-   ? : Get number of unread messages")
    print("-   read : Read all unread messages")
    print("-   +<user> \"<keyword>\" : Add mapping to contacts list")
    print("-   <group>=<user1>+<user2>+... : Create multicast group")
    print("-   <group>+=<user> : Add user to existing group")
    print("-   find <keyword> : Find contact using keyword")
    print("-   help : Print(this help message")
    print("-   quit : Quit chat")


def _print_msg(self, username, dst, msg, timestamp):
        time_str = time.asctime(time.localtime(timestamp))
        if (dst == self.name):
            print('[{}] {} says to you: {}'.format(time_str, src, msg))
        else:
            print('[{}] {} says in group <{}>: {}'.format(
                time_str, src, dst, msg))



print_help()
