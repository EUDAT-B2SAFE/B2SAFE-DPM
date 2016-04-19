Name:		irods-eudat-b2safe-dpm-client
Version:	%{_version}
Release:	%{_release}
#Release:	1%{?dist}
Summary:	b2safe dpm client application for iRODS v4

Group:		Application
License:	open BSD License
URL:		http://www.eudat.eu/b2safe
BuildArch:	noarch
#Source0:	
BuildRoot:	%(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

#BuildRequires:	
Requires:	irods-icat

%define _whoami %(whoami)
%define _b2safehomepackaging %(pwd)
%define _irodsPackage /opt/eudat/b2safe-dpm-client
 
%description
B2SAFE DPM client are a set of scripts to implement policies in iRODS.


# get all our source code in the $RPM_SOURCE_DIR
%prep
echo "the spec file directory is %{_b2safehomepackaging}"
echo "The user that built this is %{_whoami}"
# create string where git repo is started..
workingdir=`pwd`
cd %{_b2safehomepackaging}
cd ../..
b2safehome=`pwd`
cd $workingdir
# empty source directory and copy new files
rm -rf $RPM_SOURCE_DIR/*
cp -ar $b2safehome/* $RPM_SOURCE_DIR

# build images. We don't have to make them so exit
%build
exit 0


# put images in correct place
%install
rm -rf %{buildroot}
mkdir -p $RPM_BUILD_ROOT%{_irodsPackage}/cmd
mkdir -p $RPM_BUILD_ROOT%{_irodsPackage}/conf
mkdir -p $RPM_BUILD_ROOT%{_irodsPackage}/rules
mkdir -p $RPM_BUILD_ROOT%{_irodsPackage}/output
mkdir -p $RPM_BUILD_ROOT%{_irodsPackage}/test

cp $RPM_SOURCE_DIR/client/cmd/* $RPM_BUILD_ROOT%{_irodsPackage}/cmd
cp $RPM_SOURCE_DIR/client/conf/* $RPM_BUILD_ROOT%{_irodsPackage}/conf
cp $RPM_SOURCE_DIR/client/test/* $RPM_BUILD_ROOT%{_irodsPackage}/test
cp $RPM_SOURCE_DIR/schema/*.xsd $RPM_BUILD_ROOT%{_irodsPackage}/conf

mkdir -p $RPM_BUILD_ROOT/var/log/irods

touch $RPM_BUILD_ROOT%{_irodsPackage}/cmd/toBeExcludedFile.pyc
touch $RPM_BUILD_ROOT%{_irodsPackage}/cmd/toBeExcludedFile.pyo


# cleanup
%clean
rm -rf %{buildroot}


#provide files to rpm. Set attributes 
%files
# default attributes
%defattr(-,-,-,-)
# files
# exclude .pyc and .py files
%exclude %{_irodsPackage}/cmd/*.pyc
%exclude %{_irodsPackage}/cmd/*.pyo
#include files
%{_irodsPackage}/cmd
%{_irodsPackage}/conf
%{_irodsPackage}/output
%{_irodsPackage}/rules
%{_irodsPackage}/test
# attributes on files and directory's
%attr(-,-,-)   %{_irodsPackage}
%attr(700,-,-) %{_irodsPackage}/cmd/*.py
%attr(600,-,-) %{_irodsPackage}/conf/*.ini
%attr(600,-,-) %{_irodsPackage}/conf/*.xsd
%attr(600,-,-) %{_irodsPackage}/test/*.xml
%attr(-,-,-)   /var/log/irods
%doc
# config files
%config(noreplace) %{_irodsPackage}/conf/config.ini

%post
# symbolic link creation
if [ -e "/var/lib/irods/iRODS/server/bin/cmd" ]
then
    ln -sf %{_irodsPackage}/cmd/PolicyManager.py /var/lib/irods/iRODS/server/bin/cmd/runPolicyManager.py
fi
# only show info on first installation
if [ "$1" = "1" ]
then 
# show actions to do after installation
cat << EOF

To install/configure b2safe dpm client in iRODS do following as the user who runs iRODS : 

source /etc/irods/service_account.config
su - \$IRODS_SERVICE_ACCOUNT_NAME
cd %{_irodsPackage}/conf
# update config.ini with correct parameters with your favorite editor

EOF
fi

# set owner of files to the user who run's iRODS
IRODS_SERVICE_ACCOUNT_CONFIG=/etc/irods/service_account.config
if [ -e $IRODS_SERVICE_ACCOUNT_CONFIG ]
then
    source $IRODS_SERVICE_ACCOUNT_CONFIG
    chown -R $IRODS_SERVICE_ACCOUNT_NAME:$IRODS_SERVICE_GROUP_NAME %{_irodsPackage}
    chown -R $IRODS_SERVICE_ACCOUNT_NAME:$IRODS_SERVICE_GROUP_NAME /var/log/irods
    chown -R $IRODS_SERVICE_ACCOUNT_NAME:$IRODS_SERVICE_GROUP_NAME /var/lib/irods/iRODS/server/bin/cmd/runPolicyManager.py
fi


%postun
# symbolic link deletion after last rpm deletion
if [ "$1" = "0" ]
then 
    if [ -e "/var/lib/irods/iRODS/server/bin/cmd" -a "$1" -eq "0"  ]
    then
        rm -f /var/lib/irods/iRODS/server/bin/cmd/runPolicyManager.py
    fi
fi
%changelog
* Wed Aug 12 2015  Robert Verkerk <robert.verkerk@surfsara.nl> 1.0
- Initial version of b2safe dpm client package
