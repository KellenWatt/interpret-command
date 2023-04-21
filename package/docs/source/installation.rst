Installation
============


.. tab:: Windows

    To install the Interpreter Command, run the command

    .. code-block:: sh
        
        py -3 -m pip install interpreter-command

    To upgrade to the latest version, run

    .. code-block:: sh

        py -3 -m pip install --upgrade interpreter-command

    To verify installation, you can either run 

    .. code-block:: sh 

        py -3 -m pip list 
        
    and check for interpreter-command in the list, or run

    .. code-block:: sh

        py -3 -c "import interpretercommand"

    If there aren't any errors, then the package has been installed
    
.. tab:: macOS/Linux

    To install the Interpreter Command, run the command

    .. code-block:: sh

        pip3 install interpreter-command
    
    To upgrade to the latest version, run

    .. code-block:: sh

        pip3 install --upgrade interpreter-command
    
    
    To verify installation, you can either run 
    

    .. code-block:: sh 

        pip3 list | grep "interpreter-command"

    If there is output, then the package is installed.

    .. code-block:: sh

        python3 -c "import interpretercommand"

    If there aren't any errors, then the package has been installed


The interpreter-command package has been tested on Windows 10 and macOS 13.1 (Ventura), but should work on 
any system that RobotPy is supported. This package is written in pure Python.


Next, let's `cover the basics <basics>`_ of usage.


