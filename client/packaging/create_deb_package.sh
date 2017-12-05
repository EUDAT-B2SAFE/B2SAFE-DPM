#!/bin/bash
#
#set -x

USERNAME=`whoami`
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
        echo "Run this script/procedure as any user except root"
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
mkdir -p $RPM_BUILD_ROOT${PACKAGE}${IRODS_PACKAGE_DIR}/cmd
mkdir -p $RPM_BUILD_ROOT${PACKAGE}${IRODS_PACKAGE_DIR}/conf
mkdir -p $RPM_BUILD_ROOT${PACKAGE}${IRODS_PACKAGE_DIR}/output
mkdir -p $RPM_BUILD_ROOT${PACKAGE}${IRODS_PACKAGE_DIR}/rules
mkdir -p $RPM_BUILD_ROOT${PACKAGE}${IRODS_PACKAGE_DIR}/test

# copy files and images
cp $RPM_SOURCE_DIR/cmd/*           $RPM_BUILD_ROOT${PACKAGE}${IRODS_PACKAGE_DIR}/cmd
cp $RPM_SOURCE_DIR/conf/*          $RPM_BUILD_ROOT${PACKAGE}${IRODS_PACKAGE_DIR}/conf
cp $RPM_SOURCE_DIR/test/*          $RPM_BUILD_ROOT${PACKAGE}${IRODS_PACKAGE_DIR}/test
cp $RPM_SOURCE_DIR/../schema/*.xsd $RPM_BUILD_ROOT${PACKAGE}${IRODS_PACKAGE_DIR}/conf

mkdir -p                          $RPM_BUILD_ROOT${PACKAGE}/var/log/irods

# set mode of specific files
chmod 700 $RPM_BUILD_ROOT${PACKAGE}${IRODS_PACKAGE_DIR}/cmd/*.py
chmod 600 $RPM_BUILD_ROOT${PACKAGE}${IRODS_PACKAGE_DIR}/conf/*.ini
chmod 600 $RPM_BUILD_ROOT${PACKAGE}${IRODS_PACKAGE_DIR}/conf/*.xsd
chmod 600 $RPM_BUILD_ROOT${PACKAGE}${IRODS_PACKAGE_DIR}/rules/*.xml

# create packaging directory
mkdir -p  $RPM_BUILD_ROOT${PACKAGE}/DEBIAN

# create control file
cat > $RPM_BUILD_ROOT${PACKAGE}/DEBIAN/control << EOF

Package: $PRODUCT
Version: ${VERSION}-${RELEASE}
Section: unknown
Priority: optional
Architecture: all
Depends: irods-icat (>= 4.0.0) | irods-server (>= 4.2.0) | irods-icommands (>= 4.2.0)
Maintainer: Robert Verkerk <robert.verkerk@surfsara.nl>
Description: B2SAFE DPM client for iRODS package
B2SAFE DPM client are a set of scripts to implement policies in iRODS.

EOF

# create postinstall scripts
cat > $RPM_BUILD_ROOT${PACKAGE}/DEBIAN/postinst << EOF
#!/bin/bash
# create symbolic links
IRODS_DIR=/var/lib/irods
if [ -e "\${IRODS_DIR}/msiExecCmd_bin" ]
then
  IRODS_LINK_DIR="\${IRODS_DIR}/msiExecCmd_bin"
else
  IRODS_LINK_DIR="\${IRODS_DIR}/iRODS/server/bin/cmd"
fi 
ln -sf ${IRODS_PACKAGE_DIR}/cmd/PolicyManager.py \${IRODS_LINK_DIR}/runPolicyManager.py

# show package installation/configuration info 
cat << EOF1

The package b2safe dpm client has been installed in ${IRODS_PACKAGE_DIR}
To install/configure it in iRODS do following as the user who runs iRODS :

# update config.ini with correct parameters with your favorite editor
sudo vi ${IRODS_PACKAGE_DIR}/conf/config.ini

EOF1

# set owner of files to the user who run's iRODS
IRODS_SERVICE_ACCOUNT_CONFIG=/etc/irods/service_account.config
if [ -e \$IRODS_SERVICE_ACCOUNT_CONFIG ]
then
    source \$IRODS_SERVICE_ACCOUNT_CONFIG
    chown -R \$IRODS_SERVICE_ACCOUNT_NAME:\$IRODS_SERVICE_GROUP_NAME ${IRODS_PACKAGE_DIR} 
    chown -R \$IRODS_SERVICE_ACCOUNT_NAME:\$IRODS_SERVICE_GROUP_NAME /var/log/irods
    chown -R \$IRODS_SERVICE_ACCOUNT_NAME:\$IRODS_SERVICE_GROUP_NAME \${IRODS_LINK_DIR}/runPolicyManager.py
fi

EOF

#make sure the file is executable
chmod +x  $RPM_BUILD_ROOT${PACKAGE}/DEBIAN/postinst


# build rpm
dpkg-deb --build $RPM_BUILD_ROOT${PACKAGE}

# done..
