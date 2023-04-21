.. interpreter-command documentation master file, created by
   sphinx-quickstart on Sun Mar 19 11:25:09 2023.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Interpreter Command Suite
=========================

.. toctree::
   :maxdepth: 2
   :caption: Fundamentals
   :hidden:

   installation
   basics
   commands
   conditions

.. toctree::
   :maxdepth: 2
   :caption: Advanced Usage
   :hidden:

   advanced/dispatchers
   advanced/parsers
   advanced/conditions

.. toctree::
   :caption: API

   api
   


Welcome! The Interpreter Command suite provides a way to create `Domain-specific Languages <https://en.wikipedia.org/wiki/Domain-specific_language>`_ 
to control any aspect of a robot's behaviour. Ostensibly, this can be used to generate autonomous routines on-the-fly,
but this can be used anywhere that complex, sequential behaviours are useful.

This software is designed to be used with `RobotPy <https://robotpy.readthedocs.io/en/stable/>`_ and 
`WPILib <https://docs.wpilib.org/en/stable/index.html>`_. Use outside of these contexts probably won't work.

These docs assume that you have reasonable familiarity with Python and the WPILib Command-based framework. As such, we will not 
explain the basics of these unless doing so helps illustrate a point.

Let's start by :doc:`installing the package <installation>`!


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
