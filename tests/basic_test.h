/* Copied from https://code.asaeppel.dev/asaeppel4231/lib-brlyt-reader/src/branch/master/src/errors/errors.c#L43 */

#define CHECK_NULL_PARAM(param_name, no) \
do{ \
    if((param_name) == NULL){ \
        fprintf(stream, LIB_NAME ": " IN_FUNC ERROR WH_HDL_SC "INVALID_POINTER_PARAM_%d: %s is null\n", __func__, no, #param_name); \
        break; \
    } \
}while(0)

/* Test */

#define CHECK_NULL_PARAM_NO_COUNT(param_name, status_code) \
do{ \
    if((param_name) == NULL){ \
        fprintf(stream, LIB_NAME ": " IN_FUNC ERROR WH_HDL_SC "%s: %s is null\n", __func__, #status_code, #param_name); \
        break; \
    } \
}while(0)
