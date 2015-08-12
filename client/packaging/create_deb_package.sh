#!/bin/bash
#
#set -x

USERNAME=`whoami`
IRODSUID=`id -un $USERNAME`
IRODSGID=`id -gn $USERNAME`
B2SAFEHOMEPACKAGING="$(cd $(dirname "$0"); pwd)"
B2SAFEHOME=`dirname $B2SAFEHOMEPACKAGING`
RPM_BUILD_ROOT="${HOME}/debbuild/"
RPM_SOURCE_DIR=$B2SAFEHOME
PRODUCT="irods-eudat-b2safe-dpm-client"
IRODS_PACKAGE_DIR=`grep -i _irodsPackage ${PRODUCT}.spec | head -n 1 | awk '{print $3}'`
INSTALL_CONFIG=./version.sh

if [ "$USERNAME" = "root" ]
then
	echo "We are NOT allowed to run as root, exit"
        echo "Run this script/procedure as the user who run's iRODS"
	exit 1
fi

# check existence of rpmbuild
which dpkg-deb > /dev/null 2>&1
STATUS=$?

if [ $STATUS -gt 0 ]
then
	echo "Please install dpkg-deb. It is not present at the machine"
	exit 1
fi 

if [ -e $INSTALL_CONFIG ]
then
	. $INSTALL_CONFIG
else
	echo "ERROR: $INSTALL_CONFIG not present!"
	exit 1
fi
PACKAGE="${PRODUCT}_${VERSION}-${SUB_VERS}"



# create build directory's
mkdir -p $RPM_BUILD_ROOT${PACKAGE}
rm -rf   $RPM_BUILD_ROOT${PACKAGE}/*

# create package directory's
mkdir -p $RPM_BUILD_ROOT${PACKAGE}${IRODS_PACKAGE_DIR}/conf
mkdir -p $RPM_BUILD_ROOT${PACKAGE}${IRODS_PACKAGE_DIR}/lib
mkdir -p $RPM_BUILD_ROOT${PACKAGE}${IRODS_PACKAGE_DIR}/packaging

# copy files and images
cp $RPM_SOURCE_DIR/conf/*         $RPM_BUILD_ROOT${PACKAGE}${IRODS_PACKAGE_DIR}/conf
cp $RPM_SOURCE_DIR/lib/*          $RPM_BUILD_ROOT${PACKAGE}${IRODS_PACKAGE_DIR}/lib
cp $RPM_SOURCE_DIR/packaging/install.sh $RPM_BUILD_ROOT${PACKAGE}${IRODS_PACKAGE_DIR}/packaging

# set mode of specific files
chmod 600 $RPM_BUILD_ROOT${PACKAGE}${IRODS_PACKAGE_DIR}/conf/*.ini
chmod 700 $RPM_BUILD_ROOT${PACKAGE}${IRODS_PACKAGE_DIR}/lib/*.py
chmod 700 $RPM_BUILD_ROOT${PACKAGE}${IRODS_PACKAGE_DIR}/packaging/*.sh

# create packaging directory
mkdir -p  $RPM_BUILD_ROOT${PACKAGE}/DEBIAN

# create control file
cat > $RPM_BUILD_ROOT${PACKAGE}/DEBIAN/control << EOF

Package: $PRODUCT
Version: ${VERSION}-${RELEASE}
Section: unknown
Priority: optional
Architecture: all
Depends: irods-icat (>= 4.0.0)
Maintainer: Robert Verkerk <robert.verkerk@surfsara.nl>
Description: B2SAFE DPM client for iRODS package
 B2SAFE DPM client allows policy management in iRODS for eudat.

EOF

# create postinstall scripts
cat > $RPM_BUILD_ROOT${PACKAGE}/DEBIAN/postinst << EOF

# show package installation/configuration info 
cat << EOF1

The package b2safe DPM client has been installed in ${IRODS_PACKAGE_DIR}.
To install/configure it in iRODS do following as the user "$USERNAME" which runs iRODS 

su - $USERNAME
cd ${IRODS_PACKAGE_DIR}/conf
# update config.ini with correct parameters with your favorite editor
cd ${IRODS_PACKAGE_DIR}/packaging
./install.sh

EOF1

EOF

#make sure the file is executable
chmod +x  $RPM_BUILD_ROOT${PACKAGE}/DEBIAN/postinst


# build rpm
dpkg-deb --build $RPM_BUILD_ROOT${PACKAGE}

# done..
