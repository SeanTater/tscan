tscan
-----
Image tools for speeding up scanning


Requirements
------------
It's not on PyPI yet. (It's not complete enough)

But when it does become available, you will need to install _opencv2_. Not
pyopencv, or opencv-cython - but the one actually part of the opencv project.

On Ubuntu, you can install it via
    sudo apt-get install python-opencv

Then in the source package, 
    ./setup.py install

But this isn't a permanent solution (for one thing, you can't uninstall it).
We'll have a PyPI package soon.
