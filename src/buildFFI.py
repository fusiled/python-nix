from cffi import FFI
from pathlib import Path
import pkgconfig

ffi = FFI()

def extract_cffi(fname):
    with open(fname) as f:
        contents = f.read()
        return contents[contents.index("// cffi start"):contents.index("// cffi end")]

parsed = pkgconfig.parse("nix-expr-c nix-store-c")
nix_headers = Path(parsed["include_dirs"][0])
    
def make_ffi(name, headers, libraries, includes=[], extra_header=""):
    header_content = "\n".join([extract_cffi(nix_headers / p) for p in headers])
    if extra_header:
        header_content += "\n" + extra_header

    ffi = FFI()

    for include in includes:
        ffi.include(include)

    # Define C declarations
    ffi.cdef(header_content)

    ffi.cdef("""
        extern "Python" void iter_callback(void*, char*, char*);
        const char *nix_get_string_py(struct nix_c_context *, const struct Value *);
    """)

    # Set the C source file
    ffi.set_source(name, '''
    #include "nix_api_util.h"
    #include "nix_api_store.h"
    #include "nix_api_expr.h"
    #include "nix_api_value.h"
    #include "nix_api_external.h"
    
    static void ffi_get_string_callback(const char * start, unsigned int n, void *user_data);
    static const char *nix_get_string_py(nix_c_context * context, const Value * value);
    
    void ffi_get_string_callback(const char * start, unsigned int n, void *user_data) {
       char ** str_out = (char **)user_data;
       *str_out = strndup(start, n);
    }
    
    const char *nix_get_string_py(nix_c_context * context, const Value * value) {
            char *ptr;
            nix_get_string(context, value, ffi_get_string_callback, &ptr);
            return ptr;
    }
    
    ''',
                   libraries=parsed["libraries"],
                   library_dirs=parsed["library_dirs"],
                   include_dirs=parsed["include_dirs"])
    return ffi

libutil = make_ffi("nix._nix_api_util", ["nix_api_util.h"], ["nixutilc"])
libstore = make_ffi("nix._nix_api_store", ["nix_api_store.h"], ["nixstorec"], [libutil])
libexpr = make_ffi("nix._nix_api_expr", ["nix_api_expr.h", "nix_api_value.h", "nix_api_external.h"], ["nixexprc"], [libutil, libstore], """
extern "Python" void py_nix_primop_base(void*, struct nix_c_context*, struct EvalState*, void**, void*);
extern "Python" void py_nix_finalizer(void*, void*);
extern "Python" void py_nix_external_print(void*, nix_printer*);
extern "Python" void py_nix_external_toString(void*, nix_string_return*);
extern "Python" void py_nix_external_showType(void*, nix_string_return*);
extern "Python" void py_nix_external_typeOf(void*, nix_string_return*);
extern "Python" void py_nix_external_coerceToString(void*, nix_string_context*, int, int, nix_string_return*);
extern "Python" int py_nix_external_equal(void*, void*);
""")


# Compile the CFFI extension
if __name__ == '__main__':
    libutil.compile(verbose=True)
    libstore.compile(verbose=True)
    libexpr.compile(verbose=True)
