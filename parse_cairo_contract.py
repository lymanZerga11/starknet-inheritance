'''
Parse a .cairo contract into the following data structure:

{
    inherits: List[str]
    lang: str
    builtins: List[str]
    imports: List[Dict{
        package_name: List[str] <- imports
    }]
    storage_vars: List[Dict{
        name: str
        inputs: List[str]
        outputs: List[str]
        raw_text: str
    }
    constructor: Dict{
        inputs: List[str]
        raw_text: str
    }
    functions: List[Dict{
        name: str
        inputs: List[str]
        outputs: List[str]
        raw_text: str
    }

}