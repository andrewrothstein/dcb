from jinja2 import BaseLoader, TemplateNotFound

class CompoundLoader(BaseLoader):

    def __init__(self, loaders) :
        self._loaders = loaders

    def get_source(self, environment, template):

        def get_source_list(loaders, environment, template):
            r = None
            if len(loaders) != 0:
                try :
                    r = loaders[0].get_source(environment, template)
                except TemplateNotFound:
                    r = get_source_list(loaders[1:], environment, template)
            return r
        
        r = get_source_list(self._loaders, environment, template)
        if r:
            return r
        else:
            raise TemplateNotFound(template)

        return get_source_list(self._loaders, environment, template)
