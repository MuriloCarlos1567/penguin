from inspect import signature
import re


class Parser:
    @staticmethod
    def request_parser(request):
        match = re.match(r"(\w+)\s+(/[\w/]*)\s+(\S+)", request)
        if not match:
            raise Exception("Unexpected router error")
        method, route, _ = match.groups()
        return method, route

    @classmethod
    def path_matches(cls, defined_path, actual_path):
        actual_path = actual_path.rstrip("/")
        defined_path = defined_path.rstrip("/")
        defined_path_parts = defined_path.split("/")
        actual_path_parts = actual_path.split("/")

        if len(defined_path_parts) != len(actual_path_parts):
            return False

        for defined_part, actual_part in zip(defined_path_parts, actual_path_parts):
            if defined_part.startswith("{") and defined_part.endswith("}"):
                continue
            elif defined_part != actual_part:
                return False

        return True

    @classmethod
    def get_param_value(cls, request_line, declared_path, dead_list):
        _, path = request_line[0], request_line[1]
        path = path.rstrip("/")
        _declared_path = declared_path[1].rstrip("/")

        path_parts = path.split("/")
        declared_path_parts = _declared_path.split("/")
        param_value = None

        if len(path_parts) == len(declared_path_parts):
            for i, part in enumerate(declared_path_parts):
                if len(part) and part[0] == "{" and part[-1] == "}":
                    if declared_path_parts[i] in dead_list:
                        continue
                    param_value = path_parts[i]
                    break
        return param_value

    @classmethod
    def get_params(cls, route_function, request_line, declared_path, json_body):
        func_signature = signature(route_function)
        params = {}
        dead_list = set()

        for param_name, _ in func_signature.parameters.items():
            if param_name in ["self"]:
                continue

            param_value = (
                json_body
                if param_name == "body"
                else cls.get_param_value(request_line, declared_path, dead_list)
            )
            params[param_name] = param_value

            if param_name is not None:
                dead_list.add(param_name)

        return params
