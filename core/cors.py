class CorsAllow:

    def __call__(self, func):
        def wrapper(request, *args):
            response = func(request)
            response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
            response["Access-Control-Max-Age"] = "1000"
            response["Access-Control-Allow-Headers"] = "*"
            return response
        return wrapper
