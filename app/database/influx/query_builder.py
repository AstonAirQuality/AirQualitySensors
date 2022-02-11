class InfluxQueryBuilder:
    """Builds custom Flux queries by chaining python functions.
    Maintains query structure and logical function (required by flux) order regardless of
    call order. e.g .filter().range() is converted to .range().filter() as range comes before
    filter in the flux language.
    """

    def __init__(self, bucket):
        self.__bucket = bucket
        self.__function_chain = {"range": None, "filters": None}
        self.__fields = []

    def range(self, start="0", stop=None):
        if stop is None:
            self.__function_chain["range"] = f"range(start: {start})"
        else:
            self.__function_chain["range"] = f"range(start: {start}, stop: {stop})"
        return self

    def filter(self, expression, param_name="r"):
        """Will keep appending filter functions on each call.
        Args:
            expression: flux filter expression
            param_name: name of param in flux filter expression
        Returns:
            Instance of self
        """
        query_string = f"filter(fn: ({param_name}) => {expression})"
        if self.__function_chain["filters"] is None:
            self.__function_chain["filters"] = [query_string]
        else:
            self.__function_chain["filters"].append(query_string)
        return self

    def field(self, field):
        """Appends field to function chain.
        Returns:
            Instance of self
        """
        self.__fields.append(f'r["_field"] == "{field}"')
        return self

    def asset(self, asset):
        """Call measurement before field
        Returns:
            Instance of self
        """
        self.filter(f'r["_measurement"] == "{asset}"')
        return self

    def build(self):
        """Build the flux query from the function chain.
        Returns:
            Built Flux query string.
        """
        if self.__fields:
            self.filter(" or ".join(self.__fields))
        query = f"from(bucket: \"{self.__bucket}\")"
        for k, v in self.__function_chain.items():
            if v is not None:
                if type(v) is list:
                    for item in v:
                        query += f"\n|> {item}"
                else:
                    query += f"\n|> {v}"
        return query