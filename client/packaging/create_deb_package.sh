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
VERS_CONFIG=./version.sh

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

if [ -e $VERS_CONFIG ]
then
	. $VERS_CONFIG
else
	echo "ERROR: $VERS_CONFIG not present!"
	exit 1
fi
PACKAGE="${PRODUCT}_${VERSION}-${SUB_VERS}"



# create build directory's
mkdir -p $RPM_BUILD_ROOT${PACKAGE}
rm -rf   $RPM_BUILD_ROOT${PACKAGE}/*

# create package directory's
mkdir -p $RPM_BUILD_ROOT${PACKAGE}${IRODS_PACKAGE_DIR}/conf
mkdir -p $RPM_BUILD_ROOT${PACKAGE}${IRODS_PACKAGE_DIR}/lib

# copy files and images
cp $RPM_SOURCE_DIR/conf/*          $RPM_BUILD_ROOT${PACKAGE}${IRODS_PACKAGE_DIR}/conf
cp $RPM_SOURCE_DIR/lib/*           $RPM_BUILD_ROOT${PACKAGE}${IRODS_PACKAGE_DIR}/lib
cp $RPM_SOURCE_DIR/../schema/*.xsd $RPM_BUILD_ROOT${PACKAGE}${IRODS_PACKAGE_DIR}/conf

# set mode of specific files
chmod 600 $RPM_BUILD_ROOT${PACKAGE}${IRODS_PACKAGE_DIR}/conf/*.ini
chmod 700 $RPM_BUILD_ROOT${PACKAGE}${IRODS_PACKAGE_DIR}/lib/*.py
chmod 600 $RPM_BUILD_ROOT${PACKAGE}${IRODS_PACKAGE_DIR}/conf/*.xsd

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
B2SAFE DPM client are a set of scripts to implement policies in iRODS.

EOF

# create postinstall scripts
cat > $RPM_BUILD_ROOT${PACKAGE}/DEBIAN/postinst << EOF
# create symbolic links
if [ -e "/var/lib/irods/iRODS/server/bin/cmd" ]
then
    ln -sf ${IRODS_PACKAGE_DIR}/lib/PolicyManager.py /var/lib/irods/iRODS/server/bin/cmd/runPolicyManager.py
    ln -sf ${IRODS_PACKAGE_DIR}/lib/Upload.py /var/lib/irods/iRODS/server/bin/cmd/uploadPolicyState.py
fi

# show package installation/configuration info 
cat << EOF1

To install/configure b2saef dpm client in iRODS do following as the user "$USERNAME" :

su - $USERNAME
cd ${IRODS_PACKAGE_DIR}/conf
# update config.ini with correct parameters with your favorite editor

EOF1

EOF

#make sure the file is executable
chmod +x  $RPM_BUILD_ROOT${PACKAGE}/DEBIAN/postinst


# build rpm
dpkg-deb --build $RPM_BUILD_ROOT${PACKAGE}

# done..