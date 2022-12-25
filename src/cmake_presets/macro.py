from string import Template


class EnvironmentExpansion(Template):
    delimiter = "$env"


class ParentEnvironmentExpansion(Template):
    delimiter = "$penv"


class MacroExpander:
    pass
