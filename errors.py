##################
# Import Modules #
##################
from discord.ext import commands


class MonopolyRunError(commands.CommandError):
    pass


class InvalidPropertyName(MonopolyRunError):
    def __init__(self, argument):
        self.argument = argument
        super().__init__('Property "{}" does not exist.'.format(argument))


class NotInTeamChannel(MonopolyRunError):
    def __init__(self, argument1, argument2):
        self.argument1 = argument1
        self.argument2 = argument2
        super().__init__(f'{argument1} is not equal to {argument2}')


class AlreadyVisted(MonopolyRunError):
    def __init__(self, argument):
        self.argument = argument
        super().__init__(f'You have already visited and answered {argument}, correctly!')


class TooManyTeams(MonopolyRunError):
    pass


class NotEnoughTeams(MonopolyRunError):
    pass


class DatabaseRecordNotFound(MonopolyRunError):
    pass
