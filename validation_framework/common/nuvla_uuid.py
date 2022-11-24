""" Nuvla UUID validator class """


class NuvlaUUID(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate_nuvla_id

    @classmethod
    def validate_nuvla_id(cls, nuvla_id: str) -> str:
        id_parts: list[str] = nuvla_id.split('/')
        if len(id_parts) != 2:
            print('Validator called')
            raise ValueError("Nuvla ID's format must me a string with format: "
                             "<resource_id>/<unique-identifier>")

        return nuvla_id