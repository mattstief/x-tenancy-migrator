import oci
import configparser
import sys


config = oci.config.from_file(profile_name='BRANDON')


def intro():
    print(f'x-tenancy-migrator v0.2')

def read_config():
    print("Reading configuration.ini...")
    config_parser = configparser.ConfigParser()
    config_parser.read('configuration.ini')
    volume_group = config_parser['DEFAULT']['VOLUMEGROUP']
    target_compartment = config_parser['DEFAULT']['TARGETCOMPARTMENT']
    source_compartment = config_parser['DEFAULT']['SOURCECOMPARTMENT']
    print("completed\n")
    print(f"Source Boot Volume Group OCID: {volume_group}")
    print(f"Target Compartment OCID: {target_compartment}")
    print("\n\n")
    return volume_group, target_compartment, source_compartment

def get_boot_volumes_in_compartment(compartment):
    print(f"Getting boot volume info in compartment {compartment}...")
    bv_client = oci.core.BlockstorageClient(config)
    boot_volumes = bv_client.list_boot_volumes(compartment_id=compartment).data
    return boot_volumes

def get_volumes_in_compartment(compartment):
    print(f"Getting block volume info in compartment {compartment}...")
    bv_client = oci.core.BlockstorageClient(config)
    volumes = bv_client.list_volumes(compartment_id=compartment, lifecycle_state="AVAILABLE").data
    return volumes

def get_instance_info_from_compartment(compartment):
    print("Getting compute info from compartment...")
    compute_client = oci.core.ComputeClient(config)
    try:
        instances = compute_client.list_instances(compartment)
        for vm in instances.data:
            print(f'\tinstance id: {vm.id}\tinstance name: {vm.display_name}')
    except Exception as e:
        print(f"Error encountered getting instance info: {e}")
        sys.exit(1)

def create_target_boot_volumes(target_compartment, boot_volumes):
    print("Creating boot volumes in target tenancy...")
    bv_client = oci.core.BlockstorageClient(config)
    for boot_volume in boot_volumes:
        try:
            boot_volume_source_details = oci.core.models.BootVolumeSourceFromBootVolumeDetails(id=boot_volume.id)
            replication_output = bv_client.create_boot_volume(
                oci.core.models.CreateBootVolumeDetails(
                    source_details=boot_volume_source_details,
                    compartment_id=target_compartment,
                    display_name=boot_volume.display_name
                )
            )
            print(f"\tReplicated {boot_volume.display_name}...")
        except Exception as e:
            print(f"Error encountered while replicating {boot_volume.display_name}: {e}")
            sys.exit(1)

def create_target_volumes(target_compartment, volumes):
    print("Creating block volumes in target tenancy...")
    bv_client = oci.core.BlockstorageClient(config)
    for volume in volumes:
        try:
            volume_source_details = oci.core.models.VolumeSourceFromVolumeDetails(id=volume.id)
            replication_output = bv_client.create_volume(
                oci.core.models.CreateVolumeDetails(
                    source_details=volume_source_details,
                    compartment_id=target_compartment,
                    display_name=volume.display_name
                )
            )
            print(f"\tReplicated {volume.display_name}...")
        except Exception as e:
            print(f"Error encountered while replicating {volume.display_name}: {e}")
            sys.exit(1)

def delete_boot_volumes_in_compartment(compartment, boot_volumes):
    print(f"Deleting boot volumes in compartment {compartment}...")
    bv_client = oci.core.BlockstorageClient(config)
    for boot_volume in boot_volumes:
        bv_client.delete_boot_volume(boot_volume_id=boot_volume.id)
        print(f"\tDeleted boot volume {boot_volume.id}")

def delete_volumes_in_compartment(compartment, volumes):
    print(f"Deleting block volumes in compartment {compartment}...")
    bv_client = oci.core.BlockstorageClient(config)
    for volume in volumes:
        bv_client.delete_volume(volume_id=volume.id)
        print(f"\tDeleted volume {volume.id}")

def main():
    intro()

    volume_group, target_compartment, source_compartment = read_config()

    ### uncomment this block to delete volumes in target compartment ###
    # target_boot_volumes = get_boot_volumes_in_compartment(target_compartment)
    # target_volumes = get_volumes_in_compartment(target_compartment)
    # delete_boot_volumes_in_compartment(target_compartment, target_boot_volumes)
    # delete_volumes_in_compartment(target_compartment, target_volumes)
    # return

    source_boot_volumes = get_boot_volumes_in_compartment(source_compartment)
    source_volumes = get_volumes_in_compartment(source_compartment)
    create_target_boot_volumes(target_compartment, source_boot_volumes)
    create_target_volumes(target_compartment, source_volumes)
    # get_instance_info_from_compartment(source_compartment)

    print("Migration complete!")

if __name__ == "__main__":
    main()