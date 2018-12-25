from jinja2 import BaseLoader, TemplateNotFound
from typing import List


class CompoundLoader(BaseLoader):

    def __init__(self, loaders: List[BaseLoader]):
        self._loaders = loaders

    def get_source(self, environment, template):

        def get_source_list(loaders, e, t):
            if len(loaders) != 0:
                try:
                    return loaders[0].get_source(e, t)
                except TemplateNotFound:
                    return get_source_list(loaders[1:], e, t)
            return None
        
        r = get_source_list(self._loaders, environment, template)
        if r:
            return r
        else:
            raise TemplateNotFound(template)
