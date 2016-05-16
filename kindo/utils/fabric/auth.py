"""
Common authentication subroutines. Primarily for internal use.
"""

def get_password(user, host, port):
    from .state import env
    from .network import join_host_strings
    host_string = join_host_strings(user, host, port)
    return env.passwords.get(host_string, env.password)


def set_password(user, host, port, password):
    from .state import env
    from .network import join_host_strings
    host_string = join_host_strings(user, host, port)
    env.password = env.passwords[host_string] = password
