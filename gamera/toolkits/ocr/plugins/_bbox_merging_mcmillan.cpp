
        
    
  #include "gameramodule.hpp"
  #include "knnmodule.hpp"

    
    #include <string>
  #include <stdexcept>
  #include "Python.h"
  #include <list>

  using namespace Gamera;
  
        
    #ifndef _MSC_VER
  extern "C" {
    void init_bbox_merging_mcmillan(void);
  }
#endif

            
          static PyMethodDef _bbox_merging_mcmillan_methods[] = {
                  { nullptr }
  };
  
  static struct PyModuleDef module_bbox_merging_mcmillanDef = {
        PyModuleDef_HEAD_INIT,
        "_bbox_merging_mcmillan",
        nullptr,
        -1,
        _bbox_merging_mcmillan_methods,
        nullptr,
        nullptr,
        nullptr,
        nullptr
  };


  PyMODINIT_FUNC PyInit__bbox_merging_mcmillan(void) {
    return PyModule_Create(&module_bbox_merging_mcmillanDef);
  }
  

