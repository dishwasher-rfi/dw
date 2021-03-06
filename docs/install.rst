========================
Installation (GNU/Linux)
========================

Debian 8 (Jessie)
=================

Install required packages using apt (or any other equivalent tool)
from the main system repository. All the needed dependencies will be installed::

    # apt-get install python-guiqwt python-guidata python-tables python-astropy python-pywt libgsl0ldbl libgsl0-dev libtool libtool-bin autoconf automake autotools-dev pkg-config

install dw::

    # python setup.py install

Debian 7 (Wheezy)
=================

Install guidata and guiqwt using apt (or any other equivalent tool)
from the main system repository. This will install the dependencies for the
two packages::

    # apt-get install python-guiqwt python-guidata


Install proper version of cython, guidata, guiqwt and pytables using pip::

    # pip install Cython
    # pip install guidata==1.6.1
    # pip install guiqwt==2.3.1
    # pip install tables==3.1.1
    # pip install astropy

Install dw

CentOS 6
========

EPEL repository
---------------

Add epel repository::

    # rpm -ivh http://dl.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm

System packages
---------------

Install the following rpm packages using::

    # yum install rpm-package-name
    qt
    qt-devel
    python-pip
    gcc
    PyQt4
    PyQt4-devel
    python-devel
    hdf5
    hdf5-devel
    blas
    blas-devel
    lapack
    lapack-devel
    Cython
    sip
    sip-devel

Python packages
---------------

Intstall the following python packages using::

    # pip install python-package-name
    numpy==1.9.0
    h5py==2.3.1
    spyder==2.3.1
    scipy==0.14.0
    numexpr==2.4
    PIL==1.1.7
    guidata==1.6.1

Install QWT
-----------

Download qwt 5.2 from
http://sourceforge.net/p/qwt/code/HEAD/tarball?path=/branches/qwt-5.2

Unzip the archive::

    #unzip qwt-code-2046-branches-qwt-5.2.zip

Compile and install::

    #qmake qwt.pro
    #make
    #make install


Install PyQwt
-------------

Download PyQwt 5.2 from
http://sourceforge.net/projects/pyqwt/files/pyqwt5/PyQwt-5.2.0/PyQwt-5.2.0.tar.gz/download?use_mirror=garr&download=

Untar the archive::

    # tar xfv PyQwt-5.2.0.tar.gz

Compile and install::

    # cd PyQwt-5.2.0
    # cd configure
    # python configure.py -Q ../qwt-5.2
    # make
    # make install

Install Guiqwt
--------------

Install guiqwt using::

    # pip install guiqwt==2.3.1


Install dw

CentOS/Scientific Linux 5
=========================
To Do

Ubuntu 14.04 LTS (Trusty Tahr)
==============================

Install required packages using apt (or any other equivalent tool)
from the main system repository. All the needed dependencies will be installed::

    # apt-get install python-guiqwt python-guidata python-tables python-pywt libgsl0ldbl libgsl0-dev libtool autoconf automake autotools-dev pkg-config
    
install dw::

    # python setup.py install    

Ubuntu 12.04 LTS (Precise Pangolin)
===================================

Install guidata and guiqwt using apt (or any other equivalent tool)
from the main system repository. This will install the dependencies for the
two packages::

    # apt-get install python-guiqwt python-guidata

System packages
---------------

Install the following system packages using apt (or any other equivalent tool)::

    # apt-get install package-name
    python-tables
    python-pip
    cython
    libhdf5-serial-dev

Python packages
---------------

Intstall the following python packages using::

    # pip install python-package-name
    numexpr==2.4
    tables==3.1.1
    guidata==1.6.1
    guiqwt==2.3.1

Install dw
