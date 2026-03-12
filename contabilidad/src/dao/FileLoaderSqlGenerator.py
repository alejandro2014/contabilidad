class FileLoaderSqlGenerator:
    def select_file_loader_values(self, reader_type='csv'):
        return f"SELECT reader_type, has_header, field_name_prefix, separator, date_position, concept_position, value_position FROM file_loader_values WHERE reader_type = '{reader_type}'"
