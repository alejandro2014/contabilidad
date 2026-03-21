class KeyGetter:
    def value(self, key, object):
        split_key = key.split('.')

        for key_part in split_key:
            if not key_part in object:
                return None

            object = object[key_part]

        return object
