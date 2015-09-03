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
%define _irodsUID %(id -un `whoami`)
%define _irodsGID %(id -gn `whoami`)
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
mkdir -p $RPM_BUILD_ROOT%{_irodsPackage}/conf
mkdir -p $RPM_BUILD_ROOT%{_irodsPackage}/lib

cp $RPM_SOURCE_DIR/client/conf/* $RPM_BUILD_ROOT%{_irodsPackage}/conf
cp $RPM_SOURCE_DIR/client/lib/* $RPM_BUILD_ROOT%{_irodsPackage}/lib
cp $RPM_SOURCE_DIR/schema/*.xsd $RPM_BUILD_ROOT%{_irodsPackage}/conf

 

# cleanup
%clean
rm -rf %{buildroot}


#provide files to rpm. Set attributes 
%files
# default attributes
%defattr(-,%{_irodsUID},%{_irodsUID},-)
# files
%{_irodsPackage}/lib
%{_irodsPackage}/conf
# attributes on files and directory's
%attr(-,%{_irodsUID},%{_irodsGID})   %{_irodsPackage}
%attr(600,%{_irodsUID},%{_irodsGID}) %{_irodsPackage}/conf/*.ini
%attr(600,%{_irodsUID},%{_irodsGID}) %{_irodsPackage}/conf/*.xsd
%attr(700,%{_irodsUID},%{_irodsGID}) %{_irodsPackage}/lib/*.py
%doc
# config files
%config(noreplace) %{_irodsPackage}/conf/config.ini

%post
# symbolic link creation
if [ -e "/var/lib/irods/iRODS/server/bin/cmd" ]
then
    ln -sf %{_irodsPackage}/lib/PolicyManager.py /var/lib/irods/iRODS/server/bin/cmd/runPolicyManager.py
    ln -sf %{_irodsPackage}/lib/Upload.py /var/lib/irods/iRODS/server/bin/cmd/uploadPolicyState.py
fi
# only show info on first installation
if [ "$1" = "1" ]
then 
# show actions to do after installation
cat << EOF

To install/configure b2safe dpm client in iRODS do following as the user %{_irodsUID} : 

su - %{_irodsUID}
cd %{_irodsPackage}/conf
# update config.ini with correct parameters with your favorite editor

EOF
fi

%postun
# symbolic link deletion after last rpm deletion
if [ "$1" = "0" ]
then 
    if [ -e "/var/lib/irods/iRODS/server/bin/cmd" -a "$1" -eq "0"  ]
    then
        rm -f /var/lib/irods/iRODS/server/bin/cmd/runPolicyManager.py
        rm -f /var/lib/irods/iRODS/server/bin/cmd/uploadPolicyState.py
    fi
fi
%changelog
* Wed Aug 12 2015  Robert Verkerk <robert.verkerk@surfsara.nl> 1.0
- Initial version of b2safe dpm client package
