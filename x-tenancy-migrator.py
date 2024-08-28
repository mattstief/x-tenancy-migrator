import oci
import configparser
import sys

boot_volume_ids = []
boot_volume_names = []
block_volume_ids = []
block_volume_names = []

config = oci.config.from_file(profile_name='BRANDON')


def intro():
    print(f'x-tenancy-migrator v0.2')

def read_config():
    print("Reading config.ini...")
    config_parser = configparser.ConfigParser()
    config_parser.read('config.ini')
    volume_group = config_parser['DEFAULT']['VOLUMEGROUP']
    target_compartment = config_parser['DEFAULT']['TARGETCOMPARTMENT']
    print("completed\n")
    print(f"Source Boot Volume Group OCID: {volume_group}")
    print(f"Target Compartment OCID: {target_compartment}")
    print("\n\n")
    return volume_group, target_compartment

def get_boot_volume_info(volume_group, target_compartment):
    print("Getting boot volume info from volume group...")
    try:
        bv_client = oci.core.BlockstorageClient(config)
        print(f'volume group ID: {volume_group}')
        print(f'tenancy OCID: {config['tenancy']}')
        boot_volumes = bv_client.list_boot_volumes(volume_group_id=volume_group)
        
        for bv in boot_volumes.data:
            boot_volume_ids.append(bv.id)
            boot_volume_names.append(bv.display_name)
    except Exception as e:
        print(f"Error encountered getting boot volume info: {e}")
        sys.exit(1)
    
    print("completed")

def get_block_volume_info(volume_group):
    print("Getting block volume info from volume group...")
    try:
        bv_client = oci.core.BlockstorageClient(config)
        block_volumes = bv_client.list_volumes(volume_group_id=volume_group)
        
        for bv in block_volumes.data:
            block_volume_ids.append(bv.id)
            block_volume_names.append(bv.display_name)
        
        print("completed")
    except Exception as e:
        print(f"Error encountered getting block volume info: {e}")
        sys.exit(1)

def create_target_boot_volumes(target_compartment):
    print("Creating boot volumes in target tenancy...")
    bv_client = oci.core.BlockstorageClient(config)
    for i in range(len(boot_volume_ids)):
        try:
            boot_volume_source_details = oci.core.models.BootVolumeSourceFromBootVolumeDetails(id=boot_volume_ids[i])
            replication_output = bv_client.create_boot_volume(
                oci.core.models.CreateBootVolumeDetails(
                    source_details=boot_volume_source_details,
                    compartment_id=target_compartment,
                    display_name=boot_volume_names[i]
                )
            )
            print(f"\tReplicated {boot_volume_names[i]}...")
        except Exception as e:
            print(f"Error encountered while replicating {boot_volume_names[i]}: {e}")
            sys.exit(1)

def create_target_block_volumes(target_compartment):
    print("Creating block volumes in target tenancy...")
    bv_client = oci.core.BlockstorageClient(config)
    for i in range(len(block_volume_ids)):
        try:
            block_volume_source_details = oci.core.models.VolumeSourceFromVolumeDetails(id=block_volume_ids[i])
            replication_output = bv_client.create_volume(
                oci.core.models.CreateVolumeDetails(
                    source_details=block_volume_source_details,
                    compartment_id=target_compartment,
                    display_name=block_volume_names[i]
                )
            )
            print(f"\tReplicated {block_volume_names[i]}...")
        except Exception as e:
            print(f"Error encountered while replicating {block_volume_names[i]}: {e}")
            sys.exit(1)

def main():
    intro()
    volume_group, target_compartment = read_config()
    get_boot_volume_info(volume_group, target_compartment)
    get_block_volume_info(volume_group)
    create_target_boot_volumes(target_compartment)
    create_target_block_volumes(target_compartment)
    print("Migration complete!")

if __name__ == "__main__":
    main()