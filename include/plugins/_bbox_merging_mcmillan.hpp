  #include "gameramodule.hpp"
  #include "knnmodule.hpp"

    
  #include <string>
  #include <stdexcept>
  #include "Python.h"
  #include <list>

  using namespace Gamera;
  
        
      extern "C" {
#ifndef _MSC_VER
    void init_bbox_merging_mcmillan(void);
#endif
                }

          static PyMethodDef _bbox_merging_mcmillan_methods[] = {
                  { NULL }
  };

            
  DL_EXPORT(void) init_bbox_merging_mcmillan(void) {
    Py_InitModule(CHAR_PTR_CAST "_bbox_merging_mcmillan", _bbox_merging_mcmillan_methods);
  }
  

