#!/bin/bash
#
# 
# 

function intro() { 
	echo -e "x-tenancy-migrator v0.1"
	echo -e "x-tenancy-migrator new run:" > migration.log
	date &> migration.log
}


function readini() {
	echo -en "Reading config.ini..."
	source config.ini
	echo -e "completed" 
	echo -e 
	echo Source Boot Volume Group OCID: ${VOLUMEGROUP}
    echo Target Compartment OCID: ${TARGETCOMPARTMENT}
	echo -e
	echo -e
}

function getbootvolumeinfo() {
    echo -en "Getting boot volume info from volume group..." 
	bootVolumes=$(oci bv boot-volume list --volume-group-id "$VOLUMEGROUP" 2>>migration.log)
	if [ "$?" != "0" ]; then 
		echo "Error encountered:" $bootVolumes
		exit 1
	fi
	#echo $bootVolumes

    while IFS=$'\t' read -r id name; do
        bootVolumeIds+=("$id")
        bootVolumeNames+=("$name")
    done < <(echo "$bootVolumes" | jq -r '.data[] | "\(.id)\t\(.["display-name"])"')
    echo "completed" 
    # for i in "${!bootVolumeIds[@]}"; do
    #     echo "ID: ${bootkVolumeIds[$i]}, Name: ${bootVolumeNames[$i]}"
    # done
}

function getblockvolumeinfo() {
    echo -en "Getting block volume info from volume group..." 
	blockVolumes=$(oci bv volume list --volume-group-id "$VOLUMEGROUP" 2>>migration.log)
	if [ "$?" != "0" ]; then 
		echo "Error encountered:" $blockVolumes
		exit 1
	fi
	#echo $blockVolumes

    while IFS=$'\t' read -r id name; do
        blockVolumeIds+=("$id")
        blockVolumeNames+=("$name")
    done < <(echo "$blockVolumes" | jq -r '.data[] | "\(.id)\t\(.["display-name"])"')

    # for i in "${!blockVolumeIds[@]}"; do
    #     echo "ID: ${blockVolumeIds[$i]}, Name: ${blockVolumeNames[$i]}"
    # done
    echo "completed" 
}


function createtargetbootvolumes() {
	echo -en "Creating boot volumes in target tenancy...\n" 
    for i in "${!bootVolumeIds[@]}"; do
        # echo "ID: ${bootVolumeIds[$i]}, Name: ${bootVolumeNames[$i]}"
        replicationOutput=$(oci bv boot-volume create --source-boot-volume-id "${bootVolumeIds[$i]}" --compartment-id "$TARGETCOMPARTMENT" --display-name "${bootVolumeNames[$i]}" 2>>migration.log)
        echo -e "\tReplicated ${bootVolumeNames[$i]}..."
        # echo "Replication: $replicationOutput"
    done
}

function createtargetblockvolumes() {
	echo -en "Creating block volumes in target tenancy...\n" 
    for i in "${!blockVolumeIds[@]}"; do
        # echo "ID: ${blockVolumeIds[$i]}, Name: ${blockVolumeNames[$i]}"
        replicationOutput=$(oci bv volume create --source-volume-id "${blockVolumeIds[$i]}" --compartment-id "$TARGETCOMPARTMENT" --display-name "${blockVolumeNames[$i]}" 2>>migration.log)
        echo -e "\tReplicated ${blockVolumeNames[$i]}..."
        # echo "Replication: $replicationOutput"
    done
}

echo -e "Migration complete!"

intro
readini
getbootvolumeinfo
getblockvolumeinfo
createtargetbootvolumes
createtargetblockvolumes