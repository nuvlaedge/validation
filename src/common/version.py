"""

"""


class Version(str):
    """
    String extension for version control and validation
    """
    major: int
    medium: int
    minor: int

    def __new__(cls, value, *args, **kwargs):
        versions: list[int] = [int(i) for i in value.split('.')]
        if len(versions) != 3:
            raise ValueError(f'Version provided {value} does not correspond with NuvlaEge format X.X.X )')
        cls.major = versions[0]
        cls.medium = versions[1]
        cls.minor = versions[2]
        return super(Version, cls).__new__(cls, value)
