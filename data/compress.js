/* I am compressable */

(function(){
     /* descriptive comment */
     window.NameSpace = {};
     var long_internal_var = [1,2,3,4];
     //incidental comment
     var long_internal_var2 = [long_internal_var, long_internal_var];
     window.NameSpace.extra_var = long_internal_var2;
 })();

Namespace.Node = {
    class_var: 5,
    /* descriptive comment */
    api_method:function(some_argument){
        var long_name_var = some_argument + 1;
        return long_name_var;
    },
    /* descriptive comment */
    api_method2:function(some_argument){
        //incidental comment
        return this.api_method(some_argument) + this.class_var;
    }
};