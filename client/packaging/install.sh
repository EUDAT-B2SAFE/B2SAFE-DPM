#!/bin/bash
#
# procedure to install the B2SAFE DPM client module using a bash script
#
# set tabstop=4
# set expandtab
#
#set -x
#
#
#
# set default parameters for installation
STATUS=0

# start default parameters for setup
IRODS_CONF_DIR=/etc/irods
#
IRODS_DIR=/var/lib/irods/iRODS
#
B2SAFE_PACKAGE_DIR=/opt/eudat/b2safe-dpm-client
#
# end default parameters for setup



########################
# Functions
########################

create_links() {

    # create new symbolic links
    echo "ln -sf $B2SAFE_PACKAGE_DIR/lib/PolicyManager.py $IRODS_DIR/server/bin/cmd/runPolicyManager.py"
    ln -sf $B2SAFE_PACKAGE_DIR/lib/PolicyManager.py $IRODS_DIR/server/bin/cmd/runPolicyManager.py

    echo "ln -sf $B2SAFE_PACKAGE_DIR/lib/Upload.py $IRODS_DIR/server/bin/cmd/uploadPolicyState.py"
    ln -sf $B2SAFE_PACKAGE_DIR/lib/Upload.py $IRODS_DIR/server/bin/cmd/uploadPolicyState.py

    return $STATUS
}


update_server_config() {

    EUDAT_SERVER_CONFIG=$IRODS_CONF_DIR/server.config

    if [ -n "$EUDAT_RULEFILES" ]
    then
       if [ ! -e ${EUDAT_SERVER_CONFIG}.org.${DATE_TODAY} ]
       then
           cp ${EUDAT_SERVER_CONFIG} ${EUDAT_SERVER_CONFIG}.org.${DATE_TODAY} 
       fi
        cat $EUDAT_SERVER_CONFIG | \
            awk -v EUDAT_RULEFILES=$EUDAT_RULEFILES '{
                if ($1 ~ /reRuleSet/) {
                    $2=$2""EUDAT_RULEFILES
                } print $0
            }' > $EUDAT_SERVER_CONFIG.new
            if [ $? -eq 0 ]
            then
                mv $EUDAT_SERVER_CONFIG.new  $EUDAT_SERVER_CONFIG
            else
                echo "ERROR: updating $EUDAT_SERVER_CONFIG failed!"
                STATUS=1
            fi
    fi

    echo "*********************************************************************"
    echo ""
    echo "Please check the file: ${EUDAT_SERVER_CONFIG} by hand                "
    echo "    grep ^reRuleSet ${EUDAT_SERVER_CONFIG}                           "
    echo ""
    echo "It should only have the following eudat{n}.re files mentioned:       "
    echo "    `cd $IRODS_CONF_DIR ; ls -C eudat*.re`       "
    echo ""
    echo "*********************************************************************"


    return $STATUS
}

update_server_config_json() {

    EUDAT_SERVER_CONFIG=$IRODS_CONF_DIR/server_config.json

    if [ -n "$EUDAT_RULEFILES" ]
    then
       if [ ! -e ${EUDAT_SERVER_CONFIG}.org.${DATE_TODAY} ]
       then
           cp ${EUDAT_SERVER_CONFIG} ${EUDAT_SERVER_CONFIG}.org.${DATE_TODAY} 
       fi
       # put json file in a single string so it easier to process.
       EUDAT_SERVER_CONFIG_JSON_STRING=`awk 1 ORS=' ' ${EUDAT_SERVER_CONFIG} | sed 's/ //g'`
       JSON_RULESET=`echo $EUDAT_SERVER_CONFIG_JSON_STRING | sed 's/.*re_rulebase_set":/re_rulebase_set":/' | sed 's/}].*$/}]/'` 
       # append rules..
       JSON_RULESET_WORK=`echo $JSON_RULESET | sed 's/]//'`
       EUDAT_RULEFILES=`echo $EUDAT_RULEFILES | sed 's/,/ /g'`
       for file in $EUDAT_RULEFILES
       do
            JSON_RULESET_WORK+=",{\"filename\":\"$file\"}"
       done
       JSON_RULESET_WORK+="]"
       # substitute the new string for the old string
       perl -pi -e "undef $/; s/re_rulebase_set[^\]]*\]/$JSON_RULESET_WORK/" $EUDAT_SERVER_CONFIG
       if [ $? -eq 0 ]
       then
            echo "The file $EUDAT_SERVER_CONFIG has been updated!"
       else
            echo "ERROR: updating $EUDAT_SERVER_CONFIG failed!"
            STATUS=1
       fi
    fi

    echo "*********************************************************************"
    echo ""
    echo "Please check the file: ${EUDAT_SERVER_CONFIG} by hand                "
    echo "    grep -A5 re_rulebase_set ${EUDAT_SERVER_CONFIG}                  "
    echo ""
    echo "It should only have the following eudat{n}.re files mentioned:       "
    echo "    `cd $IRODS_CONF_DIR ; ls -C eudat*.re`       "
    echo ""
    echo "*********************************************************************"


    return $STATUS
}

configure_irods_hooks() {

    IRODS_COREFILE=$IRODS_CONF_DIR/core.re
    TMP_FILE=/tmp/irodshooks.re
    if [ ! -e ${IRODS_COREFILE}.org.${DATE_TODAY} ]
    then
        cp $IRODS_COREFILE ${IRODS_COREFILE}.org.${DATE_TODAY} 
    fi

    status=$(awk '/acPostProcForPut/{f=1}/(\*\.replicate)|(\*\.pid\.create)/{g=1;exit}END{print g&&f ?1:0}' $IRODS_COREFILE)
    if [ $status -eq 0 ]
    then

        cat > $TMP_FILE << EOF

acPostProcForPut {
    ON(\$objPath like "\*.replicate") {
        processReplicationCommandFile(\$objPath);
    }
}
acPostProcForPut {
    ON(\$objPath like "\*.pid.create") {
        processPIDCommandFile(\$objPath);
    }
}

EOF

       if [ $? -eq 0 ]
       then
            cat $TMP_FILE $IRODS_COREFILE > $IRODS_COREFILE.new
            if [ $? -eq 0 ]
            then
                mv $IRODS_COREFILE.new  $IRODS_COREFILE
            else
                echo "ERROR: creating $IRODS_COREFILE.new failed!"
                STATUS=1
            fi
       else
            echo "ERROR: creating $TMP_FILE failed!"
            STATUS=1
       fi
    fi

    return $STATUS
}

update_irods_core_resource() {

    IRODS_COREFILE=$IRODS_CONF_DIR/core.re
    if [ ! -e ${IRODS_COREFILE}.org.${DATE_TODAY} ]
    then
        cp $IRODS_COREFILE ${IRODS_COREFILE}.org.${DATE_TODAY} 
    fi
    cat $IRODS_COREFILE | \
        awk -v DEFAULT_RESOURCE=$DEFAULT_RESOURCE '{
            if ( $1 ~ /acSetRescSchemeForCreate|acSetRescSchemeForRepl/ ) {
                $2="{msiSetDefaultResc(\""DEFAULT_RESOURCE"\",\"null\"); }"
                $0=$1" "$2
            } print $0
        }' >  $IRODS_COREFILE.new
        if [ $? -eq 0 ]
        then
            mv $IRODS_COREFILE.new  $IRODS_COREFILE
        else
            echo "ERROR: updating $IRODS_COREFILE failed!"
            STATUS=1
        fi

    return $STATUS
}

install_python_scripts() {

    for file in `find $B2SAFE_PACKAGE_DIR/cmd/* | egrep -v ".new|.org|.~" | sort `
    do
        SHORTFILE="${file##*/}"
        EXTENSION="${file##*.}"
        PYTHON_LINKFILE=$IRODS_DIR/server/bin/cmd/$SHORTFILE
        if [ -e $PYTHON_LINKFILE ]
        then
            echo "rm $PYTHON_LINKFILE"
            rm $PYTHON_LINKFILE
        fi
        echo "ln -sf $file $PYTHON_LINKFILE"
        ln -sf $file $PYTHON_LINKFILE

        # make the file executable
        if [ "$EXTENSION" == "py" ]
        then
            chmod u+x $file
        fi

    done

    return $STATUS
}

update_get_epic_api_parameters() {

    B2SAFE_LOCALFILE=$B2SAFE_PACKAGE_DIR/rulebase/local.re
    if [ ! -e ${B2SAFE_LOCALFILE}.org.${DATE_TODAY} ]
    then
        cp $B2SAFE_LOCALFILE ${B2SAFE_LOCALFILE}.org.${DATE_TODAY} 
    fi
    cat $B2SAFE_LOCALFILE | \
        awk -F= -v CRED_STORE_TYPE=$CRED_STORE_TYPE -v CRED_FILE_PATH=$CRED_FILE_PATH -v SERVER_ID=$SERVER_ID '{
            if ( $1 ~ /^ +\*credStoreType/ ) {
                $1=$1"=\""CRED_STORE_TYPE"\";"
                $2=""
            }
            if ( $1 ~ /^ +\*credStorePath/ ) {
                $1=$1"=\""CRED_FILE_PATH"\";"
                $2=""
            }
            if ( $1 ~ /^ +\*serverID/ ) {
                $1=$1"=\""SERVER_ID"\";"
                $2=""
            } print $0
        }' >  $B2SAFE_LOCALFILE.new
    if [ $? -eq 0 ]
    then
        mv $B2SAFE_LOCALFILE.new  $B2SAFE_LOCALFILE
    else
        echo "ERROR: updating $B2SAFE_LOCALFILE failed!"
        STATUS=1
    fi

    return $STATUS
}

update_credentials() {

    echo -n "enter the password belonging to the credentals of username: $USERNAME for prefix: $PREFIX :"
    read -s PASSWORD
    echo ""

    if [ ! -e ${CRED_FILE_PATH}.org.${DATE_TODAY} ]
    then
        if [ -e $CRED_FILE_PATH ]
        then
           cp $CRED_FILE_PATH ${CRED_FILE_PATH}.org.${DATE_TODAY} 
           # set access mode to file
           chmod 600 ${CRED_FILE_PATH}.org.${DATE_TODAY}
        fi
    fi

    CRED_FILE_PATH_EXAMPLE=$B2SAFE_PACKAGE_DIR/conf/credentials_example
    cat $CRED_FILE_PATH_EXAMPLE | \
        awk -v BASE_URI=$BASE_URI -v USERNAME=$USERNAME -v PREFIX=$PREFIX -v PASSWORD=$PASSWORD '{
            if ( $1 ~ /baseuri/ ) {
                $0="    \"baseuri\": \""BASE_URI"\","
            }
            if ( $1 ~ /"username/ ) {
                $0="    \"username\": \""USERNAME"\","
            }
            if ( $1 ~ /prefix/ ) {
                $0="    \"prefix\": \""PREFIX"\","
            }
            if ( $1 ~ /password/ ) {
                $0="    \"password\": \""PASSWORD"\","
            } print $0
        }' >  $CRED_FILE_PATH.new
    if [ $? -eq 0 ]
    then
        mv $CRED_FILE_PATH.new   $CRED_FILE_PATH
    else
        echo "ERROR: updating $CRED_FILE_PATH failed!"
        STATUS=1
    fi

    # set access mode to file
    chmod 600 $CRED_FILE_PATH

    return $STATUS
}

update_get_auth_parameters() {

    AUTH_MAP_PATH=$B2SAFE_PACKAGE_DIR/conf/authz.map.json
    B2SAFE_LOCALFILE=$B2SAFE_PACKAGE_DIR/rulebase/local.re
    if [ ! -e ${B2SAFE_LOCALFILE}.org.${DATE_TODAY} ]
    then
        cp $B2SAFE_LOCALFILE ${B2SAFE_LOCALFILE}.org.${DATE_TODAY} 
    fi
    cat $B2SAFE_LOCALFILE | \
        awk -F= -v AUTH_MAP_PATH=$AUTH_MAP_PATH '{
            if ( $1 ~ /^ +\*authZMapPath/ ) {
                $1=$1"=\""AUTH_MAP_PATH"\";"
                $2=""
            } print $0
        }' >  $B2SAFE_LOCALFILE.new
    if [ $? -eq 0 ]
    then
        mv $B2SAFE_LOCALFILE.new  $B2SAFE_LOCALFILE
    else
        echo "ERROR: updating $B2SAFE_LOCALFILE failed!"
        STATUS=1
    fi

    return $STATUS
}

update_authz_map_json() {
    AUTH_MAP_PATH=$B2SAFE_PACKAGE_DIR/conf/authz.map.json
    TMP_FILE=/tmp/authz.map.json
    if [ ! -e ${AUTH_MAP_PATH}.org.${DATE_TODAY} ]
    then
        cp $AUTH_MAP_PATH ${AUTH_MAP_PATH}.org.${DATE_TODAY} 
    fi

    # constrict a list of users to fill in the userlist
    let count=0
    for user in $USERS 
    do
        if [ "$count" -lt "1" ]
        then
            userlist=$user
        else
            userlist+="\",\"$user"
        fi
    let count=$count+1
    done

    cat > $TMP_FILE << EOF
{
"assertion 1":
	{ "subject":
		[ "$userlist" ],
	  "action":
		[ "read" ],
	  "target":
		[ "${IRODS_DIR}/server/bin/cmd/*","${B2SAFE_PACKAGE_DIR}/conf/*" ]
	}
}

EOF
    if [ $? -eq 0 ]
    then
        mv $TMP_FILE $AUTH_MAP_PATH
        if [ ! $? -eq 0 ]
        then
            echo "ERROR: moving $AUTH_MAP_PATH failed!"
            STATUS=1
        fi
    else
        echo "ERROR: creating $TMP_FILE failed!"
        STATUS=1
    fi

    # set access mode to file
    chmod 600 $AUTH_MAP_PATH

    return $STATUS
}

update_get_log_parameters() {

    LOG_MANAGER_CONF=$B2SAFE_PACKAGE_DIR/conf/log.manager.conf
    B2SAFE_LOCALFILE=$B2SAFE_PACKAGE_DIR/rulebase/local.re
    if [ ! -e ${B2SAFE_LOCALFILE}.org.${DATE_TODAY} ]
    then
        cp $B2SAFE_LOCALFILE ${B2SAFE_LOCALFILE}.org.${DATE_TODAY} 
    fi
    cat $B2SAFE_LOCALFILE | \
        awk -F= -v LOG_MANAGER_CONF=$LOG_MANAGER_CONF '{
            if ( $1 ~ /^ +\*logConfPath/ ) {
                $1=$1"=\""LOG_MANAGER_CONF"\";"
                $2=""
            } print $0
        }' >  $B2SAFE_LOCALFILE.new
    if [ $? -eq 0 ]
    then
        mv $B2SAFE_LOCALFILE.new  $B2SAFE_LOCALFILE
    else
        echo "ERROR: updating $B2SAFE_LOCALFILE failed!"
        STATUS=1
    fi

    return $STATUS
}

update_log_manager_conf() {

    LOG_MANAGER_CONF=$B2SAFE_PACKAGE_DIR/conf/log.manager.conf

    if [ ! -e ${LOG_MANAGER_CONF}.org.${DATE_TODAY} ]
    then
        cp $LOG_MANAGER_CONF ${LOG_MANAGER_CONF}.org.${DATE_TODAY} 
    fi

    cat $LOG_MANAGER_CONF | \
        awk -v LOG_LEVEL=$LOG_LEVEL -v LOG_DIR=$LOG_DIR '{
            if ( $1 ~ /log_level/ ) {
                $0="\"log_level\": \""LOG_LEVEL"\","
            }
            if ( $1 ~ /log_dir/ ) {
                $0="\"log_dir\": \""LOG_DIR"\","
            } print $0
        }' >  $LOG_MANAGER_CONF.new
    if [ $? -eq 0 ]
    then
        mv $LOG_MANAGER_CONF.new   $LOG_MANAGER_CONF
    else
        echo "ERROR: updating $LOG_MANAGER_CONF failed!"
        STATUS=1
    fi

    return $STATUS
}


########################
# main program
########################


#
# create symbolic links to the eudat rulebase
#
if [ $? -eq 0 ]
then
    echo "create_links"
    create_links
fi

exit

#
# configure iRODS hooks
#
if [ $? -eq 0 ]
then
    echo "configure_irods_hooks"
    configure_irods_hooks
fi

#
# properly configure the default resource in /etc/irods/core.re
#
if [ $? -eq 0 ]
then
    echo "update_irods_core_resource"
    update_irods_core_resource
fi

#
# install python scripts
#
if [ $? -eq 0 ]
then
    echo "install_python_scripts"
    install_python_scripts
fi

#
# update the 'getEpicApiParameters' rule in '/opt/eudat/b2safe/rulebase/local.re'
#
if [ $? -eq 0 ]
then
    echo "update_get_epic_api_parameters"
    update_get_epic_api_parameters
fi

#
# Set the proper values in the credentials file
#
if [ $? -eq 0 ]
then
    echo "update_credentials"
    update_credentials
fi

#
# update the 'getAuthZParameters' rule in '/opt/eudat/b2safe/rulebase/local.re'
# update authz.map.json
#
if [ $? -eq 0 ]
then
    echo "update_authz_map_json"
    update_get_auth_parameters
    #update_authz_map_json
fi

#
# update the "getLogParameters" rule in "/opt/eudat/b2safe/rulebase/local.re"
# update log.manager.conf
#
if [ $? -eq 0 ]
then
    echo "update_log_manager_conf"
    update_get_log_parameters
    update_log_manager_conf
fi

#
# create a shared space in all zones as configured in the eudat.re rulebase getSharedCollection function.
#


