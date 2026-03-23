"""
Monkey patch for pkg_resources in Python 3.13+
"""
try:
    import pkg_resources
except ImportError:
    import importlib_resources as pkg_resources
    # Add resource_filename compatibility
    def resource_filename(package, resource):
        import importlib.resources
        with importlib.resources.files(package) as files:
            return str(files.joinpath(resource))
    
    pkg_resources.resource_filename = resource_filename
