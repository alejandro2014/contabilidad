class FileLoaderFormatter:
    def format_file_loader_values(self, file_loader_values_raw):
        file_loader_values_raw = file_loader_values_raw[0]

        return {
            "readerType": file_loader_values_raw[0],
            "hasHeader": file_loader_values_raw[1],
            "fieldNamePrefix": file_loader_values_raw[2],
            "separator": file_loader_values_raw[3].replace("\\t", "\t"),
            "fields": {
                "date": file_loader_values_raw[4],
                "concept": file_loader_values_raw[5],
                "value": file_loader_values_raw[6]
            }
        }
